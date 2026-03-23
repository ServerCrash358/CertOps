# CertOps Test Suite

This directory contains comprehensive tests for CertOps components and the full pipeline.

## Test Structure

```
test/
├── cases/                    # Individual test cases
│   ├── test_ml_model.py      # ML model tests
│   ├── test_rl_agent.py      # RL agent tests
│   ├── test_simulator.py     # Simulator tests
│   ├── test_safety.py        # Safety verification tests
│   ├── test_certificate.py   # Certificate generation tests
│   ├── test_integration.py   # Integration tests
│   └── test_pipeline.py      # Full pipeline tests
├── utils.py                  # Test utilities
└── README.md                 # This file
```

## Running Tests

### Run All Tests

```bash
# From the test directory
cd test

# Run all test cases
python -m pytest cases/ -v

# Or run individual test files
python cases/test_ml_model.py
python cases/test_rl_agent.py
```

### Run Specific Test

```bash
# Run ML model tests
python cases/test_ml_model.py

# Run RL agent tests
python cases/test_rl_agent.py

# Run integration tests
python cases/test_integration.py
```

### Run with pytest

```bash
# Install pytest (if not installed)
pip install pytest

# Run all tests with verbose output
pytest cases/ -v

# Run specific test file
pytest cases/test_ml_model.py -v

# Run specific test function
pytest cases/test_ml_model.py::test_ml_prediction -v
```

## Test Cases

### 1. ML Model Tests (`test_ml_model.py`)

Tests the RandomForest classifier and fallback strategy:
- ML model initialization
- Feature extraction
- Prediction with trained model
- Fallback prediction when untrained
- Training data recording
- Model training and persistence

### 2. RL Agent Tests (`test_rl_agent.py`)

Tests the Q-learning agent:
- Agent initialization
- State discretization
- Action selection
- Q-value learning
- Policy generation
- Pre-training (500 episodes)

### 3. Simulator Tests (`test_simulator.py`)

Tests counterfactual simulation:
- Scale action simulation
- Restart action simulation
- Plan selection
- Latency improvement calculation
- Cost increase calculation

### 4. Safety Verification Tests (`test_safety.py`)

Tests Z3 SMT solver integration:
- Safety constraint verification
- Scaling limit checks
- Policy enforcement
- Formal verification

### 5. Certificate Generation Tests (`test_certificate.py`)

Tests certificate generation:
- Certificate creation
- SHA256 hashing
- Safety proofs bundling
- Certificate signing
- Certificate validation

### 6. Integration Tests (`test_integration.py`)

Tests component interactions:
- Full pipeline workflow
- Data flow between components
- Error handling
- Edge cases

### 7. Pipeline Tests (`test_pipeline.py`)

Tests the complete pipeline:
- Incident detection
- Root cause analysis
- ML and RL predictions
- Simulation and planning
- Safety verification
- Certificate generation
- Execution
- Outcome recording

## Test Utilities

The `utils.py` file provides:
- Test fixtures
- Mock data generators
- Assertion helpers
- Test data setup/teardown

## Creating New Tests

### Test File Template

```python
"""Test template for CertOps components."""

import pytest
from certops import module_to_test


class TestComponent:
    """Test class for component."""

    def test_functionality(self):
        """Test basic functionality."""
        # Arrange
        # Act
        # Assert
        pass

    def test_edge_cases(self):
        """Test edge cases."""
        pass

    def test_error_handling(self):
        """Test error handling."""
        pass
```

### Best Practices

1. **Use descriptive test names**: `test_ml_prediction_with_trained_model`
2. **Follow Arrange-Act-Assert pattern**:
   - Arrange: Setup test data
   - Act: Execute the code under test
   - Assert: Verify the results
3. **Test edge cases**: Empty inputs, invalid values, boundary conditions
4. **Test error handling**: Verify proper error messages and exceptions
5. **Keep tests independent**: Each test should run independently
6. **Use fixtures**: For common setup/teardown operations

## Test Data

Test data is stored in the `test/data/` directory:
- `incidents.json` - Sample incident data
- `metrics.json` - Sample metrics data
- `policies.json` - Sample safety policies
- `actions.json` - Sample remediation actions

## Mocking External Services

Tests mock external services like Prometheus and Kubernetes:

```python
from unittest.mock import patch, MagicMock

@patch('certops.prometheus_client.get_live_metrics')
def test_with_mock_prometheus(mock_metrics):
    # Setup mock
    mock_metrics.return_value = {
        'cpu': 80.0,
        'memory': 70.0,
        'latency': 300.0,
        'traffic': 150.0,
        'errors': 0.05
    }

    # Test code
    result = get_live_metrics('default')

    # Assertions
    assert result['cpu'] == 80.0
```

## Continuous Integration

Tests are designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: CertOps Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest

      - name: Run tests
        run: |
          pytest test/cases/ -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

## Test Coverage

To measure test coverage:

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest test/cases/ --cov=certops --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Performance Testing

For performance testing:

```bash
# Install performance testing tools
pip install locust

# Run load testing
locust -f test/performance/load_test.py

# Access locust web UI at http://localhost:8089
```

## Stress Testing

Stress tests verify system behavior under heavy load:

```bash
# Run stress tests
python test/stress/test_high_load.py
```

## Documentation Tests

Docstring tests verify documentation examples:

```bash
# Run doctest
python -m doctest certops/*.py -v
```

## Test Results

Test results are stored in:
- `test-results/` - JUnit XML reports
- `htmlcov/` - HTML coverage reports
- `logs/` - Test execution logs

## Troubleshooting

### Test Failures

```bash
# Run tests with verbose output
pytest test/cases/ -v

# Run specific failing test
pytest test/cases/test_ml_model.py::test_training -v

# Check test output
pytest test/cases/ -v --tb=short
```

### Debugging Tests

```bash
# Run test with breakpoint
python -m pytest test/cases/test_ml_model.py -v --pdb

# Run test with logging
python -m pytest test/cases/test_ml_model.py -v -s
```

### Skipping Tests

```python
import pytest

@pytest.mark.skip(reason="Feature not implemented yet")
def test_not_implemented():
    pass

@pytest.mark.skipif(not HAS_KUBECTL, reason="kubectl not available")
def test_kubernetes():
    pass
```

## Summary

The test suite provides:
- ✅ Unit tests for individual components
- ✅ Integration tests for component interactions
- ✅ Pipeline tests for end-to-end workflows
- ✅ Mocking for external services
- ✅ CI/CD compatibility
- ✅ Test coverage measurement
- ✅ Performance and stress testing

All tests follow best practices and are designed for maintainability and extensibility.
