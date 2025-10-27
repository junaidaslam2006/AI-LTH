from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
import os
from datetime import datetime
import re
import requests
from dotenv import load_dotenv
from agents.query_agent import QueryUnderstandingAgent
from agents.ocr_agent import OCRAgent
from agents.dataset_agent import DatasetSearchAgent
from agents.explanation_agent import ExplanationAgent
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Swagger UI
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AI-LTH API Documentation",
        "description": "AI-Powered Medicine Information & Transparency System for Pakistan\n\n"
                      "This API provides comprehensive medicine information through multiple modes:\n"
                      "- Text queries for medicine information\n"
                      "- Image upload for OCR-based medicine identification\n"
                      "- Camera scan support\n\n"
                      "Features:\n"
                      "- Multi-agent AI architecture\n"
                      "- Pakistan pharmaceutical database (1,630+ medicines)\n"
                      "- Tesseract OCR for image processing\n"
                      "- OpenRouter AI for intelligent explanations\n"
                      "- Safety validation (no dosage recommendations)",
        "version": "1.0.0",
        "contact": {
            "name": "AI-LTH Team",
            "email": "support@ai-lth.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {
            "name": "Health",
            "description": "System health and status endpoints"
        },
        {
            "name": "Medicine Information",
            "description": "Get medicine information via text or image"
        },
        {
            "name": "Database",
            "description": "Direct database access endpoints"
        },
        {
            "name": "Agents",
            "description": "AI agent system monitoring"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Load API keys from environment variables
OPENROUTER_VISION_API_KEY = os.getenv('OPENROUTER_VISION_API_KEY')
OPENROUTER_TEXT_API_KEY = os.getenv('OPENROUTER_TEXT_API_KEY')

# Initialize agents
query_agent = QueryUnderstandingAgent()
ocr_agent = OCRAgent(api_key=OPENROUTER_VISION_API_KEY)  # Pass OpenRouter API key for Vision
dataset_agent = DatasetSearchAgent()
explanation_agent = ExplanationAgent()

def sanitize_input(text):
    """
    Sanitize user input to prevent injection attacks
    """
    # Remove potential SQL injection patterns
    dangerous_patterns = [
        r'(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bEXEC\b|\bEXECUTE\b)',
        r'(<script|javascript:|onerror=|onclick=)',
        r'(union.*select|select.*from)',
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return None  # Reject malicious input
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limit length
    if len(text) > 500:
        text = text[:500]
    
    return text.strip()

# Medicine-related keywords for validation
MEDICINE_KEYWORDS = [
    'medicine', 'drug', 'tablet', 'capsule', 'syrup', 'injection', 'pill',
    'medication', 'pharmaceutical', 'antibiotic', 'painkiller', 'fever',
    'dosage', 'prescription', 'pharmacy', 'treatment', 'cure', 'disease',
    'pain', 'headache', 'cough', 'cold', 'infection', 'vitamin', 'supplement'
]

def is_medicine_related(query):
    """Check if query is medicine-related"""
    query_lower = query.lower()
    
    # Check for medicine keywords
    for keyword in MEDICINE_KEYWORDS:
        if keyword in query_lower:
            return True
    
    # Check for common question patterns
    if any(phrase in query_lower for phrase in [
        'what is', 'tell me about', 'explain', 'side effect', 
        'used for', 'how to use', 'dosage', 'can i take'
    ]):
        return True
    
    return True  # Allow all for now, AI will filter

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check if the API is running
    description: Returns the current status and timestamp of the AI-LTH backend system
    responses:
      200:
        description: System is healthy and running
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: AI-LTH Backend is running
            timestamp:
              type: string
              format: date-time
              example: 2025-10-26T12:00:00Z
    """
    return jsonify({
        'status': 'success',
        'message': 'AI-LTH Backend is running',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Text-based Medicine Query
    ---
    tags:
      - Medicine Information
    summary: Get medicine information by text query
    description: |
      Submit a text query to get comprehensive medicine information.
      
      **How it works:**
      1. Query Understanding Agent parses the input
      2. Dataset Search Agent searches Pakistan pharmaceutical database
      3. AI Explanation Agent generates structured explanation
      
      **Input validation:**
      - Sanitizes input to prevent injection attacks
      - Validates if query is medicine-related using AI
      - Rejects non-medical queries
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Medicine query request
        required: true
        schema:
          type: object
          required:
            - query
          properties:
            query:
              type: string
              example: What is Panadol?
              description: Medicine name or health-related question
    responses:
      200:
        description: Successfully retrieved medicine information
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            mode:
              type: string
              example: text
            medicine_name:
              type: string
              example: Panadol
            generic_name:
              type: string
              example: Paracetamol
            manufacturer:
              type: string
              example: GSK Pakistan
            description:
              type: string
              example: Panadol is a pain reliever and fever reducer containing paracetamol...
            uses:
              type: string
              example: Used for relief of mild to moderate pain and fever...
            side_effects:
              type: array
              items:
                type: string
              example: ["Nausea", "Skin rash", "Allergic reactions"]
            warnings:
              type: string
              example: Do not exceed recommended dose. Consult doctor if symptoms persist...
            disclaimer:
              type: string
              example: This AI provides informational content only...
      400:
        description: Invalid input or non-medical query
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: Please enter a medicine name or question.
      500:
        description: Server error
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: An error occurred while processing your query.
    """
    try:
        data = request.json
        user_query = data.get('query', '')
        
        if not user_query.strip():
            return jsonify({
                'status': 'error',
                'message': 'Please enter a medicine name or question.'
            }), 400
        
        # Sanitize input
        user_query = sanitize_input(user_query)
        if user_query is None:
            return jsonify({
                'status': 'error',
                'message': 'Invalid input detected. Please enter a valid medicine name or question.'
            }), 400
        
        print(f"📝 Query: {user_query}")
        
        # Validate if query is medicine-related (quick keyword check)
        # Use LLM to intelligently detect if query is medicine-related
        validation_prompt = f"""Is this query about a medicine, medical condition, or healthcare product?
Query: "{user_query}"

Answer ONLY "YES" if it's about:
- Medicine names (Panadol, Aspirin, etc.)
- Symptoms/conditions (headache, fever, diabetes, etc.)
- Medical products (tablets, syrups, injections, etc.)
- Healthcare questions related to medicines

Answer ONLY "NO" if it's:
- Greetings (hello, hi, hey)
- General questions (weather, time, jokes)
- Non-medical topics

Answer with only YES or NO:"""

        try:
            validation_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {explanation_agent.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": explanation_agent.model,
                    "messages": [{"role": "user", "content": validation_prompt}],
                    "max_tokens": 10,
                    "temperature": 0.1
                },
                timeout=5
            )
            
            if validation_response.status_code == 200:
                validation_result = validation_response.json()
                answer = validation_result['choices'][0]['message']['content'].strip().upper()
                
                if "NO" in answer:
                    return jsonify({
                        'status': 'error',
                        'message': 'I can only provide information about medicines and medical conditions. Please ask about a specific medicine name or health condition.'
                    }), 400
        except:
            # If validation fails, continue anyway (fail open, not closed)
            pass
        
        # Agent 1: Query Understanding Agent - Parse user input
        parsed_query = query_agent.parse(user_query)
        
        # Agent 2: Dataset Search Agent - Check database first
        medicine_data = dataset_agent.search(parsed_query['medicine_name'])
        
        # Agent 3: Explanation Agent - Generate explanation
        if medicine_data:
            # Found in dataset - AI explains with dataset info
            explanation_data = explanation_agent.generate(medicine_data)
            
            # Handle both dict and string responses (backwards compatibility)
            if isinstance(explanation_data, dict):
                description = explanation_data.get('description', '')
                side_effects = explanation_data.get('side_effects', [])
                uses = explanation_data.get('uses', 'N/A')
                warnings = explanation_data.get('warnings', '')
            else:
                description = explanation_data
                side_effects = []
                uses = 'N/A'
                warnings = ''
            
            agent_chain = [
                '1. Query Understanding Agent',
                '2. Dataset Search Agent (Found in Pakistan Database)',
                '3. AI Explanation Agent (OpenRouter GPT-3.5)'
            ]
            
            return jsonify({
                'status': 'success',
                'mode': 'text',
                'input_query': user_query,
                'medicine_name': medicine_data.get('brand_name'),
                'generic_name': medicine_data.get('generic_name', 'N/A'),
                'description': description,
                'uses': uses,
                'warnings': warnings,
                'ai_explanation': description,
                'side_effects': side_effects if side_effects else ['Information not available'],
                'manufacturer': medicine_data.get('manufacturer', 'N/A'),
                'agent_used': 'TextAgent',
                'dataset_match': True,
                'confidence': medicine_data.get('confidence', 0.95),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'disclaimer': 'This AI provides informational content only and is not a substitute for professional medical advice. Always consult a qualified healthcare professional.'
            })
        else:
            # Not found in dataset - AI uses general knowledge
            medicine_data_empty = {
                'brand_name': parsed_query['medicine_name'],
                'generic_name': 'N/A',
                'manufacturer': 'N/A'
            }
            explanation_data = explanation_agent.generate(medicine_data_empty)
            
            # Handle both dict and string responses
            if isinstance(explanation_data, dict):
                description = explanation_data.get('description', '')
                side_effects = explanation_data.get('side_effects', [])
                uses = explanation_data.get('uses', 'N/A')
                warnings = explanation_data.get('warnings', '')
            else:
                description = explanation_data
                side_effects = []
                uses = 'N/A'
                warnings = ''
            
            agent_chain = [
                '1. Query Understanding Agent',
                '2. Dataset Search Agent (Not found in Pakistan Database)',
                '3. AI Explanation Agent (OpenRouter GPT-3.5 - General Knowledge)'
            ]
            
            return jsonify({
                'status': 'success',
                'mode': 'text',
                'input_query': user_query,
                'medicine_name': parsed_query['medicine_name'],
                'generic_name': 'N/A',
                'description': description,
                'uses': uses,
                'warnings': warnings,
                'ai_explanation': description,
                'side_effects': side_effects if side_effects else ['Information not available'],
                'manufacturer': 'N/A',
                'agent_used': 'TextAgent',
                'dataset_match': False,
                'confidence': 0.50,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'disclaimer': 'This AI provides informational content only and is not a substitute for professional medical advice. Always consult a qualified healthcare professional.'
            })
    except Exception as e:
        print(f"❌ Error in /api/query: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your query.',
            'details': str(e)
        }), 500

