import re

class QueryUnderstandingAgent:
    def __init__(self):
        self.common_words = ['what', 'is', 'tell', 'me', 'about', 'for', 'used', 'medicine', 'tablet', 'syrup']
    
    def parse(self, query):
        """
        Extract medicine name from user query
        """
        # Remove common question words
        query_lower = query.lower()
        
        # Remove common words
        words = query_lower.split()
        filtered_words = [w for w in words if w not in self.common_words]
        
        # Extract potential medicine name (capitalize first letter)
        medicine_name = ' '.join(filtered_words).strip()
        
        # If empty, use original query
        if not medicine_name:
            medicine_name = query.strip()
        else:
            # Capitalize first letter of each word
            medicine_name = ' '.join(word.capitalize() for word in filtered_words)
        
        return {
            'medicine_name': medicine_name,
            'original_query': query
        }
