from sentence_transformers import SentenceTransformer, util

semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_semantic_top_k(query, texts, top_k=5):
    if not texts:
        return []

    query_embedding = semantic_model.encode(query, convert_to_tensor=True)
    text_embeddings = semantic_model.encode(texts, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, text_embeddings)[0]
    top_results = similarities.topk(k=top_k)

    return [texts[idx] for idx in top_results.indices]
