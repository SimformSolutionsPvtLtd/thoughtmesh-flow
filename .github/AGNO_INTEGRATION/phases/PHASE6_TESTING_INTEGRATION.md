# Phase 6: Testing & Integration

## Overview
This phase focuses on comprehensive testing of the Agno framework integration, ensuring quality, reliability, and proper integration with existing Langflow components.

## Objectives
- Implement comprehensive test suites for Agno integration
- Set up integration testing pipeline
- Validate agent behavior and workflow execution
- Ensure backward compatibility with existing flows
- Performance testing and optimization

## Prerequisites
- Phases 1-5 completed successfully
- All core Agno components integrated
- API layer functional
- Database configuration complete

## Implementation Tasks

### 6.1 Unit Testing Framework

#### Task: Set up Agno-specific unit tests
```bash
# Create test structure
mkdir -p src/backend/tests/agno/
mkdir -p src/backend/tests/agno/agents/
mkdir -p src/backend/tests/agno/workflows/
mkdir -p src/backend/tests/agno/components/
```

#### Files to create/modify:
- `src/backend/tests/agno/test_agent_manager.py`
- `src/backend/tests/agno/test_workflow_engine.py`
- `src/backend/tests/agno/test_agno_components.py`
- `src/backend/tests/agno/agents/test_agent_lifecycle.py`
- `src/backend/tests/agno/workflows/test_workflow_execution.py`

#### Test Agent Manager:
```python
# src/backend/tests/agno/test_agent_manager.py
import pytest
from unittest.mock import Mock, patch
from langflow.agno.manager import AgentManager
from langflow.agno.types import AgentConfig, AgentType

class TestAgentManager:
    @pytest.fixture
    def agent_manager(self):
        return AgentManager()
    
    @pytest.fixture
    def sample_agent_config(self):
        return AgentConfig(
            name="test_agent",
            type=AgentType.CONVERSATIONAL,
            model="gpt-3.5-turbo",
            system_prompt="You are a test agent",
            tools=[]
        )
    
    def test_create_agent(self, agent_manager, sample_agent_config):
        agent = agent_manager.create_agent(sample_agent_config)
        assert agent is not None
        assert agent.name == "test_agent"
        assert agent.type == AgentType.CONVERSATIONAL
    
    def test_agent_lifecycle(self, agent_manager, sample_agent_config):
        # Test create
        agent = agent_manager.create_agent(sample_agent_config)
        agent_id = agent.id
        
        # Test retrieve
        retrieved = agent_manager.get_agent(agent_id)
        assert retrieved.id == agent_id
        
        # Test update
        updated_config = sample_agent_config.copy()
        updated_config.system_prompt = "Updated prompt"
        agent_manager.update_agent(agent_id, updated_config)
        
        updated_agent = agent_manager.get_agent(agent_id)
        assert updated_agent.system_prompt == "Updated prompt"
        
        # Test delete
        agent_manager.delete_agent(agent_id)
        with pytest.raises(ValueError):
            agent_manager.get_agent(agent_id)
    
    def test_agent_execution(self, agent_manager, sample_agent_config):
        agent = agent_manager.create_agent(sample_agent_config)
        
        # Mock the execution
        with patch.object(agent, 'execute') as mock_execute:
            mock_execute.return_value = "Test response"
            
            response = agent_manager.execute_agent(
                agent.id, 
                {"message": "Hello"}
            )
            
            assert response == "Test response"
            mock_execute.assert_called_once()
```

