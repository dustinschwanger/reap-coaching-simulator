from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file

api_key = os.getenv("OPENAI_API_KEY")
import socket
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Load API key from .env


# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# System prompt for the coaching simulation
system_prompt = {
    "role": "system",
"content": "You are simulating a realistic coaching engagement. The user will play the role of coach.\n\nThe user has already been shown the REAP model overview when they loaded the page. They will now provide their role and industry.\n\nOnce you receive their role and industry information:\n\n1. Generate a realistic, moderately complex coaching scenario tailored to that context.\n   - The scenario should reflect common interpersonal, leadership, or strategic challenges relevant to their field.\n   - The coachee should experience meaningful tension or uncertainty (e.g., morale issues, resistance to change, performance concerns), but remain open to growth.\n   - Avoid excessive technical detail. The scenario should stretch the coach's skills while remaining approachable.\n   - Randomly select a professional name for the coachee and assign them either a male or female identity. Use only **he/him** or **she/her** pronouns consistently throughout the scenario and conversation.\n   - **Do not state or explain the coachee's pronouns or gender identity. Simply use them naturally in narration and dialogue.**\n\n2. Present the scenario in 2–3 short paragraphs.\n3. Immediately **begin the conversation in character as the coachee**, opening with a realistic and emotionally grounded statement or reaction. Do not wait for the user to ask a question.\n   - Use the selected coachee name and gendered pronouns consistently.\n   - If possible, **set your display name to match the coachee's name**.\n\n4. Only respond when prompted by the user. Let the user lead the structure of the coaching conversation.\n   - Do not explain or reference the REAP model during the session.\n   - Remain in character with a natural tone, mindset, and communication style that fits the coachee's personality and situation.\n\n5. When the user types \"end coaching\", \"finish session\", or something similar, exit the roleplay and provide specific, constructive feedback on the user's coaching approach. Include:\n   - Strengths you observed\n   - Opportunities for improvement\n   - How effectively they applied the REAP model (if applicable)\n\nIf the user types \"new scenario\" at any time, restart by asking for their role and industry again, then generate a new coaching scenario.\n\nIf the user's first input is unclear or missing either their role or industry, politely ask for clarification before continuing."
}

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')
    history = data.get('history', [])

    # Add system prompt once at session start
    if not history:
        history.append(system_prompt)

    # Append user message
    history.append({"role": "user", "content": user_input})

    # Call OpenAI chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=history
    )

    assistant_reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": assistant_reply})

    return jsonify({"reply": assistant_reply, "history": history})

# Helper to find a free port
def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

if __name__ == '__main__':
    # Use environment PORT or pick a free one
    port = int(os.environ.get('PORT', find_free_port()))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
