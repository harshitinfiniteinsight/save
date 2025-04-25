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
                {"role": "system", "content": """You are a legal information assistant specializing in name change processes.
                Provide accurate, up-to-date information about legal name change procedures.
                Always include appropriate disclaimers about not being legal advice.
                Focus on general procedures and requirements while encouraging users to verify with local courts."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def get_state_requirements(state, reason, client):
    prompt = f"""Provide detailed information about name change requirements in {state}, specifically for someone changing their name due to {reason}.
    Include:
    1. Required court filings
    2. Typical fees
    3. Required documentation
    4. Estimated timeframe
    5. Special considerations for {reason}
    Remember to note this is general information and may vary by county."""
    return get_ai_response(prompt, client)

def get_process_steps(state, reason, client):
    prompt = f"""List the step-by-step process for changing one's name in {state}, specifically for {reason}.
    Include:
    1. Initial preparation steps
    2. Court filing process
    3. Required waiting periods or notices
    4. Court hearing details (if applicable)
    5. Post-approval steps
    Make it clear these are general guidelines and actual steps may vary."""
    return get_ai_response(prompt, client)

def get_document_checklist(state, reason, client):
    prompt = f"""Create a checklist of required documents for a name change in {state} due to {reason}.
    Include:
    1. Court forms
    2. Identity documents
    3. Supporting documentation specific to {reason}
    4. Additional requirements that may apply
    Note that requirements may vary by county."""
    return get_ai_response(prompt, client)

def render_legal_info():
    st.header("Legal Information")
    st.write("Learn about the legal requirements and procedures for changing your name.")

    # State selection
    state = st.selectbox(
        "Select your state:",
        ["California", "New York", "Texas", "Florida", "Other"]
    )

    if state:
        client = get_ai_client()
        if client and st.button("Get State Requirements"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing legal information about name change processes."},
                        {"role": "user", "content": f"What are the legal requirements and procedures for changing your name in {state}?"}
                    ]
                )
                st.write("State Requirements:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting requirements: {str(e)}")

    # Common legal questions
    st.subheader("Common Legal Questions")
    st.markdown("""
    - What documents do I need?
    - How long does the process take?
    - What are the filing fees?
    - Do I need a lawyer?
    """)

    # Get answers to specific questions
    user_question = st.text_input("Ask a legal question:")
    if user_question:
        client = get_ai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing general legal information about name changes. Always remind users to consult with legal professionals for specific advice."},
                        {"role": "user", "content": user_question}
                    ]
                )
                st.write("Answer:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting answer: {str(e)}")

    # Legal disclaimer
    st.markdown("""
    ---
    **Disclaimer**: This information is for general guidance only and does not constitute legal advice. 
    Please consult with a legal professional for advice specific to your situation.
    """)

    # Resources section
    st.markdown("---")
    st.subheader("Additional Resources")
    
    # Generate relevant resources based on user's situation
    if state:
        resources_prompt = f"Provide 3-4 relevant official resources (with URLs) for name changes in {state}."
        resources = get_ai_response(resources_prompt, client)
        if resources:
            st.markdown(resources)
    else:
        st.markdown("""
        - [National Center for Transgender Equality ID Documents Center](https://transequality.org/documents)
        - [US State Department Name Change Info](https://travel.state.gov/content/travel/en/passports/need-passport/change-of-name.html)
        - [Social Security Administration](https://www.ssa.gov/ssnumber/change-name.htm)
        """) 