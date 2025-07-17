import { useEffect } from "react";
import { useFrameworkStore } from "../stores/frameworkStore";

/**
 * Hook to initialize framework store on app load
 * Call this in your main App component or a high-level component
 */
export const useFrameworkInitialization = () => {
  const { loadFrameworks, frameworks } = useFrameworkStore();

  useEffect(() => {
    // Only load if we don't already have frameworks loaded
    // Ensure frameworks is an array before checking length
    const safeFrameworks = Array.isArray(frameworks) ? frameworks : [];
    if (safeFrameworks.length === 0) {
      console.log('Loading frameworks from useFrameworkInitialization...');
      loadFrameworks();
    }
  }, [loadFrameworks, frameworks]);
};

export default useFrameworkInitialization;
