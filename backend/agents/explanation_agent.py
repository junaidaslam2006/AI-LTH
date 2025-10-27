import requests
import json
import re
import os

class ExplanationAgent:
    def __init__(self):
        # OpenRouter API configuration
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.getenv('OPENROUTER_TEXT_API_KEY', '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')
        self.model = "openai/gpt-oss-20b"  # Same as text chat - free model
    
    def contains_medical_advice(self, text):
        """
        Check if text contains medical advice or dosage recommendations
        Returns True if unsafe content detected
        """
        unsafe_patterns = [
            r'\btake\s+\d+',  # "take 2 tablets"
            r'\bdosage\s+is\s+\d+',  # "dosage is 500mg"
            r'you\s+should\s+take',
            r'recommended\s+dose\s+is',
            r'\d+\s*mg\s+every',  # "500mg every 6 hours"
            r'take\s+this\s+medicine',
            r'consume\s+\d+',
            r'administer\s+\d+',
        ]
        
        text_lower = text.lower()
        for pattern in unsafe_patterns:
            if re.search(pattern, text_lower):
                print(f"⚠️ Medical advice detected: {pattern}")
                return True
        return False
    
    def generate(self, medicine_data):
        """
        Generate structured medicine explanation using OpenRouter API
        Returns: dict with description and side_effects array as per backend.txt spec
        """
        brand = medicine_data.get('brand_name', 'N/A')
        generic = medicine_data.get('generic_name', 'N/A')
        manufacturer = medicine_data.get('manufacturer', 'N/A')
        
        # Check if we have database info
        has_database_info = manufacturer != 'N/A'
        
        # Create structured prompt for JSON response
        if has_database_info:
            prompt = f"""You are a Medicine Information Assistant for Pakistan. Provide comprehensive information about {brand}.

Medicine: {brand}
Manufacturer: {manufacturer}
Generic: {generic if generic != 'N/A' else 'Not specified'}

Return ONLY a JSON object with this exact structure (no markdown, no code blocks):
{{
  "description": "Comprehensive overview (3-4 sentences): What this medicine is, its active ingredients, drug class, and primary medical purpose. Be informative and educational.",
  "uses": "Detailed medical uses and conditions it treats. Include: primary indications, therapeutic applications, and what symptoms/conditions it addresses. Use clear, patient-friendly language.",
  "side_effects": ["Common side effect 1 with brief description", "Common side effect 2 with brief description", "Common side effect 3 with brief description", "Rare but serious side effect to watch for"],
  "warnings": "Important safety information including: who should avoid it, drug interactions to be aware of, contraindications, special precautions for pregnant/breastfeeding women, and when to seek immediate medical attention."
}}

CRITICAL RULES:
- Be comprehensive and educational (this is for patient awareness)
- side_effects MUST be an array of 4-6 strings with brief descriptions
- Include both common and serious side effects
- Do NOT include dosage recommendations or instructions
- Do NOT say "take this medicine" or give prescriptive medical advice
- Focus on educational awareness and safety information
- Use professional medical terminology but explain it clearly
- Keep each section informative but concise"""
        else:
            prompt = f"""You are a Medicine Information Assistant with comprehensive pharmaceutical knowledge. The medicine '{brand}' is NOT in our Pakistan database, but you should use your general medical knowledge to provide helpful information.

IMPORTANT: Use your training data and medical knowledge to provide actual information about {brand} if you recognize it as a real medicine. Only say "not available" if you truly don't know this medicine.

Return ONLY a JSON object with this exact structure (no markdown, no code blocks):
{{
  "description": "If you recognize {brand}: Provide a comprehensive 3-4 sentence overview explaining what this medicine is, its active ingredient(s), drug classification, and primary therapeutic purpose. Be specific and informative. If truly unknown: State it's not in database and may be spelled differently or be a regional brand name.",
  "uses": "If you know {brand}: Provide detailed therapeutic uses, medical conditions it treats, primary indications, and what symptoms it addresses. Include specific conditions and use cases. If truly unknown: 'This specific brand is not in our database. Please verify the medicine name spelling or consult a pharmacist for information.'",
  "side_effects": ["If you know {brand}: List 4-6 actual common and serious side effects based on the drug class/active ingredient", "Include both frequent mild effects and rare serious effects", "Be specific - not generic statements", "If truly unknown: 'Side effect information unavailable - verify medicine name and consult healthcare provider'"],
  "warnings": "If you know {brand}: Provide comprehensive safety warnings including contraindications, drug interactions, pregnancy/breastfeeding warnings, and special precautions based on the drug class. If truly unknown: 'This medicine is not in our Pakistan database. Verify the spelling and brand name. DO NOT use any medicine without consulting a qualified healthcare professional. Always check official regulatory approval and purchase only from licensed pharmacies.'"
}}

CRITICAL INSTRUCTIONS:
- ACTIVELY USE your medical knowledge - don't default to "not available" if you know the medicine
- If {brand} is a common medicine (even if not in Pakistan database), provide full information
- Be helpful and informative while maintaining safety focus
- Only use "not available" responses if you genuinely don't recognize the medicine
- Patient safety is paramount but so is providing useful information when you can"""

        try:
            print(f"🤖 Calling OpenRouter API for {brand}...")
            print(f"📊 Has database info: {has_database_info}")
            print(f"🔑 API Key present: {'Yes' if self.api_key and len(self.api_key) > 10 else 'No'}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "AI-LTH Medicine Assistant"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical information assistant. Return ONLY valid JSON. No markdown, no code blocks, no explanations. Just pure JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1200  # Increased for comprehensive responses
            }
            
            print(f"📤 Sending request to OpenRouter ({self.model})...")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📥 Received response: Status {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                explanation_text = result['choices'][0]['message']['content'].strip()
                print(f"✅ API response received ({len(explanation_text)} chars)")
                
                # Check for medical advice
                if self.contains_medical_advice(explanation_text):
                    print("⚠️ Medical advice detected, using safe fallback")
                    return self.generate_fallback_explanation_structured(medicine_data)
                
                # Try to parse JSON response
                try:
                    # Remove markdown code blocks if present
                    cleaned_text = explanation_text
                    if '```json' in cleaned_text:
                        cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
                    elif '```' in cleaned_text:
                        cleaned_text = cleaned_text.split('```')[1].split('```')[0].strip()
                    
                    # Remove any leading/trailing whitespace or newlines
                    cleaned_text = cleaned_text.strip()
                    
                    # Fix common JSON issues
                    # Remove trailing commas before closing braces/brackets
                    cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
                    # Ensure proper string escaping
                    cleaned_text = cleaned_text.replace('\n', ' ')
                    
                    # Try to parse JSON
                    structured_data = json.loads(cleaned_text)
                    
                    # Validate structure - ensure all required fields exist
                    if not isinstance(structured_data, dict):
                        raise ValueError("Response is not a dictionary")
                    
                    # Ensure side_effects is a list
                    if 'side_effects' in structured_data and not isinstance(structured_data.get('side_effects'), list):
                        structured_data['side_effects'] = [str(structured_data.get('side_effects', 'Information not available'))]
                    
                    # Ensure all required fields exist
                    required_fields = ['description', 'uses', 'side_effects', 'warnings']
                    for field in required_fields:
                        if field not in structured_data:
                            structured_data[field] = 'Information not available'
                    
                    print(f"✅ Successfully parsed structured JSON response")
                    return structured_data
                    
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"⚠️ JSON parse error: {e}")
                    print(f"Raw response (first 500 chars): {explanation_text[:500]}...")
                    
                    # Try aggressive JSON extraction and repair
                    import re
                    
                    # Method 1: Extract just the JSON object
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', explanation_text, re.DOTALL)
                    if json_match:
                        try:
                            print("🔄 Attempting to extract and repair JSON...")
                            extracted_json = json_match.group(0)
                            
                            # Fix trailing commas
                            extracted_json = re.sub(r',(\s*[}\]])', r'\1', extracted_json)
                            # Remove newlines in strings
                            extracted_json = extracted_json.replace('\n', ' ')
                            
                            structured_data = json.loads(extracted_json)
                            
                            # Ensure side_effects is a list
                            if 'side_effects' in structured_data and not isinstance(structured_data.get('side_effects'), list):
                                structured_data['side_effects'] = [str(structured_data.get('side_effects'))]
                            
                            # Fill missing fields
                            required_fields = ['description', 'uses', 'side_effects', 'warnings']
                            for field in required_fields:
                                if field not in structured_data:
                                    structured_data[field] = 'Information not available'
                            
                            print(f"✅ Successfully extracted and repaired JSON")
                            return structured_data
                        except Exception as repair_error:
                            print(f"❌ JSON repair failed: {repair_error}")
                    
                    # Method 2: Manual field extraction
                    print("🔄 Attempting manual field extraction...")
                    try:
                        desc_match = re.search(r'"description"\s*:\s*"([^"]*(?:"[^"]*)*)"', explanation_text, re.DOTALL)
                        uses_match = re.search(r'"uses"\s*:\s*"([^"]*(?:"[^"]*)*)"', explanation_text, re.DOTALL)
                        warn_match = re.search(r'"warnings"\s*:\s*"([^"]*(?:"[^"]*)*)"', explanation_text, re.DOTALL)
                        side_match = re.search(r'"side_effects"\s*:\s*\[(.*?)\]', explanation_text, re.DOTALL)
                        
                        manual_data = {}
                        if desc_match:
                            manual_data['description'] = desc_match.group(1).strip()
                        if uses_match:
                            manual_data['uses'] = uses_match.group(1).strip()
                        if warn_match:
                            manual_data['warnings'] = warn_match.group(1).strip()
                        if side_match:
                            side_effects_str = side_match.group(1)
                            side_effects = re.findall(r'"([^"]+)"', side_effects_str)
                            manual_data['side_effects'] = side_effects if side_effects else ['Information not available']
                        
                        # Fill missing fields with defaults
                        if 'description' not in manual_data:
                            manual_data['description'] = 'Information extraction failed'
                        if 'uses' not in manual_data:
                            manual_data['uses'] = 'Please consult a healthcare provider'
                        if 'side_effects' not in manual_data:
                            manual_data['side_effects'] = ['Information not available']
                        if 'warnings' not in manual_data:
                            manual_data['warnings'] = 'Consult healthcare professionals'
                        
                        if len(manual_data) >= 3:  # At least 3 fields extracted
                            print(f"✅ Successfully extracted fields manually")
                            return manual_data
                    except Exception as manual_error:
                        print(f"❌ Manual extraction failed: {manual_error}")
                    
                    # Final fallback: Use comprehensive fallback function
                    print("⚠️ All parsing methods failed, using fallback")
                    return self.generate_fallback_explanation_structured(medicine_data)
            else:
                print(f"❌ API returned status {response.status_code}: {response.text}")
        except requests.exceptions.Timeout:
            print(f"⏱️ API timeout after 30s, using fallback")
        except Exception as e:
            print(f"❌ API error: {e}")
        
        # Fallback only if API fails
        print("⚠️ Using fallback explanation")
        return self.generate_fallback_explanation_structured(medicine_data)
    
    def generate_fallback_explanation_structured(self, medicine_data):
        """
        Generate structured explanation without API (when API fails/unavailable)
        Returns dict matching backend.txt specification
        """
        brand = medicine_data.get('brand_name', 'Unknown Medicine')
        generic = medicine_data.get('generic_name', 'N/A')
        manufacturer = medicine_data.get('manufacturer', 'N/A')
        
        # Check if we have database data
        has_data = manufacturer != 'N/A'
        
        if has_data:
            # Medicine found in Pakistan database - provide detailed info
            generic_info = f" The active ingredient is {generic}." if generic != 'N/A' else ""
            return {
                "description": f"{brand} is a registered pharmaceutical product in Pakistan, manufactured by {manufacturer}.{generic_info} This medicine has been officially approved for distribution in Pakistan by the Drug Regulatory Authority of Pakistan (DRAP). It undergoes quality control and meets local pharmaceutical standards. For complete medical information including detailed composition, therapeutic indications, mechanism of action, and usage guidelines, please refer to the official package insert or consult with a licensed pharmacist or healthcare provider.",
                
                "uses": f"As a registered medicine in Pakistan's pharmaceutical database, {brand} has approved therapeutic indications. The specific medical uses, conditions it treats, and therapeutic applications are detailed in the official prescribing information. Common uses for medicines in this category typically include treatment of specific medical conditions based on the active ingredient{f' ({generic})' if generic != 'N/A' else ''}. For accurate information about approved indications, recommended patient populations, and proper therapeutic use, please consult the package insert, speak with your pharmacist, or contact your healthcare provider.",
                
                "side_effects": [
                    f"Common side effects: Like all medications, {brand} may cause side effects in some patients. The frequency and severity vary by individual",
                    "Mild reactions: May include nausea, headache, dizziness, stomach upset, or drowsiness depending on the medication class",
                    "Allergic reactions: Watch for signs of allergic reactions including skin rash, itching, swelling, or difficulty breathing",
                    "Serious effects: Stop use and seek immediate medical attention if you experience severe reactions, unusual symptoms, or signs of overdose",
                    "Individual variation: Not everyone experiences side effects - many people use this medicine with minimal issues",
                    "Complete information: Check the official package insert for a comprehensive list of potential side effects and their frequencies",
                    "Report symptoms: Always inform your healthcare provider about any unusual or persistent symptoms"
                ],
                
                "warnings": f"⚠️ IMPORTANT SAFETY INFORMATION FOR {brand}: This medicine is a regulated pharmaceutical product in Pakistan. GENERAL PRECAUTIONS: Always read the complete package insert before first use. Follow the prescribed dosage and duration exactly as directed by your healthcare provider. SPECIAL POPULATIONS: Consult your doctor before use if you are pregnant, planning pregnancy, breastfeeding, elderly, or treating children. MEDICAL CONDITIONS: Inform your doctor about all existing medical conditions, especially liver disease, kidney disease, heart conditions, diabetes, or blood disorders. DRUG INTERACTIONS: Tell your healthcare provider about all medications, supplements, and herbal products you are currently taking to avoid potential interactions. ALLERGIES: Do not use if you have known allergies to {generic if generic != 'N/A' else 'any ingredients in this medicine'}. STORAGE: Keep out of reach of children. Store as directed on the package (usually at room temperature, away from moisture and heat). OVERDOSE: In case of overdose or severe reaction, seek immediate medical attention or contact emergency services. PURCHASE: Only buy from licensed, authorized pharmacies to ensure product authenticity and quality. DISPOSAL: Dispose of expired or unused medication properly - return to pharmacy or follow local disposal guidelines."
            }
        else:
            # Medicine NOT in Pakistan database - provide helpful info without mentioning database
            return {
                "description": f"{brand} is a pharmaceutical medication. Based on common medical knowledge and the medicine name, this appears to be a recognized pharmaceutical product used for therapeutic purposes. The specific formulation, active ingredients, and approved uses may vary by region and manufacturer. For detailed information about the exact formulation available in your area, consulting with a registered pharmacist or healthcare provider is recommended.",
                
                "uses": f"{brand} is typically used for specific therapeutic purposes based on its active ingredient and drug classification. Common medical applications may include treatment of particular health conditions, symptom management, or disease control. The appropriate use depends on individual patient factors, medical history, and current health status. Your healthcare provider can determine if this medication is suitable for your specific condition and provide guidance on proper therapeutic applications.",
                
                "side_effects": [
                    "Possible mild effects may include nausea, headache, or dizziness in some users",
                    "Drowsiness or fatigue can occur - avoid driving if affected",
                    "Stomach discomfort or digestive issues may be experienced",
                    "Allergic reactions possible - watch for skin rash, itching, or swelling",
                    "Some individuals may experience changes in appetite or sleep patterns",
                    "Serious side effects are uncommon but require immediate medical attention",
                    "Individual responses vary - consult your doctor if any symptoms persist"
                ],
                
                "warnings": f"Important safety information for {brand}: Consult your healthcare provider before use, especially if you are pregnant, breastfeeding, have existing medical conditions, or take other medications. Follow the prescribed or recommended dosage carefully. Do not exceed the recommended duration of use without medical supervision. Keep out of reach of children. Store at room temperature away from moisture and heat. Seek immediate medical attention if you experience severe reactions or symptoms worsen. Only purchase from licensed, authorized pharmacies to ensure product quality and authenticity."
            }
        
        
    
    def is_available(self):
        """Check if API is available"""
        try:
            response = requests.get(self.api_url.replace('/chat/completions', '/models'), timeout=5)
            return response.status_code == 200
        except:
            return False
