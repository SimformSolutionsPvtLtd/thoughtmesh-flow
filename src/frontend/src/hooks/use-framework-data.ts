import { useEffect } from "react";
import { useGetFrameworkComponents } from "@/controllers/API/queries/frameworks";
import { useFrameworkStore } from "@/stores/frameworkStore";
import { useTypesStore } from "@/stores/typesStore";
import { transformFrameworkComponentsToAPIData } from "@/utils/frameworkUtils";

export function useFrameworkData() {
  const {
    selectedFramework,
    setFrameworkComponents,
    setLoading,
    getCurrentFrameworkData,
  } = useFrameworkStore();

  const { setData } = useTypesStore();

  // Fetch components for the selected framework
  const {
    data: frameworkComponentsData,
    isLoading: isLoadingComponents,
    error,
  } = useGetFrameworkComponents(
    { framework: selectedFramework },
    {
      enabled: selectedFramework !== "langflow", // Don't fetch for langflow since it's handled by existing API
      retry: 2,
    }
  );

  // Update loading state
  useEffect(() => {
    setLoading(isLoadingComponents);
  }, [isLoadingComponents, setLoading]);

  // Process and store framework components
  useEffect(() => {
    if (frameworkComponentsData?.components && selectedFramework !== "langflow") {
      const transformedData = transformFrameworkComponentsToAPIData(
        frameworkComponentsData.components
      );
      
      // Store in framework store
      setFrameworkComponents(selectedFramework, transformedData);
      
      // Update the types store with framework data
      setData(transformedData);
    }
  }, [
    frameworkComponentsData,
    selectedFramework,
    setFrameworkComponents,
    setData,
  ]);

  // Handle langflow framework (use existing ALL API)
  useEffect(() => {
    if (selectedFramework === "langflow") {
      // For langflow, we rely on the existing data fetching mechanism
      // Reset to original data from the types store for langflow
      const currentTypesData = useTypesStore.getState().types;
      if (currentTypesData && Object.keys(currentTypesData).length > 0) {
        setData(currentTypesData);
      }
    }
  }, [selectedFramework, setData]);

  return {
    loading: isLoadingComponents,
    error,
    hasFrameworkData: !!getCurrentFrameworkData(),
  };
}
