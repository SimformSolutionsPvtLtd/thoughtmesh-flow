import { create } from "zustand";

export interface FrameworkStoreType {
  selectedFramework: string;
  setSelectedFramework: (framework: string) => void;
}

export const useFrameworkStore = create<FrameworkStoreType>((set, get) => ({
  selectedFramework: "langflow", // default to langflow
  setSelectedFramework: (framework: string) => {
    set({ selectedFramework: framework });
  },
}));
