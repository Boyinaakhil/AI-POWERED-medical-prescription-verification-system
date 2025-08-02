import os
import requests
from typing import List, Dict, Any
import streamlit as st

class NERExtractor:
    def __init__(self):
        self.huggingface_token = os.getenv("HUGGINGFACE_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        
        # Model URLs for different entity types
        self.models = {
            'drugs': "https://api-inference.huggingface.co/models/OpenMed/OpenMed-NER-PharmaDetect-SuperClinical-434M",
            'diseases': "https://api-inference.huggingface.co/models/OpenMed/OpenMed-NER-DiseaseDetect-SuperClinical-184M",
            'clinical': "https://api-inference.huggingface.co/models/Posos/ClinicalNER"
        }
    
    def extract_entities(self, text: str, entity_type: str = 'drugs') -> List[Dict[str, Any]]:
        """Extract entities from medical text using specified model"""
        try:
            if not self.huggingface_token:
                return self._extract_entities_fallback(text, entity_type)
            
            if entity_type not in self.models:
                return self._extract_entities_fallback(text, entity_type)
            
            api_url = self.models[entity_type]
            payload = {"inputs": text}
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                entities = response.json()
                if isinstance(entities, list) and entities:
                    processed_entities = []
                    
                    for entity in entities:
                        processed_entity = {
                            'text': entity.get('word', ''),
                            'label': entity.get('entity_group', entity.get('entity', '')),
                            'confidence': entity.get('score', 0.0),
                            'start': entity.get('start', 0),
                            'end': entity.get('end', 0)
                        }
                        processed_entities.append(processed_entity)
                    
                    return processed_entities
                else:
                    return self._extract_entities_fallback(text, entity_type)
            else:
                return self._extract_entities_fallback(text, entity_type)
                
        except Exception as e:
            return self._extract_entities_fallback(text, entity_type)
    
    def _extract_entities_fallback(self, text: str, entity_type: str) -> List[Dict[str, Any]]:
        """Fallback method for entity extraction using pattern matching"""
        import re
        
        entities = []
        text_lower = text.lower()
        
        if entity_type == 'drugs':
            # Common drug name patterns
            drug_patterns = [
                r'\b(?:metformin|lisinopril|atorvastatin|amlodipine|metoprolol|losartan|simvastatin|aspirin|ibuprofen|acetaminophen|warfarin|furosemide|prednisone|omeprazole|levothyroxine|insulin|tramadol|sertraline|fluoxetine|gabapentin|hydrochlorothiazide|albuterol|montelukast|ciprofloxacin|amoxicillin|azithromycin|pantoprazole|citalopram|trazodone|alprazolam|lorazepam|hydrocodone|glipizide|sitagliptin)\b',
                r'\b\w+(?:in|ol|ide|ine|ate|pam|zole|statin|cillin|mycin|prazole|lol|pine|sartan|ide)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+\d+\s*mg\b'
            ]
            
            for pattern in drug_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': 'DRUG',
                        'confidence': 0.85,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        elif entity_type == 'diseases':
            # Common medical conditions
            disease_patterns = [
                r'\b(?:hypertension|diabetes|depression|anxiety|asthma|copd|arthritis|pneumonia|bronchitis|sinusitis|migraine|insomnia|gerd|ibs|uti|infection)\b',
                r'\b(?:high blood pressure|type 2 diabetes|heart failure|atrial fibrillation|coronary artery disease)\b'
            ]
            
            for pattern in disease_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': 'DISEASE',
                        'confidence': 0.80,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return entities
    
    def extract_drug_details(self, text: str) -> Dict[str, List[str]]:
        """Extract detailed drug information from text"""
        drug_entities = self.extract_entities(text, 'drugs')
        clinical_entities = self.extract_entities(text, 'clinical')
        
        # Combine and categorize entities
        drug_details = {
            'drugs': [],
            'dosages': [],
            'frequencies': [],
            'durations': [],
            'forms': []
        }
        
        # Process drug entities
        for entity in drug_entities:
            label = entity['label'].upper()
            text_content = entity['text']
            
            if 'CHEMICAL' in label or 'DRUG' in label or 'PHARMA' in label:
                if text_content not in drug_details['drugs']:
                    drug_details['drugs'].append(text_content)
        
        # Process clinical entities for dosage information
        for entity in clinical_entities:
            label = entity['label'].upper()
            text_content = entity['text']
            
            if 'STRENGTH' in label or 'DOSAGE' in label:
                if text_content not in drug_details['dosages']:
                    drug_details['dosages'].append(text_content)
            elif 'FREQUENCY' in label:
                if text_content not in drug_details['frequencies']:
                    drug_details['frequencies'].append(text_content)
            elif 'DURATION' in label:
                if text_content not in drug_details['durations']:
                    drug_details['durations'].append(text_content)
            elif 'FORM' in label:
                if text_content not in drug_details['forms']:
                    drug_details['forms'].append(text_content)
        
        return drug_details
    
    def analyze_medical_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of medical text"""
        analysis_result = {
            'drugs': self.extract_entities(text, 'drugs'),
            'diseases': self.extract_entities(text, 'diseases'),
            'clinical_info': self.extract_entities(text, 'clinical'),
            'summary': {}
        }
        
        # Generate summary
        drug_count = len([e for e in analysis_result['drugs'] if e['confidence'] > 0.8])
        disease_count = len([e for e in analysis_result['diseases'] if e['confidence'] > 0.8])
        
        analysis_result['summary'] = {
            'total_drugs_found': drug_count,
            'total_diseases_found': disease_count,
            'confidence_threshold': 0.8,
            'text_length': len(text),
            'analysis_timestamp': self._get_timestamp()
        }
        
        return analysis_result
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def format_entities_for_display(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format entities for Streamlit display"""
        formatted_entities = []
        
        for entity in entities:
            if entity['confidence'] > 0.5:  # Filter low confidence entities
                formatted_entity = {
                    'Entity': entity['text'],
                    'Type': entity['label'],
                    'Confidence': f"{entity['confidence']:.2%}",
                    'Position': f"{entity['start']}-{entity['end']}"
                }
                formatted_entities.append(formatted_entity)
        
        return formatted_entities