#### Test Workflow Engine:
```python
# src/backend/tests/agno/test_workflow_engine.py
import pytest
from unittest.mock import Mock, patch
from langflow.agno.workflow import WorkflowEngine, WorkflowConfig
from langflow.agno.types import WorkflowStep, WorkflowTrigger

class TestWorkflowEngine:
    @pytest.fixture
    def workflow_engine(self):
        return WorkflowEngine()
    
    @pytest.fixture
    def sample_workflow_config(self):
        return WorkflowConfig(
            name="test_workflow",
            description="Test workflow",
            triggers=[
                WorkflowTrigger(
                    type="manual",
                    config={}
                )
            ],
            steps=[
                WorkflowStep(
                    id="step_1",
                    agent_id="agent_1",
                    input_mapping={"message": "input.message"},
                    output_mapping={"response": "output.response"}
                )
            ]
        )
    
    def test_create_workflow(self, workflow_engine, sample_workflow_config):
        workflow = workflow_engine.create_workflow(sample_workflow_config)
        assert workflow is not None
        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 1
    
    def test_workflow_execution(self, workflow_engine, sample_workflow_config):
        workflow = workflow_engine.create_workflow(sample_workflow_config)
        
        with patch.object(workflow_engine, '_execute_step') as mock_execute:
            mock_execute.return_value = {"response": "Test output"}
            
            result = workflow_engine.execute_workflow(
                workflow.id,
                {"message": "Test input"}
            )
            
            assert result is not None
            mock_execute.assert_called()
    
    def test_workflow_validation(self, workflow_engine):
        # Test invalid workflow configuration
        invalid_config = WorkflowConfig(
            name="",  # Invalid empty name
            description="Test",
            triggers=[],  # No triggers
            steps=[]  # No steps
        )
        
        with pytest.raises(ValueError):
            workflow_engine.create_workflow(invalid_config)
```

### 6.2 Integration Testing

#### Task: Create integration test suite
```python
# src/backend/tests/agno/test_integration.py
import pytest
from langflow.agno.manager import AgentManager
from langflow.agno.workflow import WorkflowEngine
from langflow.agno.types import AgentConfig, WorkflowConfig, AgentType
from langflow.graph import Graph
from langflow.graph.vertex import Vertex

class TestAgnoIntegration:
    @pytest.fixture
    def setup_integration(self):
        """Set up integration test environment"""
        agent_manager = AgentManager()
        workflow_engine = WorkflowEngine()
        
        # Create test agent
        agent_config = AgentConfig(
            name="integration_test_agent",
            type=AgentType.CONVERSATIONAL,
            model="gpt-3.5-turbo",
            system_prompt="Integration test agent"
        )
        agent = agent_manager.create_agent(agent_config)
        
        return {
            "agent_manager": agent_manager,
            "workflow_engine": workflow_engine,
            "agent": agent
        }
    
    def test_langflow_graph_integration(self, setup_integration):
        """Test integration with Langflow graph system"""
        agent = setup_integration["agent"]
        
        # Create a simple graph with Agno agent
        graph = Graph()
        
        # Add Agno agent vertex
        agno_vertex = Vertex(
            data={
                "type": "AgnoAgent",
                "node": {
                    "template": {
                        "agent_id": {"value": agent.id}
                    }
                }
            }
        )
        
        graph.add_vertex(agno_vertex)
        
        # Test graph execution
        result = graph.run(inputs={"message": "Test message"})
        assert result is not None
    
    def test_workflow_chain_execution(self, setup_integration):
        """Test multi-step workflow execution"""
        agent_manager = setup_integration["agent_manager"]
        workflow_engine = setup_integration["workflow_engine"]
        
        # Create multiple agents
        agent1_config = AgentConfig(
            name="preprocessor",
            type=AgentType.TASK_ORIENTED,
            system_prompt="Preprocess input data"
        )
        agent1 = agent_manager.create_agent(agent1_config)
        
        agent2_config = AgentConfig(
            name="processor",
            type=AgentType.CONVERSATIONAL,
            system_prompt="Process the data"
        )
        agent2 = agent_manager.create_agent(agent2_config)
        
        # Create workflow
        workflow_config = WorkflowConfig(
            name="chain_test",
            description="Test chain execution",
            steps=[
                {
                    "id": "preprocess",
                    "agent_id": agent1.id,
                    "input_mapping": {"data": "input.raw_data"}
                },
                {
                    "id": "process",
                    "agent_id": agent2.id,
                    "input_mapping": {"data": "preprocess.output"}
                }
            ]
        )
        
        workflow = workflow_engine.create_workflow(workflow_config)
        
        # Execute workflow
        result = workflow_engine.execute_workflow(
            workflow.id,
            {"raw_data": "Test input data"}
        )
        
        assert result is not None
```

