# 🏗️ Core Workflow Implementation Guide

## 📁 **Core Module Overview**

The `src/core/` module contains the workflow orchestration system for the AI Finance Assistant, implementing multi-agent routing and state management.

```
src/core/
├── state.py              # ✅ State schema definitions with TypedDict
├── workflow_v2.py        # ✅ PRIMARY - LangGraph with dict state
├── simple_workflow.py    # ✅ FALLBACK - Custom implementation
├── workflow.py           # ⚠️ ABANDONED - TypedDict compatibility issues
└── README.md            # 📖 This documentation
```

## 🎯 **Current Workflow Implementation Priority**

### **Primary Implementation: `workflow_v2.py`** ✅ **PREFERRED**
- **File**: `src/core/workflow_v2.py`
- **Class**: `FinanceAssistantWorkflowV2`
- **Type**: LangGraph implementation with simple dictionary state
- **Features**:
  - Full LangGraph workflow orchestration
  - Dictionary-based state management (avoids TypedDict issues)
  - Complete agent routing and execution
  - Error handling and fallback mechanisms
- **Status**: **Active** - Tried first in application startup

### **Fallback Implementation: `simple_workflow.py`** ✅ **BACKUP**
- **File**: `src/core/simple_workflow.py`
- **Class**: `SimpleFinanceWorkflow`
- **Type**: Custom implementation without LangGraph dependencies
- **Features**:
  - Rule-based query routing via keyword matching
  - Simple agent execution and state management
  - Fast and reliable (no external graph dependencies)
  - Comprehensive error handling
- **Status**: **Active** - Used if workflow_v2 fails

### **Abandoned Implementation: `workflow.py`** ⚠️ **NOT USED**
- **File**: `src/core/workflow.py`
- **Class**: `FinanceAssistantWorkflow`
- **Type**: LangGraph with TypedDict state schema
- **Issues**: TypedDict compatibility problems with LangGraph
- **Status**: **Abandoned** - Kept for reference only

## 🔄 **Workflow Selection Logic**

The application uses a **cascading fallback system** in `src/web_app/main.py`:

```python
def load_workflow(self):
    """Initialize workflow with intelligent fallback system"""
    
    # Step 1: Try LangGraph implementation (preferred)
    try:
        from src.core.workflow_v2 import FinanceAssistantWorkflowV2
        workflow = FinanceAssistantWorkflowV2(agents)
        print("✅ FinanceAssistantWorkflowV2 (LangGraph) created")
        return workflow
    except Exception as e:
        print(f"Workflow V2 failed: {e}")
        
        # Step 2: Fallback to simple implementation
        try:
            from src.core.simple_workflow import SimpleFinanceWorkflow
            workflow = SimpleFinanceWorkflow(agents)
            print("✅ SimpleFinanceWorkflow created as fallback")
            return workflow
        except Exception as e2:
            print(f"All workflow implementations failed: {e2}")
            return None
```

## 🎯 **Query Routing Implementation**

### **Current Approach: Rule-Based Keyword Matching**
Both active workflows use **keyword-based pattern matching** for intent classification:

- **No LLM calls** in routing decision (fast & cost-efficient)
- **String matching** against predefined keyword lists
- **Fallback logic** to Finance Q&A when specialized agents unavailable

#### **Routing Categories:**
```python
# Portfolio queries
Keywords: "portfolio", "allocation", "diversification", "holdings", "rebalance"

# Market queries  
Keywords: "market", "stock price", "ticker", "nasdaq", "s&p", "AAPL", "MSFT"

# Goal queries
Keywords: "retirement", "save", "plan", "target", "emergency fund"

# Default: Finance Q&A for educational content
```

### **Future Enhancement Options:**
- **LLM-Based Intent Classification**: Use OpenAI for semantic intent understanding
- **Few-Shot Prompting**: Train classifier with examples for better accuracy
- **Hybrid Approach**: Combine keyword matching with LLM fallback for edge cases
- **Confidence Scoring**: Add routing confidence metrics for better agent handoffs

