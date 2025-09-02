# Test Organization Guide

This document describes the organized test structure for the AI Finance Assistant project. All tests have been reorganized into logical categories for better maintainability and clarity.

## Test Directory Structure

```
tests/
├── test_agents/          # Unit tests for agents
├── test_core/           # Unit tests for core components  
├── test_utils/          # Unit tests for utilities
├── integration/         # Integration tests
├── phase_tests/         # Development phase tests
├── performance/         # Performance tests
└── conftest.py         # Shared test configuration
```

## Directory Descriptions

### 🤖 `test_agents/`
Unit tests for individual AI agents and their functionality.

**Contents:**
- `test_finance_qa_agent.py` - Tests for the Finance Q&A agent
- `test_portfolio_agent.py` - Tests for the Portfolio Analysis agent

**Purpose:** Verify that each agent works correctly in isolation, including:
- Agent initialization
- Query processing
- Response generation
- Error handling

### ⚙️ `test_core/`
Unit tests for core system components and workflow orchestration.

**Contents:**
- `test_workflow.py` - Tests for the main workflow orchestrator

**Purpose:** Ensure core system functionality works correctly:
- Workflow initialization
- Query routing logic
- Agent coordination
- Error handling workflows

### 🛠️ `test_utils/`
Unit tests for utility functions and helper modules.

**Contents:**
- `test_portfolio_calc.py` - Tests for portfolio calculation utilities

**Purpose:** Verify utility functions work correctly:
- Financial calculations
- Data processing helpers
- Mathematical computations

### 🔗 `integration/`
Integration tests that verify components work together correctly.

**Contents:**
- `test_rag_integration.py` - RAG (Retrieval-Augmented Generation) integration tests
- `test_goals_api_isolation.py` - API isolation tests for Goals functionality
- `simple_goals_test.py` - Simple integration test for Goals features
- `test_extraction.py` - Data extraction integration tests

**Purpose:** Test system integration points:
- Multi-component workflows
- External API interactions
- Data flow between modules
- End-to-end functionality

### 📋 `phase_tests/`
Development phase tests that validate specific implementation milestones.

**Contents:**
- `test_phase4.py` - Phase 4 portfolio analysis tests
- `test_phase4_final.py` - Final Phase 4 validation tests
- `test_phase4_simple.py` - Simplified Phase 4 tests
- `test_phase5_market.py` - Phase 5 market dashboard tests
- `test_phase6_complete.py` - Phase 6 complete system tests
- `test_phase6_goals.py` - Phase 6 goal planning tests
- `test_phase6_verification.py` - Phase 6 verification tests

**Purpose:** Validate development milestones:
- Feature completeness for each phase
- Integration of new capabilities
- Regression testing for existing features

### ⚡ `performance/`
Performance and optimization tests.

**Contents:**
- `test_goals_performance.py` - Performance tests for Goals functionality

**Purpose:** Ensure system performance meets requirements:
- Load time optimization
- Memory usage validation
- API response time testing
- Resource utilization monitoring

## Running Tests

### Using the Centralized Test Runner

The project includes a centralized test runner (`run_tests.py`) for organized test execution:

```bash
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py unit          # test_agents/, test_core/, test_utils/
python run_tests.py integration   # integration/
python run_tests.py phase         # phase_tests/
python run_tests.py performance   # performance/

# Run with verbose output
python run_tests.py unit -v
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/

# Run specific categories
pytest tests/test_agents/
pytest tests/integration/
pytest tests/phase_tests/
pytest tests/performance/

# Run specific test files
pytest tests/test_agents/test_portfolio_agent.py -v
pytest tests/integration/test_rag_integration.py -v
```

## Test Configuration

### `conftest.py`
Contains shared test configuration and fixtures used across all test files:

- **Mock objects**: Pre-configured mocks for external dependencies
- **Test fixtures**: Reusable test data and setup
- **Helper functions**: Common test utilities
- **Test environment setup**: Standardized test environment configuration

### Import Path Setup

All test files use a consistent import path setup to access the source modules:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now you can import from src
from src.agents.portfolio_agent import PortfolioAnalysisAgent
from src.utils.portfolio_calc import PortfolioCalculator
```

## Best Practices

### When Adding New Tests

1. **Choose the right category**:
   - Unit tests → `test_agents/`, `test_core/`, or `test_utils/`
   - Integration tests → `integration/`
   - Feature milestone tests → `phase_tests/`
   - Performance tests → `performance/`

2. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Test classes: `Test*`

3. **Use shared fixtures**: Leverage fixtures in `conftest.py` for common setup

4. **Import path consistency**: Use the standard import path setup shown above

### Test Organization Guidelines

- **Keep tests focused**: Each test should verify one specific behavior
- **Use descriptive names**: Test names should clearly indicate what they're testing
- **Maintain independence**: Tests should not depend on each other
- **Mock external dependencies**: Use mocks for APIs, databases, and external services

## Coverage and Quality

The test suite includes coverage reporting to ensure comprehensive testing:

- Coverage reports are generated automatically during test runs
- HTML coverage reports are available in `htmlcov/`
- Aim for high coverage of critical business logic

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the import path setup is correct in your test file
2. **Missing fixtures**: Check if required fixtures are defined in `conftest.py`
3. **Test isolation**: Make sure tests don't interfere with each other

### Getting Help

- Check existing test files for examples
- Review `conftest.py` for available fixtures
- Use `pytest --fixtures` to see all available fixtures
- Run `python run_tests.py --help` for test runner options

---

This organized test structure ensures maintainable, comprehensive testing of the AI Finance Assistant while supporting efficient development workflows and high code quality.
