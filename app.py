import logging
import re
from flask import Flask, request, render_template, jsonify
import google.generativeai as genai

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

genai.configure(api_key="AIzaSyCiEzJVhfGwvjnlHxHG7BIPcxlhbFlLpgk")  
model = genai.GenerativeModel("gemini-pro")

# 🎯 运动计划页面
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    user_data = request.form

    prompt = "Generate a customized workout plan based on these inputs:\n"
    for key, value in user_data.items():
        prompt += f"{key}: {value}\n"

    try:
        response = model.generate_content(prompt)
        plan = response.text if response.text else "No response received."
    except Exception as e:
        plan = f"Error: {str(e)}"

    return render_template('result.html', plan=plan)


# 🤖 机器人客服页面
@app.route('/chatbox')
def chatbox():
    return render_template('chatbox.html')

@app.route('/query', methods=['POST'])
def query_gemini():
    user_question = request.form.get("question")
    logger.debug(f"Received question: {user_question}")
    
    if not user_question:
        return jsonify({"error": "Please provide a question"})

    try:
        prompt = f"""
        Please provide a detailed answer to the question "{user_question}", including:
        1. Action instructions and key points
        2. Related image descriptions and search keywords
        3. Notes and suggestions
        """

        response = model.generate_content(prompt)
        formatted_text = format_response(response.text)

        image_keywords = re.findall(r'\*\*Search Keywords: (.*?)\*\*', response.text)

        return jsonify({
            "text": formatted_text,
            "imageKeywords": image_keywords
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# 📌 格式化 AI 响应
def format_response(text):
    paragraphs = text.split("\n\n")
    formatted_sections = []

    for section in paragraphs:
        if section.startswith("# "):  # 处理标题
            section = f"<h2>{section.strip('# ')}</h2>"
        elif section.startswith("* "):  # 处理列表
            items = section.split("\n* ")
            formatted_items = ['<li>' + item.strip('* ') + '</li>' for item in items if item]
            section = '<ul>' + ''.join(formatted_items) + '</ul>'
        else:
            section = f"<p>{section}</p >"
        
        formatted_sections.append(section)

    return ''.join(formatted_sections)


if __name__ == '__main__':
    app.run(debug=True)

