import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_ai_client():
    """Initialize OpenAI client with API key from environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return None
    return OpenAI(api_key=api_key)

def get_ai_response(prompt, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": """You are an intake specialist focusing on name change processes.
                Provide personalized guidance and validation for name change information.
                Be empathetic and supportive while ensuring accuracy and completeness.
                Help users understand why each piece of information is important."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def validate_name(name, reason, client):
    prompt = f"""Validate this name change request:
    Current Name: {name}
    Reason: {reason}
    Consider:
    1. Common naming conventions
    2. Legal restrictions
    3. Special considerations for {reason}
    4. Potential issues to address
    Provide feedback in a supportive way."""
    return get_ai_response(prompt, client)

def get_next_steps(answers, client):
    prompt = f"""Based on these intake answers, suggest next steps:
    {answers}
    Include:
    1. Immediate actions needed
    2. Important considerations
    3. Potential challenges
    4. Helpful resources
    5. Timeline expectations"""
    return get_ai_response(prompt, client)

def get_personalized_guidance(question, previous_answers, client):
    prompt = f"""Provide personalized guidance for this intake question:
    Question: {question}
    Previous Answers: {previous_answers}
    Include:
    1. Why this information is important
    2. Things to consider
    3. Examples if helpful
    4. Common pitfalls to avoid"""
    return get_ai_response(prompt, client)

# Define questions to ask during intake
INTAKE_QUESTIONS = [
    {
        "id": "reason",
        "question": "Why are you changing your name?",
        "options": ["Divorce", "Marriage", "Gender Identity", "Personal Choice", "Other"],
        "type": "select",
        "help_text": "This helps us provide guidance specific to your situation."
    },
    {
        "id": "current_name",
        "question": "What is your current full name?",
        "type": "text",
        "help_text": "Enter your name exactly as it appears on legal documents."
    },
    {
        "id": "new_name",
        "question": "What name would you like to change to?",
        "type": "text",
        "help_text": "Consider how this name will appear on all your documents."
    },
    {
        "id": "state",
        "question": "What state do you reside in?",
        "type": "select",
        "options": ["California", "New York", "Texas", "Florida", "Other"],
        "help_text": "Name change requirements vary by state."
    },
    {
        "id": "voting_concerns",
        "question": "Do you have voting-related concerns?",
        "type": "radio",
        "options": ["Yes", "No"],
        "help_text": "We'll help ensure your voting rights are protected."
    },
    {
        "id": "voting_details",
        "question": "Please share any specific voting concerns you have:",
        "type": "text_area",
        "conditional": {"id": "voting_concerns", "value": "Yes"},
        "help_text": "This helps us provide targeted guidance for voting rights."
    }
]

