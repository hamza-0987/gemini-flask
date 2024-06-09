from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

my_api_key_gemini = os.getenv('MY_API_KEY_GEMINI')

if not my_api_key_gemini:
    raise ValueError("No API key found. Set the MY_API_KEY_GEMINI environment variable.")

genai.configure(api_key=my_api_key_gemini)

model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# Define your 404 error handler to redirect to the index page
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            prompt = request.form['prompt']
            question = prompt

            response = model.generate_content(question)
            # Debug: print the full response to check its structure
            print(f"Full API response: {response}")

            # Extract the text from the response
            if response and response.candidates:
                for candidate in response.candidates:
                    # Check for safety ratings and blockages
                    if candidate.safety_ratings and any(rating.blocked for rating in candidate.safety_ratings):
                        return jsonify({"text": "Sorry, but Gemini didn't want to answer that due to safety concerns!"})
                    elif candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                return jsonify({"text": part.text})
            
            return jsonify({"text": "Sorry, but Gemini didn't want to answer that!"})
        except Exception as e:
            return jsonify({"text": f"Sorry, but Gemini didn't want to answer that! Error: {str(e)}"})

    return render_template('index.html', **locals())

if __name__ == '__main__':
    app.run(debug=True)
