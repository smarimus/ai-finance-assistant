# 🚀 AI Finance Assistant - Setup Guide

This guide ensures you can replicate the working environment anywhere.

## 📋 Prerequisites

- **Python 3.9.6+** (tested and working with 3.9.6)
- **Poetry** (optional but recommended)
- **Git**

## 🛠️ Setup Options

### Option 1: Poetry Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/smarimus/ai-finance-assistant.git
cd ai-finance-assistant

# 2. Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Create and activate virtual environment
poetry env use python3.9
poetry shell

# 4. Install dependencies
poetry install

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY=your_openai_api_key_here
# - ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### Option 2: pip + venv Setup (Alternative)

```bash
# 1. Clone the repository
git clone https://github.com/smarimus/ai-finance-assistant.git
cd ai-finance-assistant

# 2. Create virtual environment
python3.9 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

### Required API Keys

1. **OpenAI API Key** (for LLM functionality)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

2. **Alpha Vantage API Key** (for market data)
   - Get from: https://www.alphavantage.co/support/#api-key
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

### Optional Configuration

Edit `config.yaml` for custom settings:
- Model preferences
- Market data sources
- RAG settings

## 🚀 Running the Application

### Start Streamlit App
```bash
# Make sure virtual environment is activated
# Poetry:
poetry shell

# Or venv:
source .venv/bin/activate

# Run the application
streamlit run streamlit_app.py
```

The app will be available at: http://localhost:8501

## ✅ Verify Installation

### 1. Test Core Functionality
```bash
# Run basic tests
python -m pytest tests/ -v

# Or using poetry
poetry run pytest tests/ -v
```

### 2. Test Agent Routing
```bash
# Run the routing test
python test_routing_fix.py
```

Expected output: All routing tests should pass (18/18).

### 3. Test in Browser
1. Open http://localhost:8501
2. Try these test queries:
   - "How do ETFs work?" → Should route to **finance_qa** agent
   - "Analyze my portfolio allocation" → Should route to **portfolio_analysis** agent
   - "What's the current market trend?" → Should route to **market_analysis** agent
   - "Help me plan for retirement" → Should route to **goal_planning** agent

## 🧪 Known Working Versions

This project is tested and working with these exact versions:

### Core AI Stack
- `langchain==0.1.20`
- `openai==1.99.9`
- `streamlit==1.48.1`
- `faiss-cpu==1.12.0`
- `sentence-transformers==2.7.0`

### Python Environment
- **Python**: 3.9.6
- **OS**: macOS (also works on Linux/Windows)

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure virtual environment is activated
poetry shell  # or source .venv/bin/activate

# Reinstall dependencies
poetry install  # or pip install -r requirements.txt
```

**2. OpenAI API Errors**
- Check your API key in `.env`
- Verify you have credits in your OpenAI account
- Test with: `python -c "import openai; print('OpenAI OK')"`

**3. Vector Store Issues**
```bash
# The app will fallback to mock retriever if vector store fails
# Check logs for: "Using mock retriever"
```

**4. Market Data Issues**
- Verify Alpha Vantage API key
- Check rate limits (5 API calls per minute for free tier)

**5. Port Already in Use**
```bash
# If port 8501 is busy, use different port:
streamlit run streamlit_app.py --server.port 8502
```

### Performance Tips

1. **For Apple Silicon Macs**: The app uses MPS (Metal Performance Shaders) for embeddings
2. **For CUDA GPUs**: PyTorch will automatically use CUDA if available
3. **Memory**: Ensure at least 4GB RAM available for sentence transformers

## 📁 Project Structure

```
ai_finance_assistant/
├── src/
│   ├── agents/          # AI agents (finance_qa, portfolio, market, goals)
│   ├── core/           # Workflow and state management
│   ├── rag/            # RAG system and vector store
│   ├── data/           # Market data providers
│   ├── utils/          # Utilities and calculations
│   └── web_app/        # Streamlit interface
├── tests/              # Test suite
├── docs/               # Documentation
├── requirements.txt    # pip dependencies
├── pyproject.toml     # Poetry dependencies
├── streamlit_app.py   # Main application entry point
└── .env.example       # Environment variables template
```

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: The app shows debug information in the terminal
2. **Test routing**: Run `python test_routing_fix.py`
3. **Verify dependencies**: Compare your installed versions with `requirements.txt`
4. **API keys**: Ensure all required API keys are set correctly

## 🎯 Success Indicators

You'll know the setup is working when:

- ✅ Streamlit app loads without errors
- ✅ All 4 agents are loaded (finance_qa, portfolio_analysis, market_analysis, goal_planning)
- ✅ Questions route to the correct agents
- ✅ OpenAI LLM shows as "Active" in the interface
- ✅ No error messages in the terminal logs

---

**Last Updated**: September 2025  
**Status**: All flows working, routing fixes applied, dependencies synchronized