def render_intake_form():
    st.header("Intake Form")
    st.write("Let's gather some information to help with your name change process.")

    # Initialize session state for answers if not exists
    if "intake_answers" not in st.session_state:
        st.session_state.intake_answers = {}

    # Questions
    questions = {
        "current_name": "What is your current legal name?",
        "new_name": "What name would you like to change to?",
        "reason": "What is your reason for changing your name?",
        "state": "Which state do you live in?",
        "voting_concern": "Are you concerned about your voting rights after the name change?"
    }

    # Display questions and collect answers
    for key, question in questions.items():
        if key == "reason":
            st.session_state.intake_answers[key] = st.selectbox(
                question,
                ["Marriage", "Divorce", "Gender Identity", "Personal Choice", "Other"]
            )
        elif key == "state":
            st.session_state.intake_answers[key] = st.selectbox(
                question,
                ["California", "New York", "Texas", "Florida", "Other"]
            )
        elif key == "voting_concern":
            st.session_state.intake_answers[key] = st.radio(
                question,
                ["Yes", "No"]
            )
        else:
            st.session_state.intake_answers[key] = st.text_input(question)

    # Get AI guidance based on answers
    if all(st.session_state.intake_answers.values()):
        client = get_ai_client()
        if client and st.button("Get Personalized Guidance"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing guidance for name changes."},
                        {"role": "user", "content": f"Based on these details:\n- Current name: {st.session_state.intake_answers['current_name']}\n- New name: {st.session_state.intake_answers['new_name']}\n- Reason: {st.session_state.intake_answers['reason']}\n- State: {st.session_state.intake_answers['state']}\nWhat should they know about the name change process?"}
                    ]
                )
                st.write("Guidance:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting guidance: {str(e)}")

    # Display summary
    if all(st.session_state.intake_answers.values()):
        st.subheader("Summary of Your Information")
        for key, value in st.session_state.intake_answers.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        st.success("✅ Intake form completed! You can now explore other sections for detailed guidance.")

    # Initialize OpenAI client only when needed
    client = None
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="👨‍⚖️"):
                st.write(message["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])
    
    # Current question handling
    current_index = st.session_state.current_question_index
    
    # Check if we've completed all questions
    if current_index >= len(INTAKE_QUESTIONS):
        st.success("✅ Information Collection Complete!")
        
        # Initialize OpenAI client only when generating summary
        if client is None:
            client = get_ai_client()
        
        # Get AI-generated summary and next steps
        summary = get_next_steps(st.session_state.intake_answers, client)
        if summary:
            st.markdown("""
            <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h4>Your Personalized Summary & Next Steps</h4>
                {summary}
            </div>
            """.format(summary=summary), unsafe_allow_html=True)
        
        # Display information summary
        st.subheader("Your Information Summary")
        summary_cols = st.columns(2)
        
        with summary_cols[0]:
            st.markdown("#### Personal Details")
            st.write(f"**Current Name:** {st.session_state.intake_answers.get('current_name', 'N/A')}")
            st.write(f"**New Name:** {st.session_state.intake_answers.get('new_name', 'N/A')}")
            st.write(f"**State:** {st.session_state.intake_answers.get('state', 'N/A')}")
            
        with summary_cols[1]:
            st.markdown("#### Change Information")
            st.write(f"**Reason for Change:** {st.session_state.intake_answers.get('reason', 'N/A')}")
            st.write(f"**Voting Concerns:** {st.session_state.intake_answers.get('voting_concerns', 'N/A')}")
            if st.session_state.intake_answers.get('voting_concerns') == "Yes":
                st.write(f"**Voting Details:** {st.session_state.intake_answers.get('voting_details', 'N/A')}")
        
        # Validation of name change
        if 'new_name' in st.session_state.intake_answers and 'reason' in st.session_state.intake_answers:
            if client is None:
                client = get_ai_client()
            validation = validate_name(
                st.session_state.intake_answers['new_name'],
                st.session_state.intake_answers['reason'],
                client
            )
            if validation:
                st.markdown("""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h4>Name Change Validation</h4>
                    {validation}
                </div>
                """.format(validation=validation), unsafe_allow_html=True)
        
        # Reset button
        if st.button("Start Over", key="start_over_btn"):
            st.session_state.current_question_index = 0
            st.session_state.intake_answers = {}
            st.session_state.chat_history = []
            st.rerun()
            
        return
    
    # Get current question
    current_q = INTAKE_QUESTIONS[current_index]
    
    # Check if this question should be skipped based on conditional logic
    if "conditional" in current_q:
        condition = current_q["conditional"]
        if st.session_state.intake_answers.get(condition["id"]) != condition["value"]:
            st.session_state.current_question_index += 1
            st.rerun()
    
    # Display current question without AI guidance initially
    with st.chat_message("assistant", avatar="👨‍⚖️"):
        st.write(current_q["question"])
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px; font-size: 0.9em;">
            {current_q.get('help_text', '')}
        </div>
        """, unsafe_allow_html=True)
    
    # Handle user input based on question type
    user_input = None
    
    if current_q["type"] == "text":
        user_input = st.chat_input(
            current_q.get("help_text", "Type your answer here..."),
            key=f"chat_input_{current_q['id']}"
        )
    elif current_q["type"] == "text_area":
        user_input = st.chat_input(
            current_q.get("help_text", "Type your details here..."),
            key=f"chat_textarea_{current_q['id']}"
        )
    elif current_q["type"] == "select":
        temp_input = st.selectbox(
            current_q.get("help_text", "Select an option:"),
            current_q["options"],
            key=f"temp_{current_q['id']}"
        )
        if st.button("Submit", key=f"submit_{current_q['id']}"):
            user_input = temp_input
    elif current_q["type"] == "radio":
        temp_input = st.radio(
            current_q.get("help_text", "Select an option:"),
            current_q["options"],
            key=f"temp_{current_q['id']}"
        )
        if st.button("Submit", key=f"submit_{current_q['id']}"):
            user_input = temp_input
    
    # Process user input
    if user_input:
        # Add user response to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Store answer in session state
        st.session_state.intake_answers[current_q["id"]] = user_input
        
        # Initialize OpenAI client only after user input
        if client is None:
            client = get_ai_client()
        
        # Get AI guidance for next question
        next_index = current_index + 1
        if next_index < len(INTAKE_QUESTIONS):
            next_q = INTAKE_QUESTIONS[next_index]
            guidance = get_personalized_guidance(
                next_q["question"],
                st.session_state.intake_answers,
                client
            )
            if guidance:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": guidance
                })
        
        # Move to next question
        st.session_state.current_question_index += 1
        
        # Rerun to update UI
        st.rerun() 