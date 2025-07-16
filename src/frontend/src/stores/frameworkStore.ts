import { create } from "zustand";
import { FrameworkStoreType } from "../types/zustand/framework";

export const useFrameworkStore = create<FrameworkStoreType>((set, get) => ({
  selectedFramework: "langflow", // Default to langflow
  frameworks: ["langflow"], // Initialize with langflow as default
  frameworkComponents: {},
  loading: false,
  setSelectedFramework: (framework: string) => {
    set({ selectedFramework: framework });
  },
  setFrameworks: (frameworks: string[]) => {
    // Always include langflow and ensure no duplicates
    const uniqueFrameworks = Array.from(new Set(["langflow", ...frameworks]));
    set({ frameworks: uniqueFrameworks });
  },
  setFrameworkComponents: (framework: string, components: any) => {
    set((state) => ({
      frameworkComponents: {
        ...state.frameworkComponents,
        [framework]: components,
      },
    }));
  },
  setLoading: (loading: boolean) => {
    set({ loading });
  },
  getCurrentFrameworkData: () => {
    const { selectedFramework, frameworkComponents } = get();
    return frameworkComponents[selectedFramework] || {};
  },
}));
