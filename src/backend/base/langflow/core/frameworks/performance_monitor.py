"""
Performance Monitoring System for Agno Framework Integration
Provides comprehensive performance tracking, metrics collection, and analytics.
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric"""

    name: str
    value: float
    timestamp: datetime
    component: str | None = None
    category: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentPerformanceStats:
    """Performance statistics for a component"""

    component_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    min_execution_time: float = float("inf")
    max_execution_time: float = 0.0
    last_24h_executions: int = 0
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0


class PerformanceMonitor:
    """Comprehensive performance monitoring system for Agno framework"""

    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.component_stats: dict[str, ComponentPerformanceStats] = {}
        self.real_time_metrics: dict[str, float] = {}
        self.alert_thresholds: dict[str, float] = {
            "max_execution_time": 30.0,
            "error_rate_threshold": 0.1,
            "memory_usage_mb": 1000,
            "cpu_usage_percent": 80,
        }
        self.active_monitoring = True
        self.monitoring_tasks: list = []

        logger.info("PerformanceMonitor initialized")

    async def start_monitoring(self):
        """Start background monitoring tasks"""
        self.active_monitoring = True

        # Start background tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._collect_system_metrics()),
            asyncio.create_task(self._cleanup_old_metrics()),
            asyncio.create_task(self._check_alerts()),
        ]

        logger.info("Performance monitoring started")

    async def stop_monitoring(self):
        """Stop monitoring and cleanup tasks"""
        self.active_monitoring = False

        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self.monitoring_tasks.clear()
        logger.info("Performance monitoring stopped")

    def record_execution(
        self, component_name: str, execution_time: float, success: bool, metadata: dict[str, Any] | None = None
    ):
        """Record component execution metrics"""
        metric = PerformanceMetric(
            name="execution_time",
            value=execution_time,
            timestamp=datetime.now(),
            component=component_name,
            category="execution",
            metadata=metadata or {},
        )

        self.metrics_history.append(metric)
        self._update_component_stats(component_name, execution_time, success)

        # Update real-time metrics
        self.real_time_metrics[f"{component_name}_last_execution_time"] = execution_time
        self.real_time_metrics["total_executions"] = self.real_time_metrics.get("total_executions", 0) + 1

        # Check for performance alerts
        if execution_time > self.alert_thresholds["max_execution_time"]:
            self._trigger_alert("slow_execution", f"Component {component_name} took {execution_time:.2f}s")

    def record_metric(
        self,
        name: str,
        value: float,
        component: str | None = None,
        category: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Record a custom performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            component=component,
            category=category,
            metadata=metadata or {},
        )

        self.metrics_history.append(metric)
        self.real_time_metrics[name] = value

    def get_component_stats(self, component_name: str) -> ComponentPerformanceStats | None:
        """Get performance statistics for a specific component"""
        return self.component_stats.get(component_name)

    def get_all_component_stats(self) -> dict[str, ComponentPerformanceStats]:
        """Get performance statistics for all components"""
        return self.component_stats.copy()

    def get_real_time_metrics(self) -> dict[str, float]:
        """Get current real-time metrics"""
        return self.real_time_metrics.copy()

    def get_metrics_history(
        self,
        component: str | None = None,
        category: str | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[PerformanceMetric]:
        """Get filtered metrics history"""
        filtered_metrics = []

        for metric in self.metrics_history:
            # Apply filters
            if component and metric.component != component:
                continue
            if category and metric.category != category:
                continue
            if since and metric.timestamp < since:
                continue

            filtered_metrics.append(metric)

            if limit and len(filtered_metrics) >= limit:
                break

        return filtered_metrics

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall performance summary"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)

        # Calculate summary statistics
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= last_hour]
        daily_metrics = [m for m in self.metrics_history if m.timestamp >= last_24h]

        summary = {
            "total_components": len(self.component_stats),
            "total_executions": sum(stats.total_executions for stats in self.component_stats.values()),
            "successful_executions": sum(stats.successful_executions for stats in self.component_stats.values()),
            "failed_executions": sum(stats.failed_executions for stats in self.component_stats.values()),
            "overall_error_rate": 0,
            "average_execution_time": 0,
            "executions_last_hour": len([m for m in recent_metrics if m.name == "execution_time"]),
            "executions_last_24h": len([m for m in daily_metrics if m.name == "execution_time"]),
            "top_performers": [],
            "slow_components": [],
            "high_error_components": [],
        }

        # Calculate overall error rate
        total_executions = summary["total_executions"]
        if total_executions > 0:
            summary["overall_error_rate"] = summary["failed_executions"] / total_executions

        # Calculate average execution time
        execution_times = [m.value for m in self.metrics_history if m.name == "execution_time"]
        if execution_times:
            summary["average_execution_time"] = statistics.mean(execution_times)

        # Identify top performers and problem components
        sorted_components = sorted(self.component_stats.values(), key=lambda x: x.average_execution_time)

        summary["top_performers"] = [comp.component_name for comp in sorted_components[:5]]
        summary["slow_components"] = [comp.component_name for comp in sorted_components[-5:]]
        summary["high_error_components"] = [
            comp.component_name for comp in self.component_stats.values() if comp.error_rate > 0.1
        ]

        return summary

    def generate_performance_report(self) -> str:
        """Generate a detailed performance report"""
        summary = self.get_performance_summary()

        report = f"""
# Performance Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Statistics
- Total Components: {summary["total_components"]}
- Total Executions: {summary["total_executions"]}
- Success Rate: {(1 - summary["overall_error_rate"]) * 100:.1f}%
- Average Execution Time: {summary["average_execution_time"]:.3f}s
- Executions (Last Hour): {summary["executions_last_hour"]}
- Executions (Last 24h): {summary["executions_last_24h"]}

## Top Performing Components
{chr(10).join(f"- {comp}" for comp in summary["top_performers"])}

## Components Needing Attention
### Slow Components
{chr(10).join(f"- {comp}" for comp in summary["slow_components"])}

### High Error Rate Components  
{chr(10).join(f"- {comp}" for comp in summary["high_error_components"])}

## Component Details
"""

        for comp_name, stats in self.component_stats.items():
            report += f"""
### {comp_name}
- Executions: {stats.total_executions} (Success: {stats.successful_executions}, Failed: {stats.failed_executions})
- Error Rate: {stats.error_rate * 100:.1f}%
- Execution Time: Avg {stats.average_execution_time:.3f}s, Min {stats.min_execution_time:.3f}s, Max {stats.max_execution_time:.3f}s
- Throughput: {stats.throughput_per_minute:.1f} executions/min
"""

        return report

    def get_component_trend_data(self, component_name: str, hours: int = 24) -> dict[str, Any]:
        """Get trend data for a specific component"""
        since = datetime.now() - timedelta(hours=hours)
        component_metrics = self.get_metrics_history(component=component_name, category="execution", since=since)

        if not component_metrics:
            return {"component": component_name, "no_data": True}

        # Group by hour for trend analysis
        hourly_data = defaultdict(list)
        for metric in component_metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(metric.value)

        trend_data = []
        for hour, values in sorted(hourly_data.items()):
            trend_data.append(
                {
                    "timestamp": hour.isoformat(),
                    "count": len(values),
                    "avg_time": statistics.mean(values),
                    "min_time": min(values),
                    "max_time": max(values),
                }
            )

        return {
            "component": component_name,
            "trend_data": trend_data,
            "total_executions": len(component_metrics),
            "time_range_hours": hours,
        }

    async def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        while self.active_monitoring:
            try:
                try:
                    import psutil

                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.record_metric("cpu_usage_percent", cpu_percent, category="system")

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.record_metric("memory_usage_mb", memory.used / 1024 / 1024, category="system")
                    self.record_metric("memory_usage_percent", memory.percent, category="system")

                    # Check alerts
                    if cpu_percent > self.alert_thresholds["cpu_usage_percent"]:
                        self._trigger_alert("high_cpu", f"CPU usage: {cpu_percent:.1f}%")

                    if memory.used / 1024 / 1024 > self.alert_thresholds["memory_usage_mb"]:
                        self._trigger_alert("high_memory", f"Memory usage: {memory.used / 1024 / 1024:.1f}MB")

                except ImportError:
                    # psutil not available, record basic metrics
                    self.record_metric(
                        "system_status", 1.0, category="system", metadata={"note": "psutil not available"}
                    )

            except Exception as e:
                logger.exception("Error collecting system metrics", extra={"error": str(e)})

            await asyncio.sleep(10)  # Collect every 10 seconds

    async def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory issues"""
        while self.active_monitoring:
            try:
                # Remove metrics older than 7 days
                cutoff_time = datetime.now() - timedelta(days=7)

                old_count = len(self.metrics_history)
                # Note: deque automatically handles max size, but we can do additional cleanup
                filtered_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
                self.metrics_history.clear()
                self.metrics_history.extend(filtered_metrics)

                new_count = len(self.metrics_history)

                if old_count != new_count:
                    logger.info("Cleaned up old metrics", extra={"old_count": old_count, "new_count": new_count})

            except Exception as e:
                logger.exception("Error during metrics cleanup", extra={"error": str(e)})

            await asyncio.sleep(3600)  # Cleanup every hour

    async def _check_alerts(self):
        """Check for performance alerts"""
        while self.active_monitoring:
            try:
                # Check component error rates
                for comp_name, stats in self.component_stats.items():
                    if stats.error_rate > self.alert_thresholds["error_rate_threshold"]:
                        self._trigger_alert(
                            "high_error_rate", f"Component {comp_name} error rate: {stats.error_rate * 100:.1f}%"
                        )

            except Exception as e:
                logger.exception("Error checking alerts", extra={"error": str(e)})

            await asyncio.sleep(60)  # Check every minute

    def _update_component_stats(self, component_name: str, execution_time: float, success: bool):
        """Update component performance statistics"""
        if component_name not in self.component_stats:
            self.component_stats[component_name] = ComponentPerformanceStats(component_name=component_name)

        stats = self.component_stats[component_name]

        # Update basic counts
        stats.total_executions += 1
        if success:
            stats.successful_executions += 1
        else:
            stats.failed_executions += 1

        # Update execution time statistics
        if stats.total_executions == 1:
            stats.average_execution_time = execution_time
        else:
            stats.average_execution_time = (
                stats.average_execution_time * (stats.total_executions - 1) + execution_time
            ) / stats.total_executions

        stats.min_execution_time = min(stats.min_execution_time, execution_time)
        stats.max_execution_time = max(stats.max_execution_time, execution_time)

        # Update error rate
        stats.error_rate = stats.failed_executions / stats.total_executions

        # Update 24h executions and throughput
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        recent_executions = len(
            [
                m
                for m in self.metrics_history
                if m.component == component_name and m.name == "execution_time" and m.timestamp >= last_24h
            ]
        )
        stats.last_24h_executions = recent_executions
        stats.throughput_per_minute = recent_executions / (24 * 60)  # executions per minute over 24h

    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger a performance alert"""
        alert_metric = PerformanceMetric(
            name=f"alert_{alert_type}",
            value=1.0,
            timestamp=datetime.now(),
            category="alert",
            metadata={"message": message},
        )

        self.metrics_history.append(alert_metric)
        logger.warning("Performance Alert", extra={"alert_type": alert_type, "message": message})

    def set_alert_threshold(self, metric_name: str, threshold: float):
        """Set custom alert threshold"""
        self.alert_thresholds[metric_name] = threshold
        logger.info("Alert threshold updated", extra={"metric": metric_name, "threshold": threshold})

    def get_alert_history(self, hours: int = 24) -> list[PerformanceMetric]:
        """Get recent alert history"""
        since = datetime.now() - timedelta(hours=hours)
        return self.get_metrics_history(category="alert", since=since)

    def export_metrics(self, format_type: str = "json") -> str | dict:
        """Export metrics in specified format"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "component_stats": {
                name: {
                    "component_name": stats.component_name,
                    "total_executions": stats.total_executions,
                    "successful_executions": stats.successful_executions,
                    "failed_executions": stats.failed_executions,
                    "average_execution_time": stats.average_execution_time,
                    "min_execution_time": stats.min_execution_time,
                    "max_execution_time": stats.max_execution_time,
                    "error_rate": stats.error_rate,
                    "throughput_per_minute": stats.throughput_per_minute,
                }
                for name, stats in self.component_stats.items()
            },
            "recent_metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "component": m.component,
                    "category": m.category,
                    "metadata": m.metadata,
                }
                for m in list(self.metrics_history)[-100:]  # Last 100 metrics
            ],
            "real_time_metrics": self.real_time_metrics,
        }

        if format_type == "json":
            import json

            return json.dumps(data, indent=2)
        else:
            return data

    def reset_stats(self, component_name: str | None = None):
        """Reset statistics for a component or all components"""
        if component_name:
            if component_name in self.component_stats:
                del self.component_stats[component_name]
                logger.info("Reset component stats", extra={"component": component_name})
        else:
            self.component_stats.clear()
            self.metrics_history.clear()
            self.real_time_metrics.clear()
            logger.info("Reset all performance stats")
