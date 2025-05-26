#This file implements the authentication system (NOT for companies)
from flask import Blueprint, request, jsonify
from app.models import User,Company
from app.utils.database import db
from app.utils.security import hash_password, verify_password
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)


#REGISTER
'''
This is used for the registration of both the customers and the agents.
both must provide their name, email, password, role, company_id
customers should not provide department but it is must for agents.
this is sufficient to update the User Table.
THESE VALUES CANNOT BE CHANGED!!!
'''
@auth_bp.route('/register', methods=['POST'])
def register():
    #fetch post data
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    department = data.get('department')
    company_id = data.get('company_id')
    #check for missing and unique values
    if not all([name, email, password, role]):
        return jsonify({'error': 'Missing required fields'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409
    
    #check if role is customer or agent if yes, check if company id was provided and if it was valid
    role = role.lower()
    if role == 'agent' or role == 'customer':
        if not company_id:
            return jsonify({'error': 'company_id is required for agents'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Invalid company_id'}), 404
    else:
        return jsonify({'error': 'Invalid role'}), 400

    if role == 'agent' and not department:
        return jsonify({'error': 'Department is required for agents'}), 400

    #generate hashed password
    hashed_pw = hash_password(password)
    #add data to the Users Table
    new_user = User(
        name=name,
        email=email,
        password=hashed_pw,
        role=role,
        department=department,
        company_id=company_id
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f'{role.capitalize()} registered successfully', 'user_id': new_user.id}), 201


#USER LOGIN
'''
user must login to access their respective protected routes
based on the token user will be identified as customer or agent 
and will have access to their respective routes
this will allow them to use their chatbots or veiw their tickets
also to access customer or agent dashboard.
this only returns the token.
'''
@auth_bp.route('/login', methods=['POST'])
def login():
    #fetch post request
    data = request.json
    email = data.get('email')
    password = data.get('password')
    #check missing values
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    #access the user and verify email and password
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401
    #tokenise user.id
    access_token = create_access_token(identity=str(user.id))

    return jsonify(access_token=access_token), 200
