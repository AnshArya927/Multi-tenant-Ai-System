#AGENT CHATBOT
from transformers import pipeline
from datetime import datetime
from app.utils.database import db
from app.services.embedding_model import get_semantic_top_k
from app.models import Suggestion, Ticket, Company, TicketMessage, Article, FAQ, ChatLog, User

#Model used
pipe = pipeline("text-generation", model="gpt2", max_new_tokens=100)

#gets context as company details, similar faqs and articles, similar suggestions, recent chats and ticket details
def get_context(ticket_id,question):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return None

    company = Company.query.get(ticket.company_id)
    chat = TicketMessage.query.filter_by(ticket_id=ticket.id).order_by(TicketMessage.sent_at.desc()).limit(5).all()
    chat_logs = ChatLog.query.filter_by(user_id=ticket.customer_id).order_by(ChatLog.created_at.desc()).limit(5).all()
    articles = Article.query.filter_by(company_id=company.id).all()
    faqs = FAQ.query.filter_by(company_id=company.id).all()
    suggestions = Suggestion.query.join(User, Suggestion.agent_id == User.id).filter(User.company_id == company.id).all()
    
    query_text = f"{ticket.subject or ''} {ticket.description or ''}"

    article_texts = [f"{a.title}: {a.content}" for a in articles]
    top_articles = get_semantic_top_k(query_text, article_texts, top_k=1)

    faq_pairs = [(f.question, f.answer) for f in faqs]
    faq_texts = [f"{q} {a}" for q, a in faq_pairs]
    top_faq_texts = get_semantic_top_k(query_text, faq_texts, top_k=5)
    
    suggestion_texts = [s.suggestion for s in suggestions]
    top_suggestions = get_semantic_top_k(query_text, suggestion_texts, top_k=5)
    
    return {
        "company_name": company.name,
        "company_description": company.description,
        "subject": ticket.subject,
        "description": ticket.description,
        "chat": [m.message for m in reversed(chat)],
        "chat_history": [f"User: {cl.input_text}\nBot: {cl.response_text}" for cl in reversed(chat_logs)],
        "articles": top_articles,
        "faqs": [faq for faq in faq_pairs if f"{faq[0]} {faq[1]}" in top_faq_texts],
        "suggestions": top_suggestions,
        "question": question
    }

#builds prompt out of context
def build_agent_prompt(context):
    if not context:
        return "No context available."

    prompt_parts = [
        f"Company: {context.get('company_name', 'N/A')}",
        f"Description: {context.get('company_description', 'N/A')}",

        f"\nTicket Subject: {context.get('subject', 'N/A')}",
        f"Ticket Description: {context.get('description', 'N/A')}",

        "\nRecent Chat:",
        "\n".join(f"- {line}" for line in context.get("chat", [])),

        "\nRecent Chat History:",
        "\n".join(f"- {line}" for line in context.get("chat_history", [])),

        "\nRelevant Articles:",
        "\n".join(f"- {article}" for article in context.get("articles", [])),

        "\nRelevant FAQs:"
    ]

    for q, a in context.get("faqs", []):
        prompt_parts.append(f"Q: {q}\nA: {a}")

    prompt_parts.append("\nPrevious Suggestions:")
    prompt_parts += [f"- {suggestion}" for suggestion in context.get("suggestions", [])]

    prompt_parts.append(f"\nAgent's Question: {context.get('question')}")

    return "\n".join(prompt_parts).strip()

#generates ai response, adds it to suggestions database (sufficient to create one suggestion)
def generate_agent_suggestion(ticket_id, agent_id, question):
    context = get_context(ticket_id,question)
    prompt = build_agent_prompt(context)
    suggestion = pipe(prompt)[0]["generated_text"]

    s = Suggestion(ticket_id=ticket_id, agent_id=agent_id, suggestions=suggestion, created_at=datetime.utcnow())
    db.session.add(s)
    db.session.commit()

    return {"suggestion": suggestion}

