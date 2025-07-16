import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useGetFrameworks } from "@/controllers/API/queries/frameworks";
import { useFrameworkStore } from "@/stores/frameworkStore";
import { memo, useEffect } from "react";

interface FrameworkSelectorProps {
  disabled?: boolean;
}

export const FrameworkSelector = memo(function FrameworkSelector({
  disabled = false,
}: FrameworkSelectorProps) {
  const {
    selectedFramework,
    frameworks,
    setSelectedFramework,
    setFrameworks,
    loading,
  } = useFrameworkStore();

  const { data: frameworksData, isLoading: isLoadingFrameworks } =
    useGetFrameworks({
      enabled: true,
    });

  // Update frameworks when data is loaded
  useEffect(() => {
    if (frameworksData?.frameworks) {
      setFrameworks(frameworksData.frameworks);
    }
  }, [frameworksData, setFrameworks]);

  const handleFrameworkChange = (framework: string) => {
    setSelectedFramework(framework);
  };

  // Always show the selector, with fallback frameworks if needed
  const availableFrameworks = frameworks.length > 0 ? frameworks : ["langflow"];
  const currentFramework = selectedFramework || "langflow";

  return (
    <div
      className="rounded border border-gray-300 px-3 pb-2"
      data-testid="framework-selector"
    >
      <div className="mb-2 text-xs font-medium text-muted-foreground">
        Framework ({availableFrameworks.length} available)
      </div>
      <Select
        value={currentFramework}
        onValueChange={handleFrameworkChange}
        disabled={disabled || loading || isLoadingFrameworks}
      >
        <SelectTrigger className="h-8 text-sm">
          <SelectValue
            placeholder={
              isLoadingFrameworks ? "Loading..." : "Select framework..."
            }
          />
        </SelectTrigger>
        <SelectContent>
          {availableFrameworks.map((framework) => (
            <SelectItem key={framework} value={framework}>
              <div className="flex items-center capitalize">
                {framework}
                {framework === "langflow" && " (default)"}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {isLoadingFrameworks && (
        <div className="mt-1 text-xs text-muted-foreground">
          Loading frameworks...
        </div>
      )}
    </div>
  );
});

FrameworkSelector.displayName = "FrameworkSelector";
