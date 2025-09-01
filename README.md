# AI Finance Assistant

A comprehensive AI-powered finance assistant with intelligent agents, knowledge base scraping, and web interface for financial analysis and education.

## 🚀 Features

### 📚 Knowledge Base & Vector Database
- **Professional Content Sources**: Scrapes high-quality financial education content from multiple sources
- **41+ Articles**: Currently contains 77,283+ words of professional financial content
- **Comprehensive Topics**: Covers retirement planning (401k, IRA), personal finance, stocks, crypto, and investment strategies
- **FAISS Vector Database**: Semantic search with embeddings for intelligent information retrieval
- **AI-Ready Format**: Clean JSON structure and vector embeddings perfect for LLM training and RAG systems

### 🤖 AI Agents (Planned)
- **Portfolio Agent**: Portfolio analysis and optimization
- **Market Agent**: Market data analysis and insights  
- **Goal Agent**: Financial planning and goal tracking
- **Finance QA Agent**: General financial question answering
- **Base Agent**: Core agent functionality

### 🌐 Web Interface (Planned)
- **Chat Interface**: Natural language financial conversations
- **Portfolio Dashboard**: Visual portfolio management
- **Market Analysis**: Real-time market insights
- **Goal Tracking**: Financial goal monitoring

## 📁 Project Structure

```
├── src/
│   ├── agents/              # AI agent implementations
│   ├── core/               # Core system components
│   ├── data/               # Data management and scraping
│   │   ├── financial_scraper.py    # Main scraper
│   │   └── knowledge_base/         # Scraped content (77K+ words)
│   ├── rag/                # RAG system with FAISS vector store
│   │   ├── vector_store.py         # FAISS vector database
│   │   ├── retriever.py           # Intelligent retrieval system
│   │   └── embeddings.py          # Embedding utilities
│   ├── utils/              # Utility functions
│   └── web_app/            # Streamlit web interface
├── scripts/                # Organized project scripts
│   ├── scrapers/           # Knowledge base scraping
│   ├── vector_db/          # FAISS vector database tools
│   └── utils/              # Testing and utilities
├── tests/                  # Test suite
├── main.py                 # Main entry point for all scripts
├── run_scraper.py         # Convenience: Start scraping
├── build_vector_db.py     # Convenience: Build vector database
└── check_progress.py      # Convenience: Monitor progress
```

## 🔧 Quick Start

### 1. Knowledge Base & Vector Database Setup

Build your financial knowledge base and create a searchable vector database:

```bash
# Option 1: Use main entry point (recommended)
python main.py scrape           # Build knowledge base
python main.py scrape-retirement # Add retirement content (401k, IRA)
python main.py scrape-personal  # Add personal finance content  
python main.py build-db         # Build FAISS vector database  
python main.py test-db          # Test functionality

# Option 2: Use convenience scripts
python run_scraper.py          # Build knowledge base
python build_vector_db.py      # Build vector database
python check_progress.py       # Monitor progress

# Option 3: Direct script access
python scripts/scrapers/run_scraper.py
python scripts/scrapers/retirement_scraper.py
python scripts/scrapers/common_finance_scraper.py
python scripts/vector_db/build_vector_db.py
python scripts/utils/check_progress.py
```

This will create:
- **Knowledge Base**: 41+ high-quality articles (77,283+ words)
- **Vector Database**: FAISS index for semantic search
- **Topics**: Retirement planning (401k, IRA), personal finance, investing, crypto

### 2. Using the Vector Database

```python
from src.rag.vector_store import FinanceVectorStore
from src.rag.retriever import FinanceRetriever

# Load vector database
vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
retriever = FinanceRetriever(vector_store)

# Search for information
results = retriever.retrieve("401k retirement planning", k=5)

# Build context for AI
context = retriever.build_context("What is a 401k?", results)
```

### 3. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (required for embeddings)
export OPENAI_API_KEY='your-openai-api-key'

# Or create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4. Run Tests

```bash
# Run all tests
python main.py test

# Or use convenience script
python scripts/utils/run_tests.py
```

## 🎯 Quick Commands

| Task | Command |
|------|---------|
| Show all commands | `python main.py help` |
| Build knowledge base | `python main.py scrape` |
| Create vector database | `python main.py build-db` |
| Test everything | `python main.py test-db` |
| Check progress | `python main.py progress` |
| Interactive examples | `python main.py db-examples` |
| Run all tests | `python main.py test` |

