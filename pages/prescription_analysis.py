import streamlit as st
from models.ocr_processor import OCRProcessor
from models.ner_extractor import NERExtractor
from PIL import Image
import pandas as pd

def show():
    st.markdown("## 📄 Prescription Image Analysis")
    st.markdown("Upload a prescription image to extract drug names and check for interactions")
    
    # Initialize models
    if 'ocr_processor' not in st.session_state:
        st.session_state.ocr_processor = OCRProcessor()
    
    if 'ner_extractor' not in st.session_state:
        st.session_state.ner_extractor = NERExtractor()
    
    # Create columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload prescription in any format")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Drag and drop file here",
            type=['png', 'jpg', 'jpeg', 'pdf', 'tiff', 'bmp', 'webp', 'heic'],
            help="Limit 200MB per file • PNG, JPG, JPEG, BMP, TIFF, PDF, WEBP, HEIC"
        )
        
        # OCR type selection
        ocr_type = st.selectbox(
            "Prescription Type",
            ["Printed", "Handwritten", "Structured"],
            help="Select the type of prescription for optimal OCR processing"
        )
        
        # Browse files button (for UI consistency)
        if st.button("Browse Files", type="secondary", use_container_width=True):
            st.info("Please use the file uploader above to select your prescription image.")
    
    with col2:
        st.markdown("### 🎯 Try Demo")
        st.markdown("Select prescription type to simulate:")
        
        demo_type = st.selectbox(
            "Select prescription type to simulate:",
            ["General Medicine", "Cardiology", "Diabetes"],
            key="demo_prescription_type"
        )
        
        if st.button("Generate Demo Prescription", type="primary", use_container_width=True):
            demo_text = st.session_state.ocr_processor.generate_demo_prescription(demo_type)
            st.session_state.demo_prescription = demo_text
            st.session_state.ocr_result = {
                'success': True,
                'extracted_text': demo_text,
                'confidence': 0.95,
                'model_used': 'demo-generator'
            }
    
    # Process uploaded image
    if uploaded_file is not None:
        try:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Prescription", use_container_width=True)
            
            # Process with OCR
            with st.spinner("Processing prescription image..."):
                ocr_type_map = {
                    "Printed": "printed",
                    "Handwritten": "handwritten", 
                    "Structured": "structured"
                }
                
                result = st.session_state.ocr_processor.process_prescription_image(
                    image, 
                    ocr_type_map[ocr_type]
                )
                st.session_state.ocr_result = result
                
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    
    # Display OCR results
    if hasattr(st.session_state, 'ocr_result'):
        result = st.session_state.ocr_result
        
        if result['success']:
            st.markdown("---")
            st.markdown("## 📝 Extracted Text")
            
            # Show confidence and model info
            col1, col2 = st.columns(2)
            with col1:
                confidence_color = "🟢" if result['confidence'] > 0.8 else "🟡" if result['confidence'] > 0.6 else "🔴"
                st.metric("Confidence", f"{confidence_color} {result['confidence']:.1%}")
            with col2:
                st.metric("Model Used", result['model_used'])
            
            # Display extracted text
            extracted_text = result['extracted_text']
            st.text_area("Extracted Text", extracted_text, height=200, disabled=True)
            
            # Extract structured drug information
            if st.button("Extract Drug Information", type="primary"):
                with st.spinner("Analyzing extracted text..."):
                    # Use NER to extract drug information
                    analysis = st.session_state.ner_extractor.analyze_medical_text(extracted_text)
                    st.session_state.prescription_analysis = analysis
        else:
            st.error(f"OCR Processing Failed: {result['error']}")
    
    # Display drug analysis results
    if hasattr(st.session_state, 'prescription_analysis'):
        analysis = st.session_state.prescription_analysis
        
        st.markdown("---")
        st.markdown("## 🎯 Drug Information Analysis")
        
        # Summary metrics
        summary = analysis['summary']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Drugs Found", summary['total_drugs_found'])
        with col2:
            st.metric("Diseases Found", summary['total_diseases_found'])
        with col3:
            st.metric("Text Length", f"{summary['text_length']} chars")
        with col4:
            st.metric("Confidence Threshold", f"{summary['confidence_threshold']:.1%}")
        
        # Drugs section
        if analysis['drugs']:
            st.markdown("### 💊 Detected Drugs")
            drug_entities = st.session_state.ner_extractor.format_entities_for_display(analysis['drugs'])
            if drug_entities:
                df_drugs = pd.DataFrame(drug_entities)
                st.dataframe(df_drugs, use_container_width=True)
        
        # Diseases section
        if analysis['diseases']:
            st.markdown("### 🏥 Detected Medical Conditions")
            disease_entities = st.session_state.ner_extractor.format_entities_for_display(analysis['diseases'])
            if disease_entities:
                df_diseases = pd.DataFrame(disease_entities)
                st.dataframe(df_diseases, use_container_width=True)
        
        # Clinical information
        if analysis['clinical_info']:
            st.markdown("### 📋 Clinical Information")
            clinical_entities = st.session_state.ner_extractor.format_entities_for_display(analysis['clinical_info'])
            if clinical_entities:
                df_clinical = pd.DataFrame(clinical_entities)
                st.dataframe(df_clinical, use_container_width=True)
    
    # Universal Format Support info
    st.markdown("---")
    st.markdown("### 🌍 Universal Format Support")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **✓ Handwritten prescriptions** (all writing styles) • **✓ Printed prescriptions** (all fonts and layouts) • 
        **✓ Mobile phone photos** (automatic perspective correction) • **✓ Scanned documents** (all quality levels) • 
        **✓ Fax transmissions and carbon copies** • **✓ Low quality/damaged prescriptions** • 
        **✓ Multilingual prescriptions** (15+ languages) • **✓ All formats:** JPG, PNG, TIFF, BMP, WEBP, HEIC, PDF
        """)
    
    with col2:
        st.info("""
        **🔍 AI Features**
        
        **Available AI Capabilities:**
        
        • **Advanced NER:** Uses BioBERT for medical entity recognition
        • **Drug Extraction:** Identifies medications from unstructured text  
        • **Dosage Parsing:** Extracts dosage amounts and units
        • **Interaction Analysis:** AI-powered drug interaction insights
        • **Drug Information:** Comprehensive medication details
        • **Question Answering:** Medical text comprehension
        
        **Note:** AI features require a valid Hugging Face API key. The system uses state-of-the-art medical NLP models for enhanced accuracy.
        """)
    
    # Help section
    with st.expander("ℹ️ How to Use Prescription Analysis"):
        st.markdown("""
        **Upload Process:**
        1. **Choose your prescription type** for optimal processing
        2. **Upload image** using the file uploader or drag & drop
        3. **Review extracted text** and confidence score
        4. **Extract drug information** using AI analysis
        
        **Supported Formats:**
        - All major image formats (PNG, JPG, PDF, etc.)
        - Handwritten and printed prescriptions
        - Mobile photos and scanned documents
        - Low quality and damaged prescriptions
        
        **AI Analysis:**
        - Uses OpenMed NER models for drug extraction
        - TrOCR for text recognition
        - Clinical NER for comprehensive analysis
        
        **Demo Mode:**
        Try the demo feature to see how the system works with sample prescriptions.
        """)