### 6.3 Performance Testing

#### Task: Implement performance benchmarks
```python
# src/backend/tests/agno/test_performance.py
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langflow.agno.manager import AgentManager
from langflow.agno.types import AgentConfig, AgentType

class TestAgnoPerformance:
    @pytest.fixture
    def performance_setup(self):
        agent_manager = AgentManager()
        
        # Create multiple test agents
        agents = []
        for i in range(5):
            config = AgentConfig(
                name=f"perf_agent_{i}",
                type=AgentType.CONVERSATIONAL,
                model="gpt-3.5-turbo",
                system_prompt=f"Performance test agent {i}"
            )
            agents.append(agent_manager.create_agent(config))
        
        return {"agent_manager": agent_manager, "agents": agents}
    
    def test_agent_creation_performance(self, performance_setup):
        """Test agent creation performance"""
        agent_manager = performance_setup["agent_manager"]
        
        start_time = time.time()
        
        # Create 10 agents
        for i in range(10):
            config = AgentConfig(
                name=f"speed_test_{i}",
                type=AgentType.CONVERSATIONAL,
                system_prompt="Speed test agent"
            )
            agent_manager.create_agent(config)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 10 agents in less than 5 seconds
        assert creation_time < 5.0
        print(f"Created 10 agents in {creation_time:.2f} seconds")
    
    def test_concurrent_agent_execution(self, performance_setup):
        """Test concurrent agent execution"""
        agent_manager = performance_setup["agent_manager"]
        agents = performance_setup["agents"]
        
        def execute_agent(agent):
            return agent_manager.execute_agent(
                agent.id,
                {"message": "Concurrent test"}
            )
        
        start_time = time.time()
        
        # Execute 5 agents concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(execute_agent, agent) 
                for agent in agents
            ]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(results) == 5
        assert all(result is not None for result in results)
        print(f"Executed 5 agents concurrently in {execution_time:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_async_workflow_performance(self, performance_setup):
        """Test asynchronous workflow execution performance"""
        # Implementation for async workflow testing
        pass
```

### 6.4 Compatibility Testing

#### Task: Ensure backward compatibility
```python
# src/backend/tests/agno/test_compatibility.py
import pytest
from langflow.graph import Graph
from langflow.processing.processor import Processor
from langflow.agno.compatibility import LegacyFlowAdapter

class TestBackwardCompatibility:
    def test_legacy_flow_execution(self):
        """Test that existing flows still work with Agno integration"""
        # Load a legacy flow configuration
        legacy_flow = {
            "nodes": [
                {
                    "id": "input",
                    "type": "TextInput",
                    "data": {"value": "Hello"}
                },
                {
                    "id": "output",
                    "type": "TextOutput",
                    "data": {}
                }
            ],
            "edges": [
                {
                    "source": "input",
                    "target": "output"
                }
            ]
        }
        
        # Execute legacy flow
        graph = Graph.from_dict(legacy_flow)
        result = graph.run()
        
        assert result is not None
    
    def test_agno_legacy_interop(self):
        """Test Agno agents working with legacy components"""
        # Create mixed flow with Agno and legacy components
        mixed_flow = {
            "nodes": [
                {
                    "id": "input",
                    "type": "TextInput",
                    "data": {"value": "Test input"}
                },
                {
                    "id": "agno_agent",
                    "type": "AgnoAgent",
                    "data": {
                        "agent_config": {
                            "name": "compat_test",
                            "type": "conversational"
                        }
                    }
                },
                {
                    "id": "output",
                    "type": "TextOutput",
                    "data": {}
                }
            ],
            "edges": [
                {"source": "input", "target": "agno_agent"},
                {"source": "agno_agent", "target": "output"}
            ]
        }
        
        graph = Graph.from_dict(mixed_flow)
        result = graph.run()
        
        assert result is not None
```

