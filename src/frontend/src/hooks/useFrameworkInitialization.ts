import { useEffect } from "react";
import { useFrameworkStore } from "../stores/frameworkStore";

/**
 * Hook to initialize framework store on app load
 * Call this in your main App component or a high-level component
 */
export const useFrameworkInitialization = () => {
  const { initialize, frameworks, selectedFramework } = useFrameworkStore();

  useEffect(() => {
    // Only initialize if we don't already have frameworks loaded
    // Ensure frameworks is an array before checking length
    const safeFrameworks = Array.isArray(frameworks) ? frameworks : [];
    if (safeFrameworks.length === 0) {
      console.log('Initializing framework store...');
      initialize().catch(console.error);
    }
  }, [initialize, frameworks]);

  return { selectedFramework, isInitialized: frameworks.length > 0 };
};

export default useFrameworkInitialization;
