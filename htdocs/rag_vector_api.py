from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)
CORS(app)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create or get collections
knowledge_collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
conversations_collection = chroma_client.get_or_create_collection(
    name="conversations",
    metadata={"hnsw:space": "cosine"}
)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the vector database is accessible"""
    try:
        # Test collection access
        knowledge_collection.count()
        return jsonify({
            "status": "healthy",
            "vector_db_connected": True,
            "model_loaded": True
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "vector_db_connected": False
        }), 500

@app.route('/api/add-knowledge', methods=['POST'])
def add_knowledge():
    """Add knowledge to the vector database"""
    try:
        data = request.json
        text = data.get('text')
        metadata = data.get('metadata', {})
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate embedding
        embedding = model.encode([text])[0].tolist()
        
        # Generate unique ID
        vector_id = str(uuid.uuid4())
        
        # Add to collection
        knowledge_collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                **metadata,
                "timestamp": datetime.now().isoformat(),
                "id": vector_id
            }],
            ids=[vector_id]
        )
        
        return jsonify({
            "success": True,
            "id": vector_id,
            "message": "Knowledge added successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-knowledge', methods=['POST'])
def search_knowledge():
    """Search for relevant knowledge using vector similarity"""
    try:
        data = request.json
        query = data.get('query')
        k = data.get('k', 3)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Generate query embedding
        query_embedding = model.encode([query])[0].tolist()
        
        # Search for similar vectors
        results = knowledge_collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        formatted_results = []
        if results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": float(results['distances'][0][i]) if results['distances'][0] else 0.0
                })
        
        return jsonify({
            "results": formatted_results,
            "count": len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-all-knowledge', methods=['GET'])
def get_all_knowledge():
    """Get all knowledge vectors from the database"""
    try:
        # Get all vectors from collection
        results = knowledge_collection.get()
        
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'])):
                formatted_results.append({
                    "id": results['ids'][i],
                    "text": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
        
        return jsonify({
            "vectors": formatted_results,
            "count": len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-knowledge/<vector_id>', methods=['PUT'])
def update_knowledge(vector_id):
    """Update a knowledge vector"""
    try:
        data = request.json
        text = data.get('text')
        metadata = data.get('metadata', {})
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate new embedding
        embedding = model.encode([text])[0].tolist()
        
        # Update in collection
        knowledge_collection.update(
            ids=[vector_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                **metadata,
                "updated_at": datetime.now().isoformat(),
                "id": vector_id
            }]
        )
        
        return jsonify({
            "success": True,
            "message": "Knowledge updated successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-knowledge/<vector_id>', methods=['DELETE'])
def delete_knowledge(vector_id):
    """Delete a knowledge vector"""
    try:
        knowledge_collection.delete(ids=[vector_id])
        
        return jsonify({
            "success": True,
            "message": "Knowledge deleted successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-conversation', methods=['POST'])
def save_conversation():
    """Save a conversation to the vector database"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        messages = data.get('messages', [])
        
        if not conversation_id:
            return jsonify({"error": "Conversation ID is required"}), 400
        
        # Convert conversation to text for embedding
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        
        # Generate embedding
        embedding = model.encode([conversation_text])[0].tolist()
        
        # Add to conversations collection
        conversations_collection.add(
            embeddings=[embedding],
            documents=[conversation_text],
            metadatas=[{
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "timestamp": datetime.now().isoformat(),
                "type": "conversation"
            }],
            ids=[conversation_id]
        )
        
        return jsonify({
            "success": True,
            "message": "Conversation saved successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-conversations', methods=['POST'])
def search_conversations():
    """Search for similar conversations"""
    try:
        data = request.json
        query = data.get('query')
        k = data.get('k', 3)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Generate query embedding
        query_embedding = model.encode([query])[0].tolist()
        
        # Search for similar conversations
        results = conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        formatted_results = []
        if results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "conversation_id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": float(results['distances'][0][i]) if results['distances'][0] else 0.0
                })
        
        return jsonify({
            "results": formatted_results,
            "count": len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-rag-response', methods=['POST'])
def generate_rag_response():
    """Generate a RAG (Retrieval-Augmented Generation) response"""
    try:
        data = request.json
        query = data.get('query')
        conversation_history = data.get('conversation_history', [])
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Search for relevant knowledge
        query_embedding = model.encode([query])[0].tolist()
        knowledge_results = knowledge_collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        # Search for relevant conversations
        conversation_results = conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=2
        )
        
        # Combine contexts
        contexts = []
        
        if knowledge_results['ids'][0]:
            for i in range(len(knowledge_results['ids'][0])):
                contexts.append({
                    "type": "knowledge",
                    "content": knowledge_results['documents'][0][i],
                    "metadata": knowledge_results['metadatas'][0][i],
                    "similarity": float(knowledge_results['distances'][0][i]) if knowledge_results['distances'][0] else 0.0
                })
        
        if conversation_results['ids'][0]:
            for i in range(len(conversation_results['ids'][0])):
                contexts.append({
                    "type": "conversation",
                    "content": conversation_results['documents'][0][i],
                    "metadata": conversation_results['metadatas'][0][i],
                    "similarity": float(conversation_results['distances'][0][i]) if conversation_results['distances'][0] else 0.0
                })
        
        # Sort by similarity and take top results
        contexts.sort(key=lambda x: x['similarity'])
        relevant_contexts = [ctx for ctx in contexts if ctx['similarity'] > 0.7][:3]
        
        # Generate response (simplified - in real implementation, use LLM)
        if relevant_contexts:
            context_text = "\n---\n".join([ctx['content'] for ctx in relevant_contexts])
            response = f"Based on the relevant information I found:\n\n{context_text}\n\nIn response to your question: {query}"
        else:
            response = f"I don't have specific information about that in my knowledge base. Regarding your question: {query}"
        
        return jsonify({
            "response": response,
            "contexts": relevant_contexts,
            "context_count": len(relevant_contexts)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch-add-knowledge', methods=['POST'])
def batch_add_knowledge():
    """Add multiple knowledge items at once"""
    try:
        data = request.json
        items = data.get('items', [])
        
        if not items:
            return jsonify({"error": "Items are required"}), 400
        
        ids = []
        texts = []
        embeddings = []
        metadatas = []
        
        for item in items:
            text = item.get('text')
            metadata = item.get('metadata', {})
            
            if text:
                vector_id = str(uuid.uuid4())
                embedding = model.encode([text])[0].tolist()
                
                ids.append(vector_id)
                texts.append(text)
                embeddings.append(embedding)
                metadatas.append({
                    **metadata,
                    "timestamp": datetime.now().isoformat(),
                    "id": vector_id
                })
        
        if ids:
            knowledge_collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        
        return jsonify({
            "success": True,
            "added_count": len(ids),
            "message": "Batch knowledge added successfully"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create vector_db directory if it doesn't exist
    os.makedirs('./vector_db', exist_ok=True)
    
    print("🚀 Starting RAG Chatbot Vector Database API...")
    print("📡 API Endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/add-knowledge")
    print("  - POST /api/search-knowledge")
    print("  - GET  /api/get-all-knowledge")
    print("  - PUT  /api/update-knowledge/<id>")
    print("  - DELETE /api/delete-knowledge/<id>")
    print("  - POST /api/save-conversation")
    print("  - POST /api/search-conversations")
    print("  - POST /api/generate-rag-response")
    print("  - POST /api/batch-add-knowledge")
    print("\n🔧 Starting Flask server on port 5000...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)