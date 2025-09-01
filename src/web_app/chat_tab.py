# Create the chat interface tab with conversation history and agent indicators
# Include message formatting, source citations, quick action buttons

import streamlit as st
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
import logging

# Add root directory to path for imports
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_dir)

# Load environment variables first
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

# Import existing components
RAG_AVAILABLE = False
LLM_AVAILABLE = False
ChatLLM = None

try:
    # Add to path for imports
    from src.agents.finance_qa_agent import FinanceQAAgent
    from src.rag.vector_store import FinanceVectorStore
    from src.rag.retriever import FinanceRetriever
    RAG_AVAILABLE = True
    print("DEBUG: RAG components imported successfully")
except ImportError as e:
    print(f"RAG components not available: {e}")

# Try to import LLM - check various langchain versions
try:
    from langchain_openai import ChatOpenAI
    ChatLLM = ChatOpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    LLM_AVAILABLE = bool(api_key and api_key != "your_openai_api_key_here")
    print(f"DEBUG: OpenAI import successful, API key available: {LLM_AVAILABLE}")
except ImportError as e:
    print(f"DEBUG: langchain_openai import failed: {e}")
    try:
        from langchain.chat_models import ChatOpenAI
        ChatLLM = ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        LLM_AVAILABLE = bool(api_key and api_key != "your_openai_api_key_here")
        print(f"DEBUG: Fallback OpenAI import successful, API key available: {LLM_AVAILABLE}")
    except ImportError as e2:
        print(f"DEBUG: Fallback import also failed: {e2}")
        try:
            from langchain.llms import OpenAI
            ChatLLM = OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            LLM_AVAILABLE = bool(api_key and api_key != "your_openai_api_key_here")
            print(f"DEBUG: Legacy OpenAI import successful, API key available: {LLM_AVAILABLE}")
        except ImportError as e3:
            print(f"DEBUG: All OpenAI imports failed: {e3}")
            LLM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def should_show_workflow_status() -> bool:
    """Check if workflow status should be displayed based on config or environment"""
    # Check environment variable first
    show_status = os.getenv("SHOW_WORKFLOW_STATUS", "false").lower()
    if show_status in ["true", "1", "yes", "on"]:
        return True
    
    # Check config file if available
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config.get("app", {}).get("show_workflow_status", False)
    except Exception as e:
        print(f"DEBUG: Could not load config: {e}")
    
    # Default to hidden
    return False

