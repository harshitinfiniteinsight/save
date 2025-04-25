import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import json

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
                {"role": "system", "content": """You are a document preparation specialist focusing on name change forms.
                Provide accurate guidance for completing legal forms and documentation requirements.
                Focus on clarity and completeness while noting the importance of verification with official sources.
                Always include appropriate disclaimers about seeking legal review when necessary."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def get_form_requirements(state, reason, client):
    prompt = f"""List all required forms and supporting documents for a name change in {state} due to {reason}.
    Include:
    1. Court forms needed
    2. Identity documents required
    3. Supporting documentation specific to {reason}
    4. Number of copies needed
    5. Any special requirements
    Note that requirements may vary by county."""
    return get_ai_response(prompt, client)

def get_form_instructions(state, reason, client):
    prompt = f"""Provide detailed instructions for completing name change forms in {state} for {reason}.
    Include:
    1. Step-by-step guidance
    2. Common mistakes to avoid
    3. Special considerations for {reason}
    4. Tips for accurate completion
    5. What to do after completion"""
    return get_ai_response(prompt, client)

def get_filing_instructions(state, reason, client):
    prompt = f"""Explain the process of filing name change forms in {state} for {reason}.
    Include:
    1. Where to file
    2. Filing fees and payment methods
    3. Processing timeline
    4. Next steps after filing
    5. Follow-up procedures"""
    return get_ai_response(prompt, client)

def render_form_preview():
    st.header("Form Preview")
    st.write("Preview and download your name change forms.")

    # Check if we have the required information
    if "intake_answers" not in st.session_state or not st.session_state.intake_answers:
        st.warning("Please complete the intake form first to generate your documents.")
        return

    # Display form preview
    st.subheader("Social Security Administration Form")
    
    # Mock data for privacy
    current_name = st.session_state.intake_answers.get("current_name", "CURRENT NAME")
    new_name = st.session_state.intake_answers.get("new_name", "NEW NAME")
    
    st.markdown(f"""
    ### Form SS-5: Application for a Social Security Card
    
    **IMPORTANT**: This is a preview. The actual form will need to be filled out in person.
    
    1. NAME TO BE SHOWN ON CARD: {new_name}
    2. FULL NAME AT BIRTH: {current_name}
    
    [Additional form fields would be displayed here]
    """)

    # Get AI-powered form completion tips
    if st.button("Get Form Completion Tips"):
        client = get_ai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing guidance on completing name change forms."},
                        {"role": "user", "content": "What are the key things to remember when filling out the Social Security name change form?"}
                    ]
                )
                st.write("Tips:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting tips: {str(e)}")

    # Download button (mock)
    st.download_button(
        label="Download Form Preview",
        data="This would be the actual form data",
        file_name="name_change_preview.pdf",
        mime="application/pdf"
    )

    # Legal Disclaimer
    st.markdown("""
    <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
        <h4 style="color: #e65100;">📝 Document Preparation Notice</h4>
        <p>The forms and guidance provided here are for reference only. Please verify all requirements with your local court 
        and consider consulting with a legal professional to review your documents before filing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user information from session state
    user_info = st.session_state.intake_answers
    reason = user_info.get('reason', '')
    state = user_info.get('state', '')
    
    if not all([current_name, new_name, reason, state]):
        st.info("Please complete the intake form to access personalized form preparation guidance.")
        return
    
    # Form Requirements
    st.subheader("Required Forms & Documents")
    requirements = get_form_requirements(state, reason, client)
    if requirements:
        st.markdown(requirements)
    
    # Form Preview Section
    st.subheader("Form Preview")
    
    # Create tabs for different forms
    tab1, tab2, tab3 = st.tabs(["Petition for Name Change", "Social Security Form", "Court Order Template"])
    
    with tab1:
        st.markdown("### Petition for Name Change")
        # Generate petition preview
        petition_prompt = f"""Create a preview of a Petition for Name Change form for {state} with these details:
        Current Name: {current_name}
        New Name: {new_name}
        Reason: {reason}
        Include standard legal language and formatting."""
        petition_preview = get_ai_response(petition_prompt, client)
        if petition_preview:
            st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #f9f9f9;">
                {petition_preview}
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Social Security Card Application")
        # Display SSA form preview
        st.markdown("""
        <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #f9f9f9;">
            <h4>APPLICATION FOR A SOCIAL SECURITY CARD (Form SS-5)</h4>
            <p><strong>Current Name:</strong> {current_name}</p>
            <p><strong>New Name:</strong> {new_name}</p>
            <p><strong>Reason for Change:</strong> {reason}</p>
            <em>Additional fields will be completed in person at the Social Security office.</em>
        </div>
        """.format(current_name=current_name, new_name=new_name, reason=reason), unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Court Order Template")
        # Generate court order template
        order_prompt = f"""Create a preview of a Court Order template for {state} with these details:
        Current Name: {current_name}
        New Name: {new_name}
        Reason: {reason}
        Include standard legal language and formatting."""
        order_preview = get_ai_response(order_prompt, client)
        if order_preview:
            st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; background-color: #f9f9f9;">
                {order_preview}
            </div>
            """, unsafe_allow_html=True)
    
    # Form Completion Instructions
    st.subheader("Form Completion Instructions")
    instructions = get_form_instructions(state, reason, client)
    if instructions:
        st.markdown(instructions)
    
    # Filing Instructions
    st.subheader("Filing Instructions")
    filing = get_filing_instructions(state, reason, client)
    if filing:
        st.markdown(filing)
    
    # Interactive Help
    st.subheader("Need Help with Forms?")
    form_question = st.text_input("Ask a question about form completion or filing:")
    if form_question:
        help_prompt = f"Answer this question about name change forms in {state} for {reason}: {form_question}"
        help_response = get_ai_response(help_prompt, client)
        if help_response:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 10px;">
                {help_response}
            </div>
            """, unsafe_allow_html=True)
    
    # Document Checklist
    st.subheader("Final Checklist")
    checklist_prompt = f"""Create a final checklist for name change document preparation in {state} for {reason}.
    Include all forms, supporting documents, copies needed, and filing requirements."""
    checklist = get_ai_response(checklist_prompt, client)
    if checklist:
        st.markdown(f"""
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h4>Document Preparation Checklist</h4>
            {checklist}
        </div>
        """, unsafe_allow_html=True)
    
    # Resources
    st.markdown("---")
    st.subheader("Additional Resources")
    resources_prompt = f"Provide 3-4 official resources for name change form preparation in {state}, particularly for {reason}."
    resources = get_ai_response(resources_prompt, client)
    if resources:
        st.markdown(resources) 