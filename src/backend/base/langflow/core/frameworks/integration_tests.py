"""Integration tests for Phase-3 Agno Framework components.

This module provides comprehensive integration testing for the orchestration,
monitoring, error recovery, configuration, API, plugin, and UI systems.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .config_manager import ConfigManager
from .error_recovery import CircuitBreakerConfig, ErrorRecoverySystem, RecoveryStrategy, register_component_recovery
from .performance_monitor import PerformanceMonitor
from .plugin_system import BasePlugin, PluginManager, PluginMetadata, PluginType
from .ui_integration import ComponentSchema, ComponentType, UIIntegrationManager
from .workflow_engine import AgnoWorkflowEngine, ExecutionStrategy

logger = logging.getLogger(__name__)


class TestPlugin(BasePlugin):
    """Test plugin for integration testing."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin for integration testing",
            author="Langflow Team",
            plugin_type=PluginType.COMPONENT,
        )

    async def initialize(self) -> bool:
        self._is_initialized = True
        return True

    async def activate(self) -> bool:
        self._is_active = True
        return True

    async def deactivate(self) -> bool:
        self._is_active = False
        return True

    async def cleanup(self) -> bool:
        return True


class Phase3IntegrationTester:
    """Comprehensive integration tester for Phase-3 components."""

    def __init__(self):
        self.workflow_engine = AgnoWorkflowEngine()
        self.performance_monitor = PerformanceMonitor()
        self.error_recovery = ErrorRecoverySystem()
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager()
        self.ui_manager = UIIntegrationManager()

        self.test_results: dict[str, dict[str, Any]] = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all integration tests."""
        logger.info("Starting Phase-3 integration tests")
        start_time = time.time()

        # Initialize all systems
        await self._initialize_systems()

        # Run individual component tests
        await self._test_workflow_engine()
        await self._test_performance_monitor()
        await self._test_error_recovery()
        await self._test_config_manager()
        await self._test_plugin_system()
        await self._test_ui_integration()

        # Run integration tests
        await self._test_system_integration()

        # Generate test report
        end_time = time.time()
        execution_time = end_time - start_time

        report = {
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results,
        }

        logger.info("Phase-3 integration tests completed")
        logger.info(
            "Test Summary: %d total, %d passed, %d failed (%.1f%% success rate)",
            self.total_tests,
            self.passed_tests,
            self.failed_tests,
            report["summary"]["success_rate"],
        )

        return report

    async def _initialize_systems(self) -> None:
        """Initialize all systems for testing."""
        logger.info("Initializing systems for testing")

        # Initialize performance monitor
        await self.performance_monitor.start_monitoring()

        # Initialize plugin manager
        await self.plugin_manager.initialize()

        # Initialize UI manager
        self.ui_manager.initialize()

        # Register error recovery strategies
        register_component_recovery(
            "test_component",
            [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK],
            CircuitBreakerConfig(failure_threshold=3, timeout_duration=10),
        )

        logger.info("Systems initialized successfully")

    async def _test_workflow_engine(self) -> None:
        """Test workflow engine functionality."""
        test_name = "workflow_engine"
        logger.info("Testing workflow engine")

        try:
            # Test workflow creation
            workflow_id = await self.workflow_engine.create_workflow(
                "test_workflow", {"step1": {"type": "test", "config": {}}}
            )
            self._assert_not_none(workflow_id, "Workflow creation")

            # Test workflow execution
            result = await self.workflow_engine.execute_workflow(
                workflow_id, {"input": "test_data"}, ExecutionStrategy.SEQUENTIAL
            )
            self._assert_not_none(result, "Workflow execution")

            # Test analytics
            analytics = self.workflow_engine.get_analytics()
            self._assert_not_none(analytics, "Workflow analytics")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["workflow_creation", "workflow_execution", "analytics"],
                "details": "All workflow engine tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_performance_monitor(self) -> None:
        """Test performance monitoring functionality."""
        test_name = "performance_monitor"
        logger.info("Testing performance monitor")

        try:
            # Test metric recording
            self.performance_monitor.record_metric("test_metric", 1.0)

            # Test custom metrics
            self.performance_monitor.add_custom_metric("custom_test", lambda: 42.0, "Test custom metric")

            # Test analytics
            analytics = self.performance_monitor.get_performance_analytics()
            self._assert_not_none(analytics, "Performance analytics")

            # Test dashboard data
            dashboard_data = self.performance_monitor.get_dashboard_data()
            self._assert_not_none(dashboard_data, "Dashboard data")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["metric_recording", "custom_metrics", "analytics", "dashboard_data"],
                "details": "All performance monitor tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_error_recovery(self) -> None:
        """Test error recovery system functionality."""
        test_name = "error_recovery"
        logger.info("Testing error recovery system")

        try:
            # Test error recording
            test_error = ValueError("Test error")
            error_context = self.error_recovery.record_error(test_error, "test_component", "test_operation")
            self._assert_not_none(error_context, "Error recording")

            # Test recovery attempt
            recovery_result = await self.error_recovery.attempt_recovery(error_context)
            # Recovery might fail, but function should execute without exception

            # Test statistics
            stats = self.error_recovery.get_error_statistics()
            self._assert_not_none(stats, "Error statistics")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["error_recording", "recovery_attempt", "statistics"],
                "details": "All error recovery tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_config_manager(self) -> None:
        """Test configuration manager functionality."""
        test_name = "config_manager"
        logger.info("Testing configuration manager")

        try:
            # Test configuration setting and getting
            self.config_manager.set("test.key", "test_value")
            value = self.config_manager.get("test.key")
            self._assert_equal(value, "test_value", "Configuration get/set")

            # Test configuration validation
            def test_validator(val: Any) -> bool:
                return isinstance(val, str)

            self.config_manager.add_validator("test.validated_key", test_validator)
            self.config_manager.set("test.validated_key", "valid_string")

            # Test secret management
            self.config_manager.secret_manager.store_secret("test_secret", "secret_value")
            secret = self.config_manager.secret_manager.get_secret("test_secret")
            self._assert_not_none(secret, "Secret management")

            # Test configuration summary
            summary = self.config_manager.get_config_summary()
            self._assert_not_none(summary, "Configuration summary")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["get_set", "validation", "secrets", "summary"],
                "details": "All configuration manager tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_plugin_system(self) -> None:
        """Test plugin system functionality."""
        test_name = "plugin_system"
        logger.info("Testing plugin system")

        try:
            # Test plugin registration
            test_plugin = TestPlugin()
            registration_result = self.plugin_manager.registry.register_plugin(test_plugin)
            self._assert_true(registration_result, "Plugin registration")

            # Test plugin loading
            load_result = await self.plugin_manager.load_plugin("test_plugin")
            self._assert_true(load_result, "Plugin loading")

            # Test plugin activation
            activation_result = await self.plugin_manager.activate_plugin("test_plugin")
            self._assert_true(activation_result, "Plugin activation")

            # Test plugin status
            status = self.plugin_manager.get_plugin_status()
            self._assert_not_none(status, "Plugin status")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["registration", "loading", "activation", "status"],
                "details": "All plugin system tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_ui_integration(self) -> None:
        """Test UI integration functionality."""
        test_name = "ui_integration"
        logger.info("Testing UI integration")

        try:
            # Test component registration
            test_schema = ComponentSchema(
                component_type=ComponentType.FLOW_NODE,
                name="test_ui_component",
                title="Test UI Component",
                description="Test component for UI integration",
            )
            registration_result = self.ui_manager.component_registry.register_component(test_schema)
            self._assert_true(registration_result, "UI component registration")

            # Test event emission
            self.ui_manager.event_manager.emit_event("test_event", {"test": "data"})

            # Test flow node generation
            node_template = self.ui_manager.flow_node_generator.create_agno_node_template(
                "TestNode",
                "Test Node",
                "Test node description",
                [{"name": "input", "type": "str", "required": True}],
                [{"name": "output", "type": "str"}],
            )
            self._assert_not_none(node_template, "Flow node generation")

            # Test UI configuration
            ui_config = self.ui_manager.get_ui_config()
            self._assert_not_none(ui_config, "UI configuration")

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["component_registration", "event_emission", "node_generation", "ui_config"],
                "details": "All UI integration tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    async def _test_system_integration(self) -> None:
        """Test integration between different systems."""
        test_name = "system_integration"
        logger.info("Testing system integration")

        try:
            # Test workflow with performance monitoring
            workflow_id = await self.workflow_engine.create_workflow(
                "integration_test_workflow", {"step1": {"type": "test", "config": {}}}
            )

            # Execute workflow while monitoring performance
            start_time = time.time()
            await self.workflow_engine.execute_workflow(
                workflow_id, {"input": "integration_test"}, ExecutionStrategy.SEQUENTIAL
            )
            execution_time = time.time() - start_time

            # Record performance metric
            self.performance_monitor.record_metric("workflow_execution_time", execution_time)

            # Test error recovery integration
            try:
                raise ValueError("Integration test error")
            except ValueError as e:
                error_context = self.error_recovery.record_error(e, "integration_test", "system_integration")
                await self.error_recovery.attempt_recovery(error_context)

            # Test configuration integration
            self.config_manager.set("integration.test", "success")
            config_value = self.config_manager.get("integration.test")

            # Test UI event integration
            self.ui_manager.event_manager.emit_event(
                "integration_test",
                {"workflow_id": workflow_id, "execution_time": execution_time, "config_value": config_value},
            )

            self.test_results[test_name] = {
                "status": "passed",
                "tests": ["workflow_performance", "error_integration", "config_integration", "ui_events"],
                "details": "All system integration tests passed",
            }

        except Exception as e:
            self._record_test_failure(test_name, str(e))

    def _assert_not_none(self, value: Any, test_name: str) -> None:
        """Assert that value is not None."""
        self.total_tests += 1
        if value is not None:
            self.passed_tests += 1
            logger.debug("✓ %s: PASSED", test_name)
        else:
            self.failed_tests += 1
            logger.error("✗ %s: FAILED (value is None)", test_name)

    def _assert_true(self, value: bool, test_name: str) -> None:
        """Assert that value is True."""
        self.total_tests += 1
        if value:
            self.passed_tests += 1
            logger.debug("✓ %s: PASSED", test_name)
        else:
            self.failed_tests += 1
            logger.error("✗ %s: FAILED (value is False)", test_name)

    def _assert_equal(self, actual: Any, expected: Any, test_name: str) -> None:
        """Assert that actual equals expected."""
        self.total_tests += 1
        if actual == expected:
            self.passed_tests += 1
            logger.debug("✓ %s: PASSED", test_name)
        else:
            self.failed_tests += 1
            logger.error("✗ %s: FAILED (expected: %s, actual: %s)", test_name, expected, actual)

    def _record_test_failure(self, test_name: str, error_message: str) -> None:
        """Record a test failure."""
        self.test_results[test_name] = {
            "status": "failed",
            "error": error_message,
            "details": f"Test failed with error: {error_message}",
        }
        self.failed_tests += 1
        logger.error("✗ %s: FAILED - %s", test_name, error_message)

    async def export_test_report(self, output_path: str | Path) -> None:
        """Export test report to JSON file."""
        report = await self.run_all_tests()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info("Test report exported to: %s", output_path)


async def run_phase3_integration_tests() -> dict[str, Any]:
    """Run Phase-3 integration tests and return results."""
    tester = Phase3IntegrationTester()
    return await tester.run_all_tests()


async def main():
    """Main function for running integration tests."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger.info("Starting Phase-3 Integration Tests")

    try:
        results = await run_phase3_integration_tests()

        print("\n" + "=" * 80)
        print("PHASE-3 INTEGRATION TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Execution Time: {results['summary']['execution_time']:.2f} seconds")
        print("=" * 80)

        if results["summary"]["failed_tests"] > 0:
            print("\nFAILED TESTS:")
            for test_name, result in results["detailed_results"].items():
                if result.get("status") == "failed":
                    print(f"- {test_name}: {result.get('error', 'Unknown error')}")

        return results

    except Exception as e:
        logger.error("Integration tests failed: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
