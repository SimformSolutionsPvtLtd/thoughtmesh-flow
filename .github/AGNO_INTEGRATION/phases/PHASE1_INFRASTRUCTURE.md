# Phase-1 Implementation Instructions: Foundation & Framework Abstraction

## 🎯 Objective
Establish the foundational framework integration system with proper abstractions, base classes, and a simulated Agno adapter to validate the architecture before implementing real components.

## 📋 Prerequisites
- Langflow development environment set up
- Access to the codebase in `src/backend/base/langflow/core/frameworks/`
- Basic understanding of async Python programming
- Familiarity with abstract base classes and type hints

## 🏗️ Core Architecture Components

### 1. Type Definitions (`types.py`)

#### Component Categories and Types
```python
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

class ComponentCategory(Enum):
    """Comprehensive component categories"""
    MODEL = "model"
    TOOL = "tool"
    VECTOR_STORE = "vector_store"
    KNOWLEDGE_BASE = "knowledge_base"
    EMBEDDER = "embedder"
    MEMORY = "memory"
    STORAGE = "storage"
    RERANKER = "reranker"
    CHUNKING = "chunking"
    DOCUMENT_READER = "document_reader"
    AGENT = "agent"
    TEAM = "team"
    WORKFLOW = "workflow"

class ComponentStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable" 
    ERROR = "error"
    SIMULATED = "simulated"

class ExecutionMode(Enum):
    REAL = "real"
    SIMULATED = "simulated"
    HYBRID = "hybrid"
```

#### Core Data Structures
```python
@dataclass
class ComponentInfo:
    """Metadata for framework components"""
    name: str
    category: ComponentCategory
    description: str
    version: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]
    status: ComponentStatus
    metadata: Dict[str, Any]

@dataclass
class ExecutionResult:
    """Result of component execution"""
    success: bool
    output: Any
    error: Optional[str]
    execution_time: float
    mode: ExecutionMode
    metadata: Dict[str, Any]

@dataclass
class ValidationResult:
    """Component validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
```

### 2. Base Framework Adapter (`base.py`)