@app.route('/api/image', methods=['POST'])
def handle_image():
    """
    Image-based Medicine Recognition
    ---
    tags:
      - Medicine Information
    summary: Upload medicine image for OCR and information extraction
    description: |
      Upload a photo of medicine packaging to extract text and get information.
      
      **How it works:**
      1. OCR Agent (Tesseract) extracts text from image
      2. Medicine name is identified and cleaned
      3. AI validates if content is medicine-related
      4. Dataset Search Agent searches database
      5. AI Explanation Agent generates explanation
      
      **Image requirements:**
      - Format: .jpg, .jpeg, .png
      - Clear, well-lit photo
      - Medicine name visible
      - Max size: 10MB
      
      **OCR Features:**
      - Multiple PSM modes for better accuracy
      - Image preprocessing (upscaling, contrast, sharpness)
      - Pattern-based medicine detection
    consumes:
      - multipart/form-data
    produces:
      - application/json
    parameters:
      - in: formData
        name: image
        type: file
        required: true
        description: Medicine packaging image (JPEG/PNG)
    responses:
      200:
        description: Successfully processed image and retrieved medicine information
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            mode:
              type: string
              example: image
            medicine_name:
              type: string
              example: Panadol
            generic_name:
              type: string
              example: Paracetamol
            manufacturer:
              type: string
              example: GSK Pakistan
            ocr_text:
              type: string
              example: Panadol Tablets 500mg...
            ocr_confidence:
              type: number
              format: float
              example: 0.85
            model_info:
              type: object
              properties:
                ocr_engine:
                  type: string
                  example: Tesseract OCR (Local & Free)
                version:
                  type: string
                  example: 5.5.0
            description:
              type: string
              example: Panadol is a pain reliever...
            uses:
              type: string
              example: Used for pain and fever relief...
            side_effects:
              type: array
              items:
                type: string
              example: ["Nausea", "Skin rash"]
            warnings:
              type: string
              example: Do not exceed recommended dose...
            disclaimer:
              type: string
              example: This AI provides informational content only...
      400:
        description: Invalid file or image does not contain medicine
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: Could not read text from the image. Please upload a clearer photo...
      500:
        description: Server error during image processing
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: An error occurred while processing the image.
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image provided'
            }), 400
        
        image_file = request.files['image']
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid file type. Only .jpg, .jpeg, .png are allowed.'
            }), 400
        
        print(f"📸 Received image: {image_file.filename}")
        
        # Agent 1: OCR processing
        ocr_result = ocr_agent.extract_text(image_file)
        
        print(f"🔍 OCR Result: {ocr_result}")
        
        # Check if OCR failed
        if ocr_result.get('error'):
            print(f"❌ OCR Error: {ocr_result['error']}")
            return jsonify({
                'status': 'error',
                'message': 'OCR processing failed',
                'details': ocr_result['error']
            }), 500
        
        # Check if image contains medicine-related content
        # Don't reject based on OCR patterns alone - let the extracted text decide
        extracted_text = ocr_result.get('raw_text', '').strip()
        medicine_name = ocr_result.get('medicine_name', '').strip()
        
        # If OCR got no text at all, image is likely unreadable
        if len(extracted_text) < 3 and not medicine_name:
            return jsonify({
                'status': 'error',
                'message': 'Could not read text from the image. Please try:\n\n1. Upload a clearer photo with good lighting\n2. Make sure the medicine name is clearly visible\n3. Or use the Chat feature and type the medicine name directly'
            }), 400
        
        # If we got some text but no clear medicine name, still try to process
        if not medicine_name or medicine_name == 'Unknown Medicine':
            # Try to extract first meaningful word from raw text
            words = extracted_text.split()
            if words:
                medicine_name = words[0]
                print(f"⚠️ Using first word as medicine name: {medicine_name}")
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Could not read the medicine name from the image. Please try:\n\n1. Upload a clearer photo with good lighting\n2. Make sure the medicine name is clearly visible\n3. Or use the Chat feature and type the medicine name directly'
                }), 400
        
        # Validate with LLM: Is this actually a medicine?
        print(f"🔍 Validating if '{medicine_name}' is medicine-related...")
        validation_prompt = f"""Is this text about a medicine, pharmaceutical product, or medical treatment?
