import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useTypesStore } from "@/stores/typesStore";
import { APIObjectType, useQueryFunctionType } from "../../../../types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

// Import the framework store from the component
import { useFrameworkStore } from "@/components/frameworkSwitcher";

export const useGetTypes: useQueryFunctionType<
  undefined,
  any,
  { checkCache?: boolean }
> = (options) => {
  const { query } = UseRequestProcessor();
  const setLoading = useFlowsManagerStore((state) => state.setIsLoading);
  const setTypes = useTypesStore((state) => state.setTypes);
  const selectedFramework = useFrameworkStore((state) => state.selectedFramework);

  const getTypesFn = async (checkCache = false) => {
    try {
      if (checkCache) {
        const data = useTypesStore.getState().types;
        if (data && Object.keys(data).length > 0) {
          return data;
        }
      }

      console.log("Fetching types for framework:", selectedFramework);

      let response;
      // If it's langflow or no framework selected, use the existing /api/v1/all endpoint
      if (!selectedFramework || selectedFramework === "langflow") {
        response = await api.get<APIObjectType>(
          `${getURL("ALL")}?force_refresh=true`,
        );
      } else {
        // For other frameworks, use the new framework-specific endpoint
        response = await api.get<APIObjectType>(
          `${getURL("FRAMEWORKS")}/${selectedFramework}/components`,
        );
      }
      
      let data = response?.data;
      
      console.log("Received API response data:", data);
      
      // Validate the response data
      if (!data || typeof data !== 'object') {
        console.error("Invalid API response:", data);
        throw new Error("Invalid API response format");
      }
      
      // The backend now returns properly categorized data for all frameworks
      // No need for frontend conversion
      console.log("Setting types data:", data);
      console.log("Data structure:", Object.keys(data));
      if (data && typeof data === 'object') {
        console.log("Categories and component counts:", Object.entries(data).map(([cat, comps]: [string, any]) => [cat, Object.keys(comps || {}).length]));
      }
      setTypes(data);
      return data;
    } catch (error) {
      console.error("[Types] Error fetching types:", error);
      setLoading(false);
      throw error;
    }
  };

  const queryResult = query(
    ["useGetTypes", selectedFramework],
    () => getTypesFn(options?.checkCache),
    {
      refetchOnWindowFocus: false,
      ...options,
    },
  );

  return queryResult;
};
