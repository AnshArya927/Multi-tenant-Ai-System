from app.models import Ticket, User
from app.utils.database import db
from datetime import datetime
from transformers import pipeline

#model used for prioritization and categorization
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#labels required(can be extended)
labels_department = ["Billing", "Technical Support", "General Support"]
labels_urgency = ["low", "medium", "high"]

#ai_categorize_and_prioritize
def ai_categorize_and_prioritize(description):
    desc = description.lower()

    department_result = classifier(desc, labels_department)
    urgency_result = classifier(desc, labels_urgency)

    suggested_department = department_result['labels'][0]
    priority = urgency_result['labels'][0]

    return suggested_department, priority

def get_customer_priority_boost(customer_id):
    past_tickets = Ticket.query.filter_by(customer_id=customer_id).all()
    open_tickets = [t for t in past_tickets if t.status == 'open']
    escalated_tickets = [t for t in past_tickets if 'escalate' in (t.description or '').lower()]

    boost = 0
    if len(open_tickets) > 3:
        boost += 1
    if len(escalated_tickets) >= 1:
        boost += 1
    return boost


def estimate_resolution_time(priority):
    if priority == 'high':
        return 2.0
    elif priority == 'medium':
        return 8.0
    else:
        return 24.0

def assign_agent(company_id, suggested_department):
    agents = User.query.filter_by(company_id=company_id, role='agent', department=suggested_department).all()
    
    if not agents:
        agents = User.query.filter_by(company_id=company_id, role='agent').all()
    
    if not agents:
        return None
    
    agent_ticket_counts = {
        agent.id: Ticket.query.filter_by(suggested_agent_id=agent.id, status='open').count()
        for agent in agents
    }

    return min(agent_ticket_counts, key=agent_ticket_counts.get)

def create_fallback_ticket(user, company_id, description):
    suggested_department, ai_priority = ai_categorize_and_prioritize(description)
    history_boost = get_customer_priority_boost(user.id)

    # Convert to numeric scale
    priority_map = {'low': 1, 'medium': 2, 'high': 3}
    inverse_map = {1: 'low', 2: 'medium', 3: 'high'}

    adjusted_score = min(3, priority_map[ai_priority] + history_boost)
    final_priority = inverse_map[adjusted_score]

    estimated_resolution_hours = estimate_resolution_time(final_priority)
    suggested_agent_id = assign_agent(company_id, suggested_department)

    ticket = Ticket(
        customer_id=user.id,
        company_id=company_id,
        suggested_agent_id=suggested_agent_id,
        status="open",
        priority=final_priority,
        subject="Chatbot fallback",
        description=description,
        suggested_department=suggested_department,
        estimated_resolution_hours=estimated_resolution_hours,
        created_at=datetime.utcnow()
    )
    db.session.add(ticket)
    db.session.commit()
    return ticket
