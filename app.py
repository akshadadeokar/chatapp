import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import openai
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Get OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# Database Configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Creates site.db in your project directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress warning

db = SQLAlchemy(app)

# --- Database Models ---
class CommunityMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"CommunityMessage('{self.message}', '{self.timestamp}')"

# --- Create Database Tables (Run once, e.g., in an interactive shell or a dedicated script) ---
# with app.app_context():
#     db.create_all()

# --- API Endpoints ---

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot queries."""
    data = request.json
    user_query = data.get("query")

    if not user_query:
        return jsonify({"reply": "Error: No query provided."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in RoboAnalyzer software and robotics."},
                {"role": "user", "content": user_query}
            ]
        )
        bot_reply = response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        app.logger.error(f"OpenAI API Error: {e}")
        bot_reply = "Error: Unable to get response from AI. Please try again later."
        return jsonify({"reply": bot_reply}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        bot_reply = "An unexpected error occurred."
        return jsonify({"reply": bot_reply}), 500

    return jsonify({"reply": bot_reply})

@app.route("/community/post", methods=["POST"])
def post_community_message():
    """Handles posting new community messages."""
    data = request.json
    message_content = data.get("message")

    if not message_content:
        return jsonify({"status": "error", "message": "No message content provided."}), 400

    try:
        new_message = CommunityMessage(message=message_content)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"status": "success", "message": "Message posted successfully!"}), 201
    except Exception as e:
        app.logger.error(f"Database error posting message: {e}")
        return jsonify({"status": "error", "message": "Failed to post message."}), 500

@app.route("/community/messages", methods=["GET"])
def get_community_messages():
    """Retrieves all community messages."""
    try:
        messages = CommunityMessage.query.order_by(CommunityMessage.timestamp.asc()).all()
        # Convert SQLAlchemy objects to a list of dictionaries for JSON serialization
        messages_list = [{"id": msg.id, "message": msg.message, "timestamp": msg.timestamp.isoformat()} for msg in messages]
        return jsonify(messages_list), 200
    except Exception as e:
        app.logger.error(f"Database error retrieving messages: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve messages."}), 500


if __name__ == "__main__":
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True) # debug=True will restart the server on code changes