#### Abstract Base Class
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseFrameworkAdapter(ABC):
    """Abstract base class for all framework adapters"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self._components: Dict[str, ComponentInfo] = {}
        self._health_status = True
    
    @abstractmethod
    async def discover_components(self) -> List[ComponentInfo]:
        """Discover all available components in the framework"""
        pass
    
    @abstractmethod
    async def validate_component(self, component_name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate component configuration"""
        pass
    
    @abstractmethod
    async def execute_component(self, component_name: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> ExecutionResult:
        """Execute a component with given inputs and configuration"""
        pass
    
    @abstractmethod
    async def check_dependencies(self, component_name: str) -> ValidationResult:
        """Check if component dependencies are satisfied"""
        pass
    
    @abstractmethod
    async def get_component_schema(self, component_name: str) -> Dict[str, Any]:
        """Get the input/output schema for a component"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check the health status of the framework adapter"""
        pass
    
    # Concrete helper methods
    def get_components(self) -> Dict[str, ComponentInfo]:
        """Get all discovered components"""
        return self._components.copy()
    
    def get_component(self, name: str) -> Optional[ComponentInfo]:
        """Get specific component by name"""
        return self._components.get(name)
    
    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        return self._health_status
```

### 3. Simulated Agno Adapter (`agno_adapter.py`)

#### Implementation with Mock Components
```python
import asyncio
import random
from typing import Any, Dict, List, Optional
from .base import BaseFrameworkAdapter
from .types import ComponentInfo, ComponentCategory, ComponentStatus, ValidationResult, ExecutionResult, ExecutionMode

class AgnoAdapter(BaseFrameworkAdapter):
    """Simulated Agno framework adapter for Phase-1 validation"""
    
    def __init__(self):
        super().__init__("agno", "1.0.0")
        self._setup_mock_components()
    
    def _setup_mock_components(self):
        """Initialize mock components for testing"""
        mock_components = [
            ComponentInfo(
                name="openai_model",
                category=ComponentCategory.MODEL,
                description="OpenAI GPT model integration",
                version="1.0.0",
                inputs=["prompt", "temperature", "max_tokens"],
                outputs=["response", "usage"],
                dependencies=["openai"],
                status=ComponentStatus.SIMULATED,
                metadata={"provider": "openai", "type": "language_model"}
            ),
            ComponentInfo(
                name="duckduckgo_search",
                category=ComponentCategory.TOOL,
                description="DuckDuckGo search tool",
                version="1.0.0",
                inputs=["query", "max_results"],
                outputs=["results"],
                dependencies=["duckduckgo_search"],
                status=ComponentStatus.SIMULATED,
                metadata={"provider": "duckduckgo", "type": "search"}
            ),
            ComponentInfo(
                name="pdf_knowledge_base",
                category=ComponentCategory.KNOWLEDGE_BASE,
                description="PDF-based knowledge base",
                version="1.0.0",
                inputs=["pdf_path", "chunk_size"],
                outputs=["knowledge_base"],
                dependencies=["pypdf", "sentence_transformers"],
                status=ComponentStatus.SIMULATED,
                metadata={"type": "document_kb", "formats": ["pdf"]}
            ),
            ComponentInfo(
                name="basic_agent",
                category=ComponentCategory.AGENT,
                description="Basic conversational agent",
                version="1.0.0",
                inputs=["model", "tools", "instructions"],
                outputs=["response", "tool_calls"],
                dependencies=["agno"],
                status=ComponentStatus.SIMULATED,
                metadata={"type": "conversational", "capabilities": ["tool_use"]}
            ),
            ComponentInfo(
                name="sequential_workflow",
                category=ComponentCategory.WORKFLOW,
                description="Sequential component workflow",
                version="1.0.0",
                inputs=["components", "initial_inputs"],
                outputs=["final_output", "intermediate_results"],
                dependencies=["agno"],
                status=ComponentStatus.SIMULATED,
                metadata={"type": "sequential", "execution": "linear"}
            ),
        ]
        
        for component in mock_components:
            self._components[component.name] = component
    
    async def discover_components(self) -> List[ComponentInfo]:
        """Simulate component discovery with delay"""
        await asyncio.sleep(0.1)  # Simulate discovery time
        return list(self._components.values())
    
    async def validate_component(self, component_name: str, config: Dict[str, Any]) -> ValidationResult:
        """Simulate component validation"""
        await asyncio.sleep(0.05)  # Simulate validation time
        
        component = self._components.get(component_name)
        if not component:
            return ValidationResult(
                is_valid=False,
                errors=[f"Component '{component_name}' not found"],
                warnings=[],
                suggestions=[f"Available components: {list(self._components.keys())}"]
            )
        
        # Simulate validation logic
        missing_inputs = [inp for inp in component.inputs if inp not in config]
        if missing_inputs:
            return ValidationResult(
                is_valid=False,
                errors=[f"Missing required inputs: {missing_inputs}"],
                warnings=[],
                suggestions=[f"Required inputs: {component.inputs}"]
            )
        
        return ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
    
    async def execute_component(self, component_name: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> ExecutionResult:
        """Simulate component execution"""
        start_time = asyncio.get_event_loop().time()
        
        # Simulate execution delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        component = self._components.get(component_name)
        if not component:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Component '{component_name}' not found",
                execution_time=execution_time,
                mode=ExecutionMode.SIMULATED,
                metadata={"component": component_name}
            )
        
        # Generate mock output based on component type
        mock_output = self._generate_mock_output(component, inputs)
        execution_time = asyncio.get_event_loop().time() - start_time
        
        return ExecutionResult(
            success=True,
            output=mock_output,
            error=None,
            execution_time=execution_time,
            mode=ExecutionMode.SIMULATED,
            metadata={"component": component_name, "inputs": inputs}
        )
    
    async def check_dependencies(self, component_name: str) -> ValidationResult:
        """Simulate dependency checking"""
        await asyncio.sleep(0.02)
        
        component = self._components.get(component_name)
        if not component:
            return ValidationResult(
                is_valid=False,
                errors=[f"Component '{component_name}' not found"],
                warnings=[],
                suggestions=[]
            )
        
        # Simulate dependency check (always pass in simulation)
        return ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[f"Dependencies {component.dependencies} not actually checked in simulation mode"],
            suggestions=["Run in real mode for actual dependency verification"]
        )
    
    async def get_component_schema(self, component_name: str) -> Dict[str, Any]:
        """Get component input/output schema"""
        component = self._components.get(component_name)
        if not component:
            return {}
        
        return {
            "inputs": {inp: {"type": "string", "required": True} for inp in component.inputs},
            "outputs": {out: {"type": "any"} for out in component.outputs},
            "description": component.description,
            "category": component.category.value
        }
    
    async def health_check(self) -> bool:
        """Simulate health check"""
        await asyncio.sleep(0.01)
        return True
    
    def _generate_mock_output(self, component: ComponentInfo, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic mock output based on component type"""
        if component.category == ComponentCategory.MODEL:
            return {
                "response": f"Mock response to: {inputs.get('prompt', 'No prompt provided')}",
                "usage": {"tokens": 150, "cost": 0.003}
            }
        elif component.category == ComponentCategory.TOOL:
            return {
                "results": [
                    {"title": f"Mock result for: {inputs.get('query', 'test')}", "url": "https://example.com"},
                    {"title": "Another mock result", "url": "https://example2.com"}
                ]
            }
        elif component.category == ComponentCategory.KNOWLEDGE_BASE:
            return {
                "knowledge_base": f"Mock knowledge base created from {inputs.get('pdf_path', 'unknown.pdf')}"
            }
        elif component.category == ComponentCategory.AGENT:
            return {
                "response": "Mock agent response",
                "tool_calls": [{"tool": "mock_tool", "input": "mock_input", "output": "mock_output"}]
            }
        elif component.category == ComponentCategory.WORKFLOW:
            return {
                "final_output": "Mock workflow completion",
                "intermediate_results": ["step1_result", "step2_result", "step3_result"]
            }
        else:
            return {"output": f"Mock output for {component.category.value}"}
```

### 4. Framework Manager (`manager.py`)

#### Multi-Adapter Coordination
```python
import asyncio
from typing import Dict, List, Optional, Type
from .base import BaseFrameworkAdapter
from .types import ComponentInfo, ValidationResult, ExecutionResult

class FrameworkManager:
    """Manages multiple framework adapters"""
    
    def __init__(self):
        self._adapters: Dict[str, BaseFrameworkAdapter] = {}
        self._component_registry: Dict[str, str] = {}  # component_name -> adapter_name
        self._health_checks_enabled = True
    
    def register_adapter(self, adapter: BaseFrameworkAdapter) -> None:
        """Register a framework adapter"""
        self._adapters[adapter.name] = adapter
        print(f"Registered framework adapter: {adapter.name} v{adapter.version}")
    
    def unregister_adapter(self, adapter_name: str) -> bool:
        """Unregister a framework adapter"""
        if adapter_name in self._adapters:
            del self._adapters[adapter_name]
            # Clean up component registry
            self._component_registry = {
                comp: adapter for comp, adapter in self._component_registry.items()
                if adapter != adapter_name
            }
            return True
        return False
    
    async def discover_all_components(self) -> Dict[str, List[ComponentInfo]]:
        """Discover components from all registered adapters"""
        all_components = {}
        
        for adapter_name, adapter in self._adapters.items():
            try:
                components = await adapter.discover_components()
                all_components[adapter_name] = components
                
                # Update component registry
                for component in components:
                    self._component_registry[component.name] = adapter_name
                    
            except Exception as e:
                print(f"Error discovering components from {adapter_name}: {e}")
                all_components[adapter_name] = []
        
        return all_components
    
    async def execute_component(self, component_name: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> ExecutionResult:
        """Execute a component using the appropriate adapter"""
        adapter_name = self._component_registry.get(component_name)
        if not adapter_name:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Component '{component_name}' not found in any registered adapter",
                execution_time=0.0,
                mode=ExecutionMode.SIMULATED,
                metadata={"available_components": list(self._component_registry.keys())}
            )
        
        adapter = self._adapters.get(adapter_name)
        if not adapter:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Adapter '{adapter_name}' not found",
                execution_time=0.0,
                mode=ExecutionMode.SIMULATED,
                metadata={"component": component_name}
            )
        
        return await adapter.execute_component(component_name, inputs, config)
    
    async def validate_component(self, component_name: str, config: Dict[str, Any]) -> ValidationResult:
        """Validate a component using the appropriate adapter"""
        adapter_name = self._component_registry.get(component_name)
        if not adapter_name:
            return ValidationResult(
                is_valid=False,
                errors=[f"Component '{component_name}' not found"],
                warnings=[],
                suggestions=[f"Available components: {list(self._component_registry.keys())}"]
            )
        
        adapter = self._adapters[adapter_name]
        return await adapter.validate_component(component_name, config)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all registered adapters"""
        health_status = {}
        
        for adapter_name, adapter in self._adapters.items():
            try:
                health_status[adapter_name] = await adapter.health_check()
            except Exception as e:
                print(f"Health check failed for {adapter_name}: {e}")
                health_status[adapter_name] = False
        
        return health_status
    
    def get_component_info(self, component_name: str) -> Optional[ComponentInfo]:
        """Get information about a specific component"""
        adapter_name = self._component_registry.get(component_name)
        if not adapter_name:
            return None
        
        adapter = self._adapters.get(adapter_name)
        if not adapter:
            return None
        
        return adapter.get_component(component_name)
    
    def get_all_components(self) -> Dict[str, ComponentInfo]:
        """Get all components from all adapters"""
        all_components = {}
        
        for adapter in self._adapters.values():
            all_components.update(adapter.get_components())
        
        return all_components
    
    def get_adapters_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered adapters"""
        return {
            name: {
                "name": adapter.name,
                "version": adapter.version,
                "healthy": adapter.is_healthy(),
                "component_count": len(adapter.get_components())
            }
            for name, adapter in self._adapters.items()
        }
```

### 5. Integration Module (`__init__.py`)

#### Public API and Initialization
```python
"""
Langflow Framework Integration System

This module provides a unified interface for integrating external AI frameworks
into Langflow, starting with the Agno AI framework.
"""

from .types import (
    ComponentCategory,
    ComponentStatus,
    ExecutionMode,
    ComponentInfo,
    ExecutionResult,
    ValidationResult
)
from .base import BaseFrameworkAdapter
from .manager import FrameworkManager
from .agno_adapter import AgnoAdapter

# Global framework manager instance
framework_manager = FrameworkManager()

def initialize_frameworks():
    """Initialize and register all available framework adapters"""
    # Register Agno adapter (simulated in Phase-1)
    agno_adapter = AgnoAdapter()
    framework_manager.register_adapter(agno_adapter)
    
    print("Framework integration system initialized")
    print(f"Registered adapters: {list(framework_manager._adapters.keys())}")

# Auto-initialize when module is imported
initialize_frameworks()

# Public API
__all__ = [
    'ComponentCategory',
    'ComponentStatus', 
    'ExecutionMode',
    'ComponentInfo',
    'ExecutionResult',
    'ValidationResult',
    'BaseFrameworkAdapter',
    'FrameworkManager',
    'AgnoAdapter',
    'framework_manager'
]
```

### 6. Exception Handling (`exceptions.py`)

#### Framework-Specific Exceptions
```python
"""Framework-specific exceptions"""

class FrameworkException(Exception):
    """Base exception for framework operations"""
    pass

class ComponentNotFoundError(FrameworkException):
    """Raised when a component is not found"""
    def __init__(self, component_name: str, available_components: list = None):
        self.component_name = component_name
        self.available_components = available_components or []
        super().__init__(f"Component '{component_name}' not found")

class ComponentExecutionError(FrameworkException):
    """Raised when component execution fails"""
    def __init__(self, component_name: str, error_message: str):
        self.component_name = component_name
        self.error_message = error_message
        super().__init__(f"Component '{component_name}' execution failed: {error_message}")

class ComponentValidationError(FrameworkException):
    """Raised when component validation fails"""
    def __init__(self, component_name: str, validation_errors: list):
        self.component_name = component_name
        self.validation_errors = validation_errors
        super().__init__(f"Component '{component_name}' validation failed: {validation_errors}")

class AdapterNotFoundError(FrameworkException):
    """Raised when an adapter is not found"""
    def __init__(self, adapter_name: str):
        self.adapter_name = adapter_name
        super().__init__(f"Adapter '{adapter_name}' not found")

class DependencyError(FrameworkException):
    """Raised when component dependencies are not satisfied"""
    def __init__(self, component_name: str, missing_dependencies: list):
        self.component_name = component_name
        self.missing_dependencies = missing_dependencies
        super().__init__(f"Component '{component_name}' missing dependencies: {missing_dependencies}")
```

## 🧪 Testing Framework

### 1. Unit Tests (`test_phase1.py`)

```python
import pytest
import asyncio
from langflow.core.frameworks import (
    framework_manager,
    ComponentCategory,
    ComponentStatus,
    ExecutionMode
)

class TestPhase1Integration:
    """Test Phase-1 framework integration"""
    
    @pytest.mark.asyncio
    async def test_framework_manager_initialization(self):
        """Test framework manager initializes correctly"""
        assert len(framework_manager._adapters) > 0
        assert "agno" in framework_manager._adapters
    
    @pytest.mark.asyncio
    async def test_component_discovery(self):
        """Test component discovery across all adapters"""
        components = await framework_manager.discover_all_components()
        assert "agno" in components
        assert len(components["agno"]) >= 5  # Should have at least 5 mock components
    
    @pytest.mark.asyncio
    async def test_component_execution(self):
        """Test component execution through framework manager"""
        # Test model component
        result = await framework_manager.execute_component(
            "openai_model",
            {"prompt": "Hello, world!", "temperature": 0.7},
            {}
        )
        assert result.success
        assert result.mode == ExecutionMode.SIMULATED
        assert "response" in result.output
    
    @pytest.mark.asyncio
    async def test_component_validation(self):
        """Test component validation"""
        # Valid configuration
        valid_result = await framework_manager.validate_component(
            "openai_model",
            {"prompt": "test", "temperature": 0.7, "max_tokens": 100}
        )
        assert valid_result.is_valid
        
        # Invalid configuration (missing required input)
        invalid_result = await framework_manager.validate_component(
            "openai_model",
            {"temperature": 0.7}  # Missing 'prompt'
        )
        assert not invalid_result.is_valid
        assert len(invalid_result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_health_checks(self):
        """Test health checking functionality"""
        health_status = await framework_manager.health_check_all()
        assert "agno" in health_status
        assert health_status["agno"] is True
    
    @pytest.mark.asyncio
    async def test_component_categories(self):
        """Test all component categories are represented"""
        components = await framework_manager.discover_all_components()
        agno_components = components["agno"]
        
        categories = {comp.category for comp in agno_components}
        expected_categories = {
            ComponentCategory.MODEL,
            ComponentCategory.TOOL,
            ComponentCategory.KNOWLEDGE_BASE,
            ComponentCategory.AGENT,
            ComponentCategory.WORKFLOW
        }
        
        assert expected_categories.issubset(categories)
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self):
        """Test performance requirements are met"""
        import time
        
        # Test discovery performance (<500ms)
        start_time = time.time()
        await framework_manager.discover_all_components()
        discovery_time = time.time() - start_time
        assert discovery_time < 0.5
        
        # Test execution performance (<100ms for simple operations)
        start_time = time.time()
        await framework_manager.execute_component(
            "duckduckgo_search",
            {"query": "test", "max_results": 5},
            {}
        )
        execution_time = time.time() - start_time
        assert execution_time < 0.6  # Allowing for simulation delay

if __name__ == "__main__":
    asyncio.run(test_main())

async def test_main():
    """Run all tests"""
    test_instance = TestPhase1Integration()
    
    print("Testing Phase-1 Framework Integration...")
    
    await test_instance.test_framework_manager_initialization()
    print("✅ Framework manager initialization")
    
    await test_instance.test_component_discovery()
    print("✅ Component discovery")
    
    await test_instance.test_component_execution()
    print("✅ Component execution")
    
    await test_instance.test_component_validation()
    print("✅ Component validation")
    
    await test_instance.test_health_checks()
    print("✅ Health checks")
    
    await test_instance.test_component_categories()
    print("✅ Component categories")
    
    await test_instance.test_performance_requirements()
    print("✅ Performance requirements")
    
    print("\n🎉 All Phase-1 tests completed successfully!")
```

## 📋 Implementation Checklist

### Core Components
- [ ] Implement `types.py` with all enums and data structures
- [ ] Create `BaseFrameworkAdapter` abstract class in `base.py`
- [ ] Implement `AgnoAdapter` simulated adapter in `agno_adapter.py`
- [ ] Create `FrameworkManager` in `manager.py`
- [ ] Set up public API in `__init__.py`
- [ ] Add exception classes in `exceptions.py`

### Testing & Validation
- [ ] Create comprehensive test suite in `test_phase1.py`
- [ ] Test all abstract methods are implemented
- [ ] Validate performance requirements (<500ms discovery, <100ms execution)
- [ ] Test error handling and edge cases
- [ ] Verify component discovery and execution workflows

### Documentation
- [ ] Add docstrings to all classes and methods
- [ ] Create usage examples and integration guides
- [ ] Document the adapter interface and extension points
- [ ] Add troubleshooting guide for common issues

## 🎯 Success Criteria

### Functional Requirements
- ✅ All abstract methods in `BaseFrameworkAdapter` are implemented
- ✅ Framework manager successfully coordinates multiple adapters
- ✅ Component discovery returns 5+ mock components across different categories
- ✅ Component execution works with realistic mock outputs
- ✅ Component validation properly checks inputs and configuration
- ✅ Health checks work for all registered adapters

### Performance Requirements
- ✅ Component discovery completes in <500ms
- ✅ Component execution completes in <100ms (excluding simulation delays)
- ✅ Framework manager handles multiple concurrent operations
- ✅ Memory usage remains stable during operation

### Integration Requirements
- ✅ Module can be imported without errors
- ✅ Framework manager auto-initializes on import
- ✅ All public APIs work as expected
- ✅ Error handling is comprehensive and informative

## 🚀 Next Steps

After Phase-1 completion:
1. **Validate Architecture**: Ensure all abstract methods work correctly
2. **Performance Testing**: Verify performance requirements are met
3. **Integration Testing**: Test with actual Langflow components
4. **Documentation**: Complete API documentation and usage guides
5. **Phase-2 Preparation**: Begin analysis of real Agno repository

**Expected Timeline**: 2-3 weeks  
**Key Milestone**: Fully functional framework integration foundation with simulated components

---

**🎯 Phase-1 Goal**: Establish a robust, extensible foundation for framework integration that can seamlessly transition to real component implementations in Phase-2.
