#!/usr/bin/env python3
"""
Quick setup test script to verify the AI Finance Assistant is working correctly.
Run this script to test core functionality without needing API keys.
"""

def test_imports():
    """Test that all core modules can be imported successfully."""
    print("🔍 Testing imports...")
    
    try:
        from src.agents.base_agent import BaseFinanceAgent
        print("✅ Base agent import successful")
        
        from src.agents.finance_qa_agent import FinanceQAAgent
        print("✅ Finance QA agent import successful")
        
        from src.agents.portfolio_agent import PortfolioAnalysisAgent
        print("✅ Portfolio agent import successful")
        
        from src.agents.market_agent import MarketAnalysisAgent
        print("✅ Market agent import successful")
        
        from src.agents.goal_agent import GoalPlanningAgent
        print("✅ Goal agent import successful")
        
        from src.core.config import AppConfig, APIConfig
        print("✅ Configuration classes import successful")
        
        from src.core.state import FinanceAssistantState
        print("✅ State management import successful")
        
        from src.rag.vector_store import FinanceVectorStore
        print("✅ Vector store import successful")
        
        from src.utils.portfolio_calc import FinancialCalculator
        print("✅ Financial calculator import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dependencies():
    """Test that key dependencies are installed and accessible."""
    print("\n🔍 Testing dependencies...")
    
    try:
        import langchain
        print(f"✅ LangChain: {langchain.__version__}")
        
        import langgraph
        print(f"✅ LangGraph: {langgraph.__version__}")
        
        import openai
        print(f"✅ OpenAI: {openai.__version__}")
        
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
        
        import pandas
        print(f"✅ Pandas: {pandas.__version__}")
        
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
        
        import faiss
        print(f"✅ FAISS: {faiss.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Dependency error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from src.utils.portfolio_calc import FinancialCalculator
        
        # Test financial calculations
        calc = FinancialCalculator()
        
        # Test future value calculation
        result = calc.future_value(present_value=1000, rate=0.07, periods=10)
        print(f"✅ Future value calculation: ${result:.2f}")
        
        # Test monthly savings calculation
        monthly_savings = calc.monthly_savings_required(goal_amount=50000, rate=0.07, years=10)
        print(f"✅ Monthly savings calculation: ${monthly_savings:.2f}")
        
        # Test basic portfolio metrics
        portfolio_data = {
            'AAPL': {'shares': 10, 'price': 150.0},
            'MSFT': {'shares': 5, 'price': 300.0}
        }
        
        total_value = sum(stock['shares'] * stock['price'] for stock in portfolio_data.values())
        print(f"✅ Portfolio value calculation: ${total_value:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🚀 AI Finance Assistant - Setup Test")
    print("="*50)
    
    tests = [
        test_imports,
        test_dependencies,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: poetry run streamlit run src/web_app/main.py")
        print("3. Or run specific agents with: poetry run python -m src.agents.finance_qa_agent")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    main()
