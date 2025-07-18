import useFlowsManagerStore from "@/stores/flowsManagerStore";
import { useFrameworkStore } from "@/stores/frameworkStore";
import { useTypesStore } from "@/stores/typesStore";
import { APIObjectType, useQueryFunctionType } from "../../../../types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export const useGetTypes: useQueryFunctionType<
  undefined,
  any,
  { checkCache?: boolean }
> = (options) => {
  const { query } = UseRequestProcessor();
  const setLoading = useFlowsManagerStore((state) => state.setIsLoading);
  const setTypes = useTypesStore((state) => state.setTypes);
  const { selectedFramework, loadComponents, components } = useFrameworkStore();

  const getTypesFn = async (checkCache = false) => {
    try {
      if (checkCache) {
        const data = useTypesStore.getState().types;
        if (data && Object.keys(data).length > 0) {
          return data;
        }
      }

      // Use framework-specific component loading if a framework is selected
      if (selectedFramework && selectedFramework !== "all") {
        console.log(`Loading components for framework: ${selectedFramework}`);
        
        // Use the enhanced /all endpoint with framework parameter for backward compatibility
        const response = await api.get<APIObjectType>(
          `${getURL("ALL")}?framework=${selectedFramework}&force_refresh=true`,
        );
        const data = response?.data;
        setTypes(data);
        return data;
      }

      // Fallback to original /all endpoint if no specific framework selected
      const response = await api.get<APIObjectType>(
        `${getURL("ALL")}?force_refresh=true`,
      );
      const data = response?.data;
      setTypes(data);
      return data;
    } catch (error) {
      console.error("[Types] Error fetching types:", error);
      setLoading(false);
      throw error;
    }
  };

  const queryResult = query(
    ["useGetTypes", selectedFramework], // Include selectedFramework in query key
    () => getTypesFn(options?.checkCache),
    {
      refetchOnWindowFocus: false,
      ...options,
    },
  );

  return queryResult;
};
