import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export const useGetFrameworkComponents: useQueryFunctionType<
  string,
  any,
  { enabled?: boolean }
> = (framework, options) => {
  const { query } = UseRequestProcessor();

  const getFrameworkComponentsFn = async (framework: string): Promise<any> => {
    try {
      // If it's langflow, use the existing /api/v1/all endpoint
      if (framework === "langflow") {
        const response = await api.get(`${getURL("ALL")}?force_refresh=true`);
        return response?.data;
      } else {
        // For other frameworks, use the new framework-specific endpoint
        const response = await api.get(`${getURL("FRAMEWORKS")}/${framework}/components`);
        const data = response?.data;
        
        // Convert agno format to langflow format for compatibility
        if (data?.components && Array.isArray(data.components)) {
          const converted: any = {};
          
          // Group components by category
          data.components.forEach((component: any) => {
            const category = component.category || "Other";
            if (!converted[category]) {
              converted[category] = {};
            }
            
            // Convert agno component to langflow format
            converted[category][component.name] = {
              template: component.inputs?.reduce((acc: any, input: any) => {
                acc[input.name] = {
                  display_name: input.display_name,
                  type: input.type,
                  required: input.required,
                  description: input.description,
                  default: input.default,
                  options: input.options,
                  min_value: input.min_value,
                  max_value: input.max_value,
                };
                return acc;
              }, {}) || {},
              description: component.description,
              icon: component.icon || component.category,
              base_classes: [component.outputs?.[0]?.type || "Component"],
              display_name: component.display_name,
              documentation: component.documentation_url,
              minimized: false,
              custom_fields: {},
              output_types: component.outputs?.map((output: any) => output.type) || [],
              pinned: false,
              conditional_paths: [],
              frozen: false,
              outputs: component.outputs?.map((output: any) => ({
                display_name: output.display_name,
                name: output.name,
                type: output.type,
                description: output.description,
              })) || [],
              field_order: component.inputs?.map((input: any) => input.name) || [],
              beta: false,
              legacy: false,
              edited: false,
              metadata: {
                framework: component.framework,
                version: component.version,
                id: component.id,
              },
              tool_mode: false,
            };
          });
          
          return converted;
        }
        
        return data;
      }
    } catch (error) {
      console.error(`[Framework Components] Error fetching components for ${framework}:`, error);
      throw error;
    }
  };

  const queryResult = query(
    ["useGetFrameworkComponents", framework],
    () => getFrameworkComponentsFn(framework),
    {
      refetchOnWindowFocus: false,
      enabled: !!framework,
      ...options,
    },
  );

  return queryResult;
};