def render_chat_tab(workflow, session_state: Dict[str, Any]):
    """
    Render the main chat interface - Phase 3 Enhanced
    
    Features:
    - Multi-agent workflow integration with intelligent routing
    - Agent indicators showing which agent is responding
    - Enhanced conversation history with agent metadata
    - Source citations and confidence indicators
    - Quick action buttons for testing agent routing
    """
    
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Phase 3 status indicators - now configurable
    if should_show_workflow_status():
        render_phase3_status(workflow)
    
    # Display conversation history
    render_conversation_history(session_state.get("conversation_history", []))
    
    # Chat input area
    render_chat_input(workflow, session_state)
    
    # Agent testing buttons - always show for easy access
    render_agent_testing_buttons(workflow, session_state)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_phase3_status(workflow):
    """Display Phase 3 multi-agent workflow status"""
    st.markdown("### 🚀 Phase 3: Multi-Agent Workflow Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if workflow:
            st.success("✅ LangGraph Workflow: Active")
            st.caption(f"🤖 Agents Available: {len(workflow.agents)}")
            
            # Show agent status
            for agent_name in workflow.agents.keys():
                if agent_name == "finance_qa":
                    st.markdown("• 💬 **Finance Q&A**: Active (LLM + RAG)")
                elif agent_name == "portfolio_analysis":
                    st.markdown("• 📊 **Portfolio Agent**: Ready (Phase 4)")
                elif agent_name == "market_analysis":
                    # Check if it's a real market agent with Alpha Vantage
                    agent = workflow.agents[agent_name]
                    if hasattr(agent, 'market_provider'):
                        status = "Active (Alpha Vantage)" if not agent.market_provider.mock_mode else "Mock Mode"
                    else:
                        status = "Mock Mode"
                    st.markdown(f"• 📈 **Market Agent**: {status}")
                elif agent_name == "goal_planning":
                    st.markdown("• 🎯 **Goal Agent**: Ready (Phase 6)")
        else:
            st.warning("⚠️ LangGraph Workflow: Not Available")
            st.caption("❌ Falling back to single agent mode")
    
    with col2:
        # Technology status
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            st.success("✅ OpenAI LLM: Active")
        else:
            st.warning("⚠️ OpenAI LLM: Mock Mode")
        
        faiss_exists = os.path.exists("src/data/faiss_index.faiss")
        if faiss_exists:
            st.success("✅ FAISS RAG: Active")
        else:
            st.warning("⚠️ FAISS RAG: Mock Mode")
        
        # Alpha Vantage status
        av_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if av_key and av_key != "your_alpha_vantage_api_key_here":
            st.success("✅ Alpha Vantage: Active")
        else:
            st.warning("⚠️ Alpha Vantage: Mock Mode")

def render_conversation_history(conversation_history: List[Dict[str, Any]]):
    """Display formatted conversation history with Phase 3 enhancements"""
    
    print(f"DEBUG: Rendering conversation history with {len(conversation_history)} entries")
    
    if not conversation_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            🚀 Welcome: Multi-Agent Finance Assistant!<br>
            Ask me any financial question and I'll route it to the best agent.<br>
            Try questions about portfolios, market data, or financial planning.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display messages
    for i, message in enumerate(conversation_history):
        print(f"DEBUG: Rendering message {i+1}: User='{message.get('user', 'N/A')[:50]}', Agent='{message.get('agent', 'N/A')}'")
        render_message(message)

def render_message(message: Dict[str, Any]):
    """Render individual message with proper formatting and Phase 3 enhancements"""
    
    # User message
    with st.chat_message("user"):
        st.write(message.get("user", message.get("user_query", "")))
    
    # Assistant message with enhanced metadata
    with st.chat_message("assistant"):
        assistant_response = message.get("assistant", "")
        st.write(assistant_response)
        
        # Phase 3 enhanced metadata display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Show which agent responded
            agent_name = message.get("agent", message.get("agent_name", "assistant"))
            agent_display = {
                "finance_qa": "💬 Finance Q&A",
                "portfolio_analysis": "📊 Portfolio",
                "market_analysis": "📈 Market",
                "goal_planning": "🎯 Goals",
                "finance_qa_agent": "💬 Finance Q&A"
            }.get(agent_name, f"🤖 {agent_name}")
            
            st.markdown(f"**Agent**: {agent_display}")
        
        with col2:
            # Show confidence score
            if message.get("confidence") is not None:
                confidence = message["confidence"]
                if confidence >= 0.8:
                    confidence_class = "confidence-high"
                    confidence_text = "High"
                elif confidence >= 0.6:
                    confidence_class = "confidence-medium"
                    confidence_text = "Medium"
                else:
                    confidence_class = "confidence-low"
                    confidence_text = "Low"
                
                st.markdown(f'<span class="confidence-score {confidence_class}">Confidence: {confidence_text}</span>', unsafe_allow_html=True)
        
        with col3:
            # Show source count
            source_count = len(message.get("sources", []))
            st.markdown(f"📚 **Sources**: {source_count}")
        
        with col4:
            # Show routing info if next_agent is suggested
            if message.get("next_agent"):
                st.markdown(f"➡️ **Next**: {message['next_agent']}")
        
        # Show sources if available
        if message.get("sources"):
            with st.expander(f"📖 View {len(message['sources'])} Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f'<div class="source-citation">{i}. {source}</div>', unsafe_allow_html=True)

def render_chat_input(workflow, session_state: Dict[str, Any]):
    """Render chat input area with send functionality"""
    
    # Chat input
    user_input = st.chat_input("Ask me anything about finance, investing, or retirement planning...")
    
    # Process input from chat
    if user_input:
        process_user_input(user_input, workflow, session_state)

def process_user_input(user_input: str, workflow, session_state: Dict[str, Any]):
    """Process user input using Phase 3 multi-agent workflow"""
    
    # Prevent duplicate processing of the same input
    last_processed = session_state.get("last_processed_input")
    if last_processed == user_input:
        print(f"DEBUG: Skipping duplicate processing of: '{user_input}'")
        return
    
    session_state["last_processed_input"] = user_input
    
    print(f"DEBUG: Processing user input with Phase 3 workflow: '{user_input}'")
    print(f"DEBUG: Workflow available: {workflow is not None}")
    print(f"DEBUG: Session state keys: {list(session_state.keys())}")
    print(f"DEBUG: Portfolio data in session state: {session_state.get('portfolio_data')}")
    if workflow:
        print(f"DEBUG: Workflow has {len(workflow.agents)} agents: {list(workflow.agents.keys())}")
    
    conversation_entry = {
        "user": user_input,
        "assistant": "Processing your question...",
        "sources": [],
        "confidence": 0.0,
        "agent": "processing",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if workflow:
            print("DEBUG: Using LangGraph workflow for processing")
            
            # Use the workflow to process the query
            result = workflow.run(user_input, session_state)
            print(f"DEBUG: Workflow response keys: {list(result.keys())}")
            
            # Update conversation entry with workflow result
            conversation_entry.update({
                "assistant": result.get("response", "No response generated"),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.0),
                "agent": result.get("agent", "unknown"),
                "next_agent": result.get("next_agent")
            })
            
            # Update session state with any changes from workflow
            updated_state = result.get("updated_state", {})
            for key in ["portfolio_data", "market_context", "investment_goals", "user_profile"]:
                if key in updated_state:
                    session_state[key] = updated_state[key]
            
            print("DEBUG: Workflow response processed successfully")
        else:
            print("DEBUG: Workflow not available, using fallback")
            # Fallback to single agent mode
            agent = session_state.get("finance_qa_agent")
            if agent:
                state = {
                    "user_query": user_input,
                    "conversation_history": session_state.get("conversation_history", [])
                }
                response = agent.execute(state)
                conversation_entry.update({
                    "assistant": response["agent_response"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.0),
                    "agent": response.get("agent_name", "finance_qa"),
                    "next_agent": response.get("next_agent")
                })
            else:
                conversation_entry["assistant"] = "Sorry, the system is not available right now. Please try refreshing the page."
            
    except Exception as e:
        print(f"DEBUG: Exception in process_user_input: {e}")
        logger.error(f"Error processing user input: {e}")
        conversation_entry.update({
            "assistant": f"Error processing question: {str(e)}",
            "agent": "error",
            "confidence": 0.0
        })
    
    print("DEBUG: Adding conversation entry to history")
    # Update conversation history
    if "conversation_history" not in session_state:
        session_state["conversation_history"] = []
    
    # Check if this entry already exists to prevent duplicates
    existing_entries = [entry for entry in session_state["conversation_history"] 
                       if entry.get("user") == user_input and entry.get("timestamp")]
    
    if not existing_entries:
        session_state["conversation_history"].append(conversation_entry)
        print(f"DEBUG: Added new conversation entry. History now has {len(session_state['conversation_history'])} entries")
    else:
        print(f"DEBUG: Conversation entry already exists, skipping duplicate. History has {len(session_state['conversation_history'])} entries")
    
    st.rerun()

def render_agent_testing_buttons(workflow, session_state: Dict[str, Any]):
    """Render buttons to test different agent routing"""
    
    st.markdown("#### 🧪 Test Agent Routing")
    st.markdown("Try these questions to test the multi-agent routing system:")
    
    # Create test questions for each agent
    test_questions = {
        "Finance Q&A": [
            "What is diversification and why is it important?",
            "Explain compound interest with examples",
            "How do ETFs work?"
        ],
        "Portfolio": [
            "Analyze my portfolio allocation",
            "How should I diversify my holdings?", 
            "What's my portfolio risk level?"
        ],
        "Market": [
            "What's the current market trend?",
            "How is Apple stock performing?",
            "Show me S&P 500 data"
        ],
        "Goals": [
            "Help me plan for retirement",
            "Set a savings goal for a house",
            "Create an emergency fund plan"
        ]
    }
    
    # Create columns for test buttons
    cols = st.columns(4)
    
    for i, (category, questions) in enumerate(test_questions.items()):
        with cols[i]:
            st.markdown(f"**{category}**")
            for question in questions:
                if st.button(question, key=f"test_{category}_{question[:20]}", use_container_width=True):
                    process_user_input(question, workflow, session_state)
                    break  # Only process one at a time

def render_quick_actions(workflow, session_state: Dict[str, Any]):
    """Render quick action buttons for common financial questions"""
    
    st.markdown("### 🎯 Sample Questions")
    sample_questions = [
        "What is diversification and why is it important?",
        "Explain compound interest with examples",
        "How do I start investing as a beginner?",
        "What's the difference between ETFs and mutual funds?",
        "How should I plan for retirement?",
        "What is dollar-cost averaging?"
    ]
    
    # Create columns for buttons
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        col = cols[i % 2]
        with col:
            if st.button(question, key=f"quick_action_{i}", use_container_width=True):
                process_user_input(question, workflow, session_state)