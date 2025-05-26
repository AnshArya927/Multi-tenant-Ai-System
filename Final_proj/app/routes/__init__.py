from flask import Blueprint

from .auth import auth_bp
from .dashboard import dashboard_bp
from .chatbot import chatbot_bp
from .tickets import tickets_bp
from .admin import admin_bp
from .feedback import feedback_bp

all_blueprints = [
    auth_bp,
    dashboard_bp,
    chatbot_bp,
    tickets_bp,
    admin_bp,
    feedback_bp
]
