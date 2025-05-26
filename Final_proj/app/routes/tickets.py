#It handles ticket related routes(complete)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Ticket, TicketMessage, User
from app.utils.database import db
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__)

# Get all tickets for the logged-in user (role-based)
@tickets_bp.route('/tickets', methods=['GET'])
@jwt_required()
def get_tickets():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role == 'company_admin':
        tickets = Ticket.query.filter_by(company_id=user.company_id).all()
    elif user.role == 'agent':
        tickets = Ticket.query.filter_by(suggested_agent_id=user_id).all()
    else:
        tickets = Ticket.query.filter_by(customer_id=user_id).all()


    tickets_list = [{
        'id': t.id,
        'subject': t.subject,
        'status': t.status,
        'priority': t.priority,
        'created_at': t.created_at.isoformat(),
        'description': t.description,
        'customer_id': t.customer_id,
        'suggested_department': t.suggested_department,
        'suggested_agent_id': t.suggested_agent_id,
        'closed_at': t.closed_at.isoformat() if t.closed_at else None,
        'estimated_resolution_hours': t.estimated_resolution_hours
    } for t in tickets]


    return jsonify(tickets_list), 200

# Get one ticket in full detail.
@tickets_bp.route('/ticket-about/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    ticket = Ticket.query.get_or_404(ticket_id)

    if user.role == 'customer' and ticket.customer_id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    if user.role in ['agent', 'company_admin'] and ticket.company_id != user.company_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    ticket_messages = TicketMessage.query.filter_by(ticket_id=ticket_id).all()
    messages = [{
        'id': m.id,
        'sender_id': m.sender_id,
        'message': m.message,
        'created_at': m.sent_at.isoformat()
    } for m in ticket_messages]

    ticket_data = {
        'id': ticket.id,
        'subject': ticket.subject,
        'status': ticket.status,
        'priority': ticket.priority,
        'description': ticket.description,
        'created_at': ticket.created_at.isoformat(),
        'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None,
        'estimated_resolution_hours': ticket.estimated_resolution_hours,
        'customer_id': ticket.customer_id,
        'company_id': ticket.company_id,
        'suggested_department': ticket.suggested_department,
        'suggested_agent_id': ticket.suggested_agent_id,
        'messages': messages
    }


    return jsonify(ticket_data), 200

# Add a reply to a ticket (agent or customer)
@tickets_bp.route('/ticket-reply/<int:ticket_id>/messages', methods=['POST'])
@jwt_required()
def add_ticket_message(ticket_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.json
    message_text = data.get('message')
    
    if not message_text:
        return jsonify({'error': 'Message content is required'}), 400

    ticket = Ticket.query.get_or_404(ticket_id)

    if user.role == 'customer' and ticket.customer_id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    if user.role in ['agent', 'company_admin'] and ticket.company_id != user.company_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    new_message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        message=message_text,
        sent_at=datetime.utcnow()
    )
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'Message added to ticket'}), 201

# Updates status and priority of a ticket (agent or company_admin)
@tickets_bp.route('/ticket-up/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.json

    ticket = Ticket.query.get_or_404(ticket_id)

    if user.role not in ['agent', 'company_admin']:
        return jsonify({'error': 'Unauthorized'}), 403

    if ticket.company_id != user.company_id:
        return jsonify({'error': 'Unauthorized'}), 403

    status = data.get('status')
    priority = data.get('priority')
    est_res_hours = data.get('estimated_resolution_hours')
    
    ALLOWED_STATUSES = {'open', 'closed'}
    ALLOWED_PRIORITIES = {'low', 'medium', 'high'}

    if status is not None and status not in ALLOWED_STATUSES:
        return jsonify({'error': 'Invalid status value'}), 400
    if priority is not None and priority not in ALLOWED_PRIORITIES:
        return jsonify({'error': 'Invalid priority value'}), 400

    
    if est_res_hours is not None:
        try:
            est_res_hours = float(est_res_hours)
            if est_res_hours < 0:
                raise ValueError()
        except ValueError:
            return jsonify({'error': 'Invalid estimated_resolution_hours value'}), 400

    
    if est_res_hours is not None:
        ticket.estimated_resolution_hours = est_res_hours

    if ticket.status == 'closed' and status == 'open':
        ticket.closed_at = None
    elif ticket.status == 'open' and status == 'closed':
        ticket.closed_at = datetime.utcnow()

    
    if status:
        ticket.status = status
    if priority:
        ticket.priority = priority

    db.session.commit()

    return jsonify({'message': 'Ticket updated'}), 200
