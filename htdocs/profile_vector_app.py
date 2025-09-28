import streamlit as st
import chromadb
from chromadb.config import Settings
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid
import json

# Page configuration
st.set_page_config(
    page_title="Profile Vector Database System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_profile_id' not in st.session_state:
    st.session_state.current_profile_id = None
if 'profiles' not in st.session_state:
    st.session_state.profiles = []

@st.cache_resource
def init_vector_db():
    """Initialize ChromaDB vector database"""
    try:
        # Create ChromaDB client with persistent storage
        client = chromadb.PersistentClient(path="./vector_db")
        
        # Create or get collection for profiles
        collection = client.get_or_create_collection(
            name="user_profiles",
            metadata={"hnsw:space": "cosine"}
        )
        return client, collection
    except Exception as e:
        st.error(f"Error initializing vector database: {str(e)}")
        return None, None

@st.cache_resource
def init_embedding_model():
    """Initialize sentence transformer model for embeddings"""
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        st.error(f"Error loading embedding model: {str(e)}")
        return None

def create_profile_embedding(profile_data, model):
    """Create vector embedding from profile data"""
    # Combine profile information into a single text
    profile_text = f"""
    Name: {profile_data.get('name', '')}
    Age: {profile_data.get('age', '')}
    Gender: {profile_data.get('gender', '')}
    Medical History: {profile_data.get('medical_history', '')}
    Allergies: {profile_data.get('allergies', '')}
    Address: {profile_data.get('address', '')}
    Phone: {profile_data.get('phone', '')}
    Email: {profile_data.get('email', '')}
    """
    
    # Generate embedding
    embedding = model.encode(profile_text).tolist()
    return embedding

def add_profile_to_vector_db(profile_data, collection, model):
    """Add profile to vector database"""
    try:
        profile_id = str(uuid.uuid4())
        embedding = create_profile_embedding(profile_data, model)
        
        # Prepare metadata
        metadata = {
            "name": profile_data.get('name', ''),
            "age": str(profile_data.get('age', '')),
            "gender": profile_data.get('gender', ''),
            "email": profile_data.get('email', ''),
            "phone": profile_data.get('phone', ''),
            "address": profile_data.get('address', ''),
            "created_at": datetime.now().isoformat()
        }
        
        # Add to collection
        collection.add(
            embeddings=[embedding],
            documents=[json.dumps(profile_data)],
            metadatas=[metadata],
            ids=[profile_id]
        )
        
        return profile_id
    except Exception as e:
        st.error(f"Error adding profile to vector database: {str(e)}")
        return None

def search_similar_profiles(query_text, collection, model, n_results=5):
    """Search for similar profiles using vector similarity"""
    try:
        # Create embedding for search query
        query_embedding = model.encode(query_text).tolist()
        
        # Search in vector database
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return results
    except Exception as e:
        st.error(f"Error searching profiles: {str(e)}")
        return None

def get_all_profiles(collection):
    """Get all profiles from vector database"""
    try:
        results = collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        return results
    except Exception as e:
        st.error(f"Error retrieving profiles: {str(e)}")
        return None

def delete_profile(profile_id, collection):
    """Delete profile from vector database"""
    try:
        collection.delete(ids=[profile_id])
        return True
    except Exception as e:
        st.error(f"Error deleting profile: {str(e)}")
        return False

def create_profile_visualization(profiles_data):
    """Create visualizations for profile data"""
    if not profiles_data or not profiles_data.get('metadatas'):
        return None
    
    # Extract data for visualization
    metadata_list = profiles_data['metadatas']
    
    # Age distribution
    ages = [int(meta.get('age', 0)) for meta in metadata_list if meta.get('age', '').isdigit()]
    
    # Gender distribution
    genders = [meta.get('gender', 'Unknown') for meta in metadata_list]
    gender_counts = pd.Series(genders).value_counts()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Age Distribution', 'Gender Distribution', 'Profile Count Over Time', 'Medical Conditions'),
        specs=[[{"type": "histogram"}, {"type": "pie"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # Age histogram
    if ages:
        fig.add_trace(
            go.Histogram(x=ages, name="Age Distribution", nbinsx=10),
            row=1, col=1
        )
    
    # Gender pie chart
    if len(gender_counts) > 0:
        fig.add_trace(
            go.Pie(labels=gender_counts.index, values=gender_counts.values, name="Gender"),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(height=800, showlegend=True, title_text="Profile Analytics Dashboard")
    
    return fig

# Main application
def main():
    st.title("🧬 Profile Vector Database System")
    st.markdown("---")
    
    # Initialize database and model
    client, collection = init_vector_db()
    model = init_embedding_model()
    
    if not collection or not model:
        st.error("Failed to initialize system components. Please check your setup.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("🚀 Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose an option:",
        ["🏠 Dashboard", "➕ Create Profile", "🔍 Search Profiles", "📊 Analytics", "🗂️ View All Profiles"]
    )
    
    if app_mode == "🏠 Dashboard":
        show_dashboard(collection, model)
    elif app_mode == "➕ Create Profile":
        create_profile_page(collection, model)
    elif app_mode == "🔍 Search Profiles":
        search_profiles_page(collection, model)
    elif app_mode == "📊 Analytics":
        analytics_page(collection)
    elif app_mode == "🗂️ View All Profiles":
        view_all_profiles_page(collection)

def show_dashboard(collection, model):
    """Display dashboard with system overview"""
    st.header("📈 System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get statistics
    all_profiles = get_all_profiles(collection)
    
    with col1:
        st.metric(
            label="Total Profiles",
            value=len(all_profiles['ids']) if all_profiles and all_profiles.get('ids') else 0,
            delta="Active users"
        )
    
    with col2:
        st.metric(
            label="Vector Dimensions",
            value="384",
            delta="MiniLM-L6-v2"
        )
    
    with col3:
        st.metric(
            label="Database Status",
            value="🟢 Online",
            delta="ChromaDB"
        )
    
    with col4:
        st.metric(
            label="Model Status",
            value="🟢 Loaded",
            delta="Sentence Transformer"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create New Profile", use_container_width=True):
            st.session_state.page = "create_profile"
            st.rerun()
    
    with col2:
        if st.button("🔍 Search Profiles", use_container_width=True):
            st.session_state.page = "search"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()

def create_profile_page(collection, model):
    """Profile creation interface"""
    st.header("➕ Create New Profile")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter full name")
            email = st.text_input("Email *", placeholder="Enter email address")
            phone = st.text_input("Phone Number", placeholder="Enter phone number")
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
        
        with col2:
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            address = st.text_area("Address", placeholder="Enter full address")
            medical_history = st.text_area("Medical History", placeholder="Describe any past medical conditions, surgeries, or treatments")
            allergies = st.text_area("Allergies", placeholder="List any known allergies")
        
        submitted = st.form_submit_button("Create Profile", type="primary")
        
        if submitted and name and email:
            profile_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "age": age,
                "gender": gender,
                "address": address,
                "medical_history": medical_history,
                "allergies": allergies,
                "created_at": datetime.now().isoformat()
            }
            
            profile_id = add_profile_to_vector_db(profile_data, collection, model)
            
            if profile_id:
                st.success(f"✅ Profile created successfully! ID: {profile_id}")
                st.info("🎯 The profile has been stored in the vector database with embeddings for semantic search.")
            else:
                st.error("❌ Failed to create profile. Please try again.")

def search_profiles_page(collection, model):
    """Profile search interface"""
    st.header("🔍 Search Profiles")
    
    search_query = st.text_area(
        "Search Query",
        placeholder="Enter search terms (e.g., 'male patients with diabetes', 'people allergic to peanuts', 'users in their 30s')",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        num_results = st.number_input("Results", min_value=1, max_value=20, value=5)
    
    if st.button("🔍 Search Profiles", type="primary") and search_query:
        with st.spinner("Searching vector database..."):
            results = search_similar_profiles(search_query, collection, model, num_results)
            
            if results and results.get('documents'):
                st.success(f"Found {len(results['documents'][0])} similar profiles")
                
                # Display results
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    profile_data = json.loads(doc)
                    
                    with st.expander(f"👤 {metadata['name']} (Similarity: {(1-distance):.2%})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Email:** {metadata['email']}")
                            st.write(f"**Age:** {metadata['age']}")
                            st.write(f"**Gender:** {metadata['gender']}")
                            st.write(f"**Phone:** {metadata['phone']}")
                        
                        with col2:
                            st.write(f"**Address:** {metadata['address']}")
                            st.write(f"**Medical History:** {profile_data.get('medical_history', 'N/A')}")
                            st.write(f"**Allergies:** {profile_data.get('allergies', 'N/A')}")
            else:
                st.warning("No profiles found matching your search criteria.")

def analytics_page(collection):
    """Analytics and visualization page"""
    st.header("📊 Profile Analytics")
    
    # Get all profiles
    all_profiles = get_all_profiles(collection)
    
    if not all_profiles or not all_profiles.get('metadatas'):
        st.info("No profiles available for analytics. Please create some profiles first.")
        return
    
    # Create visualizations
    fig = create_profile_visualization(all_profiles)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional statistics
    st.subheader("📈 Detailed Statistics")
    
    metadata_list = all_profiles['metadatas']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Age statistics
        ages = [int(meta.get('age', 0)) for meta in metadata_list if meta.get('age', '').isdigit()]
        if ages:
            st.metric("Average Age", f"{np.mean(ages):.1f}")
            st.metric("Age Range", f"{min(ages)} - {max(ages)}")
    
    with col2:
        # Gender distribution
        genders = [meta.get('gender', 'Unknown') for meta in metadata_list]
        gender_counts = pd.Series(genders).value_counts()
        st.write("**Gender Distribution:**")
        for gender, count in gender_counts.items():
            st.write(f"{gender}: {count}")
    
    with col3:
        # Profile creation timeline
        created_dates = [meta.get('created_at', '') for meta in metadata_list if meta.get('created_at')]
        if created_dates:
            st.write(f"**Total Profiles:** {len(metadata_list)}")
            st.write(f"**Database Size:** {len(all_profiles.get('embeddings', []))} vectors")

def view_all_profiles_page(collection):
    """View all profiles page"""
    st.header("🗂️ All Profiles")
    
    all_profiles = get_all_profiles(collection)
    
    if not all_profiles or not all_profiles.get('metadatas'):
        st.info("No profiles found in the database.")
        return
    
    # Display profiles in a grid
    metadata_list = all_profiles['metadatas']
    document_list = all_profiles['documents']
    
    # Search/filter functionality
    search_term = st.text_input("🔍 Filter profiles", placeholder="Search by name, email, or any field...")
    
    filtered_indices = range(len(metadata_list))
    if search_term:
        filtered_indices = [
            i for i in range(len(metadata_list))
            if search_term.lower() in json.dumps(metadata_list[i]).lower() or
               search_term.lower() in document_list[i].lower()
        ]
    
    st.write(f"Showing {len(filtered_indices)} profiles")
    
    # Display profiles
    for i in filtered_indices:
        metadata = metadata_list[i]
        profile_data = json.loads(document_list[i])
        profile_id = all_profiles['ids'][i]
        
        with st.expander(f"👤 {metadata.get('name', 'Unknown')} ({metadata.get('email', 'No email')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**ID:** {profile_id}")
                st.write(f"**Age:** {metadata.get('age', 'N/A')}")
                st.write(f"**Gender:** {metadata.get('gender', 'N/A')}")
                st.write(f"**Phone:** {metadata.get('phone', 'N/A')}")
                st.write(f"**Address:** {metadata.get('address', 'N/A')}")
                st.write(f"**Medical History:** {profile_data.get('medical_history', 'N/A')}")
                st.write(f"**Allergies:** {profile_data.get('allergies', 'N/A')}")
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{profile_id}"):
                    if delete_profile(profile_id, collection):
                        st.success("Profile deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete profile.")

if __name__ == "__main__":
    main()