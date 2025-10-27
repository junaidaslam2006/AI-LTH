from rapidfuzz import fuzz, process
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class MedicineSearchEngine:
    def __init__(self):
        self.model = None
        self.embeddings_cache = {}
        
    def load_embedding_model(self):
        """Load sentence transformer model for semantic search"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully")
        except Exception as e:
            print(f"Could not load embedding model: {e}")
            self.model = None
    
    def fuzzy_search(self, query, candidates, threshold=70):
        """Fuzzy string matching"""
        result = process.extractOne(query, candidates, scorer=fuzz.ratio)
        if result and result[1] >= threshold:
            return result[0], result[1] / 100.0
        return None, 0.0
    
    def semantic_search(self, query, candidates, threshold=0.7):
        """Semantic search using embeddings"""
        if not self.model:
            return None, 0.0
        
        try:
            query_embedding = self.model.encode(query)
            candidate_embeddings = self.model.encode(candidates)
            
            # Calculate cosine similarity
            similarities = np.dot(candidate_embeddings, query_embedding) / (
                np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score >= threshold:
                return candidates[best_idx], float(best_score)
            
        except Exception as e:
            print(f"Semantic search error: {e}")
        
        return None, 0.0
    
    def hybrid_search(self, query, candidates, threshold=70):
        """Combine fuzzy and semantic search"""
        # Try fuzzy first (faster)
        fuzzy_result, fuzzy_score = self.fuzzy_search(query, candidates, threshold)
        
        if fuzzy_score > 0.85:  # High confidence
            return fuzzy_result, fuzzy_score
        
        # Try semantic search
        semantic_result, semantic_score = self.semantic_search(query, candidates, threshold=0.7)
        
        # Return best result
        if semantic_score > fuzzy_score:
            return semantic_result, semantic_score
        
        return fuzzy_result, fuzzy_score
