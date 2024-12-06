import streamlit as st
import anthropic
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
if not firebase_admin._apps:
    # Initialize with credentials from Streamlit secrets
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": "googleapis.com"
    })
    firebase_admin.initialize_app(cred)
    db = firestore.client()

# Firebase helper functions
def save_chat_to_firebase(chat_id, messages, user_id="default"):
    """Save chat messages to Firebase"""
    doc_ref = db.collection('chats').document(f"{user_id}_{chat_id}")
    doc_ref.set({
        'messages': messages,
        'updated_at': datetime.now(),
        'user_id': user_id
    })

def load_chats_from_firebase(user_id="default"):
    """Load all chats for a user from Firebase"""
    chats = {}
    chat_docs = db.collection('chats').where('user_id', '==', user_id).stream()
    
    for doc in chat_docs:
        chat_id = doc.id.replace(f"{user_id}_", "")
        chat_data = doc.to_dict()
        chats[chat_id] = chat_data['messages']
    
    if not chats:
        chats["Default Chat"] = []
        save_chat_to_firebase("Default Chat", [])
    
    return chats

# Set page config
st.set_page_config(
    page_title="Claude AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .sidebar-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sidebar-subheader {
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #1e2030 0%, #2d3250 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .title-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        letter-spacing: 0.5px;
    }
    .info-section {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .info-badge {
        background: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        white-space: nowrap;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .info-badge:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .info-badge .icon {
        font-size: 1rem;
        opacity: 0.9;
    }
    .info-badge .label {
        font-weight: 500;
    }
    .chat-info {
        background: linear-gradient(120deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        white-space: nowrap;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .token-info {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    .credits {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    .credits a {
        color: #4facfe;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    .credits a:hover {
        color: #66a6ff;
        text-decoration: underline;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .header-container {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# Available Claude models
CLAUDE_MODELS = {
    "Claude 3 Haiku": "claude-3-haiku-20240307",
    "Claude 3 Sonnet": "claude-3-sonnet-20240229",
    "Claude 3 Opus": "claude-3-opus-20240229",
    "Claude 3.5 Sonnet (Default)": "claude-3-5-sonnet-20240620",
    "Claude 3.5 Sonnet (Latest)": "claude-3-5-sonnet-20241022"
}

# Initialize session states
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats_from_firebase()
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Default Chat"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful AI assistant."
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 4000
if "temperature" not in st.session_state:
    st.session_state.temperature = 1.0
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Claude 3.5 Sonnet (Default)"

# Initialize default chat if it doesn't exist
if "Default Chat" not in st.session_state.all_chats:
    st.session_state.all_chats["Default Chat"] = []
    save_chat_to_firebase("Default Chat", [])

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-header">🤖 Configuration</p>', unsafe_allow_html=True)
    
    # API Key Section
    with st.expander("🔑 API KEY", expanded=True):
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-api...",
            help="Enter your Anthropic API key",
            key="api_key_input"
        )
        st.markdown("""
            <p style="font-size: 0.8em; color: #666;">
                Don't have an API key? Get one from 
                <a href="https://console.anthropic.com/" target="_blank">Anthropic's Console</a>
            </p>
        """, unsafe_allow_html=True)
    
    # Model Settings Section
    with st.expander("🎯 MODEL SETTINGS", expanded=True):
        st.markdown('<p class="sidebar-subheader">Select Model</p>', unsafe_allow_html=True)
        selected_model = st.selectbox(
            "🤖 Model",
            options=list(CLAUDE_MODELS.keys()),
            index=list(CLAUDE_MODELS.keys()).index(st.session_state.selected_model),
            help="Select the Claude model to use for this chat",
            label_visibility="collapsed"
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
        
        st.markdown('<p class="sidebar-subheader">System Prompt</p>', unsafe_allow_html=True)
        new_system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            help="Define the AI assistant's role and behavior",
            label_visibility="collapsed"
        )
        if new_system_prompt != st.session_state.system_prompt:
            st.session_state.system_prompt = new_system_prompt
        
        st.markdown('<p class="sidebar-subheader">Response Settings</p>', unsafe_allow_html=True)
        
        # Max Tokens Interface
        st.markdown("🔢 **Maximum Response Length**")
        token_mode = st.radio(
            "Token Mode",
            options=["Standard (up to 4K)", "Extended (up to 8K)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if token_mode == "Standard (up to 4K)":
            new_max_tokens = st.slider(
                "Standard Tokens",
                min_value=1000,
                max_value=4000,
                value=min(st.session_state.max_tokens, 4000),
                step=100,
                label_visibility="collapsed"
            )
            st.markdown(f'<p class="token-info">Current setting: {new_max_tokens:,} tokens</p>', unsafe_allow_html=True)
        else:
            new_max_tokens = st.slider(
                "Extended Tokens",
                min_value=4000,
                max_value=8192,
                value=max(st.session_state.max_tokens, 4000),
                step=100,
                label_visibility="collapsed"
            )
            st.markdown(f'<p class="token-info">Current setting: {new_max_tokens:,} tokens (Extended)</p>', unsafe_allow_html=True)
        
        if new_max_tokens != st.session_state.max_tokens:
            st.session_state.max_tokens = new_max_tokens
        
        st.markdown("🌡️ **Creativity Level**")
        new_temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Controls response creativity (0 = focused, 1 = creative)",
            label_visibility="collapsed"
        )
        st.markdown(f'<p class="token-info">Current setting: {new_temperature:.1f} ({("More Creative" if new_temperature > 0.5 else "More Focused")})</p>', unsafe_allow_html=True)
        if new_temperature != st.session_state.temperature:
            st.session_state.temperature = new_temperature
    
    st.markdown("---")
    
    # Chat Management Section
    with st.expander("💬 CHAT MANAGEMENT", expanded=True):
        st.markdown('<p class="sidebar-subheader">Create New Chat</p>', unsafe_allow_html=True)
        new_chat_name = st.text_input(
            "Chat Name",
            placeholder="Enter chat name...",
            label_visibility="collapsed"
        )
        if st.button("➕ Create New Chat", use_container_width=True):
            if new_chat_name:
                if new_chat_name in st.session_state.all_chats:
                    base_name = new_chat_name
                    counter = 1
                    while f"{base_name} ({counter})" in st.session_state.all_chats:
                        counter += 1
                    new_chat_name = f"{base_name} ({counter})"
                st.session_state.all_chats[new_chat_name] = []
                st.session_state.current_chat_id = new_chat_name
                save_chat_to_firebase(new_chat_name, [])
                st.rerun()
    
    # Chat History Section
    with st.expander("📚 CHAT HISTORY", expanded=True):
        for chat_id in st.session_state.all_chats:
            chat_container = st.container()
            col1, col2 = chat_container.columns([4, 1])
            
            if chat_id == st.session_state.current_chat_id:
                button_style = "primary"
                button_label = f"📍 {chat_id}"
            else:
                button_style = "secondary"
                button_label = f"💭 {chat_id}"
            
            if col1.button(
                button_label,
                key=f"select_{chat_id}",
                use_container_width=True,
                type=button_style
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
            
            if chat_id != "Default Chat":
                if col2.button("🗑️", key=f"delete_{chat_id}"):
                    del st.session_state.all_chats[chat_id]
                    # Delete from Firebase
                    db.collection('chats').document(f"default_{chat_id}").delete()
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = "Default Chat"
                    st.rerun()
    
    # Credits at bottom of sidebar
    st.markdown("""
        <div class="credits">
            Created by <a href="https://www.linkedin.com/in/bettercallmanav/" target="_blank">Manav</a><br>
            View on <a href="https://github.com/bettercallmanav/Claude-AI-Web-Interface" target="_blank">GitHub</a>
        </div>
    """, unsafe_allow_html=True)

# Main chat interface header
st.markdown(f"""
    <div class="header-container">
        <div class="title-section">
            <h1 class="main-title">Claude AI Assistant</h1>
            <div class="credits">
                by <a href="https://www.linkedin.com/in/bettercallmanav/" target="_blank">Manav</a>
            </div>
        </div>
        <div class="info-section">
            <div class="info-badge">
                <span class="icon">🤖</span>
                <span class="label">{st.session_state.selected_model.split(" (")[0]}</span>
            </div>
            <div class="info-badge">
                <span class="icon">🔢</span>
                <span class="label">{st.session_state.max_tokens//1000}K tokens</span>
            </div>
            <div class="info-badge">
                <span class="icon">🌡️</span>
                <span class="label">Temp {st.session_state.temperature:.1f}</span>
            </div>
            <div class="chat-info">
                <span class="icon">💬</span>
                <span class="label">{st.session_state.current_chat_id}</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Check if API key is provided
if not api_key:
    st.warning("Please enter your Anthropic API key in the sidebar to start chatting.")
    st.stop()

try:
    # Initialize Anthropic client with the provided API key
    client = anthropic.Anthropic(api_key=api_key)
    
    # Display current chat messages
    current_messages = st.session_state.all_chats[st.session_state.current_chat_id]
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to current chat
        current_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Prepare messages for Claude
        claude_messages = []
        for msg in current_messages:
            claude_messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            })

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            with client.messages.stream(
                model=CLAUDE_MODELS[st.session_state.selected_model],
                max_tokens=st.session_state.max_tokens,
                temperature=st.session_state.temperature,
                system=st.session_state.system_prompt,
                messages=claude_messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    message_placeholder.markdown(full_response + "▌")
                
                # Remove cursor and display final response
                message_placeholder.markdown(full_response)
            
            # Add assistant response to current chat
            current_messages.append({"role": "assistant", "content": full_response})
            
            # Save to Firebase after each message
            save_chat_to_firebase(st.session_state.current_chat_id, current_messages)
            
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
