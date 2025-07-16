"""
UI Integration Components for Agno Framework Integration.

This module provides frontend integration helpers, React components,
and utilities for seamless UI integration with the Agno framework.
"""

import json
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of UI components."""

    FLOW_NODE = "flow_node"
    INPUT_FIELD = "input_field"
    OUTPUT_DISPLAY = "output_display"
    CONTROL_PANEL = "control_panel"
    VISUALIZATION = "visualization"
    DASHBOARD = "dashboard"


class ThemeMode(Enum):
    """UI theme modes."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


@dataclass
class ComponentSchema:
    """Schema definition for UI components."""

    component_type: ComponentType
    name: str
    title: str
    description: str
    props: dict[str, Any] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    styling: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class UIState:
    """UI state management."""

    current_theme: ThemeMode = ThemeMode.AUTO
    active_components: list[str] = field(default_factory=list)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    layout_config: dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class UIEventManager:
    """Manages UI events and communication between frontend and backend."""

    def __init__(self):
        self.event_handlers: dict[str, list[Callable]] = {}
        self.event_history: list[dict[str, Any]] = []
        self.max_history = 1000

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug("Event handler registered for: %s", event_type)

    def unregister_handler(self, event_type: str, handler: Callable) -> bool:
        """Unregister an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug("Event handler unregistered for: %s", event_type)
            return True
        return False

    def emit_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.event_history),
        }

        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Call handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("Error in event handler for %s: %s", event_type, e)

    def get_event_history(self, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get event history, optionally filtered by type."""
        events = self.event_history
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:] if limit else events


