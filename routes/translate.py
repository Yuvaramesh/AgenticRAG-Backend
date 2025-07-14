from flask import Blueprint, request, jsonify
from deep_translator import GoogleTranslator

translate_bp = Blueprint("translate", __name__)

@translate_bp.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get("text", "")
    target_lang = data.get("target_lang", "ta")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
