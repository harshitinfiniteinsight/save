import streamlit as st
from modules.ai_support import render_ai_support
from modules.emotional_support import render_emotional_support
from modules.intake import render_intake_form
from modules.voting_rights import render_voting_rights
from modules.todo_list import render_todo_list
from modules.form_preview import render_form_preview
from modules.legal_info import render_legal_info

# Initialize session state variables
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "intake_answers" not in st.session_state:
    st.session_state.intake_answers = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "llm_messages" not in st.session_state:
    st.session_state.llm_messages = [
        {"role": "system", "content": "You are a helpful and empathetic legal assistant specializing in name change processes."}
    ]

if "todo_items" not in st.session_state:
    st.session_state.todo_items = []

# Page configuration
st.set_page_config(
    page_title="Name Change Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for simple, readable theme
st.markdown("""
<style>
    /* Base theme overrides */
    .stApp {
        background-color: white;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f0f0;
        padding: 2rem 1rem;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    
    /* Text elements */
    p, li, label {
        color: #2c3e50;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background-color: white !important;
        color: #2c3e50 !important;
        border: 2px solid #2c3e50 !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div > select {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: white !important;
        border: 1px solid #bdc3c7 !important;
        padding: 1rem !important;
        border-radius: 4px !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
        padding: 1.5rem !important;
        border-radius: 4px !important;
        margin: 1rem 0 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: white !important;
        border: 1px solid #bdc3c7 !important;
        border-radius: 4px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Module containers */
    .module-container {
        background-color: white !important;
        border: 1px solid #bdc3c7 !important;
        padding: 2rem !important;
        border-radius: 4px !important;
        margin: 1rem 0 !important;
    }
    
    /* Success/Info messages */
    .stSuccess, .stInfo {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #f0f0f0 !important;
    }
    
    .stProgress > div > div > div {
        background-color: #2c3e50 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
        background-color: #f8f9fa !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #bdc3c7 !important;
        border-radius: 4px 4px 0 0 !important;
        padding: 0.5rem 1rem !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    
    /* Sidebar navigation */
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
    }
    
    /* Radio buttons in sidebar */
    .stRadio > div > div > label {
        background-color: white !important;
        border: 1px solid #bdc3c7 !important;
        padding: 0.5rem !important;
        border-radius: 4px !important;
        margin: 0.2rem 0 !important;
        color: #2c3e50 !important;
    }
    
    .stRadio > div > div > label:hover {
        background-color: #f8f9fa !important;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.title("Name Change Assistant")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    selected_module = st.radio(
        "Choose a Module",
        [
            "Intake Form",
            "AI Support",
            "Emotional Support",
            "Legal Information",
            "Voting Rights",
            "Todo List",
            "Form Preview"
        ]
    )

# Module descriptions
module_descriptions = {
    "Intake Form": "Start here! Fill out basic information about your name change process.",
    "AI Support": "Get AI-powered assistance and answers to your questions.",
    "Emotional Support": "Find resources and support for your journey.",
    "Legal Information": "Access state-specific legal requirements and procedures.",
    "Voting Rights": "Learn about updating your voter registration after a name change.",
    "Todo List": "Track your progress with a customized checklist.",
    "Form Preview": "Preview and download your completed forms."
}

# Display module description
st.markdown(f"""
    <div class="info-box">
        <h3>{selected_module}</h3>
        <p>{module_descriptions[selected_module]}</p>
    </div>
""", unsafe_allow_html=True)

# Render selected module
if selected_module == "Intake Form":
    render_intake_form()
elif selected_module == "AI Support":
    render_ai_support()
elif selected_module == "Emotional Support":
    render_emotional_support()
elif selected_module == "Legal Information":
    render_legal_info()
elif selected_module == "Voting Rights":
    render_voting_rights()
elif selected_module == "Todo List":
    render_todo_list()
elif selected_module == "Form Preview":
    render_form_preview()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #2c3e50; padding: 20px;'>
    Made with care to support your name change journey
</div>
""", unsafe_allow_html=True) 