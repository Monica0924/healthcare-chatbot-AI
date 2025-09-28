import streamlit as st
import chromadb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import plotly.express as px

# Simple test to verify all imports work
st.title("🧬 Profile Vector Database System - Test")
st.success("✅ All dependencies installed successfully!")

# Test ChromaDB connection
try:
    client = chromadb.PersistentClient(path="./test_vector_db")
    collection = client.get_or_create_collection(name="test_profiles")
    st.success("✅ ChromaDB connection successful!")
except Exception as e:
    st.error(f"❌ ChromaDB connection failed: {str(e)}")

# Test sentence transformers
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    st.success("✅ Sentence transformer model loaded successfully!")
    
    # Test embedding creation
    test_text = "This is a test profile for medical patient"
    embedding = model.encode(test_text)
    st.write(f"✅ Test embedding created with shape: {embedding.shape}")
except Exception as e:
    st.error(f"❌ Sentence transformer failed: {str(e)}")

# Test data visualization
try:
    test_data = pd.DataFrame({
        'Age': [25, 30, 35, 40, 45],
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Other'],
        'Count': [10, 15, 8, 12, 5]
    })
    
    fig = px.pie(test_data, values='Count', names='Gender', title='Gender Distribution')
    st.plotly_chart(fig)
    st.success("✅ Plotly visualization working!")
except Exception as e:
    st.error(f"❌ Plotly visualization failed: {str(e)}")

st.info("🎯 The system is ready for profile management with vector database capabilities!")