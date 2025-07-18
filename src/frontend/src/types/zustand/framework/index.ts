export type FrameworkInfo = {
  name: string;
  version: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  component_count: number;
  categories: string[];
  capabilities: string[];
  description?: string;
  last_health_check?: string;
};

export type ComponentInfo = {
  id: string;
  name: string;
  framework: string;
  category: string;
  description: string;
  status: string;
  inputs: string[];
  outputs: string[];
  version?: string;
  dependencies?: string[];
};

export type FrameworkPreferences = {
  [framework: string]: 'preferred' | 'fallback' | 'disabled';
};

export type FrameworkStoreType = {
  // Framework data
  frameworks: FrameworkInfo[];
  components: ComponentInfo[];
  selectedFramework: string | null;
  frameworkPreferences: FrameworkPreferences;
  
  // Loading states
  loading: boolean;
  componentsLoading: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  setSelectedFramework: (framework: string) => void;
  setFrameworkPreferences: (preferences: FrameworkPreferences) => void;
  updateFrameworkPreference: (framework: string, preference: 'preferred' | 'fallback' | 'disabled') => void;
  loadFrameworks: () => Promise<void>;
  loadComponents: (framework?: string) => Promise<void>;
  refreshFrameworkHealth: (framework: string) => Promise<void>;
  switchComponentFramework: (flowId: string, componentMappings: Record<string, {from: string, to: string}>) => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
  
  // Framework context for flows
  flowFrameworkContext: Record<string, FrameworkPreferences>;
  setFlowFrameworkContext: (flowId: string, preferences: FrameworkPreferences) => void;
};
