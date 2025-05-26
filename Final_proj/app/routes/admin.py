#this file contains all routes related to company related work(completed)
from flask import Blueprint, request, jsonify
from app.utils.database import db
from app.models import Company, FAQ, User, Article
from app.utils.security import hash_password, verify_password
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity

# REGISTER_ADMIN(COMPANY)
'''
To Register a Company the admin needs to provide
company's name and description
(Required data for Company Table sufficient)
and his name, email and a password
(sufficient for User as role is defined, department must be null and company id is taken)
THESE VALUES CANNOT BE CHANGED!!!
'''
admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/admin', methods=['POST'])
def register_company():
    #getting post data
    data = request.get_json()
    #for company
    name = data.get('company_name')
    description = data.get('company_description')
    #for admin-user
    admin_name = data.get('name')
    admin_email = data.get('email')
    admin_password = data.get('password')

    # check for null and unique values
    if not name or not admin_email or not admin_password or not admin_name:
        return jsonify({'error': 'Company name and admin details are required'}), 400

    if Company.query.filter_by(name=name).first():
        return jsonify({'error': 'Company with this name already exists'}), 409
    
    if User.query.filter_by(email=admin_email).first():
        return jsonify({"error": "email already registered"}), 409

    #add data to company
    company = Company(name=name, description=description)
    db.session.add(company)
    db.session.flush()
    
    #generate admin password
    admin_password = hash_password(admin_password)
    #add data to user(about admin)
    admin_user = User(
        name=admin_name,
        email=admin_email,
        password=admin_password,
        role="company_admin",
        company_id=company.id
    )
    db.session.add(admin_user)
    db.session.commit()

    return jsonify({'message': 'Company registered successfully', 'company_id': company.id}), 201


#ADMIN(COMPANY) LOGIN
'''
admin must login to continue with company configuration tools
this will allow him to add faqs, articles and view them
also to access company dashboard.
this only returns the token.
'''
@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    #fetch post data
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    #check for missing data
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    #verify email and password
    user = User.query.filter_by(email=email, role='company_admin').first()
    if not user or not verify_password(user.password, password):
        return jsonify({'error': 'Invalid admin credentials'}), 401
    #create access token(This will create a token based on user_id(String value))
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'role': user.role})


#ADD FAQS
'''
This is a protected route and can only be accessed by company_admin.
This allows them to add FAQs related to the company
faqs added are in a very specific format(list of json)
admin must follow this or frontend must implement this.
'''
@admin_bp.route('/admin/add-faq', methods=['POST'])
@jwt_required()
def add_faq():
    #get user id back from the token
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    #check if logged in user is company admin
    if not user or user.role != 'company_admin':
        return jsonify({'error': 'Unauthorized'}), 403
    #request data as a question and answer
    data = request.get_json()
    faqs = data.get('faqs')
    if faqs and isinstance(faqs, list):
        for item in faqs:
            question = item.get('question')
            answer = item.get('answer')
        if question and answer:
            faq = FAQ(company_id=user.company_id, question=question, answer=answer)
            db.session.add(faq)
    db.session.commit()
    return jsonify({'message': 'FAQs added successfully'}), 201


#ADD ARTICLES
'''
This is a protected route and can only be accessed by company_admin.
This allows them to add articles, recent news, policies, terms and conditions,... related to the company.
Admin can only add one article at a time.
title, content and tags(optional) are sufficient to update Articles Table
'''
@admin_bp.route('/admin/add-article', methods=['POST'])
@jwt_required()
def add_article():
    #get user id back from the token
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    #check if logged in user is company_admin
    if not user or user.role != 'company_admin':
        return jsonify({'error': 'Unauthorized'}), 403
    #fetch post data
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    tags = data.get('tags')  # optional but its better to be appropriately tagged
    #check for null and unique values
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    #add data to Article
    article = Article(
        company_id=user.company_id,
        title=title,
        content=content,
        tags=tags
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({'message': 'Article added successfully'}), 201


#VIEW ARTICLES
'''
This is a protected route and can only be accessed by company_admin.
This allows them to view the articles.
This returns all the data(columns) of each and every article posted.(in json)
'''
@admin_bp.route('/admin/articles', methods=['GET'])
@jwt_required()
def get_articles():
    #get user id from token
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    #check if user is company admin
    if not user or user.role != 'company_admin':
        return jsonify({'error': 'Unauthorized'}), 403
    #Fetch all articles as a list(all columns)
    articles = Article.query.filter_by(company_id=user.company_id).all()
    return jsonify([
        {
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'tags': a.tags,
            'created_at': a.created_at.isoformat()
        }
        for a in articles
    ])  #Return as a list of json


#VIEW FAQS
'''
This is a protected route and can only be accessed by company_admin.
This allows them to view the faqs.
This returns all the data(columns) of each and every faq posted.(in json)
'''
@admin_bp.route('/admin/faqs', methods=['GET'])
@jwt_required()
def get_faqs():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != 'company_admin':
        return jsonify({'error': 'Unauthorized'}), 403

    faqs = FAQ.query.filter_by(company_id=user.company_id).all()
    return jsonify([
        {
            'id': f.id,
            'question': f.question,
            'answer': f.answer,
            'created_at': f.created_at.isoformat()
        }
        for f in faqs
    ])
