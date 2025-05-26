#This provides the feedback route for both customer and agent
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Feedback, User, Ticket, Suggestion, ChatLog
from app.utils.database import db
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

#FEEDBACK
'''
This is a protected route for all users.
they can give their feedback on,
Tickets,
customer can give feedback on customer-chatbot's response but provide neccesary related id
agents can give feedback on suggestions or agent-chatbot response but provide neccesary related id
it updates feedback table as neccesary( sufficient)
'''
@feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    #get user from token
    user_id = int(get_jwt_identity())
    data = request.json

    #request post data
    feedback_type = data.get('feedback_type')
    rating = data.get('rating')
    #handle missing data and data appropriateness
    if feedback_type not in ('ticket', 'AI_answer', 'suggestion'):
        return jsonify({'error': 'Invalid feedback_type'}), 400
    if rating is None:
        return jsonify({'error': 'Rating is required'}), 400

    #optional data
    ticket_id = data.get('ticket_id')
    related_id = data.get('related_id')  # e.g. suggestion ID or chatlog ID
    comment = data.get('comment')

    #validate optional data if provided
    if ticket_id:
        if not Ticket.query.get(ticket_id):
            return jsonify({'error': 'Invalid ticket_id'}), 400

    if feedback_type == 'suggestion' and related_id:
        if not Suggestion.query.get(related_id):
            return jsonify({'error': 'Invalid related_id for suggestion'}), 400
    
    if feedback_type == 'AI_answer' and related_id:
        if not ChatLog.query.get(related_id):
            return jsonify({'error': 'Invalid related_id for suggestion'}), 400

    #add data to feedback
    feedback = Feedback(
        ticket_id=ticket_id,
        user_id=user_id,
        feedback_type=feedback_type,
        related_id=related_id,
        rating=rating,
        comment=comment,
        submitted_at=datetime.utcnow()
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'message': 'Feedback submitted successfully'}), 201
