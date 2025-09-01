# Testing Strategy for AI Finance Assistant

## Overview
This document outlines the testing approach for each component of the AI Finance Assistant.

## Test Structure
```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── test_agents/
│   ├── __init__.py
│   ├── test_base_agent.py
│   ├── test_finance_qa_agent.py
│   ├── test_portfolio_agent.py
│   ├── test_market_agent.py
│   └── test_goal_agent.py
├── test_core/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_state.py
│   └── test_workflow.py
├── test_rag/
│   ├── __init__.py
│   ├── test_vector_store.py
│   └── test_retriever.py
├── test_utils/
│   ├── __init__.py
│   ├── test_portfolio_calc.py
│   └── test_helpers.py
├── test_data/
│   ├── __init__.py
│   └── test_market_data.py
└── test_web_app/
    ├── __init__.py
    └── test_streamlit_app.py
```

## Testing Levels

### 1. Unit Tests
- Test individual functions and methods
- Mock external dependencies (APIs, LLMs)
- Fast execution

### 2. Integration Tests
- Test component interactions
- Use test databases and mock services
- Validate data flow between components

### 3. End-to-End Tests
- Test complete user workflows
- Use test environment with real-like data
- Validate UI interactions

## Test Data Requirements
- Sample portfolio data
- Mock API responses
- Test financial documents for RAG
- Sample user queries and expected responses

## Running Tests
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_agents/

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```
