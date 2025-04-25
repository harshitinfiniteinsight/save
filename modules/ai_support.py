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

def render_ai_support():
    st.header("AI Support")
    st.write("Get instant answers to your questions about the name change process.")

    # Example questions to help users get started
    st.markdown("""
    ### Example Questions:
    - What documents do I need for a name change in my state?
    - How long does the name change process typically take?
    - What are the common challenges in the name change process?
    - How much does a legal name change cost?
    """)

    # User input
    user_question = st.text_input("Type your question here:")
    
    if user_question:
        client = get_ai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specializing in name change processes."},
                        {"role": "user", "content": user_question}
                    ]
                )
                st.write("Answer:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

# Main entry point
if __name__ == "__main__":
    # Initialize session state for intake answers if it doesn't exist
    if "intake_answers" not in st.session_state:
        st.session_state.intake_answers = {}
    
    # Run the main application
    render_ai_support() 