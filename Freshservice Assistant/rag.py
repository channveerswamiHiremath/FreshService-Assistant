import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

class FreshserviceRAG:
    def __init__(self, docs_file: str):
        """Load docs + embeddings"""
        self.docs_file = docs_file
        self.text_chunks = []
        self.embeddings = None

        print("Loading documentation...")
        with open(docs_file, "r", encoding="utf-8") as f:
            self.docs_data = json.load(f)

        # Convert docs to searchable chunks
        for section in self.docs_data:
            title = section.get("section", "Unknown")
            for item in section.get("content", []):
                if isinstance(item, str):
                    self.text_chunks.append({"section": title, "content": item})
                elif isinstance(item, dict) and "table" in item:
                    table_text = "\n".join([" | ".join(row) for row in item["table"]])
                    self.text_chunks.append({"section": title, "content": table_text})

        print(f"✅ Loaded {len(self.text_chunks)} chunks")

        # Embeddings
        print("Creating embeddings...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [c["content"] for c in self.text_chunks]
        self.embeddings = model.encode(texts, show_progress_bar=False)
        self.model = model
        print("✅ Embeddings ready")

        # Initialize Gemini
        self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini API"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key =  os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("No GEMINI_API_KEY found.")
                self.gemini_model = None
                return
                
            genai.configure(api_key=api_key)
            
            # Try different model names that are available
            model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            
            for model_name in model_names:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    # Test the model with a simple query
                    test_response = self.gemini_model.generate_content("Hello")
                    print(f" Gemini model '{model_name}' ready")
                    break
                except Exception as model_error:
                    print(f" Model '{model_name}' failed: {model_error}")
                    continue
            else:
                print(" No available Gemini models found")
                self.gemini_model = None
                
        except Exception as e:
            print(f" Error initializing Gemini: {e}")
            self.gemini_model = None

    def search(self, query: str, top_k: int = 3):
        """Retrieve top-k relevant chunks"""
        q_emb = self.model.encode([query])
        sims = cosine_similarity(q_emb, self.embeddings)[0]
        top_idx = sims.argsort()[::-1][:top_k]
        results = []
        for i in top_idx:
            results.append((self.text_chunks[i], float(sims[i])))
        return results

    def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using Gemini, with fallback for general queries"""
        if not self.gemini_model:
            return f"Based on the documentation:\n\n{context[:500]}..."

    # Check for very general queries
        general_words = ["help", "hello", "hi", "support", "how are you", "can you help me"]
        if any(word in query.lower() for word in general_words) and len(query.split()) <= 5:
            return "Hello! I can help answer questions specifically about the Freshservice API documentation. Please ask a more specific question, like 'How do I create a ticket using curl?'"

        try:
            prompt = f"""You are a professional assistant. Answer clearly, accurately, and in simple English.
                        Provide a helpful answer with any relevant code examples or commands if needed. Be specific and practical.
Documentation:
{context}

Question: {query}
"""
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                'temperature': 0.3,
                'max_output_tokens': 500,
                }
            )

            if response.text:
                return response.text.strip()
            else:
                return f"Based on the documentation:\n\n{context[:500]}..."
            
        except Exception as e:
            print(f"Error with Gemini: {e}")
            return f"Based on the documentation:\n\n{context[:500]}..."


    def answer_query(self, query: str):
        """Answer query using Gemini with retrieved context"""
        docs = self.search(query, top_k=3)
        if not docs:
            return {
                "query": query,
                "answer": "No relevant information found in documentation.",
                "sources": [],
                "confidence": 0.0,
            }

        # Build context from retrieved documents
        context = ""
        for i, (doc, score) in enumerate(docs, 1):
            context += f"{doc['content']}\n\n"

        # Generate answer using Gemini
        answer = self._generate_answer(query, context)

        # Prepare sources for UI
        sources = [
            {
                "section": d["section"],
                "content_preview": d["content"][:150],
                "confidence": round(s, 2),
            }
            for d, s in docs
        ]

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
           "confidence": round(docs[0][1], 2) if docs and docs[0][1] > 0.5 else None,
        }


# Example usage
if __name__ == "__main__":
    docs_file = "output/freshservice_docs.json"
    if not os.path.exists(docs_file):
        print("Docs file not found. Run scraper first.")
    else:
        rag = FreshserviceRAG(docs_file)
        q = "Give me the curl command to create a ticket"
        result = rag.answer_query(q)
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")