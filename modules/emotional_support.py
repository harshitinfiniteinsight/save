import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

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
                {"role": "system", "content": """You are an empathetic and supportive counselor specializing in helping people through name changes.
                Your responses should be warm, understanding, and validating while providing practical emotional support.
                Focus on the emotional and psychological aspects of name changes, identity, and self-determination."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def get_personalized_quote(reason, client):
    prompt = f"Generate an inspiring and empathetic quote about identity and self-determination, specifically tailored for someone changing their name due to {reason}. The quote should be concise (max 2 sentences) and uplifting."
    return get_ai_response(prompt, client)

def get_personalized_story(reason, client):
    prompt = f"Share a brief, realistic story about someone who changed their name due to {reason}. Include their emotional journey, challenges they faced, and how they overcame them. Keep it under 200 words and make it relatable and encouraging."
    return get_ai_response(prompt, client)

def get_personalized_advice(reason, feeling, client):
    prompt = f"Provide empathetic and practical advice for someone who is changing their name due to {reason} and is feeling {feeling}. Address their emotional needs while offering concrete coping strategies."
    return get_ai_response(prompt, client)

def render_emotional_support():
    st.header("Emotional Support")
    st.write("Find support and encouragement during your name change journey.")
    
    # Emotional check-in
    st.subheader("How are you feeling today?")
    feeling = st.selectbox(
        "Select your current emotional state:",
        ["Excited", "Nervous", "Overwhelmed", "Confident", "Uncertain", "Other"]
    )

    if feeling:
        client = get_ai_client()
        if client and st.button("Get Personalized Support"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an empathetic assistant providing emotional support for people going through name changes."},
                        {"role": "user", "content": f"I'm feeling {feeling} about my name change process. Can you provide some encouragement and support?"}
                    ]
                )
                st.write("Support Message:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

    # Resources section
    st.subheader("Support Resources")
    st.markdown("""
    - Join our community forum
    - Connect with others who have changed their names
    - Access mental health resources
    - Read success stories
    """)

    # Affirmations
    st.subheader("Daily Affirmations")
    if st.button("Get Today's Affirmation"):
        client = get_ai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an empathetic assistant providing positive affirmations for people changing their names."},
                        {"role": "user", "content": "Generate a positive affirmation for someone changing their name."}
                    ]
                )
                st.write("Your Affirmation:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting affirmation: {str(e)}")

    # Get user context from intake form
    user_reason = st.session_state.intake_answers.get("reason", "Personal Choice")
    
    # Display initial supportive message
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f7ff; text-align: center; margin-bottom: 25px;">
        <h3>Your Journey Matters</h3>
        <p>Changing your name is a significant step that can bring up many emotions. We're here to support you through this process.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Share others' experiences
    st.subheader("Stories from Others Who've Changed Their Names")
    if st.button("Read a Story"):
        story = get_personalized_story(user_reason, client)
        if story:
            with st.expander("A Story That Might Resonate With You", expanded=True):
                st.write(story)
    
    # Interactive support features
    st.subheader("Support Resources")
    
    # Coping strategies
    if st.button("Get Coping Strategies"):
        with st.expander("Coping Strategies for Your Journey", expanded=True):
            strategy_prompt = f"Provide 3-4 specific coping strategies for managing emotions during a name change process, particularly for someone changing their name due to {user_reason}."
            strategies = get_ai_response(strategy_prompt, client)
            if strategies:
                st.write(strategies)
    
    # Celebration section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 15px; margin-top: 20px;">
        <h3>Your Journey Matters</h3>
        <p>Every step forward is a step toward authenticity.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Celebrate Your Progress 🎉"):
        celebration_prompt = f"Generate a short, personalized celebration message for someone who is making progress in their name change journey due to {user_reason}."
        celebration_message = get_ai_response(celebration_prompt, client)
        if celebration_message:
            st.success(celebration_message)
            st.balloons() 