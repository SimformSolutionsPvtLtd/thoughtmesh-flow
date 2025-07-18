import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { useGetFrameworks } from "@/controllers/API/queries/frameworks";
import { useGetFrameworkComponents } from "@/controllers/API/queries/frameworks";
import { useTypesStore } from "@/stores/typesStore";
import { useState, useEffect } from "react";
import { create } from "zustand";

// Create a simple global store for framework state
interface FrameworkStoreType {
  selectedFramework: string;
  setSelectedFramework: (framework: string) => void;
}

export const useFrameworkStore = create<FrameworkStoreType>((set) => ({
  selectedFramework: "langflow",
  setSelectedFramework: (framework: string) => {
    console.log("Global framework store updated to:", framework);
    set({ selectedFramework: framework });
  },
}));

export function FrameworkSwitcher() {
  const { selectedFramework, setSelectedFramework } = useFrameworkStore();
  const { setTypes, setData } = useTypesStore();

  // Debug log to ensure component is rendering
  console.log("FrameworkSwitcher is rendering! Selected framework:", selectedFramework);

  const { data: frameworks, isLoading: frameworksLoading } = useGetFrameworks();
  
  const { 
    data: frameworkComponents, 
    isLoading: componentsLoading,
    refetch: refetchComponents 
  } = useGetFrameworkComponents(selectedFramework, {
    enabled: !!selectedFramework
  });

  // Set default framework to langflow when frameworks are loaded
  useEffect(() => {
    if (frameworks?.frameworks && frameworks.frameworks.length > 0 && selectedFramework === "langflow") {
      const defaultFramework = frameworks.frameworks.includes('langflow') ? 'langflow' : frameworks.frameworks[0];
      if (defaultFramework !== selectedFramework) {
        setSelectedFramework(defaultFramework);
      }
    }
  }, [frameworks, selectedFramework, setSelectedFramework]);

  // Update types store when framework components change
  useEffect(() => {
    if (frameworkComponents) {
      console.log("Updating components for framework:", selectedFramework, frameworkComponents);
      setTypes(frameworkComponents);
      setData(frameworkComponents);
    }
  }, [frameworkComponents, setTypes, setData, selectedFramework]);

  const handleFrameworkChange = (framework: string) => {
    console.log("Framework changed from", selectedFramework, "to", framework);
    setSelectedFramework(framework);
    // The useGetFrameworkComponents hook will automatically refetch when selectedFramework changes
  };

  if (frameworksLoading) {
    return (
      <div className="flex items-center space-x-2">
        <span className="text-sm text-muted-foreground">Loading frameworks...</span>
      </div>
    );
  }

  // Fallback to hardcoded frameworks if API fails
  const availableFrameworks = frameworks?.frameworks || ["langflow", "agno"];

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium text-muted-foreground">Framework:</span>
      <Select
        value={selectedFramework}
        onValueChange={handleFrameworkChange}
        disabled={componentsLoading}
      >
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Select framework..." />
        </SelectTrigger>
        <SelectContent>
          {availableFrameworks.map((framework: string) => (
            <SelectItem key={framework} value={framework}>
              {framework.charAt(0).toUpperCase() + framework.slice(1)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {componentsLoading && (
        <span className="text-xs text-muted-foreground">Loading components...</span>
      )}
    </div>
  );
}
