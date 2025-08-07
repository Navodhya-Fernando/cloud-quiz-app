import streamlit as st
from pymongo import MongoClient
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Set page config
st.set_page_config(page_title="Cloud Quiz App", layout="centered")

st.markdown("""
    <style>
        .main-title {
            font-size: 3em;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 1.3em;
            color: #7f8c8d;
            text-align: center;
            margin-bottom: 40px;
        }
        .question-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .stButton>button {
            width: 100%;
            height: 3em;
            font-size: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<div class="main-title">☁️ Cloud Quiz App</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Test your knowledge on cloud computing topics!</div>', unsafe_allow_html=True)

# Topic selection
# Topic map: { Display Name : Collection Name }
TOPIC_MAP = {
    "App Deployment": "app_deployment",
    "Architecture": "architecture",
    "AWS Practical": "aws_practical",
    "Cloud Databases": "cloud_databases",
    "Cloud Security": "cloud_security",
    "Deployment Models": "deployment_models",
    "Fundamentals": "fundamentals",
    "Linux for Cloud": "linux_for_cloud"
    # Add more if needed
}

# Dropdown using display names
selected_display = st.selectbox("Select Topic", list(TOPIC_MAP.keys()))

# Internal value used for database querying
selected_topic = TOPIC_MAP[selected_display]

# Number of questions
num_questions = st.slider("Select Number of Questions", min_value=5, max_value=50, step=5, value=10)

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.score = 0

# Load questions
if st.button("Start Quiz"):
    st.session_state.questions = list(db[selected_topic].aggregate([{"$sample": {"size": num_questions}}]))
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.rerun()

# Display questions if loaded
if st.session_state.questions:
    if st.session_state.current_q < len(st.session_state.questions):
        question_data = st.session_state.questions[st.session_state.current_q]

        st.markdown(
            f"""<div style='color: #000000; background-color: #ffffff; 
                font-size: 16px; font-weight: bold; padding: 10px; 
                border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                Q{st.session_state.current_q + 1}: {question_data['question']}
            </div>""",
            unsafe_allow_html=True
        )
        options = question_data["options"]
        correct_answer = question_data["answer"]
        explanation = question_data.get("explanation", None)

        selected = st.radio("Choose your answer:", options, key=f"q_{st.session_state.current_q}")

        if st.button("Submit Answer"):
            if selected == correct_answer:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect! Correct answer: {correct_answer}")
            if explanation:
                st.info(f"📘 Explanation: {explanation}")

            st.session_state.current_q += 1
            st.rerun()

    else:
        st.balloons()
        st.markdown(f"## 🎉 Quiz Completed! Your Score: {st.session_state.score} / {len(st.session_state.questions)}")

        if st.button("Play Again"):
            st.session_state.questions = []
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()
