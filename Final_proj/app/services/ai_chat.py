#CUSTOMER-CHATBOT
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import util
from app.services.embedding_model import get_semantic_top_k,semantic_model
from app.services.ticket_automation import create_fallback_ticket


tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
generation_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

#collects nessecary data for building context
'''
builds context based on company name and description, top faqs,
recent customer chatbot interaction(for continuity and relevence) and customer's query
'''
def build_customer_prompt_context(recent_chats, company, customer_query, faqs):
    #gets semantically similar faqs(10)
    faq_texts = [f"{q} - {a}" for q, a in faqs]
    top_faqs = get_semantic_top_k(customer_query, faq_texts, top_k=10)
    #build context
    context = f"""Company: {company.name}
    Description: {company.description}

    FAQs:
    """
    for faq in top_faqs:
        context += f"- {faq}\n"

    context += "\nRecent Conversations:\n"
    for chat in recent_chats:
        context += f"Customer: {chat.input_text}\nBot: {chat.response_text}\n"
    

    context += f"\nCustomer Question: {customer_query}\n"

    return context.strip()

#generates response based on context
def generate_ai_answer(prompt, max_tokens=256):
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids
    outputs = generation_model.generate(input_ids, max_length=max_tokens, temperature=0.7, top_p=0.9)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


#check for fallback
'''
This checks the user's query for phrases or patterns which leads to fallback
If this occurs a ticket is created and sent to the agent.
'''
def needs_fallback(user_query, threshold=0.75):
    fallback_phrases = [
        "human help", "talk to agent", "speak to representative",
        "raise a ticket", "need agent", "not helpful", "can't solve",
        "still stuck", "want to complain", "manual support"
    ]

    top_match = get_semantic_top_k(user_query, fallback_phrases, top_k=1)[0]
    similarity_score = util.cos_sim(
        semantic_model.encode(user_query, convert_to_tensor=True),
        semantic_model.encode(top_match, convert_to_tensor=True)
    ).item()

    return similarity_score >= threshold


#calls above functions to work in order and gives final response
def customer_chatbot_answer(user, company, query, faqs, recent_chats):
    if needs_fallback(query):
        ticket = create_fallback_ticket(user, company.id, query)
        return f"It seems you need further help. A support ticket has been created (Ticket ID: {ticket.id}). Our team will get back to you shortly."
    context = build_customer_prompt_context(recent_chats,company, query, faqs)
    response = generate_ai_answer(context)
    return response
