from flask import Flask, jsonify
from flask_cors import CORS
from routes.upload import upload_bp
from routes.query import query_bp
from routes.documents import documents_bp
from routes.user_routes import user_bp
from routes.section_routes import section_bp
from routes.quiz_routes import quiz_bp
from routes.activity_routes import activity_bp
from routes.student_stats_routes import student_stats_bp
from routes.translate import translate_bp
from routes.suggest import suggest_bp   
from routes.tts import tts_bp
from routes.quiz_attempt_routes import quiz_attempt_bp
from routes.auth_routes import auth_bp # Ensure this import is present

app = Flask(__name__)

# Configure CORS properly
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Register all blueprints with /api prefix
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(query_bp, url_prefix='/api')
app.register_blueprint(documents_bp, url_prefix='/api')
app.register_blueprint(translate_bp, url_prefix='/api')
app.register_blueprint(tts_bp, url_prefix='/api')
app.register_blueprint(suggest_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(section_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')
app.register_blueprint(activity_bp, url_prefix='/api')
app.register_blueprint(student_stats_bp, url_prefix='/api')
app.register_blueprint(quiz_attempt_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api') # Ensure this registration is present

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Agentic RAG API is running. Use /api endpoints."})

@app.route("/api", methods=["GET"])
def api_home():
    return jsonify({"message": "API endpoints available"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