Extracted text: "{medicine_name}"
Raw OCR text: "{extracted_text[:200]}"

Answer ONLY "YES" if it's about:
- Medicine names (tablets, capsules, syrups, injections, etc.)
- Pharmaceutical products
- Medical treatments or drugs
- Healthcare products

Answer ONLY "NO" if it's:
- Food items
- Household products
- Random text or non-medical content
- Greetings or general conversation

Answer with only YES or NO:"""

        try:
            validation_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {explanation_agent.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": explanation_agent.model,
                    "messages": [{"role": "user", "content": validation_prompt}],
                    "max_tokens": 10,
                    "temperature": 0.1
                },
                timeout=5
            )
            
            if validation_response.status_code == 200:
                validation_result = validation_response.json()
                answer = validation_result['choices'][0]['message']['content'].strip().upper()
                print(f"✅ Validation result: {answer}")
                
                if "NO" in answer:
                    return jsonify({
                        'status': 'error',
                        'message': 'I can only provide information about medicines and pharmaceutical products. The image does not appear to contain medicine packaging. Please upload a clear photo of medicine packaging or use the Chat feature to ask about a specific medicine.'
                    }), 400
        except Exception as e:
            print(f"⚠️ Validation API failed: {e}, continuing anyway...")
            # If validation fails, continue (fail open)
        
        # Agent 2: Dataset Search Agent - Check database
        medicine_data = dataset_agent.search(ocr_result['medicine_name'])
        
        # Agent 3: Explanation Agent - Generate explanation
        if medicine_data:
            # Found in dataset - AI explains with dataset info
            explanation_data = explanation_agent.generate(medicine_data)
            
            # Handle both dict and string responses
            if isinstance(explanation_data, dict):
                description = explanation_data.get('description', '')
                side_effects = explanation_data.get('side_effects', [])
                uses = explanation_data.get('uses', 'N/A')
                warnings = explanation_data.get('warnings', '')
            else:
                description = explanation_data
                side_effects = []
                uses = 'N/A'
                warnings = ''
            
            agent_chain = [
                '1. OCR Agent (Tesseract OCR - Local)',
                '2. Dataset Search Agent (Found in Pakistan Database)',
                '3. AI Explanation Agent (OpenRouter gpt-oss-20b)'
            ]
            
            return jsonify({
                'status': 'success',
                'mode': 'image',
                'input_query': f'Image scan: {image_file.filename}',
                'ocr_text': ocr_result.get('raw_text', '')[:300],
                'detected_patterns': ocr_result.get('detected_patterns', []),
                'ocr_confidence': ocr_result.get('confidence', 0.0),
                'model_info': ocr_result.get('model_info', {}),
                'medicine_name': medicine_data.get('brand_name'),
                'generic_name': medicine_data.get('generic_name', 'N/A'),
                'description': description,
                'uses': uses,
                'warnings': warnings,
                'side_effects': side_effects if side_effects else ['Information not available'],
                'manufacturer': medicine_data.get('manufacturer', 'N/A'),
                'agent_used': 'ImageAgent',
                'dataset_match': True,
                'confidence': medicine_data.get('confidence', 0.90),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'disclaimer': 'This AI provides informational content only and is not a substitute for professional medical advice. Always consult a qualified healthcare professional.'
            })
        else:
            # Not found in dataset - AI uses general knowledge
            medicine_data_empty = {
                'brand_name': ocr_result['medicine_name'],
                'generic_name': 'N/A',
                'manufacturer': 'N/A'
            }
            explanation_data = explanation_agent.generate(medicine_data_empty)
            
            # Handle both dict and string responses
            if isinstance(explanation_data, dict):
                description = explanation_data.get('description', '')
                side_effects = explanation_data.get('side_effects', [])
                uses = explanation_data.get('uses', 'N/A')
                warnings = explanation_data.get('warnings', '')
            else:
                description = explanation_data
                side_effects = []
                uses = 'N/A'
                warnings = ''
            
            agent_chain = [
                '1. OCR Agent (Tesseract OCR - Local)',
                '2. Dataset Search Agent (Not found in Pakistan Database)',
                '3. AI Explanation Agent (OpenRouter gpt-oss-20b - General Knowledge)'
            ]
            
            return jsonify({
                'status': 'success',
                'mode': 'image',
                'input_query': f'Image scan: {image_file.filename}',
                'ocr_text': ocr_result.get('raw_text', '')[:300],
                'detected_patterns': ocr_result.get('detected_patterns', []),
                'ocr_confidence': ocr_result.get('confidence', 0.0),
                'model_info': ocr_result.get('model_info', {}),
                'medicine_name': ocr_result['medicine_name'],
                'generic_name': 'N/A',
                'description': description,
                'uses': uses,
                'warnings': warnings,
                'side_effects': side_effects if side_effects else ['Information not available'],
                'manufacturer': 'N/A',
                'agent_used': 'ImageAgent',
                'dataset_match': False,
                'confidence': 0.50,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'disclaimer': 'This AI provides informational content only and is not a substitute for professional medical advice. Always consult a qualified healthcare professional.'
            })
    except Exception as e:
        print(f"❌ Exception in /api/image: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing the image.',
            'details': str(e)
        }), 500

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    """
    Get All Medicine Names
    ---
    tags:
      - Database
    summary: Retrieve list of all medicines in the database
    description: Returns a list of all medicine names available in the Pakistan pharmaceutical database for autocomplete and reference
    responses:
      200:
        description: Successfully retrieved medicine list
        schema:
          type: object
          properties:
            medicines:
              type: array
              items:
                type: string
              example: ["Panadol", "Brufen", "Augmentin", "Disprin"]
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Database not loaded
    """
    try:
        medicines = dataset_agent.get_all_medicine_names()
        return jsonify({'medicines': medicines})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicine/<name>', methods=['GET'])
def get_medicine(name):
    """
    Get Specific Medicine Information
    ---
    tags:
      - Database
    summary: Retrieve detailed information for a specific medicine
    description: Search the database for a specific medicine by name and return all available data
    parameters:
      - in: path
        name: name
        type: string
        required: true
        description: Medicine name to search for
        example: Panadol
    responses:
      200:
        description: Medicine found in database
        schema:
          type: object
          properties:
            brand_name:
              type: string
              example: Panadol
            generic_name:
              type: string
              example: Paracetamol
            manufacturer:
              type: string
              example: GSK Pakistan
            price:
              type: string
              example: Rs 182
            pack_size:
              type: string
              example: 1x14's
            availability:
              type: string
              example: Available
      404:
        description: Medicine not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Medicine not found
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Database query failed
    """
    try:
        medicine_data = dataset_agent.search(name)
        if not medicine_data:
            return jsonify({'error': 'Medicine not found'}), 404
        return jsonify(medicine_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/status', methods=['GET'])
def agents_status():
    """
    Agent System Status
    ---
    tags:
      - Agents
    summary: Check status of all AI agents
    description: |
      Returns the operational status of the multi-agent system:
      - Query Understanding Agent
      - OCR Agent (Tesseract)
      - Dataset Search Agent
      - Explanation Agent (OpenRouter AI)
      
      Also includes database loading status and statistics
    responses:
      200:
        description: Agent system status
        schema:
          type: object
          properties:
            agents:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                    example: QueryUnderstandingAgent
                  status:
                    type: string
                    example: active
            dataset_loaded:
              type: boolean
              example: true
            dataset_records:
              type: integer
              example: 1630
            pdf_files:
              type: integer
              example: 1
            llm_available:
              type: boolean
              example: true
    """
    return jsonify({
        'agents': [
            {'name': 'QueryUnderstandingAgent', 'status': 'active'},
            {'name': 'OCRAgent', 'status': 'active'},
            {'name': 'DatasetSearchAgent', 'status': 'active'},
            {'name': 'ExplanationAgent', 'status': 'active'}
        ],
        'dataset_loaded': dataset_agent.is_loaded(),
        'dataset_records': len(dataset_agent.df) if dataset_agent.df is not None else 0,
        'pdf_files': len(dataset_agent.pdf_data),
        'llm_available': explanation_agent.is_available()
    })

@app.route('/api/dataset/info', methods=['GET'])
def dataset_info():
    """
    Dataset Information
    ---
    tags:
      - Database
    summary: Get detailed database statistics
    description: |
      Returns comprehensive information about the loaded pharmaceutical database:
      - CSV file status and record count
      - PDF file status and list
      - Column structure
      - Total unique medicines
    responses:
      200:
        description: Database information
        schema:
          type: object
          properties:
            csv_loaded:
              type: boolean
              example: true
            csv_records:
              type: integer
              example: 1630
            csv_columns:
              type: array
              items:
                type: string
              example: ["Name", "Company", "Price_before", "Discount", "Price_After", "Pack_Size", "Availability"]
            pdf_loaded:
              type: boolean
              example: true
            pdf_files:
              type: array
              items:
                type: string
              example: ["medicine-dataset-66-page.pdf"]
            total_medicines:
              type: integer
              example: 1630
      500:
        description: Error retrieving database info
        schema:
          type: object
          properties:
            error:
              type: string
              example: Database not accessible
    """
    try:
        info = {
            'csv_loaded': dataset_agent.df is not None,
            'csv_records': len(dataset_agent.df) if dataset_agent.df is not None else 0,
            'csv_columns': list(dataset_agent.df.columns) if dataset_agent.df is not None else [],
            'pdf_loaded': len(dataset_agent.pdf_data) > 0,
            'pdf_files': [pdf['filename'] for pdf in dataset_agent.pdf_data],
            'total_medicines': len(dataset_agent.get_all_medicine_names())
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
