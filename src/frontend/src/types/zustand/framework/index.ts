export type FrameworkStoreType = {
  selectedFramework: string;
  frameworks: string[];
  frameworkComponents: Record<string, any>;
  loading: boolean;
  setSelectedFramework: (framework: string) => void;
  setFrameworks: (frameworks: string[]) => void;
  setFrameworkComponents: (framework: string, components: any) => void;
  setLoading: (loading: boolean) => void;
  getCurrentFrameworkData: () => any;
};
