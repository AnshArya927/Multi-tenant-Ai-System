#This is the route for the dashboards and first veiw of all types of users(complete)
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Ticket, FAQ, Feedback, PerformanceMetric, ChatLog, Article, Suggestion
from app.utils.database import db
from sqlalchemy import func, desc
from app.services.metrics import get_agent_performance_summary
dashboard_bp = Blueprint('dashboard', __name__)


#DASHBOARD USER-ROLE-BASED
'''
This route is used to implement the role based dashboard selection based on the user id.
This is protected route,
and user of a certain role can see data related to them only
'''
@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role == 'company_admin':
        return get_company_dashboard(user.company_id)
    elif user.role == 'agent':
        return get_agent_dashboard(user.id)
    elif user.role == 'customer':
        return get_customer_dashboard(user.id)
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    

#COMPANY DASHBOARD
'''
This dashboard is accessible to only the admins
it uses queries to fetch data and metrics about companies like,
total agents, total faqs, total articles, total tickets(open and closed), feedbacks and
average metrics of all their agents(Why do we even have this)
'''
def get_company_dashboard(company_id):
    total_agents = User.query.filter_by(company_id=company_id, role='agent').count()
    total_faqs = FAQ.query.filter_by(company_id=company_id).count()
    total_articles = Article.query.filter_by(company_id=company_id).count()
    total_tickets = Ticket.query.filter_by(company_id=company_id).count()
    
    open_tickets = Ticket.query.filter_by(company_id=company_id, status='open').count()
    closed_tickets = Ticket.query.filter_by(company_id=company_id, status='closed').count()
    
    feedbacks = Feedback.query.join(Ticket).filter(Ticket.company_id == company_id).all()
    avg_rating = sum(f.rating for f in feedbacks if f.rating is not None) / len(feedbacks) if feedbacks else None
    perf_metrics = PerformanceMetric.query.join(User).filter(User.company_id == company_id).all()

    avg_response_time = avg_resolution_rate = avg_csat_score = avg_politeness_score = None
    if perf_metrics:
        avg_response_time = sum(p.avg_response_time or 0 for p in perf_metrics) / len(perf_metrics)
        avg_resolution_rate = sum(p.resolution_rate or 0 for p in perf_metrics) / len(perf_metrics)
        avg_csat_score = sum(p.csat_score or 0 for p in perf_metrics) / len(perf_metrics)
        avg_politeness_score = sum(p.politeness_score or 0 for p in perf_metrics) / len(perf_metrics)


    top_3_department = db.session.query(
        Ticket.suggested_department, func.count(Ticket.suggested_department).label('count')
    ).filter(
        Ticket.company_id == company_id,
        Ticket.suggested_department.isnot(None)
    ).group_by(
        Ticket.suggested_department
    ).order_by(
        desc('count')
    ).limit(3)

    top_departments = [
        {'department': dep, 'count': count} for dep, count in top_3_department
    ] if top_3_department else []
    
    return jsonify({
        'total_agents': total_agents,
        'total_faqs': total_faqs,
        'total_articles': total_articles,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
        'average_feedback_rating': avg_rating,
        'avg_agent_response_time': avg_response_time,
        'avg_agent_resolution_rate': avg_resolution_rate,
        'avg_agent_csat_score': avg_csat_score,
        'avg_agent_politeness_score': avg_politeness_score,
        'most_suggested_department': top_departments
    })


#AGENT DASHBOARD
'''
This is protected for user role: agents
This simply uses the PerformanceMetric Table to access all the data and display them
'''
def get_agent_dashboard(agent_id):

    return jsonify(get_agent_performance_summary(agent_id))


#CUSTOMER DASHBOARD
'''
This is accessible only to customer.
It runs queries to generate data to display like,
tickets raised, ticket info, chatbot logs(10).
Can make this better
'''
def get_customer_dashboard(customer_id):
    tickets = Ticket.query.filter_by(customer_id=customer_id).all()
    tickets_info = []
    for ticket in tickets:
        feedback = Feedback.query.filter_by(ticket_id=ticket.id).first()
        tickets_info.append({
            'ticket_id': ticket.id,
            'status': ticket.status,
            'priority': ticket.priority,
            'subject': ticket.subject,
            'created_at': ticket.created_at.isoformat(),
            'estimated_resolution_hours': ticket.estimated_resolution_hours,
            'suggested_department': ticket.suggested_department,
            'suggested_agent_id': ticket.suggested_agent_id,
            'feedback_rating': feedback.rating if feedback else None,
            'feedback_comment': feedback.comment if feedback else None
        })

    chat_logs = ChatLog.query.filter_by(user_id=customer_id).order_by(ChatLog.created_at.desc()).limit(10).all()
    chat_history = [{'input': c.input_text, 'response': c.response_text, 'date': c.created_at.isoformat()} for c in chat_logs]

    return jsonify({
        'submitted_tickets': tickets_info,
        'recent_chat_logs': chat_history
    })
