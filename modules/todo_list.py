import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
                {"role": "system", "content": """You are a task management specialist focusing on name change processes.
                Provide detailed, actionable steps for completing name changes.
                Include timing estimates, resource links, and important considerations.
                Focus on accuracy and completeness while maintaining a supportive tone."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def get_state_tasks(state, reason, client):
    prompt = f"""Create a detailed list of state-specific tasks for a name change in {state} due to {reason}.
    For each task include:
    1. Task name
    2. Detailed description
    3. Estimated time
    4. Required documents
    5. Official resources/URLs
    Focus on court processes and state-specific requirements."""
    return get_ai_response(prompt, client)

def get_post_approval_tasks(state, reason, client):
    prompt = f"""List all necessary tasks after receiving court approval for a name change in {state} due to {reason}.
    Include:
    1. Government ID updates
    2. Document updates
    3. Account notifications
    4. Professional updates
    5. Estimated timeline for each
    Order from most to least important."""
    return get_ai_response(prompt, client)

def get_timeline_estimate(state, reason, client):
    prompt = f"""Provide a realistic timeline estimate for completing a name change in {state} due to {reason}.
    Include:
    1. Total estimated time
    2. Major milestones and their timing
    3. Potential delays to consider
    4. Tips for expediting the process
    5. Important timing considerations"""
    return get_ai_response(prompt, client)

def render_todo_list():
    st.header("Todo List")
    st.write("Track your progress through the name change process.")

    # Get user information
    if "intake_answers" not in st.session_state or not st.session_state.intake_answers:
        st.warning("Please complete the intake form first to get your personalized checklist.")
        return

    state = st.session_state.intake_answers.get("state", "")
    reason = st.session_state.intake_answers.get("reason", "")

    # Generate todo list
    if state and reason:
        client = get_ai_client()
        if client and st.button("Generate Checklist"):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant creating checklists for name change processes."},
                        {"role": "user", "content": f"Create a detailed checklist for changing your name in {state} due to {reason}."}
                    ]
                )
                st.write("Your Checklist:", response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error generating checklist: {str(e)}")

    # Progress tracking
    st.subheader("Track Your Progress")
    if "todo_items" not in st.session_state:
        st.session_state.todo_items = []

    # Add new task
    new_task = st.text_input("Add a new task:")
    if st.button("Add Task") and new_task:
        st.session_state.todo_items.append({"task": new_task, "completed": False})

    # Display tasks
    for i, item in enumerate(st.session_state.todo_items):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.checkbox(
                item["task"],
                value=item["completed"],
                key=f"task_{i}",
                on_change=lambda i=i: toggle_task(i)
            )
        with col2:
            if st.button("Delete", key=f"delete_{i}"):
                st.session_state.todo_items.pop(i)
                st.rerun()

def toggle_task(index):
    """Toggle the completion status of a task"""
    st.session_state.todo_items[index]["completed"] = not st.session_state.todo_items[index]["completed"]

def render_todo_list_old():
    st.header("Personalized To-Do List")
    
    # Initialize OpenAI client
    client = get_ai_client()
    
    # Get user context from intake form
    user_state = st.session_state.intake_answers.get("state", None)
    user_reason = st.session_state.intake_answers.get("reason", None)
    
    if not user_state:
        st.info("Please complete the intake form to get your personalized to-do list.")
        user_state = st.selectbox(
            "Or select a state to view a generic to-do list:",
            ["California", "New York", "Texas", "Florida", "Other"]
        )
    
    if not user_reason:
        user_reason = st.selectbox(
            "Select your reason for name change:",
            ["Marriage", "Divorce", "Gender Identity", "Personal Choice"]
        )
    
    if user_state and user_reason:
        # Timeline Overview
        st.subheader("Estimated Timeline")
        timeline = get_timeline_estimate(user_state, user_reason, client)
        if timeline:
            st.markdown(f"""
            <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                <h4>Process Timeline</h4>
                {timeline}
            </div>
            """, unsafe_allow_html=True)
        
        # Initialize task completion in session state if not exists
        if "todo_completion" not in st.session_state:
            st.session_state.todo_completion = {}
        
        # Court Process Tasks
        st.subheader("📋 Court Process Tasks")
        court_tasks = get_state_tasks(user_state, user_reason, client)
        if court_tasks:
            st.markdown(court_tasks)
            
            # Add task tracking
            st.markdown("### Track Your Progress")
            task_list = court_tasks.split("\n")
            for i, task in enumerate(task_list):
                if task.strip() and task.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                    task_id = f"court_{user_state}_{i}"
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        if st.checkbox("", value=st.session_state.todo_completion.get(task_id, False), key=f"check_{task_id}"):
                            st.session_state.todo_completion[task_id] = True
                        else:
                            st.session_state.todo_completion[task_id] = False
                    with col2:
                        if st.session_state.todo_completion.get(task_id, False):
                            st.markdown(f"~~{task.strip()}~~")
                        else:
                            st.markdown(task.strip())
        
        # Post-Approval Tasks
        st.subheader("📝 Post-Approval Tasks")
        post_tasks = get_post_approval_tasks(user_state, user_reason, client)
        if post_tasks:
            st.markdown(post_tasks)
            
            # Add task tracking
            st.markdown("### Track Your Progress")
            task_list = post_tasks.split("\n")
            for i, task in enumerate(task_list):
                if task.strip() and task.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                    task_id = f"post_{user_state}_{i}"
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        if st.checkbox("", value=st.session_state.todo_completion.get(task_id, False), key=f"check_{task_id}"):
                            st.session_state.todo_completion[task_id] = True
                        else:
                            st.session_state.todo_completion[task_id] = False
                    with col2:
                        if st.session_state.todo_completion.get(task_id, False):
                            st.markdown(f"~~{task.strip()}~~")
                        else:
                            st.markdown(task.strip())
        
        # Progress Tracking
        st.subheader("📊 Progress Overview")
        total_tasks = len([k for k in st.session_state.todo_completion.keys() if k.startswith(("court_", "post_"))])
        completed_tasks = len([k for k, v in st.session_state.todo_completion.items() if v and k.startswith(("court_", "post_"))])
        
        if total_tasks > 0:
            progress = completed_tasks / total_tasks
            st.progress(progress)
            st.markdown(f"**{completed_tasks}** out of **{total_tasks}** tasks completed ({int(progress * 100)}%)")
        
        # Task Assistance
        st.subheader("Need Help with a Task?")
        task_question = st.text_input("Ask a question about any task:")
        if task_question:
            help_prompt = f"Answer this question about name change tasks in {user_state} for someone changing their name due to {user_reason}: {task_question}"
            help_response = get_ai_response(help_prompt, client)
            if help_response:
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 10px;">
                    {help_response}
                </div>
                """, unsafe_allow_html=True)
        
        # Resources
        st.markdown("---")
        st.subheader("Helpful Resources")
        resources_prompt = f"Provide 3-4 official resources and tools for managing a name change process in {user_state}, particularly for {user_reason}."
        resources = get_ai_response(resources_prompt, client)
        if resources:
            st.markdown(resources) 