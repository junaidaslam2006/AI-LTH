import pandas as pd
from rapidfuzz import fuzz, process
import os
import PyPDF2

class DatasetSearchAgent:
    def __init__(self):
        self.df = None
        self.pdf_data = []
        self.load_dataset()
    
    def load_csv_files(self, data_dir):
        """Load all CSV files from data directory"""
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print("No CSV files found")
            return None
        
        print(f"Found CSV files: {csv_files}")
        
        # Load first CSV or combine all CSVs
        dataframes = []
        for csv_file in csv_files:
            csv_path = os.path.join(data_dir, csv_file)
            try:
                df = pd.read_csv(csv_path, encoding='utf-8')
                print(f"Loaded {csv_file}: {len(df)} records")
                dataframes.append(df)
            except Exception as e:
                try:
                    # Try different encoding
                    df = pd.read_csv(csv_path, encoding='latin-1')
                    print(f"Loaded {csv_file} with latin-1: {len(df)} records")
                    dataframes.append(df)
                except Exception as e2:
                    print(f"Error loading {csv_file}: {e2}")
        
        if dataframes:
            # Combine all dataframes
            combined_df = pd.concat(dataframes, ignore_index=True)
            # Standardize column names
            combined_df.columns = combined_df.columns.str.lower().str.replace(' ', '_')
            return combined_df
        
        return None
    
    def load_pdf_files(self, data_dir):
        """Extract medicine data from PDF files"""
        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("No PDF files found")
            return []
        
        print(f"Found PDF files: {pdf_files}")
        
        extracted_data = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(data_dir, pdf_file)
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    
                    # Store PDF text for keyword search
                    extracted_data.append({
                        'filename': pdf_file,
                        'content': text
                    })
                    print(f"Extracted text from {pdf_file}: {len(text)} characters")
            except Exception as e:
                print(f"Error reading PDF {pdf_file}: {e}")
        
        return extracted_data
    
    def load_dataset(self):
        """Load medicine dataset from CSV and PDF files"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created data directory at {data_dir}")
                self.create_sample_dataset()
                return
            
            # Load CSV files
            self.df = self.load_csv_files(data_dir)
            
            # Load PDF files
            self.pdf_data = self.load_pdf_files(data_dir)
            
            # If no data loaded, create sample
            if self.df is None and not self.pdf_data:
                print("No dataset files found, creating sample data")
                self.create_sample_dataset()
            else:
                total_records = len(self.df) if self.df is not None else 0
                print(f"Dataset loaded successfully: {total_records} CSV records, {len(self.pdf_data)} PDF files")
                
        except Exception as e:
            print(f"Error loading dataset: {e}")
            self.create_sample_dataset()
    
    def create_sample_dataset(self):
        """Create a sample dataset if files not found"""
        sample_data = {
            'brand_name': ['Panadol', 'Brufen', 'Flagyl', 'Augmentin', 'Disprin', 'Calpol', 'Ponstan', 'Arinac'],
            'generic_name': ['Paracetamol', 'Ibuprofen', 'Metronidazole', 'Amoxicillin + Clavulanic Acid', 
                           'Aspirin', 'Paracetamol', 'Mefenamic Acid', 'Paracetamol + Chlorpheniramine'],
            'composition': ['Paracetamol 500mg', 'Ibuprofen 400mg', 'Metronidazole 400mg', 
                          'Amoxicillin 875mg + Clavulanic Acid 125mg', 'Aspirin 300mg',
                          'Paracetamol 120mg/5ml', 'Mefenamic Acid 500mg', 'Paracetamol 500mg + Chlorpheniramine 2mg'],
            'uses': ['Pain relief, fever reduction', 'Pain relief, inflammation', 
                    'Bacterial infections, parasitic infections', 'Bacterial infections',
                    'Pain relief, fever, blood thinning', 'Pain and fever in children',
                    'Pain relief, menstrual pain', 'Cold, flu, fever, allergies'],
            'side_effects': ['Nausea, rash (rare)', 'Stomach upset, dizziness', 
                           'Nausea, metallic taste', 'Diarrhea, nausea',
                           'Stomach irritation, bleeding risk', 'Nausea (rare)',
                           'Stomach upset, dizziness', 'Drowsiness, dry mouth'],
            'manufacturer': ['GSK Pakistan', 'Abbott Pakistan', 'Sanofi Pakistan', 
                           'GSK Pakistan', 'Bayer Pakistan', 'GSK Pakistan',
                           'Pfizer Pakistan', 'Hilton Pharma Pakistan']
        }
        self.df = pd.DataFrame(sample_data)
        print("Sample dataset created with 8 medicines")
    
    def search_in_csv(self, medicine_name, threshold=70):
        """Search in CSV data"""
        if self.df is None or self.df.empty:
            return None
        
        # Try to find brand_name column (could be 'brand_name', 'brandname', 'name', etc.)
        possible_name_cols = ['brand_name', 'brandname', 'name', 'medicine_name', 'product_name']
        name_col = None
        
        for col in possible_name_cols:
            if col in self.df.columns:
                name_col = col
                break
        
        if name_col is None:
            # Use first column as default
            name_col = self.df.columns[0]
            print(f"Using column '{name_col}' as medicine name")
        
        # Get all medicine names
        medicine_names = self.df[name_col].astype(str).tolist()
        
        # Fuzzy match
        result = process.extractOne(medicine_name, medicine_names, scorer=fuzz.ratio)
        
        if result and result[1] >= threshold:
            matched_name = result[0]
            confidence = result[1] / 100.0
            
            # Get the medicine row
            medicine_row = self.df[self.df[name_col] == matched_name].iloc[0]
            
            # Dynamically build response based on available columns
            response = {
                'brand_name': medicine_row.get('brand_name', medicine_row.get('brandname', medicine_row.get('name', matched_name))),
                'generic_name': medicine_row.get('generic_name', medicine_row.get('genericname', 'N/A')),
                'composition': medicine_row.get('composition', medicine_row.get('ingredients', 'N/A')),
                'uses': medicine_row.get('uses', medicine_row.get('indications', 'N/A')),
                'side_effects': medicine_row.get('side_effects', medicine_row.get('sideeffects', medicine_row.get('adverse_effects', 'N/A'))),
                'manufacturer': medicine_row.get('manufacturer', medicine_row.get('company', 'N/A')),
                'confidence': confidence,
                'source': 'CSV Database'
            }
            
            return response
        
        return None
    
    def search_in_pdf(self, medicine_name):
        """Search for medicine in PDF content"""
        if not self.pdf_data:
            return None
        
        best_match = None
        best_score = 0
        
        for pdf in self.pdf_data:
            content = pdf['content'].lower()
            medicine_lower = medicine_name.lower()
            
            # Check if medicine name appears in PDF
            if medicine_lower in content:
                # Extract context around the medicine name
                index = content.find(medicine_lower)
                start = max(0, index - 200)
                end = min(len(content), index + 500)
                context = content[start:end]
                
                # Calculate relevance score
                score = fuzz.partial_ratio(medicine_name, context)
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'brand_name': medicine_name.title(),
                        'generic_name': 'Information from PDF',
                        'composition': 'N/A',
                        'uses': context[:300] + '...',
                        'side_effects': 'Refer to full document',
                        'manufacturer': 'N/A',
                        'confidence': score / 100.0,
                        'source': f"PDF: {pdf['filename']}"
                    }
        
        return best_match if best_score > 60 else None
    
    def search(self, medicine_name, threshold=70):
        """Search for medicine in both CSV and PDF sources"""
        # Try CSV first (more structured)
        csv_result = self.search_in_csv(medicine_name, threshold)
        
        if csv_result and csv_result['confidence'] > 0.85:
            return csv_result
        
        # Try PDF if CSV match is weak or not found
        pdf_result = self.search_in_pdf(medicine_name)
        
        # Return best result
        if csv_result and pdf_result:
            return csv_result if csv_result['confidence'] > pdf_result['confidence'] else pdf_result
        
        return csv_result or pdf_result
    
    def get_all_medicine_names(self):
        """Get list of all medicine names for autocomplete"""
        names = []
        
        if self.df is not None:
            # Find name column
            possible_cols = ['brand_name', 'brandname', 'name', 'medicine_name']
            for col in possible_cols:
                if col in self.df.columns:
                    names.extend(self.df[col].astype(str).tolist())
                    break
        
        return list(set(names))  # Remove duplicates
    
    def is_loaded(self):
        """Check if dataset is loaded"""
        return (self.df is not None and not self.df.empty) or len(self.pdf_data) > 0
