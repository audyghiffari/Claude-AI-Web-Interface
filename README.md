# Claude AI Assistant Web Interface

A modern, feature-rich web application built with Streamlit for interacting with Claude AI models through the Anthropic API. This interface provides a user-friendly way to chat with various Claude models while offering extensive customization options.

## Features

- **Multiple Model Support**

  - Claude 3 Haiku
  - Claude 3 Sonnet
  - Claude 3 Opus
  - Claude 3.5 Sonnet variants

- **Customizable Settings**

  - API key management through the sidebar
  - Adjustable response length (Standard up to 4K or Extended up to 8K tokens)
  - Temperature control for response creativity
  - Customizable system prompts

- **Chat Management**

  - Create multiple chat sessions
  - Switch between different chats
  - Delete unwanted chats
  - Persistent chat history within sessions

- **Modern UI/UX**
  - Clean, intuitive interface
  - Real-time response streaming
  - Visual indicators for model, tokens, and temperature settings
  - Responsive design with custom styling

## Requirements

```
streamlit
anthropic
```

## Setup

1. Install the required packages:

   ```bash
   pip install streamlit anthropic
   ```

2. Run the application:

   ```bash
   streamlit run app.py
   ```

3. Enter your Anthropic API key in the sidebar when prompted
   - Get your API key from [Anthropic's Console](https://console.anthropic.com/)
   - The API key is stored only for the current session

## Usage

1. **Initial Setup**

   - Launch the application
   - Enter your Anthropic API key in the sidebar under "🔑 API KEY"

2. **Configure Settings**

   - Select your preferred Claude model
   - Adjust the system prompt if needed
   - Set maximum response length (4K or 8K tokens)
   - Adjust temperature (0.0 for focused responses, 1.0 for creative responses)

3. **Chat Management**

   - Create new chat sessions using the "Create New Chat" button
   - Switch between chats using the chat history panel
   - Delete unwanted chats with the 🗑️ button

4. **Chatting**
   - Type your message in the input field at the bottom
   - View responses in real-time as they stream in
   - Messages are automatically saved in the chat history

## Interface Elements

- **Header Bar**

  - Shows current model, token limit, temperature, and active chat
  - Provides quick overview of current settings

- **Sidebar**

  - API Key management
  - Model selection
  - System prompt configuration
  - Response settings (tokens and temperature)
  - Chat management tools

- **Main Chat Area**
  - Displays conversation history
  - Shows streaming responses in real-time
  - Maintains chat context for natural conversations

## Notes

- The application does not store API keys permanently - you'll need to re-enter your key when restarting the application
- Chat history persists only during the current session
- The interface automatically handles API errors and provides appropriate feedback
- All settings can be adjusted in real-time without interrupting the chat flow

## Security

- API keys are handled securely and are only stored in session state
- No data is permanently stored on disk
- All communication with Claude is done through official Anthropic API endpoints