### 6.5 Testing Configuration

#### Task: Configure test environment
```python
# src/backend/tests/conftest.py (update existing file)
import pytest
import os
import tempfile
from langflow.agno.database import init_test_database
from langflow.agno.config import AgnoConfig

@pytest.fixture(scope="session")
def agno_test_config():
    """Create test configuration for Agno"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AgnoConfig(
            database_url=f"sqlite:///{tmpdir}/test_agno.db",
            enable_logging=True,
            log_level="DEBUG",
            cache_enabled=False  # Disable caching for tests
        )
        
        # Initialize test database
        init_test_database(config.database_url)
        
        yield config

@pytest.fixture(autouse=True)
def setup_agno_test_env(agno_test_config):
    """Auto-setup Agno test environment for each test"""
    os.environ["AGNO_TEST_MODE"] = "true"
    os.environ["AGNO_DATABASE_URL"] = agno_test_config.database_url
    
    yield
    
    # Cleanup
    os.environ.pop("AGNO_TEST_MODE", None)
    os.environ.pop("AGNO_DATABASE_URL", None)
```

#### Test runner configuration:
```toml
# Update pyproject.toml test configuration
[tool.pytest.ini_options]
testpaths = ["src/backend/tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--cov=langflow.agno",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "performance: Performance tests",
    "agno: Agno framework tests"
]
```

### 6.6 CI/CD Integration

#### Task: Update GitHub workflows
```yaml
# .github/workflows/agno-tests.yml
name: Agno Integration Tests

on:
  push:
    branches: [main, develop]
    paths: 
      - 'src/backend/langflow/agno/**'
      - 'src/backend/tests/agno/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'src/backend/langflow/agno/**'
      - 'src/backend/tests/agno/**'

jobs:
  agno-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[agno,test]"
    
    - name: Run Agno unit tests
      run: |
        pytest src/backend/tests/agno/ -m "unit" --cov=langflow.agno
    
    - name: Run Agno integration tests
      run: |
        pytest src/backend/tests/agno/ -m "integration"
    
    - name: Run Agno performance tests
      run: |
        pytest src/backend/tests/agno/ -m "performance"
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: agno
        name: agno-coverage
```

## Validation Checklist

### Testing Completeness
- [ ] Unit tests cover all Agno components
- [ ] Integration tests validate Langflow compatibility
- [ ] Performance tests identify bottlenecks
- [ ] Compatibility tests ensure backward compatibility
- [ ] CI/CD pipeline runs all test suites

### Quality Metrics
- [ ] Code coverage > 80% for Agno modules
- [ ] All tests pass in CI/CD pipeline
- [ ] Performance benchmarks meet requirements
- [ ] No breaking changes to existing functionality
- [ ] Documentation updated with testing guidelines

### Integration Validation
- [ ] Agno agents work with existing Langflow components
- [ ] Legacy flows continue to function
- [ ] New features accessible through UI
- [ ] API endpoints properly tested
- [ ] Database migrations successful

## Expected Outcomes

1. **Comprehensive Test Suite**: Complete testing coverage for all Agno integration components
2. **Quality Assurance**: Automated testing pipeline ensuring code quality and reliability
3. **Performance Validation**: Benchmarks confirming acceptable performance characteristics
4. **Compatibility Assurance**: Verification that existing Langflow functionality remains intact
5. **Production Readiness**: Fully tested and validated Agno integration ready for deployment

## Next Phase
Proceed to **Phase 7: Documentation & Deployment** for final documentation, deployment preparation, and production release.
