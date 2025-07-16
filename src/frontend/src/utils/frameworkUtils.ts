import { APIClassType, APIDataType } from "@/types/api";
import { FrameworkComponent } from "@/controllers/API/queries/frameworks/use-get-framework-components";

/**
 * Transforms framework components into the APIDataType format expected by the sidebar
 */
export function transformFrameworkComponentsToAPIData(
  components: FrameworkComponent[]
): APIDataType {
  const apiData: APIDataType = {};

  components.forEach((component) => {
    const category = component.category || "Other";
    
    // Ensure category exists
    if (!apiData[category]) {
      apiData[category] = {};
    }

    // Transform inputs to template format
    const template: Record<string, any> = {};
    component.inputs.forEach((input) => {
      template[input.name] = {
        type: input.type,
        required: input.required,
        placeholder: input.description,
        list: input.type === "list",
        show: true,
        multiline: false,
        value: input.default,
        options: input.options || undefined,
        display_name: input.display_name,
        advanced: false,
        dynamic: false,
        info: input.description,
        input_types: [input.type],
        name: input.name,
      };
    });

    // Transform outputs format
    const outputs = component.outputs.map((output) => ({
      types: [output.type],
      name: output.name,
      display_name: output.display_name,
      method: output.name,
    }));

    // Create APIClassType object
    const apiClass: APIClassType = {
      base_classes: [component.category],
      description: component.description,
      template,
      display_name: component.display_name,
      documentation: component.documentation_url || "",
      custom_fields: {},
      output_types: component.outputs.map((o) => o.type),
      input_types: component.inputs.map((i) => i.type),
      type: component.id,
      icon: component.icon || undefined,
      is_input: component.category === "Inputs",
      is_output: component.category === "Outputs",
      beta: false,
      legacy: false,
      official: true,
      outputs,
      frozen: false,
      lf_version: component.version,
      last_updated: component.updated_at || component.created_at,
      field_order: component.inputs.map((i) => i.name),
    };

    apiData[category][component.display_name] = apiClass;
  });

  return apiData;
}

/**
 * Groups components by category for easier filtering
 */
export function groupComponentsByCategory(components: FrameworkComponent[]): Record<string, FrameworkComponent[]> {
  return components.reduce((acc, component) => {
    const category = component.category || "Other";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(component);
    return acc;
  }, {} as Record<string, FrameworkComponent[]>);
}