## 🏗️ **State Management**

### **State Schema (`state.py`)**
Defines comprehensive state structure using TypedDict:

```python
class FinanceAssistantState(TypedDict, total=False):
    # Required fields
    user_query: str
    conversation_history: List[Dict[str, Any]]
    
    # Agent management
    current_agent: Optional[str]
    agent_responses: List[Dict[str, Any]]
    rag_context: List[str]
    
    # Domain-specific data
    portfolio_data: Optional[Dict[str, Any]]
    market_context: Optional[Dict[str, Any]]
    investment_goals: List[Dict[str, Any]]
    
    # Session management
    session_id: str
    timestamp: datetime
    error_context: Optional[Dict[str, Any]]
```

### **State Handling Differences:**

#### **workflow_v2.py**: Dictionary State
- Uses simple `Dict[str, Any]` for LangGraph compatibility
- Avoids TypedDict serialization issues
- Maintains all state fields dynamically

#### **simple_workflow.py**: Direct State Passing
- Passes state dictionary directly between methods
- No LangGraph state management overhead
- Simple and reliable state handling

## 🚀 **Agent Integration**

### **Supported Agents:**
- **`finance_qa`**: ✅ **FULLY ACTIVE** - LLM + RAG for educational content
- **`portfolio_analysis`**: ✅ **MOCK READY** - Placeholder for Phase 4
- **`market_analysis`**: ✅ **FULLY ACTIVE** - Alpha Vantage integration
- **`goal_planning`**: ✅ **MOCK READY** - Placeholder for Phase 6

### **Agent Execution Pattern:**
```python
# Common pattern across both workflows
def execute_agent(self, agent_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    agent = self.agents.get(agent_name)
    result = agent.execute(state)
    return {
        "agent_response": result.get("agent_response"),
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", 0.0),
        "next_agent": result.get("next_agent")
    }
```

## 🔧 **Development Guidelines**

### **Adding New Workflow Features:**
1. **Primary**: Add to `workflow_v2.py` first (LangGraph implementation)
2. **Fallback**: Add equivalent feature to `simple_workflow.py` 
3. **State**: Update `state.py` if new state fields needed
4. **Testing**: Ensure both workflows handle the feature gracefully

### **Debugging Workflow Issues:**
- Check console logs for workflow selection messages
- Both workflows include comprehensive debug output
- State persistence maintained across tab switches
- Error context preserved for troubleshooting

### **Performance Considerations:**
- **Workflow Loading**: Done once per session (cached in `st.session_state`)
- **Agent Creation**: Agents created once and reused
- **State Management**: Efficient state passing without recreation
- **Routing Speed**: Keyword matching provides sub-millisecond routing

## 📊 **Workflow Comparison**

| Feature | workflow_v2.py | simple_workflow.py | workflow.py |
|---------|----------------|-------------------|-------------|
| **LangGraph Integration** | ✅ Yes | ❌ No | ✅ Yes |
| **State Management** | Dict-based | Direct passing | TypedDict |
| **Compatibility** | ✅ Stable | ✅ Stable | ⚠️ Issues |
| **Performance** | Good | Excellent | Unknown |
| **Complexity** | Medium | Low | High |
| **Debugging** | Good | Excellent | Difficult |
| **Status** | **Active** | **Fallback** | **Abandoned** |

## 🎯 **Recommended Usage**

### **For Development:**
- Use **workflow_v2.py** for new features requiring LangGraph capabilities
- Use **simple_workflow.py** for simple routing and execution needs
- Keep both implementations in sync for feature parity

### **For Production:**
- Current cascading fallback system ensures reliability
- Monitor logs to see which implementation is being used
- Both workflows provide equivalent functionality for users

### **For Future Enhancements:**
- **LLM-based routing**: Add to both workflows
- **Complex agent orchestration**: Enhance workflow_v2.py first
- **Performance optimizations**: Focus on simple_workflow.py

---

This documentation provides a comprehensive guide to the core workflow implementations and their usage patterns in the AI Finance Assistant.
