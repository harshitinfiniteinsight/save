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
                {"role": "system", "content": """You are a voting rights specialist focusing on name changes and voter registration.
                Provide accurate, up-to-date information about voting rights and registration procedures.
                Focus on practical guidance while emphasizing the importance of verifying with local election offices.
                Always include appropriate disclaimers about checking official sources."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def get_state_voting_info(state, reason, client):
    prompt = f"""Provide detailed information about voter registration requirements in {state}, specifically for someone who has changed their name due to {reason}.
    Include:
    1. Registration deadlines
    2. Required documentation
    3. Special considerations for {reason}-related name changes
    4. Online vs. in-person registration options
    5. ID requirements for voting
    Remember to note this is general information and may vary by county."""
    return get_ai_response(prompt, client)

def get_voting_checklist(state, reason, client):
    prompt = f"""Create a detailed checklist for updating voter registration in {state} after a name change due to {reason}.
    Include:
    1. Immediate steps after name change
    2. Required documentation
    3. Deadlines and timing considerations
    4. Verification steps
    5. What to bring when voting
    Note that requirements may vary by county."""
    return get_ai_response(prompt, client)

def get_voting_faqs(state, reason, client):
    prompt = f"""Generate FAQs about voting rights and registration for someone in {state} who changed their name due to {reason}.
    Address common concerns such as:
    1. Timing of registration updates
    2. Acceptable forms of ID
    3. Provisional ballot situations
    4. Special considerations for {reason}
    5. Common challenges and solutions"""
    return get_ai_response(prompt, client)

def render_voting_rights():
    st.header("Voting Rights Information")
    st.write("Learn how to update your voter registration after changing your name.")

    # State selection
    state = st.selectbox(
        "Select your state:",
        ["California", "New York", "Texas", "Florida", "Other"]
    )

    if state:
        client = get_ai_client()
        if client and st.button("Get Voter Registration Information"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing information about voter registration updates after name changes."},
                        {"role": "user", "content": f"What are the steps to update voter registration after a name change in {state}?"}
                    ]
                )
                st.write("Registration Information:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting information: {str(e)}")

    # Important deadlines
    st.subheader("Important Deadlines")
    if st.button("Check Registration Deadlines"):
        client = get_ai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant providing information about voter registration deadlines."},
                        {"role": "user", "content": f"What are the voter registration deadlines and requirements in {state}?"}
                    ]
                )
                st.write("Deadlines:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error getting deadlines: {str(e)}")

    # Resources
    st.subheader("Voter Registration Resources")
    st.markdown("""
    - [National Voter Registration Application](https://www.eac.gov/voters/national-mail-voter-registration-form)
    - [Find Your State Election Office](https://www.usa.gov/election-office)
    - [Voter Registration Deadlines](https://www.vote.org/voter-registration-deadlines/)
    """)

    # Warning section
    st.warning("""
    ⚠️ **Important Notice**
    
    Updating your voter registration after a name change is crucial to ensure you can vote in future elections.
    Contact your local election office for specific guidance on your situation.
    """)

    # Get user context from intake form
    user_state = st.session_state.intake_answers.get("state", None)
    user_reason = st.session_state.intake_answers.get("reason", None)
    
    # Main explanation
    st.markdown("""
    ## The SAVE Act and Your Right to Vote
    
    Changing your name can impact your ability to vote if your voter registration doesn't match your ID. The Securing America's Voting Equipment (SAVE) Act and other voter ID laws mean that consistency between your identification documents and voter registration is critical.
    """)
    
    if not user_state:
        user_state = st.selectbox(
            "Select your state for specific voting information:",
            ["California", "New York", "Texas", "Florida", "Other"]
        )
    
    if not user_reason:
        user_reason = st.selectbox(
            "Select your reason for name change:",
            ["Marriage", "Divorce", "Gender Identity", "Personal Choice"]
        )
    
    if user_state and user_reason:
        # State-specific voting information
        st.subheader(f"Voting Rights in {user_state}")
        voting_info = get_state_voting_info(user_state, user_reason, client)
        if voting_info:
            st.markdown(voting_info)
        
        # Personalized checklist
        st.subheader("Your Voter Registration Checklist")
        checklist = get_voting_checklist(user_state, user_reason, client)
        if checklist:
            st.markdown(checklist)
        
        # FAQs
        st.subheader("Frequently Asked Questions")
        faqs = get_voting_faqs(user_state, user_reason, client)
        if faqs:
            st.markdown(faqs)
        
        # Interactive guidance
        st.subheader("Need Specific Guidance?")
        user_question = st.text_input("Ask a question about voting rights and registration:")
        if user_question:
            prompt = f"Answer this specific question about voting rights in {user_state} for someone who changed their name due to {reason}: {user_question}"
            answer = get_ai_response(prompt, client)
            if answer:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 10px;">
                    {answer}
                </div>
                """, unsafe_allow_html=True)
    
    # Resources and verification
    st.markdown("---")
    st.subheader("Official Resources")
    
    if user_state:
        # Generate state-specific resources
        resources_prompt = f"Provide 3-4 official voting resources (with URLs) for {user_state}, including the state election office website and voter registration portal."
        resources = get_ai_response(resources_prompt, client)
        if resources:
            st.markdown(resources)
    
    # Registration status check
    st.subheader("Check Your Registration Status")
    if st.button("Find My Registration Status"):
        if user_state in ["California", "Texas", "Florida", "New York"]:
            state_urls = {
                "California": "https://voterstatus.sos.ca.gov/",
                "Texas": "https://teamrv-mvp.sos.texas.gov/MVP/mvp.do",
                "Florida": "https://registration.elections.myflorida.com/CheckVoterStatus",
                "New York": "https://voterlookup.elections.ny.gov/"
            }
            st.markdown(f"➡️ [Check your registration in {user_state}]({state_urls[user_state]})")
        else:
            st.markdown("➡️ [Check your registration at Vote.gov](https://vote.gov/)")
    
    # Bottom call to action
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #f0f7ff; border-radius: 10px; margin-top: 20px;">
        <h3>Your Name Is Your Right to Vote</h3>
        <p>Update your voter registration immediately after your legal name change to ensure you can vote in the next election.</p>
        <p style="font-size: 0.9em; color: #666;">Always verify information with your local election office for the most current requirements.</p>
    </div>
    """, unsafe_allow_html=True) 