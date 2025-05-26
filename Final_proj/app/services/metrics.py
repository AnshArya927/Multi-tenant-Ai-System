#Calculate agent performance(AI Powered)
from datetime import datetime
from app.models import Ticket,TicketMessage, PerformanceMetric, Feedback, Suggestion
from app.utils.database import db
from sqlalchemy import func
from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

#time taken to resolve a ticket
def calculate_avg_response_time(agent_id):
    tickets = Ticket.query.filter_by(suggested_agent_id=agent_id).filter(Ticket.status == 'closed').all()
    if not tickets:
        return None
    total_time = 0
    count = 0
    for ticket in tickets:
        if ticket.created_at and ticket.closed_at:
            diff = (ticket.closed_at - ticket.created_at).total_seconds() / 3600  # in hours
            total_time += diff
            count += 1
    return total_time / count if count > 0 else None

#closed tickets out of all tickets assigned
def calculate_resolution_rate(agent_id):
    total = Ticket.query.filter_by(suggested_agent_id=agent_id).count()
    if total == 0:
        return None
    closed = Ticket.query.filter_by(suggested_agent_id=agent_id, status='closed').count()
    return closed / total

#sentiment score based on feedback of customer
def calculate_sentiment_score(agent_id):
    feedbacks = Feedback.query.join(Ticket, Feedback.ticket_id == Ticket.id).filter(
        Ticket.suggested_agent_id == agent_id,
        Feedback.comment.isnot(None)
    ).all()

    if not feedbacks:
        return None

    scores = []
    for f in feedbacks:
        try:
            result = sentiment_analyzer(f.comment[:512])[0]  # truncate to avoid model limits
            if result['label'] == 'POSITIVE':
                scores.append(result['score'])
            elif result['label'] == 'NEGATIVE':
                scores.append(1 - result['score'])
            else:  # NEUTRAL
                scores.append(0.5)
        except:
            continue

    return sum(scores) / len(scores) if scores else None


#politeness score based on conversation with customer
def score_politeness(agent_id,limit=5) -> float:
    messages = (
        TicketMessage.query
        .join(Ticket, TicketMessage.ticket_id == Ticket.id)
        .filter(Ticket.suggested_agent_id == agent_id)
        .order_by(TicketMessage.sent_at.desc())
        .limit(limit)
        .all()
    )

    chat_history = [
        f"{msg.sender.lower()}: {msg.message.strip()}" for msg in reversed(messages)
    ]
    combined_text = " ".join(chat_history)
    candidate_labels = ["polite", "impolite"]

    result = classifier(combined_text, candidate_labels)
    
    if "polite" in result['labels']:
        index = result['labels'].index("polite")
        politeness_score = result['scores'][index]
    else:
        politeness_score = 0.0

    return politeness_score

#average of total rating (out of 5)
def calculate_avg_feedback_rating(agent_id):
    feedbacks = Feedback.query.join(Ticket, Feedback.ticket_id == Ticket.id).filter(
        Ticket.suggested_agent_id == agent_id,
        Feedback.rating.isnot(None)
    ).all()
    if not feedbacks:
        return None
    total_rating = sum(f.rating for f in feedbacks)
    return total_rating / len(feedbacks)

def count_suggestions_made(agent_id):
    return Suggestion.query.filter_by(agent_id=agent_id).count()

def count_tickets_open(agent_id):
    return Ticket.query.filter_by(suggested_agent_id=agent_id, status='open').count()

def count_tickets_closed(agent_id):
    return Ticket.query.filter_by(suggested_agent_id=agent_id, status='closed').count()

#customer satisfaction score(based on above metrics)(weighted average)
def calculate_csat_score(
    avg_response_time: float,
    resolution_rate: float,
    sentiment_score: float,
    avg_feedback_rating: float,
    politeness_score: float
) -> float:
    """
    Calculate CSAT score based on weighted combination of agent metrics.
    Lower response time and higher values in other metrics are preferred.
    All weights should add up to 1.
    """

    # Define safe default ranges and handle None
    if avg_response_time is None:
        avg_response_time = 24  # max allowable
    if resolution_rate is None:
        resolution_rate = 0
    if sentiment_score is None:
        sentiment_score = 0.5
    if avg_feedback_rating is None:
        avg_feedback_rating = 2.5
    if politeness_score is None:
        politeness_score = 0.5

    # Normalize metrics to 0-1 scale
    normalized_response = max(0, min(1, 1 - (avg_response_time / 24)))
    normalized_feedback = avg_feedback_rating / 5.0

    # Weights for metrics
    weights = {
        "response": 0.2,
        "resolution": 0.2,
        "sentiment": 0.2,
        "feedback": 0.2,
        "politeness": 0.2
    }

    csat_score = (
        normalized_response * weights["response"] +
        resolution_rate * weights["resolution"] +
        sentiment_score * weights["sentiment"] +
        normalized_feedback * weights["feedback"] +
        politeness_score * weights["politeness"]
    )

    return round(csat_score * 100, 2)  # CSAT on 0-100 scale


def get_agent_performance_summary(agent_id):
    avg_response_time = calculate_avg_response_time(agent_id)
    resolution_rate = calculate_resolution_rate(agent_id)
    sentiment_score = calculate_sentiment_score(agent_id)
    avg_feedback_rating = calculate_avg_feedback_rating(agent_id)
    suggestions_made = count_suggestions_made(agent_id)
    tickets_open = count_tickets_open(agent_id)
    tickets_closed = count_tickets_closed(agent_id)
    politeness_score = score_politeness(agent_id)
    csat_score = calculate_csat_score(avg_response_time,resolution_rate,sentiment_score,avg_feedback_rating,politeness_score)
    perf_metric = PerformanceMetric.query.filter_by(agent_id=agent_id).first()
    if not perf_metric:
        perf_metric = PerformanceMetric(agent_id=agent_id)
    
    perf_metric.avg_response_time = avg_response_time
    perf_metric.resolution_rate = resolution_rate
    perf_metric.sentiment_score = sentiment_score
    perf_metric.avg_feedback_rating = avg_feedback_rating
    perf_metric.suggestions_made = suggestions_made
    perf_metric.tickets_open = tickets_open
    perf_metric.tickets_closed = tickets_closed
    perf_metric.politeness_score = politeness_score
    perf_metric.csat_score = csat_score
    perf_metric.analyzed_at = datetime.utcnow()

    db.session.add(perf_metric)
    db.session.commit()

    return {
        "avg_response_time_hours": round(avg_response_time, 2) if avg_response_time else None,
        "resolution_rate_percent": round(resolution_rate * 100, 2) if resolution_rate else None,
        "sentiment_score": round(sentiment_score, 2) if sentiment_score else None,
        "politeness_score": round(politeness_score, 2) if politeness_score else None,
        "avg_feedback_rating": round(avg_feedback_rating, 2) if avg_feedback_rating else None,
        "suggestions_made": suggestions_made,
        "tickets_open": tickets_open,
        "tickets_closed": tickets_closed,
        "csat_score": csat_score,
        "analyzed_at": perf_metric.analyzed_at.isoformat(),
    }
