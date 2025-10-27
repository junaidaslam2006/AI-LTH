import os
import re
import io
import base64
import requests
from PIL import Image, ImageEnhance, ImageStat


class OCRAgent:
    def __init__(self, api_key=None):
        """Initialize OCRAgent with OpenRouter GPT-4o-mini Vision API.

        Primary OCR: OpenRouter GPT-4o-mini (Vision)
        - Cloud-based Vision API
        - Fast and reliable
        - Excellent for text extraction from images
        
        Using model: openai/gpt-4o-mini
        """
        print("ℹ️ Using OpenRouter GPT-4o-mini Vision API (cloud-based & fast)")
        
        # OpenRouter API configuration
        self.api_key = api_key or "PLACEHOLDER_KEY"  # Will be set by user
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"  # Primary vision model - fast and reliable
        self.alternative_model = "google/gemini-2.0-flash-exp:free"  # Fallback to Gemini
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "AI-LTH Medicine OCR"
        }
        
        # Set API as available
        self.vision_available = True
        print("✅ OpenRouter GPT-4o-mini Vision API configured!")
        
        # Dynamic medicine detection patterns (compiled regex for performance)
        self.medicine_patterns = [
            re.compile(r'\b\d+\s*(mg|ml|mcg|g|ml|L|IU|units?)\b', re.IGNORECASE),  # Dosage
            re.compile(r'\b(tablet|capsule|syrup|injection|cream|ointment|gel|drops|suspension|solution|powder|spray|inhaler|patch)\b', re.IGNORECASE),  # Form
            re.compile(r'\b(oral|topical|intravenous|intramuscular|subcutaneous|transdermal)\b', re.IGNORECASE),  # Route
            re.compile(r'\b(expiry|exp\.?|mfg\.?|batch|lot)\s*:?\s*\d+', re.IGNORECASE),  # Package info
            re.compile(r'\b(pharmaceutical|pharma|medicine|medication|drug|rx|℞)\b', re.IGNORECASE),  # Medical terms
            re.compile(r'\b(paracetamol|aspirin|ibuprofen|amoxicillin|metformin|omeprazole)\b', re.IGNORECASE),  # Common drugs
        ]

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results with multiple enhancement techniques."""
        try:
            # Resize if too small (OCR works better with larger images)
            min_width = 600
            if image.width < min_width:
                ratio = min_width / image.width
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📐 Upscaled image to {new_size} for better OCR")
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Dynamic contrast enhancement
            stat = ImageStat.Stat(image)
            mean_brightness = stat.mean[0]
            
            # More aggressive enhancement for better text detection
            if mean_brightness < 100:
                contrast_factor = 2.5
            elif mean_brightness < 150:
                contrast_factor = 2.0
            else:
                contrast_factor = 1.7
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast_factor)
            
            # Brightness adjustment if too dark
            if mean_brightness < 80:
                brightness_enhancer = ImageEnhance.Brightness(image)
                image = brightness_enhancer.enhance(1.5)
            
            # Sharpness enhancement for clearer text
            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(2.0)
        except Exception as e:
            print(f"⚠️ Preprocessing failed: {e}, using original image")
            return image

        return image

    def _is_medicine_related(self, text: str) -> tuple[bool, float, list]:
        """Dynamic medicine detection using pattern matching."""
        if not text or len(text.strip()) < 10:
            return False, 0.0, []
        
        detected_patterns = []
        pattern_weights = {
            0: 0.25,  # Dosage
            1: 0.20,  # Form
            2: 0.15,  # Route
            3: 0.15,  # Package info
            4: 0.15,  # Medical terms
            5: 0.10,  # Drug names
        }
        
        confidence = 0.0
        for idx, pattern in enumerate(self.medicine_patterns):
            matches = pattern.findall(text)
            if matches:
                detected_patterns.append({
                    'type': ['dosage', 'form', 'route', 'package', 'medical', 'drug_name'][idx],
                    'matches': matches[:3],
                    'weight': pattern_weights[idx]
                })
                confidence += pattern_weights[idx]
        
        is_medicine = confidence >= 0.3
        return is_medicine, min(confidence, 1.0), detected_patterns
    
    def _extract_medicine_name(self, raw_text: str, lines: list) -> str:
        """Enhanced medicine name extraction with better cleaning logic."""
        # Words to filter out (common non-medicine words)
        filter_words = {
            'tablet', 'tablets', 'capsule', 'capsules', 'syrup', 'injection', 
            'cream', 'ointment', 'gel', 'drops', 'suspension', 'solution',
            'powder', 'spray', 'inhaler', 'patch', 'mg', 'ml', 'mcg', 'gm',
            'each', 'pack', 'strip', 'box', 'bottle', 'contains', 'composition',
            'expiry', 'exp', 'mfg', 'batch', 'lot', 'date', 'pharmaceutical',
            'pharma', 'pvt', 'ltd', 'limited', 'pakistan', 'india', 'usa',
            'made', 'manufactured', 'by', 'company', 'laboratories', 'lab',
            'prescription', 'only', 'medicine', 'drug', 'store', 'between',
            'keep', 'out', 'reach', 'children', 'doctor', 'pharmacist'
        }
        
        medicine_name = ''
        
        # Strategy 1: Look for brand name patterns (usually CAPITALIZED or Title Case in first few lines)
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 2:
                continue
            
            # Skip lines that are purely dosage info
            if re.match(r'^\d+\s*(mg|ml|mcg|g|%)', line_clean, re.IGNORECASE):
                continue
            
            # Skip manufacturer lines
            if any(word in line_clean.lower() for word in ['pvt', 'ltd', 'limited', 'laboratories', 'pharma']):
                continue
            
            # Medicine names are often in first 1-2 lines and have capital letters
            has_caps = bool(re.search(r'[A-Z]', line_clean))
            
            if has_caps or i < 2:  # First 2 lines or lines with capitals
                # Clean the line
                cleaned = line_clean
                
                # Remove dosage information
                cleaned = re.sub(r'\d+\.?\d*\s*(mg|ml|mcg|g|gm|gram|%|iu|unit)', '', cleaned, flags=re.IGNORECASE)
                
                # Remove packaging info
                cleaned = re.sub(r'\d+\s*[x×]\s*\d+', '', cleaned)  # "1x10", "2×20"
                cleaned = re.sub(r'\d+[\'s]*$', '', cleaned)  # "10's", "20s" at end
                
                # Remove special characters but keep spaces, hyphens, slashes, ampersands
                cleaned = re.sub(r'[^\w\s\-\/\&\+]', ' ', cleaned)
                
                # Remove standalone numbers
                cleaned = re.sub(r'\b\d+\b', '', cleaned)
                
                # Split into words and filter
                words = cleaned.split()
                filtered_words = [
                    word for word in words 
                    if word.lower() not in filter_words 
                    and len(word) > 1
                    and not word.isdigit()
                ]
                
                # Reconstruct name
                potential_name = ' '.join(filtered_words).strip()
                
                # If we got a good name (2-30 chars), use it
                if 2 <= len(potential_name) <= 30 and potential_name:
                    medicine_name = potential_name
                    print(f"🎯 Found medicine name in line {i+1}: '{medicine_name}'")
                    break
        
        # Strategy 2: If no name found, look for the longest meaningful word sequence
        if not medicine_name:
            all_words = raw_text.split()
            filtered = [
                w for w in all_words 
                if len(w) > 2 
                and not w.isdigit() 
                and w.lower() not in filter_words
                and not re.match(r'^\d+[a-z]*$', w.lower())  # "500mg", "10ml"
            ]
            
            if filtered:
                # Take first 1-3 meaningful words as medicine name
                medicine_name = ' '.join(filtered[:3])
                print(f"📝 Extracted from keywords: '{medicine_name}'")
        
        # Strategy 3: Fallback to first line if still nothing
        if not medicine_name and lines:
            first_line = lines[0]
            # Basic cleaning
            cleaned = re.sub(r'[^\w\s\-]', ' ', first_line)
            cleaned = re.sub(r'\b\d+\b', '', cleaned)
            cleaned = ' '.join(cleaned.split())
            medicine_name = cleaned[:50]  # Limit length
            print(f"⚠️ Fallback to first line: '{medicine_name}'")
        
        # Final cleanup: remove extra spaces
        medicine_name = ' '.join(medicine_name.split())
        
        return medicine_name
    
    def _load_image(self, image_file):
        """Load an image from various sources."""
        if isinstance(image_file, Image.Image):
            return image_file

        if hasattr(image_file, 'read'):
            data = image_file.read()
            try:
                return Image.open(io.BytesIO(data))
            except Exception:
                try:
                    if hasattr(image_file, 'seek'):
                        image_file.seek(0)
                        return Image.open(image_file)
                except Exception:
                    raise

        if isinstance(image_file, str):
            return Image.open(image_file)

        raise ValueError('Unsupported image input type for OCRAgent')

    def extract_text(self, image_file):
        """Extract text from medicine packaging image using OpenRouter Gemini Vision API.

        Returns: { medicine_name, raw_text, confidence, is_medicine, model_info, (optional) error }
        """
        try:
            image = self._load_image(image_file)
            
            # Use OpenRouter Gemini Vision API
            if self.vision_available:
                print("🚀 Using OpenRouter Gemini 2.0 Flash Vision API (cloud-based & free)...")
                processed_image = self.preprocess_image(image)
                
                # Convert image to base64 for OpenRouter API
                img_byte_arr = io.BytesIO()
                processed_image.save(img_byte_arr, format='PNG')
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                
                # Create vision API request
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """Extract ALL text visible in this medicine packaging image. 
                                    Focus on: medicine name, generic name, dosage, manufacturer, batch number, expiry date.
                                    Return ONLY the extracted text, preserving the layout as much as possible.
                                    If you see a medicine name prominently displayed, mention it first."""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,  # Low temperature for accurate OCR
                    "max_tokens": 1000
                }
                
                # Try OpenRouter API call
                try:
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        raw_text = result['choices'][0]['message']['content']
                        print(f"📋 Gemini Vision extracted: {raw_text[:150]}...")
                    
                    else:
                        error_msg = response.text[:500] if response.text else "No error details"
                        print(f"❌ OpenRouter Gemini API error: {response.status_code}")
                        print(f"📄 Error details: {error_msg}")
                        
                        # Try alternative model (GPT-4o-mini)
                        print(f"🔄 Trying alternative vision model: {self.alternative_model}")
                        payload['model'] = self.alternative_model
                        
                        alt_response = requests.post(
                            self.api_url,
                            headers=self.headers,
                            json=payload,
                            timeout=30
                        )
                        
                        if alt_response.status_code == 200:
                            result = alt_response.json()
                            raw_text = result['choices'][0]['message']['content']
                            print(f"📋 Alternative model extracted: {raw_text[:150]}...")
                        else:
                            print(f"❌ Alternative model also failed: {alt_response.status_code}")
                            raise Exception(f"Both vision models failed")
                
                except Exception as api_error:
                    print(f"❌ OpenRouter Vision API failed: {api_error}")
                    print("❌ Using MOCK mode")
                    return self._mock_extract_text(image_file)

                # Update model info
                model_info = {
                    'ocr_engine': 'OpenRouter Gemini 2.0 Flash Vision (Cloud API)',
                    'model': 'google/gemini-2.0-flash-exp:free',
                    'preprocessing': 'Adaptive Contrast Enhancement',
                    'note': 'Cloud-based Vision OCR - FREE API tier'
                }

                # Analyze extracted text
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                is_medicine, pattern_confidence, detected_patterns = self._is_medicine_related(raw_text)
                
                # If text is too short, OCR likely failed
                if len(raw_text.strip()) < 10:
                    print(f"⚠️ OCR extracted very little text ({len(raw_text.strip())} chars)")
                    is_medicine = False
                    pattern_confidence = 0.0
                    detected_patterns = []
                    medicine_name = ''
                else:
                    # We got reasonable text, check if it's medicine
                    if not is_medicine:
                        # Even if patterns don't match, treat as medicine if user uploaded
                        print(f"⚠️ Pattern matching failed, but treating as medicine (user intent)")
                        is_medicine = True
                        pattern_confidence = 0.5

                medicine_name = ''
                confidence = pattern_confidence
                
                # Only extract medicine name if we have text
                if len(raw_text.strip()) >= 10:
                    medicine_name = self._extract_medicine_name(raw_text, lines)
                
                print(f"💊 Extracted medicine name: '{medicine_name}'")

                return {
                    'medicine_name': medicine_name,
                    'raw_text': raw_text,
                    'is_medicine': is_medicine,
                    'confidence': confidence,
                    'detected_patterns': detected_patterns,
                    'model_info': model_info
                }
            else:
                # OpenRouter Vision API not available, use MOCK mode
                print("⚠️ OpenRouter Vision API not available, using MOCK mode")
                return self._mock_extract_text(image_file)
                
        except Exception as e:
            print(f"❌ Exception in extract_text: {e}")
            return {
                'medicine_name': '',
                'raw_text': '',
                'is_medicine': False,
                'confidence': 0.0,
                'detected_patterns': [],
                'model_info': {'ocr_engine': 'Error', 'error': str(e)},
                'error': str(e)
            }
    
    def _mock_extract_text(self, image_file):
        """Mock OCR for testing."""
        print("🔧 MOCK MODE: Using generic medicine query")
        
        mock_text = "medicine tablet or syrup"
        is_medicine, confidence, detected_patterns = self._is_medicine_related(mock_text)
        
        return {
            'medicine_name': 'Unknown Medicine',
            'raw_text': mock_text,
            'is_medicine': True,
            'confidence': 0.4,
            'detected_patterns': detected_patterns,
            'model_info': {
                'ocr_engine': 'MOCK OCR (Fallback Mode)',
                'note': 'OCR failed - Please type the medicine name in chat'
            }
        }
