import asyncio
import logging
from flask import Flask, request, jsonify
from config import setup_logging
from orchestrator import orchestrator

# Initialize centralized logging configuration
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Main HTTP endpoint for the chat interface.
    
    Expected JSON Payload:
    {
        "message": "What is the width of 6205?",
        "session_id": "user-session-123"
    }
    """
    try:
        data = request.json
        
        # Input Validation
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
            
        user_message = data.get('message')
        session_id = data.get('session_id', 'default_user')

        if not user_message:
            logger.warning("API: Received request with missing message.")
            return jsonify({"error": "Message is required"}), 400

        logger.info(f"API: Received request from session '{session_id}'")

        # Delegate to Orchestrator
        # The orchestrator handles intent routing, plugin execution, and state management.
        response = asyncio.run(orchestrator.process_chat(user_message, session_id))
        
        # Return Response
        return jsonify({
            "session_id": session_id,
            "response": response
        })

    except Exception as e:
        logger.error(f"API: Critical error in chat endpoint: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint for monitoring uptime.
    """
    return jsonify({"status": "healthy", "service": "Product Attribute Agent"}), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)