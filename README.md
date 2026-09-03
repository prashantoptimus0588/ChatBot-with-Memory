### 🤖 LangGraph Chatbot with Streamlit Frontend

A conversational AI assistant built using **LangGraph** for state management and **Streamlit** for a dynamic chat interface. The application features persistent chat history across sessions using a local **SQLite database**. 

### ✨ Features

* **Stateful Management**: Utilizes LangGraph's native compilation to manage context graphs.
* **SQLite Persistence**: Automatically saves conversation threads to a local database (state_db.sqlite) so history remains intact after app restarts.
* **Dynamic Threading**: Supports multiple chat sessions with automatically generated titles based on the user's first prompt.
* **Streaming Output**: Leverages Streamlit's st.write_stream for smooth, real-time AI responses.

### 🛠️ Project Structure

* backend.py: Defines the LangGraph state machine, connects to the Groq LLM endpoint, and handles SQLite persistence.
* app.py: The Streamlit frontend layout, sidebar navigation, and session state tracking.
* .env: (User created) Contains sensitive API credentials.

### 🚀 Getting Started

### 1. Clone & Navigate

bash

git clone <your-repository-url>
cd <your-project-folder>

Use code with caution.

### 2. Create and Activate Virtual Environment

bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

Use code with caution.

### 3. Install Dependencies

bash

python -m pip install -r requirements.txt

Use code with caution.

### 4. Configuration

Create a .env file in the root directory and add your API keys: 

env

GROQ_API_KEY=your_groq_api_key_here

Use code with caution.

### 5. Run the Application

bash

streamlit run app.py

Use code with caution.

### 📦 Dependencies

* streamlit
* langgraph
* langgraph-checkpoint-sqlite
* langchain-core
* langchain-groq
* python-dotenv