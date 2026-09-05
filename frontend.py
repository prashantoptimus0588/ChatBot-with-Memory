import streamlit as st
from backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
    if thread_id not in st.session_state['thread_titles']:
        st.session_state['thread_titles'][thread_id] = f"Chat {str(thread_id)[:8]}..."

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()
    # Populate existing titles with first messages if available
    for t_id in st.session_state['chat_threads']:
        msgs = load_conversation(t_id)
        if msgs and isinstance(msgs[0], HumanMessage):
            # Limit title to first 30 characters
            st.session_state['thread_titles'][t_id] = msgs[0].content[:30] + "..." if len(msgs[0].content) > 30 else msgs[0].content
        else:
            st.session_state['thread_titles'][t_id] = f"Chat {str(t_id)[:8]}..."

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.markdown("---")
st.sidebar.subheader('Chat History')

for thread_id in st.session_state['chat_threads'][::-1]:
    # Dynamic label from our mapping dictionary
    button_label = st.session_state['thread_titles'].get(thread_id, str(thread_id))

    if st.sidebar.button(button_label, key=f"btn_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
        st.rerun()


# **************************************** Main UI ************************************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # Update title immediately if this is the first message in the thread
    if not st.session_state['message_history']:
        title_text = user_input[:30] + "..." if len(user_input) > 30 else user_input
        st.session_state['thread_titles'][st.session_state['thread_id']] = title_text

    # Add message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    with st.chat_message('assistant'):
        # Lazily-created status box: only appears if a tool actually gets called
        status_holder = {"box": None}
        tool_call_names = {}  # tool_call_id -> tool name, so we can label the ToolMessage result

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                # LLM asked to call one or more tools
                if isinstance(message_chunk, AIMessage) and message_chunk.tool_calls:
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status("Using tools...", expanded=True)
                    for tc in message_chunk.tool_calls:
                        tool_call_names[tc["id"]] = tc["name"]
                        arg_preview = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                        status_holder["box"].write(f"🔧 Running `{tc['name']}`({arg_preview})...")

                # A tool finished executing and returned its result
                elif isinstance(message_chunk, ToolMessage):
                    name = tool_call_names.get(
                        message_chunk.tool_call_id, getattr(message_chunk, "name", "tool")
                    )
                    if status_holder["box"] is not None:
                        status_holder["box"].write(f"✅ `{name}` finished")

                # Final assistant answer text — stream only this to the chat bubble
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Collapse the status box once everything is done
        if status_holder["box"] is not None:
            status_holder["box"].update(label="Tools finished", state="complete", expanded=False)

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()