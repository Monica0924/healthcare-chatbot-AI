/**
 * RAG Chatbot Vector Database Client
 * Connects to Python Flask backend for vector operations
 */

class RAGVectorClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.isConnected = false;
        this.knowledgeBase = [];
    }

    /**
     * Test connection to vector database
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`);
            const data = await response.json();
            this.isConnected = data.vector_db_connected;
            return data;
        } catch (error) {
            console.error('Vector DB connection failed:', error);
            this.isConnected = false;
            throw error;
        }
    }

    /**
     * Add knowledge to vector database
     */
    async addKnowledge(text, metadata = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/api/add-knowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    metadata: metadata
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to add knowledge:', error);
            throw error;
        }
    }

    /**
     * Search for relevant knowledge
     */
    async searchKnowledge(query, k = 3) {
        try {
            const response = await fetch(`${this.baseUrl}/api/search-knowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    k: k
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.results;
        } catch (error) {
            console.error('Failed to search knowledge:', error);
            throw error;
        }
    }

    /**
     * Get all knowledge vectors
     */
    async getAllKnowledge() {
        try {
            const response = await fetch(`${this.baseUrl}/api/get-all-knowledge`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.vectors;
        } catch (error) {
            console.error('Failed to get all knowledge:', error);
            throw error;
        }
    }

    /**
     * Update knowledge vector
     */
    async updateKnowledge(vectorId, text, metadata = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/api/update-knowledge/${vectorId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    metadata: metadata
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to update knowledge:', error);
            throw error;
        }
    }

    /**
     * Delete knowledge vector
     */
    async deleteKnowledge(vectorId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/delete-knowledge/${vectorId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to delete knowledge:', error);
            throw error;
        }
    }

    /**
     * Save conversation to vector database
     */
    async saveConversation(conversationId, messages) {
        try {
            const response = await fetch(`${this.baseUrl}/api/save-conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    messages: messages
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to save conversation:', error);
            throw error;
        }
    }

    /**
     * Search for similar conversations
     */
    async searchConversations(query, k = 2) {
        try {
            const response = await fetch(`${this.baseUrl}/api/search-conversations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    k: k
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.results;
        } catch (error) {
            console.error('Failed to search conversations:', error);
            throw error;
        }
    }

    /**
     * Generate RAG response
     */
    async generateRAGResponse(query, conversationHistory = []) {
        try {
            const response = await fetch(`${this.baseUrl}/api/generate-rag-response`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    conversation_history: conversationHistory
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to generate RAG response:', error);
            throw error;
        }
    }

    /**
     * Batch add multiple knowledge items
     */
    async batchAddKnowledge(items) {
        try {
            const response = await fetch(`${this.baseUrl}/api/batch-add-knowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    items: items
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to batch add knowledge:', error);
            throw error;
        }
    }
}

/**
 * Enhanced RAG Chatbot Manager
 * Integrates vector database with chatbot interface
 */
class RAGChatbotManager {
    constructor(vectorClient) {
        this.vectorClient = vectorClient;
        this.conversations = [];
        this.currentConversation = null;
        this.ragMode = true;
        this.autoSave = true;
    }

    /**
     * Initialize the chatbot manager
     */
    async initialize() {
        try {
            // Test vector database connection
            await this.vectorClient.testConnection();
            console.log('✅ Vector database connected successfully');
            
            // Load existing knowledge base
            await this.loadKnowledgeBase();
            
            // Start new conversation
            this.startNewConversation();
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize chatbot manager:', error);
            return false;
        }
    }

    /**
     * Load knowledge base from vector database
     */
    async loadKnowledgeBase() {
        try {
            const vectors = await this.vectorClient.getAllKnowledge();
            this.knowledgeBase = vectors;
            console.log(`📚 Loaded ${vectors.length} knowledge vectors`);
        } catch (error) {
            console.warn('⚠️ Failed to load knowledge base:', error);
            this.knowledgeBase = [];
        }
    }

    /**
     * Start a new conversation
     */
    startNewConversation() {
        const conversation = {
            id: Date.now().toString(),
            title: `Conversation ${this.conversations.length + 1}`,
            messages: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        
        this.conversations.push(conversation);
        this.currentConversation = conversation;
        
        return conversation;
    }

    /**
     * Send message and get RAG-powered response
     */
    async sendMessage(message) {
        if (!this.currentConversation) {
            this.startNewConversation();
        }

        // Add user message
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        };

        this.currentConversation.messages.push(userMessage);

        try {
            let response;
            let contexts = [];

            if (this.ragMode) {
                // Generate RAG response
                const ragResult = await this.vectorClient.generateRAGResponse(
                    message, 
                    this.currentConversation.messages
                );
                
                response = ragResult.response;
                contexts = ragResult.contexts || [];
            } else {
                // Simple response without RAG
                response = "I'm in simple mode. Here's my response: " + message;
            }

            // Add bot message
            const botMessage = {
                role: 'bot',
                content: response,
                timestamp: new Date().toISOString(),
                contexts: contexts
            };

            this.currentConversation.messages.push(botMessage);
            this.currentConversation.updated_at = new Date().toISOString();

            // Auto-save conversation if enabled
            if (this.autoSave) {
                await this.saveCurrentConversation();
            }

            return {
                userMessage,
                botMessage
            };

        } catch (error) {
            console.error('Error sending message:', error);
            
            // Add error message
            const errorMessage = {
                role: 'bot',
                content: 'Sorry, I encountered an error while processing your message. Please try again.',
                timestamp: new Date().toISOString(),
                error: true
            };

            this.currentConversation.messages.push(errorMessage);
            
            return {
                userMessage,
                botMessage: errorMessage
            };
        }
    }

    /**
     * Save current conversation to vector database
     */
    async saveCurrentConversation() {
        if (!this.currentConversation || this.currentConversation.messages.length === 0) {
            return;
        }

        try {
            await this.vectorClient.saveConversation(
                this.currentConversation.id,
                this.currentConversation.messages
            );
            console.log('💾 Conversation saved to vector database');
        } catch (error) {
            console.warn('⚠️ Failed to save conversation:', error);
        }
    }

    /**
     * Search for similar conversations
     */
    async searchSimilarConversations(query) {
        try {
            return await this.vectorClient.searchConversations(query);
        } catch (error) {
            console.error('Failed to search conversations:', error);
            return [];
        }
    }

    /**
     * Add knowledge to the database
     */
    async addKnowledge(text, metadata = {}) {
        try {
            const result = await this.vectorClient.addKnowledge(text, metadata);
            await this.loadKnowledgeBase(); // Refresh knowledge base
            return result;
        } catch (error) {
            console.error('Failed to add knowledge:', error);
            throw error;
        }
    }

    /**
     * Toggle RAG mode
     */
    toggleRAGMode() {
        this.ragMode = !this.ragMode;
        console.log(`🧠 RAG mode: ${this.ragMode ? 'ON' : 'OFF'}`);
        return this.ragMode;
    }

    /**
     * Get conversation history
     */
    getConversationHistory() {
        return this.conversations;
    }

    /**
     * Switch to different conversation
     */
    switchConversation(conversationId) {
        const conversation = this.conversations.find(c => c.id === conversationId);
        if (conversation) {
            this.currentConversation = conversation;
            return conversation;
        }
        return null;
    }

    /**
     * Clear current conversation
     */
    clearCurrentConversation() {
        if (this.currentConversation) {
            this.currentConversation.messages = [];
            this.currentConversation.updated_at = new Date().toISOString();
        }
    }
}

/**
 * Enhanced RAG Chatbot Interface
 * Integrates with the HTML interface
 */
class EnhancedRAGChatbot {
    constructor() {
        this.vectorClient = new RAGVectorClient();
        this.chatbotManager = new RAGChatbotManager(this.vectorClient);
        this.isInitialized = false;
    }

    /**
     * Initialize the chatbot
     */
    async initialize() {
        try {
            console.log('🚀 Initializing Enhanced RAG Chatbot...');
            
            // Initialize chatbot manager
            const success = await this.chatbotManager.initialize();
            
            if (success) {
                this.isInitialized = true;
                console.log('✅ Enhanced RAG Chatbot initialized successfully');
                
                // Update UI
                this.updateVectorStatus(true);
                
                // Load sample knowledge if database is empty
                await this.loadSampleKnowledge();
                
                return true;
            } else {
                console.warn('⚠️ Chatbot initialization failed, falling back to simple mode');
                this.updateVectorStatus(false);
                return false;
            }
            
        } catch (error) {
            console.error('❌ Enhanced RAG Chatbot initialization failed:', error);
            this.updateVectorStatus(false);
            return false;
        }
    }

    /**
     * Load sample knowledge for demonstration
     */
    async loadSampleKnowledge() {
        try {
            const sampleKnowledge = [
                {
                    text: "RAG (Retrieval-Augmented Generation) combines information retrieval with text generation to produce more accurate and contextually relevant responses.",
                    metadata: { 
                        topic: "AI", 
                        category: "definition", 
                        confidence: 0.95,
                        source: "documentation"
                    }
                },
                {
                    text: "Vector databases like ChromaDB store high-dimensional vectors (embeddings) that represent semantic meaning of text, enabling efficient similarity search.",
                    metadata: { 
                        topic: "Databases", 
                        category: "definition", 
                        confidence: 0.92,
                        source: "technical_docs"
                    }
                },
                {
                    text: "Machine learning embeddings convert text into numerical representations that capture semantic relationships, allowing computers to understand meaning and context.",
                    metadata: { 
                        topic: "AI", 
                        category: "definition", 
                        confidence: 0.88,
                        source: "research_paper"
                    }
                },
                {
                    text: "Conversational AI systems can benefit from vector databases by storing and retrieving relevant conversation history and knowledge to provide more contextual responses.",
                    metadata: { 
                        topic: "AI", 
                        category: "application", 
                        confidence: 0.85,
                        source: "case_study"
                    }
                }
            ];

            // Check if knowledge base is empty
            const existingKnowledge = await this.vectorClient.getAllKnowledge();
            
            if (existingKnowledge.length === 0) {
                console.log('📚 Loading sample knowledge...');
                await this.vectorClient.batchAddKnowledge(sampleKnowledge);
                console.log('✅ Sample knowledge loaded successfully');
            }
            
        } catch (error) {
            console.warn('⚠️ Failed to load sample knowledge:', error);
        }
    }

    /**
     * Update vector status indicator
     */
    updateVectorStatus(connected) {
        const statusIndicator = document.getElementById('vectorStatus');
        const statusText = document.getElementById('vectorStatusText');
        
        if (connected) {
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = 'Vector DB Connected';
        } else {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Vector DB Disconnected';
        }
    }

    /**
     * Send message through chatbot
     */
    async sendMessage(message) {
        if (!this.isInitialized) {
            // Fallback to simple response
            return {
                userMessage: { role: 'user', content: message },
                botMessage: { 
                    role: 'bot', 
                    content: 'I\'m currently offline. Please check the vector database connection.',
                    error: true
                }
            };
        }

        return await this.chatbotManager.sendMessage(message);
    }

    /**
     * Toggle RAG mode
     */
    toggleRAGMode() {
        const newMode = this.chatbotManager.toggleRAGMode();
        return newMode;
    }

    /**
     * Get current conversation
     */
    getCurrentConversation() {
        return this.chatbotManager.currentConversation;
    }

    /**
     * Start new conversation
     */
    startNewConversation() {
        return this.chatbotManager.startNewConversation();
    }

    /**
     * Clear current conversation
     */
    clearCurrentConversation() {
        this.chatbotManager.clearCurrentConversation();
    }

    /**
     * Get conversation history
     */
    getConversationHistory() {
        return this.chatbotManager.getConversationHistory();
    }

    /**
     * Switch conversation
     */
    switchConversation(conversationId) {
        return this.chatbotManager.switchConversation(conversationId);
    }

    /**
     * Add knowledge to database
     */
    async addKnowledge(text, metadata = {}) {
        return await this.chatbotManager.addKnowledge(text, metadata);
    }

    /**
     * Get all knowledge from database
     */
    async getAllKnowledge() {
        try {
            return await this.vectorClient.getAllKnowledge();
        } catch (error) {
            console.error('Failed to get knowledge:', error);
            return [];
        }
    }

    /**
     * Update knowledge
     */
    async updateKnowledge(vectorId, text, metadata = {}) {
        return await this.vectorClient.updateKnowledge(vectorId, text, metadata);
    }

    /**
     * Delete knowledge
     */
    async deleteKnowledge(vectorId) {
        return await this.vectorClient.deleteKnowledge(vectorId);
    }
}

// Global chatbot instance
window.ragChatbot = new EnhancedRAGChatbot();