#This contains routes for both the chatbots
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Company, FAQ, Suggestion, Ticket, ChatLog
from app.services.ai_chat import customer_chatbot_answer
from app.services.ai_assist import generate_agent_suggestion
from app.utils.database import db

chatbot_bp = Blueprint('chatbot', __name__)

#CUSTOMER CHATBOT
'''
This is a protected route which can only be used by the customer
it takes only one data as its input message
and feeds faqs, articles and input message to,
ai_chat.py file in the services directory and rest is handled there
Adds each conversation in chatlog
finally this returns the appropriate answer given by our chatbot
'''
@chatbot_bp.route('/customer-chat', methods=['POST'])
@jwt_required()
def customer_chat():
    #fetch post data
    data = request.get_json()
    input_text = data.get('input_text')
    #check missing data
    if not input_text:
        return jsonify({'error': 'Missing input text'}), 400
    #check if user is customer
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "customer":
        return jsonify({'error': 'Unauthorized'}), 403

    #get company details
    company = Company.query.get(user.company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404

    #fetch faqs and suggestions for this company
    faqs = [(faq.question, faq.answer) for faq in FAQ.query.filter_by(company_id=company.id).all()]
    #fetch recent chatbot chats for context
    recent_chats = (
        ChatLog.query.filter_by(user_id=user.id)
        .order_by(ChatLog.created_at.desc())
        .limit(5)
        .all()
    )
    #call chatbot function
    response_text = customer_chatbot_answer(user, 
                                           {'id': company.id, 'name': company.name, 'description': company.description},
                                           input_text, faqs, recent_chats)

    chat = ChatLog(
        user_id = user_id,
        company_id = user.company_id,
        input_text = input_text,
        response_text = response_text
    )
    db.session.add(chat)
    db.session.commit()
    return jsonify({'response': response_text}), 200


#AGENT-CHATBOT
'''
Here agent can post a question alongwith providing ticket id of relevant ticket and chatbot will answer it
protected route: for agent only
gives context as the ticket assigned(ticket id must be input)
takes a question
outputs a response
'''
@chatbot_bp.route('/agent_chatbot/<int:ticket_id>', methods=['POST'])
@jwt_required()
def agent_chatbot(ticket_id):
    #use token to get user id as well as get ticket reference (from the agent only)
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    ticket = Ticket.query.get(ticket_id)
    #check if user id is of an agent which was assigned to this ticket id
    if not ticket or ticket.suggested_agent_id != user_id:
        return jsonify({'error': 'Unauthorized or invalid ticket'}), 403
    #fetch post data and check if missing
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    #generate ai answer suggestion
    answer_data = generate_agent_suggestion(ticket_id, user_id, question)
    return answer_data