class ReactComponentGenerator:
    """Generates React components from component schemas."""

    def __init__(self):
        self.component_templates = self._load_component_templates()

    def _load_component_templates(self) -> dict[str, str]:
        """Load component templates for different component types."""
        return {
            ComponentType.FLOW_NODE.value: """
import React from 'react';
import { Handle, Position } from 'reactflow';

interface {component_name}Props {{
  {props_interface}
}}

const {component_name}: React.FC<{component_name}Props> = ({{
  {props_destructured}
}}) => {{
  return (
    <div className="custom-node {css_classes}">
      <Handle type="target" position={{Position.Top}} />
      <div className="node-content">
        <h3>{{{title}}}</h3>
        <div className="node-body">
          {body_content}
        </div>
      </div>
      <Handle type="source" position={{Position.Bottom}} />
    </div>
  );
}};

export default {component_name};
""",
            ComponentType.INPUT_FIELD.value: """
import React, {{ useState }} from 'react';

interface {component_name}Props {{
  {props_interface}
  onChange?: (value: any) => void;
}}

const {component_name}: React.FC<{component_name}Props> = ({{
  {props_destructured},
  onChange
}}) => {{
  const [value, setValue] = useState({default_value});

  const handleChange = (newValue: any) => {{
    setValue(newValue);
    if (onChange) {{
      onChange(newValue);
    }}
  }};

  return (
    <div className="input-field {css_classes}">
      <label htmlFor="{field_id}">{{{label}}}</label>
      {input_element}
    </div>
  );
}};

export default {component_name};
""",
            ComponentType.DASHBOARD.value: """
import React, {{ useState, useEffect }} from 'react';
import {{ Card, Grid, Typography }} from '@mui/material';

interface {component_name}Props {{
  {props_interface}
}}

const {component_name}: React.FC<{component_name}Props> = ({{
  {props_destructured}
}}) => {{
  const [dashboardData, setDashboardData] = useState<any>({{}});

  useEffect(() => {{
    // Load dashboard data
    {data_loading_logic}
  }}, []);

  return (
    <div className="dashboard {css_classes}">
      <Typography variant="h4" gutterBottom>
        {{{title}}}
      </Typography>
      <Grid container spacing={{3}}>
        {dashboard_widgets}
      </Grid>
    </div>
  );
}};

export default {component_name};
""",
        }

    def generate_component(self, schema: ComponentSchema) -> dict[str, Any]:
        """Generate React component from schema."""
        try:
            template = self.component_templates.get(schema.component_type.value)
            if not template:
                raise ValueError(f"No template for component type: {schema.component_type}")

            # Generate component code
            component_code = self._render_template(template, schema)

            # Generate TypeScript interfaces
            interfaces = self._generate_interfaces(schema)

            # Generate styles
            styles = self._generate_styles(schema)

            return {
                "component_code": component_code,
                "interfaces": interfaces,
                "styles": styles,
                "dependencies": schema.dependencies,
                "metadata": {
                    "name": schema.name,
                    "type": schema.component_type.value,
                    "generated_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error("Error generating component %s: %s", schema.name, e)
            raise

    def _render_template(self, template: str, schema: ComponentSchema) -> str:
        """Render component template with schema data."""
        replacements = {
            "component_name": self._to_pascal_case(schema.name),
            "title": schema.title,
            "css_classes": " ".join(schema.styling.get("classes", [])),
            "props_interface": self._generate_props_interface(schema.props),
            "props_destructured": ", ".join(schema.props.keys()),
        }

        # Component-specific replacements
        if schema.component_type == ComponentType.FLOW_NODE:
            replacements.update(self._get_flow_node_replacements(schema))
        elif schema.component_type == ComponentType.INPUT_FIELD:
            replacements.update(self._get_input_field_replacements(schema))
        elif schema.component_type == ComponentType.DASHBOARD:
            replacements.update(self._get_dashboard_replacements(schema))

        # Replace placeholders
        result = template
        for key, value in replacements.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result

    def _generate_props_interface(self, props: dict[str, Any]) -> str:
        """Generate TypeScript interface for props."""
        interface_lines = []
        for prop_name, prop_config in props.items():
            prop_type = prop_config.get("type", "any")
            optional = "?" if prop_config.get("optional", False) else ""
            interface_lines.append(f"  {prop_name}{optional}: {prop_type};")
        return "\n".join(interface_lines)

    def _generate_interfaces(self, schema: ComponentSchema) -> str:
        """Generate TypeScript interfaces for the component."""
        return f"""
export interface {self._to_pascal_case(schema.name)}Data {{
  {self._generate_props_interface(schema.props)}
}}

export interface {self._to_pascal_case(schema.name)}Events {{
  {"; ".join([f"on{self._to_pascal_case(event)}: () => void" for event in schema.events])}
}}
"""

    def _generate_styles(self, schema: ComponentSchema) -> str:
        """Generate CSS styles for the component."""
        base_styles = schema.styling.get("css", {})

        css_rules = []
        for selector, rules in base_styles.items():
            rule_lines = [f"  {prop}: {value};" for prop, value in rules.items()]
            css_rules.append(f"{selector} {{\n" + "\n".join(rule_lines) + "\n}")

        return "\n\n".join(css_rules)

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        return "".join(word.capitalize() for word in text.replace("-", "_").split("_"))

    def _get_flow_node_replacements(self, schema: ComponentSchema) -> dict[str, str]:
        """Get flow node specific template replacements."""
        return {"body_content": schema.props.get("body_template", "<p>Flow Node Content</p>")}

    def _get_input_field_replacements(self, schema: ComponentSchema) -> dict[str, str]:
        """Get input field specific template replacements."""
        field_type = schema.props.get("input_type", "text")
        field_id = schema.name.replace(" ", "-").lower()

        input_elements = {
            "text": f'<input type="text" id="{field_id}" value={{value}} onChange={{(e) => handleChange(e.target.value)}} />',
            "number": f'<input type="number" id="{field_id}" value={{value}} onChange={{(e) => handleChange(Number(e.target.value))}} />',
            "select": f'<select id="{field_id}" value={{value}} onChange={{(e) => handleChange(e.target.value)}}>{self._generate_select_options(schema.props.get("options", []))}</select>',
            "textarea": f'<textarea id="{field_id}" value={{value}} onChange={{(e) => handleChange(e.target.value)}} />',
        }

        return {
            "field_id": field_id,
            "label": schema.title,
            "default_value": json.dumps(schema.props.get("default_value", "")),
            "input_element": input_elements.get(field_type, input_elements["text"]),
        }

    def _get_dashboard_replacements(self, schema: ComponentSchema) -> dict[str, str]:
        """Get dashboard specific template replacements."""
        widgets = schema.props.get("widgets", [])
        widget_components = []

        for widget in widgets:
            component_name = widget.get("component", "div")
            props_json = json.dumps(widget.get("props", {}))
            width = widget.get("width", 6)

            widget_component = f"""
        <Grid item xs={{12}} md={{{width}}}>
          <Card>
            <{component_name} {{...{props_json}}} />
          </Card>
        </Grid>"""
            widget_components.append(widget_component)

        return {
            "dashboard_widgets": "\n".join(widget_components),
            "data_loading_logic": schema.props.get("data_loader", "// Load data here"),
        }

    def _generate_select_options(self, options: list[dict[str, Any]]) -> str:
        """Generate select options JSX."""
        option_elements = []
        for option in options:
            value = option.get("value", "")
            label = option.get("label", value)
            option_elements.append(f'<option value="{value}">{label}</option>')
        return "".join(option_elements)

        if event_type:
            events = [e for e in events if e["type"] == event_type]

        return events[-limit:] if limit else events


class ComponentRegistry:
    """Registry for UI components and their schemas."""

    def __init__(self):
        self.components: dict[str, ComponentSchema] = {}
        self.component_instances: dict[str, dict[str, Any]] = {}
        self.templates: dict[str, str] = {}

    def register_component(self, schema: ComponentSchema) -> bool:
        """Register a UI component schema."""
        if schema.name in self.components:
            logger.warning("Component %s is already registered", schema.name)
            return False

        self.components[schema.name] = schema
        logger.info("Component %s registered successfully", schema.name)
        return True

    def unregister_component(self, component_name: str) -> bool:
        """Unregister a UI component."""
        if component_name not in self.components:
            return False

        del self.components[component_name]
        if component_name in self.component_instances:
            del self.component_instances[component_name]
        if component_name in self.templates:
            del self.templates[component_name]

        logger.info("Component %s unregistered", component_name)
        return True

    def get_component_schema(self, component_name: str) -> ComponentSchema | None:
        """Get component schema by name."""
        return self.components.get(component_name)

    def list_components(self, component_type: ComponentType | None = None) -> list[ComponentSchema]:
        """List all registered components, optionally filtered by type."""
        components = list(self.components.values())

        if component_type:
            components = [c for c in components if c.component_type == component_type]

        return components

    def register_template(self, component_name: str, template: str) -> None:
        """Register a React/HTML template for a component."""
        self.templates[component_name] = template
        logger.debug("Template registered for component: %s", component_name)

    def get_template(self, component_name: str) -> str | None:
        """Get template for a component."""
        return self.templates.get(component_name)


class FlowNodeGenerator:
    """Generates Langflow-compatible flow node definitions."""

    def __init__(self):
        self.node_templates: dict[str, dict[str, Any]] = {}

    def create_agno_node_template(
        self,
        node_name: str,
        display_name: str,
        description: str,
        inputs: list[dict[str, Any]],
        outputs: list[dict[str, Any]],
        parameters: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a flow node template for Agno components."""
        template = {
            "template": {
                "code": {
                    "type": "code",
                    "required": True,
                    "placeholder": "# Agno component implementation",
                    "list": False,
                    "show": True,
                    "multiline": True,
                    "value": self._generate_agno_code_template(node_name),
                    "fileTypes": ["py"],
                    "file_path": "",
                    "password": False,
                    "name": "code",
                    "advanced": False,
                    "dynamic": False,
                    "info": "",
                    "load_from_db": False,
                    "title_case": False,
                }
            },
            "description": description,
            "base_classes": ["BaseComponent"],
            "display_name": display_name,
            "documentation": f"https://docs.langflow.org/components/{node_name.lower()}",
            "custom_fields": {},
            "output_types": [output["type"] for output in outputs],
            "input_types": [input_item["type"] for input_item in inputs],
            "field_formatters": {},
            "beta": False,
            "flow": False,
        }

        # Add input parameters
        for input_item in inputs:
            template["template"][input_item["name"]] = {
                "type": input_item["type"],
                "required": input_item.get("required", False),
                "placeholder": input_item.get("placeholder", ""),
                "list": input_item.get("list", False),
                "show": input_item.get("show", True),
                "multiline": input_item.get("multiline", False),
                "value": input_item.get("default", ""),
                "name": input_item["name"],
                "display_name": input_item.get("display_name", input_item["name"]),
                "advanced": input_item.get("advanced", False),
                "dynamic": input_item.get("dynamic", False),
                "info": input_item.get("description", ""),
                "title_case": input_item.get("title_case", False),
            }

        # Add custom parameters
        if parameters:
            for param in parameters:
                template["template"][param["name"]] = param

        self.node_templates[node_name] = template
        return template

    def _generate_agno_code_template(self, node_name: str) -> str:
        """Generate Python code template for Agno node."""
        return f'''
from langflow.custom import CustomComponent
from langflow.core.frameworks.agno_adapter import AgnoAdapter
from langflow.schema import Data
from typing import Optional

class {node_name}(CustomComponent):
    display_name = "{node_name}"
    description = "Agno framework integration component"
    icon = "robot"
    
    def __init__(self):
        super().__init__()
        self.agno_adapter = AgnoAdapter()
    
    def build_config(self):
        return {{
            "input_data": {{
                "display_name": "Input Data",
                "info": "Input data for Agno processing",
                "required": True
            }},
            "agno_config": {{
                "display_name": "Agno Configuration",
                "info": "Configuration for Agno component",
                "advanced": True
            }}
        }}
    
    def build(
        self,
        input_data: Optional[Data] = None,
        agno_config: Optional[dict] = None
    ) -> Data:
        try:
            # Process data using Agno adapter
            result = self.agno_adapter.process(
                data=input_data,
                config=agno_config or {{}}
            )
            
            return Data(value=result)
            
        except Exception as e:
            self.status = f"Error: {{str(e)}}"
            raise e
'''

    def get_node_template(self, node_name: str) -> dict[str, Any] | None:
        """Get node template by name."""
        return self.node_templates.get(node_name)

    def export_node_templates(self, output_dir: str | Path) -> None:
        """Export all node templates to JSON files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for node_name, template in self.node_templates.items():
            file_path = output_dir / f"{node_name.lower()}_template.json"
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)

        logger.info("Exported %d node templates to %s", len(self.node_templates), output_dir)


class DashboardManager:
    """Manages dashboard components and layouts."""

    def __init__(self):
        self.dashboards: dict[str, dict[str, Any]] = {}
        self.widgets: dict[str, dict[str, Any]] = {}
        self.layouts: dict[str, dict[str, Any]] = {}

    def create_dashboard(
        self, dashboard_id: str, title: str, description: str, widgets: list[str] | None = None
    ) -> dict[str, Any]:
        """Create a new dashboard configuration."""
        dashboard = {
            "id": dashboard_id,
            "title": title,
            "description": description,
            "widgets": widgets or [],
            "layout": "grid",
            "theme": "auto",
            "refresh_interval": 30,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self.dashboards[dashboard_id] = dashboard
        return dashboard

    def add_widget(self, widget_id: str, widget_type: str, title: str, config: dict[str, Any]) -> dict[str, Any]:
        """Add a widget configuration."""
        widget = {
            "id": widget_id,
            "type": widget_type,
            "title": title,
            "config": config,
            "position": {"x": 0, "y": 0, "w": 6, "h": 4},
            "created_at": datetime.now().isoformat(),
        }

        self.widgets[widget_id] = widget
        return widget

    def create_performance_widget(self, widget_id: str) -> dict[str, Any]:
        """Create a performance monitoring widget."""
        return self.add_widget(
            widget_id,
            "performance_chart",
            "Performance Metrics",
            {
                "metrics": ["cpu_usage", "memory_usage", "response_time"],
                "time_range": "1h",
                "chart_type": "line",
                "refresh_rate": 5,
            },
        )

    def create_error_widget(self, widget_id: str) -> dict[str, Any]:
        """Create an error monitoring widget."""
        return self.add_widget(
            widget_id,
            "error_log",
            "Error Monitor",
            {
                "max_errors": 50,
                "severity_filter": ["error", "critical"],
                "auto_refresh": True,
                "show_stack_trace": False,
            },
        )

    def create_workflow_widget(self, widget_id: str) -> dict[str, Any]:
        """Create a workflow status widget."""
        return self.add_widget(
            widget_id,
            "workflow_status",
            "Workflow Status",
            {"show_running": True, "show_completed": True, "show_failed": True, "max_workflows": 20},
        )

    def get_dashboard_config(self, dashboard_id: str) -> dict[str, Any] | None:
        """Get dashboard configuration."""
        return self.dashboards.get(dashboard_id)

    def export_dashboard_config(self, dashboard_id: str, file_path: str | Path) -> None:
        """Export dashboard configuration to JSON file."""
        dashboard = self.get_dashboard_config(dashboard_id)
        if not dashboard:
            logger.error("Dashboard %s not found", dashboard_id)
            return

        # Include widget configurations
        widget_configs = {}
        for widget_id in dashboard["widgets"]:
            if widget_id in self.widgets:
                widget_configs[widget_id] = self.widgets[widget_id]

        export_data = {"dashboard": dashboard, "widgets": widget_configs}

        file_path = Path(file_path)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        logger.info("Dashboard %s exported to %s", dashboard_id, file_path)


class UIIntegrationManager:
    """Main UI integration management system."""

    def __init__(self):
        self.event_manager = UIEventManager()
        self.component_registry = ComponentRegistry()
        self.flow_node_generator = FlowNodeGenerator()
        self.dashboard_manager = DashboardManager()
        self.ui_state = UIState()

    def initialize(self) -> None:
        """Initialize UI integration system."""
        # Register default event handlers
        self.event_manager.register_handler("component_loaded", self._on_component_loaded)
        self.event_manager.register_handler("theme_changed", self._on_theme_changed)
        self.event_manager.register_handler("user_action", self._on_user_action)

        # Create default dashboard
        self.dashboard_manager.create_dashboard(
            "main_dashboard", "Agno Framework Dashboard", "Main monitoring dashboard for Agno framework integration"
        )

        logger.info("UI integration system initialized")

    def _on_component_loaded(self, event: dict[str, Any]) -> None:
        """Handle component loaded event."""
        component_name = event["data"].get("component_name")
        if component_name:
            self.ui_state.active_components.append(component_name)
            self.ui_state.last_updated = datetime.now()

    def _on_theme_changed(self, event: dict[str, Any]) -> None:
        """Handle theme change event."""
        new_theme = event["data"].get("theme")
        if new_theme in [mode.value for mode in ThemeMode]:
            self.ui_state.current_theme = ThemeMode(new_theme)
            self.ui_state.last_updated = datetime.now()

    def _on_user_action(self, event: dict[str, Any]) -> None:
        """Handle user action event."""
        action = event["data"].get("action")
        if action:
            logger.debug("User action: %s", action)

    def generate_react_component(self, component_name: str) -> str | None:
        """Generate React component code for a registered component."""
        schema = self.component_registry.get_component_schema(component_name)
        if not schema:
            return None

        # Generate React component template
        react_code = f"""
import React, {{ useState, useEffect }} from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';

interface {schema.name}Props {{
  {self._generate_props_interface(schema.props)}
}}

export const {schema.name}: React.FC<{schema.name}Props> = ({{
  {", ".join(schema.props.keys())}
}}) => {{
  const [state, setState] = useState({{}});
  
  useEffect(() => {{
    // Component initialization
  }}, []);
  
  return (
    <Card className="agno-component {schema.name.lower()}">
      <CardHeader>
        <CardTitle>{schema.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="component-content">
          {{/* Component implementation */}}
        </div>
      </CardContent>
    </Card>
  );
}};

export default {schema.name};
"""

        return react_code

    def _generate_props_interface(self, props: dict[str, Any]) -> str:
        """Generate TypeScript interface for component props."""
        prop_lines = []
        for prop_name, prop_config in props.items():
            prop_type = prop_config.get("type", "any")
            optional = "?" if not prop_config.get("required", False) else ""
            prop_lines.append(f"  {prop_name}{optional}: {prop_type};")

        return "\n".join(prop_lines)

    def get_ui_config(self) -> dict[str, Any]:
        """Get complete UI configuration for frontend."""
        return {
            "theme": self.ui_state.current_theme.value,
            "components": [
                {
                    "name": schema.name,
                    "type": schema.component_type.value,
                    "title": schema.title,
                    "description": schema.description,
                    "props": schema.props,
                    "events": schema.events,
                }
                for schema in self.component_registry.list_components()
            ],
            "dashboards": list(self.dashboard_manager.dashboards.values()),
            "widgets": list(self.dashboard_manager.widgets.values()),
            "active_components": self.ui_state.active_components,
            "user_preferences": self.ui_state.user_preferences,
        }

    def export_frontend_config(self, output_dir: str | Path) -> None:
        """Export complete frontend configuration."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export UI config
        config_file = output_dir / "ui_config.json"
        with config_file.open("w", encoding="utf-8") as f:
            json.dump(self.get_ui_config(), f, indent=2)

        # Export React components
        components_dir = output_dir / "components"
        components_dir.mkdir(exist_ok=True)

        for component_name in self.component_registry.components:
            react_code = self.generate_react_component(component_name)
            if react_code:
                component_file = components_dir / f"{component_name}.tsx"
                with component_file.open("w", encoding="utf-8") as f:
                    f.write(react_code)

        # Export node templates
        templates_dir = output_dir / "templates"
        self.flow_node_generator.export_node_templates(templates_dir)

        logger.info("Frontend configuration exported to %s", output_dir)


# Global UI integration manager instance
ui_manager = UIIntegrationManager()


# Convenience functions
def register_ui_component(schema: ComponentSchema) -> bool:
    """Register a UI component."""
    return ui_manager.component_registry.register_component(schema)


def emit_ui_event(event_type: str, data: dict[str, Any]) -> None:
    """Emit a UI event."""
    ui_manager.event_manager.emit_event(event_type, data)


def create_flow_node(
    node_name: str, display_name: str, description: str, inputs: list[dict[str, Any]], outputs: list[dict[str, Any]]
) -> dict[str, Any]:
    """Create a Langflow node template."""
    return ui_manager.flow_node_generator.create_agno_node_template(
        node_name, display_name, description, inputs, outputs
    )


def get_ui_config() -> dict[str, Any]:
    """Get UI configuration."""
    return ui_manager.get_ui_config()


def create_dashboard_widget(widget_type: str, widget_id: str) -> dict[str, Any] | None:
    """Create a dashboard widget."""
    if widget_type == "performance":
        return ui_manager.dashboard_manager.create_performance_widget(widget_id)
    elif widget_type == "error":
        return ui_manager.dashboard_manager.create_error_widget(widget_id)
    elif widget_type == "workflow":
        return ui_manager.dashboard_manager.create_workflow_widget(widget_id)
    return None