## 📊 Current Knowledge Base Content

### Updated Statistics:
- **📄 Total Articles**: 41 (up from 25)
- **📝 Total Words**: 77,283 (up from 39,218)
- **🏦 Retirement Planning**: 7 articles covering 401k, IRA, Social Security
- **💰 Personal Finance**: 8 articles covering credit, budgeting, insurance
- **📈 Investment & Analysis**: 26 articles covering stocks, crypto, financial analysis

### Key Topics Available:
- **401(k) Plans**: Complete guide with 3,355 words
- **IRA Accounts**: Traditional vs Roth comparison (2,155 words)
- **Credit Management**: Credit scores and reports (2,432 words)
- **Emergency Funds**: Building financial safety nets (1,151 words)
- **Stock Analysis**: Valuation methods and financial ratios
- **Cryptocurrency**: Bitcoin, tokens, and ICO education
- **Insurance**: Life, homeowners, and financial protection

### Content Categories:
- **Retirement Planning**: 7 articles (13,933 words)
- **Personal Finance**: 7 articles (14,699 words)  
- **Education**: 26 articles (48,086 words)
- **General**: 1 article (565 words)

## 🛠️ Development

### Vector Database Usage

```python
# Basic search
from src.rag.vector_store import FinanceVectorStore
from src.rag.retriever import FinanceRetriever

vector_store = FinanceVectorStore()
retriever = FinanceRetriever(vector_store)

# Get relevant documents
results = retriever.retrieve("retirement planning strategies", k=5)

# Category-specific search
retirement_docs = retriever.retrieve_by_category(
    "401k vs IRA", 
    category="retirement_planning", 
    k=3
)

# Build context for LLM
context = retriever.build_context(query, results)
```

### Knowledge Base Expansion

```python
from src.data.financial_scraper import InvestingKnowledgeBaseScraper

# Scrape more content
scraper = InvestingKnowledgeBaseScraper()
articles = scraper.scrape_knowledge_base(max_articles=50)

# Rebuild vector database
# python build_vector_db.py
```

### Agent Development (Coming Soon)

```python
from src.agents.portfolio_agent import PortfolioAgent

# Initialize portfolio agent
agent = PortfolioAgent()
analysis = agent.analyze_portfolio(portfolio_data)
```

## 📚 Knowledge Base Details

The financial knowledge base contains professional-grade content covering:

- **Stock Market Analysis**: Valuation methods, financial ratios, market analysis
- **Cryptocurrency Education**: Bitcoin, altcoins, ICOs, trading strategies
- **Financial Metrics**: ROI, ROIC, cash flow analysis, earnings quality
- **Trading Fundamentals**: Order types, risk management, technical analysis
- **Investment Strategy**: Portfolio management, sector analysis, growth stocks

All content is stored in structured JSON format, making it perfect for:
- RAG (Retrieval-Augmented Generation) systems
- LLM fine-tuning
- Financial chatbot training
- Educational applications

## 🔄 Roadmap

### Phase 1: Knowledge Base ✅
- [x] Financial content scraper
- [x] Professional content from Investing.com
- [x] 25+ articles with 39K+ words
- [x] Clean JSON structure

### Phase 2: AI Agents (In Progress)
- [ ] Portfolio analysis agent
- [ ] Market data agent  
- [ ] Financial QA agent
- [ ] Goal planning agent

### Phase 3: Web Interface (Planned)
- [ ] Streamlit dashboard
- [ ] Chat interface
- [ ] Portfolio management
- [ ] Real-time market data

### Phase 4: Advanced Features (Future)
- [ ] Multi-source knowledge base
- [ ] Advanced financial models
- [ ] API endpoints
- [ ] Mobile interface

## 🤝 Contributing

1. **Knowledge Base**: Help expand content sources and improve scraping
2. **AI Agents**: Develop specialized financial agents
3. **Web Interface**: Improve user experience and functionality
4. **Testing**: Add comprehensive test coverage

## 📄 License

This project is for educational and research purposes. Please respect the terms of service of content sources.

## 🔗 Related Documentation

- [Scraper Documentation](SCRAPER_README.md) - Detailed scraper usage
- [Setup Guide](SETUP.md) - Detailed setup instructions  
- [Testing Guide](TESTING.md) - Testing procedures

---

**Built with**: Python, LangChain, BeautifulSoup, Streamlit, and professional financial content sources.
