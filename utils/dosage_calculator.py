from typing import Dict, Any, Tuple, List
import re

class DosageCalculator:
    def __init__(self):
        # Age categories
        self.age_categories = {
            'pediatric': (0, 17),
            'adult': (18, 64),
            'geriatric': (65, 120)
        }
        
        # Standard dosing guidelines (simplified)
        self.dosing_guidelines = {
            'aspirin': {
                'pediatric': {'min': 0, 'max': 0, 'unit': 'mg', 'note': 'Generally contraindicated'},
                'adult': {'min': 81, 'max': 1000, 'unit': 'mg', 'note': 'Cardioprotective: 81mg daily, Pain: 325-650mg q4-6h'},
                'geriatric': {'min': 81, 'max': 650, 'unit': 'mg', 'note': 'Use lowest effective dose'}
            },
            'metformin': {
                'pediatric': {'min': 500, 'max': 2000, 'unit': 'mg', 'note': 'Children ≥10 years: 500mg BID, max 2000mg/day'},
                'adult': {'min': 500, 'max': 2550, 'unit': 'mg', 'note': 'Initial: 500mg BID, max 2550mg/day'},
                'geriatric': {'min': 500, 'max': 2000, 'unit': 'mg', 'note': 'Monitor renal function, max 2000mg/day'}
            },
            'lisinopril': {
                'pediatric': {'min': 0.07, 'max': 0.6, 'unit': 'mg/kg', 'note': 'Children ≥6 years: 0.07mg/kg once daily'},
                'adult': {'min': 2.5, 'max': 40, 'unit': 'mg', 'note': 'Initial: 2.5-5mg daily, max 40mg daily'},
                'geriatric': {'min': 2.5, 'max': 20, 'unit': 'mg', 'note': 'Start low, titrate slowly'}
            },
            'warfarin': {
                'pediatric': {'min': 0.05, 'max': 0.34, 'unit': 'mg/kg', 'note': 'Limited data, use with extreme caution'},
                'adult': {'min': 2, 'max': 10, 'unit': 'mg', 'note': 'Initial: 2-5mg daily, adjust based on INR'},
                'geriatric': {'min': 1, 'max': 7.5, 'unit': 'mg', 'note': 'Lower initial doses, more frequent monitoring'}
            },
            'simvastatin': {
                'pediatric': {'min': 10, 'max': 40, 'unit': 'mg', 'note': 'Children ≥10 years with familial hypercholesterolemia'},
                'adult': {'min': 5, 'max': 80, 'unit': 'mg', 'note': 'Initial: 10-20mg daily, max 80mg daily'},
                'geriatric': {'min': 5, 'max': 40, 'unit': 'mg', 'note': 'Start with 5-10mg daily, avoid 80mg dose'}
            }
        }
    
    def calculate_age_category(self, age: int) -> str:
        """Determine age category based on patient age"""
        for category, (min_age, max_age) in self.age_categories.items():
            if min_age <= age <= max_age:
                return category
        return 'adult'  # Default to adult if age is out of range
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> Tuple[float, str]:
        """Calculate BMI and category"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = 'Underweight'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
        elif 25 <= bmi < 30:
            category = 'Overweight'
        else:
            category = 'Obese'
        
        return round(bmi, 1), category
    
    def parse_dosage(self, dosage_string: str) -> Dict[str, Any]:
        """Parse dosage string to extract dose, unit, and frequency"""
        # Common patterns for dosage parsing
        patterns = {
            'dose_unit': r'(\d+(?:\.\d+)?)\s*(mg|ml|g|mcg|units?)',
            'frequency': r'(once|twice|thrice|\d+\s*times?)\s*(?:daily|a day|per day)',
            'timing': r'(morning|evening|bedtime|with meals|before meals|after meals)'
        }
        
        parsed_info = {
            'dose': None,
            'unit': None,
            'frequency': None,
            'timing': None,
            'original': dosage_string
        }
        
        # Extract dose and unit
        dose_match = re.search(patterns['dose_unit'], dosage_string, re.IGNORECASE)
        if dose_match:
            parsed_info['dose'] = float(dose_match.group(1))
            parsed_info['unit'] = dose_match.group(2)
        
        # Extract frequency
        freq_match = re.search(patterns['frequency'], dosage_string, re.IGNORECASE)
        if freq_match:
            parsed_info['frequency'] = freq_match.group(1)
        
        # Extract timing
        timing_match = re.search(patterns['timing'], dosage_string, re.IGNORECASE)
        if timing_match:
            parsed_info['timing'] = timing_match.group(1)
        
        return parsed_info
    
    def verify_dosage(self, drug_name: str, dosage: str, patient_age: int, 
                     patient_weight: float = 70.0) -> Dict[str, Any]:
        """Verify if prescribed dosage is appropriate for patient"""
        drug_key = drug_name.lower().strip()
        age_category = self.calculate_age_category(patient_age)
        parsed_dosage = self.parse_dosage(dosage)
        
        verification_result = {
            'drug': drug_name,
            'prescribed_dosage': dosage,
            'parsed_dosage': parsed_dosage,
            'age_category': age_category,
            'is_appropriate': False,
            'warnings': [],
            'recommendations': [],
            'guidelines': {}
        }
        
        if drug_key not in self.dosing_guidelines:
            verification_result['warnings'].append(f"No dosing guidelines available for {drug_name}")
            return verification_result
        
        guidelines = self.dosing_guidelines[drug_key][age_category]
        verification_result['guidelines'] = guidelines
        
        if parsed_dosage['dose'] is None:
            verification_result['warnings'].append("Could not parse dose from prescription")
            return verification_result
        
        prescribed_dose = parsed_dosage['dose']
        min_dose = guidelines['min']
        max_dose = guidelines['max']
        
        # Check if dose is within recommended range
        if min_dose <= prescribed_dose <= max_dose:
            verification_result['is_appropriate'] = True
            verification_result['recommendations'].append("Dosage is within recommended range")
        else:
            if prescribed_dose < min_dose:
                verification_result['warnings'].append(
                    f"Prescribed dose ({prescribed_dose}{parsed_dosage['unit']}) is below recommended minimum ({min_dose}{guidelines['unit']})"
                )
                verification_result['recommendations'].append(
                    f"Consider increasing dose to at least {min_dose}{guidelines['unit']}"
                )
            
            if prescribed_dose > max_dose:
                verification_result['warnings'].append(
                    f"Prescribed dose ({prescribed_dose}{parsed_dosage['unit']}) exceeds recommended maximum ({max_dose}{guidelines['unit']})"
                )
                verification_result['recommendations'].append(
                    f"Consider reducing dose to maximum {max_dose}{guidelines['unit']}"
                )
        
        # Add age-specific notes
        if guidelines['note']:
            verification_result['recommendations'].append(f"Age-specific guidance: {guidelines['note']}")
        
        return verification_result
    
    def calculate_recommended_dosage(self, drug_name: str, patient_age: int, 
                                   patient_weight: float, medical_conditions: List[str] = []) -> Dict[str, Any]:
        """Calculate recommended dosage based on patient parameters"""
        drug_key = drug_name.lower().strip()
        age_category = self.calculate_age_category(patient_age)
        
        recommendation = {
            'drug': drug_name,
            'age_category': age_category,
            'recommended_dose': None,
            'dosing_frequency': None,
            'special_considerations': [],
            'contraindications': []
        }
        
        if drug_key not in self.dosing_guidelines:
            recommendation['special_considerations'].append(f"No specific guidelines available for {drug_name}")
            return recommendation
        
        guidelines = self.dosing_guidelines[drug_key][age_category]
        
        # Calculate starting dose (usually minimum or slightly above)
        if age_category == 'geriatric':
            # Start with minimum dose for elderly
            recommended_dose = guidelines['min']
        elif age_category == 'pediatric' and guidelines['unit'] == 'mg/kg':
            # Weight-based dosing for children
            recommended_dose = round(guidelines['min'] * patient_weight, 1)
        else:
            # Standard adult dosing - start with low-normal dose
            dose_range = guidelines['max'] - guidelines['min']
            recommended_dose = guidelines['min'] + (dose_range * 0.25)  # 25% into the range
        
        recommendation['recommended_dose'] = f"{recommended_dose}{guidelines['unit']}"
        recommendation['dosing_frequency'] = self._get_standard_frequency(drug_key)
        
        # Add special considerations
        if guidelines['note']:
            recommendation['special_considerations'].append(guidelines['note'])
        
        # Add medical condition considerations
        if medical_conditions:
            condition_warnings = self._get_condition_warnings(drug_key, medical_conditions)
            recommendation['special_considerations'].extend(condition_warnings)
        
        return recommendation
    
    def _get_standard_frequency(self, drug_name: str) -> str:
        """Get standard dosing frequency for a drug"""
        frequencies = {
            'aspirin': 'Once daily (cardioprotective) or every 4-6 hours (pain)',
            'metformin': 'Twice daily with meals',
            'lisinopril': 'Once daily',
            'warfarin': 'Once daily, same time each day',
            'simvastatin': 'Once daily in the evening'
        }
        return frequencies.get(drug_name, 'As directed by physician')
    
    def _get_condition_warnings(self, drug_name: str, conditions: List[str]) -> List[str]:
        """Get warnings based on patient's medical conditions"""
        warnings = []
        condition_lower = [c.lower() for c in conditions]
        
        condition_warnings = {
            'aspirin': {
                'chronic kidney disease': 'Use with caution, monitor renal function',
                'heart failure': 'Monitor for fluid retention',
                'gerd': 'Increased risk of GI bleeding'
            },
            'metformin': {
                'chronic kidney disease': 'Contraindicated if eGFR <30, use caution if eGFR 30-45',
                'heart failure': 'Monitor for lactic acidosis risk'
            },
            'lisinopril': {
                'chronic kidney disease': 'Monitor renal function and potassium',
                'diabetes type 2': 'Beneficial for renal protection'
            },
            'warfarin': {
                'atrial fibrillation': 'Indicated for stroke prevention',
                'chronic kidney disease': 'Monitor INR more frequently'
            },
            'simvastatin': {
                'diabetes type 2': 'Monitor for increased glucose levels',
                'chronic kidney disease': 'Use with caution in severe impairment'
            }
        }
        
        drug_warnings = condition_warnings.get(drug_name, {})
        for condition, warning in drug_warnings.items():
            if any(condition in c for c in condition_lower):
                warnings.append(warning)
        
        return warnings
