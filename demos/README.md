# AI Finance Assistant Demos

This folder contains demonstration scripts showcasing different features and capabilities of the AI Finance Assistant.

## Demo Scripts

### 🤖 `demo_simple_qa.py`
**Basic Finance Q&A Agent Demo**

Demonstrates the fundamental Finance Q&A Agent functionality:
- Simple financial question processing
- Basic response formatting
- Error handling
- Source attribution (when RAG is available)

**Usage:**
```bash
python demos/demo_simple_qa.py
```

**Features Demonstrated:**
- Agent initialization
- Basic query processing
- Mock LLM integration
- State management

---

### 🔍 `demo_rag_agent.py`
**RAG Integration Example**

Shows how to use the FAISS vector database with finance agents for enhanced knowledge retrieval.

**Usage:**
```bash
python demos/demo_rag_agent.py
```

**Features Demonstrated:**
- Vector store integration
- Document retrieval
- RAG-enhanced responses
- Knowledge base querying

---

### 📊 `demo_agent_patterns.py`
**Market Agent Integration Patterns**

Demonstrates different integration patterns for the Market Analysis Agent, comparing direct integration vs. tool calling approaches.

**Usage:**
```bash
python demos/demo_agent_patterns.py
```

**Features Demonstrated:**
- Enhanced Market Analysis Agent
- Direct integration pattern
- Tool calling pattern
- Market data provider integration

---

### 🛠️ `demo_tools.py`
**Individual Tool Demonstration**

Shows how Alpha Vantage tools work independently of agents, demonstrating the underlying tool functionality.

**Usage:**
```bash
python demos/demo_tools.py
```

**Features Demonstrated:**
- Alpha Vantage quote tool
- Market overview tool
- Symbol search tool
- Independent tool execution

## Running Demos

### Prerequisites

1. **Environment Setup:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Required API Keys:**
   - `OPENAI_API_KEY` - For LLM functionality
   - `ALPHA_VANTAGE_API_KEY` - For market data (some demos)

### Execution

All demos can be run from the project root directory:

```bash
# Run individual demos
python demos/demo_simple_qa.py
python demos/demo_rag_agent.py
python demos/demo_agent_patterns.py
python demos/demo_tools.py
```

### Expected Output

Each demo will show:
- ✅ Initialization confirmations
- 🔍 Processing demonstrations
- 📊 Results and responses
- ❌ Error handling examples

## Demo Categories

### **Basic Functionality**
- `demo_simple_qa.py` - Core agent functionality

### **Advanced Features**
- `demo_rag_agent.py` - Knowledge retrieval
- `demo_agent_patterns.py` - Integration patterns

### **Component Testing**
- `demo_tools.py` - Individual tool functionality

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **API Key Errors**: Check that your `.env` file contains valid API keys
3. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Debug Mode

Some demos support verbose output for debugging:
```bash
# Add debug output (if supported by the demo)
python demos/demo_simple_qa.py --verbose
```

## Educational Value

These demos are designed to:
- **Show practical usage** of each component
- **Demonstrate best practices** for integration
- **Provide learning examples** for new developers
- **Validate functionality** during development

## Contributing

When adding new demos:
1. Place them in the `demos/` folder
2. Use consistent import patterns
3. Include clear documentation
4. Add error handling examples
5. Update this README

---

**Note:** These demos are for educational and testing purposes. For production usage, refer to the main Streamlit application in `src/web_app/`.
