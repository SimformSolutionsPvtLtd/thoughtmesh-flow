import { create } from "zustand";
import { persist } from "zustand/middleware";
import { FrameworkStoreType, FrameworkInfo, ComponentInfo, FrameworkPreferences } from "../types/zustand/framework";

// API endpoints (these would be configured to match your backend)
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:7860";

export const useFrameworkStore = create<FrameworkStoreType>()(
  persist(
    (set, get) => ({
      // Initial state - ensure all arrays are properly initialized
      frameworks: [],
      components: [],
      selectedFramework: null,
      frameworkPreferences: {
        agno: 'preferred',
        langflow: 'fallback'
      },
      loading: false,
      componentsLoading: false,
      error: null,
      flowFrameworkContext: {},

      // Actions
      setSelectedFramework: (framework: string) => {
        set({ selectedFramework: framework });
      },

      setFrameworkPreferences: (preferences: FrameworkPreferences) => {
        set({ frameworkPreferences: preferences });
      },

      updateFrameworkPreference: (framework: string, preference: 'preferred' | 'fallback' | 'disabled') => {
        const currentPreferences = get().frameworkPreferences;
        set({
          frameworkPreferences: {
            ...currentPreferences,
            [framework]: preference
          }
        });
      },

      loadFrameworks: async () => {
        set({ loading: true, error: null });
        console.log('Loading frameworks from store...');
        try {
          const response = await fetch(`${API_BASE}/api/v1/frameworks/`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken') || 'dev-token'}`,
              'Content-Type': 'application/json'
            }
          });

          console.log('Frameworks API response status:', response.status);

          if (!response.ok) {
            throw new Error(`Failed to load frameworks: ${response.statusText}`);
          }

          const frameworks: FrameworkInfo[] = await response.json();
          console.log('Loaded frameworks:', frameworks);
          set({ frameworks, loading: false });
        } catch (error) {
          console.error('Error loading frameworks:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load frameworks',
            loading: false 
          });
        }
      },

      loadComponents: async (framework?: string) => {
        set({ componentsLoading: true, error: null });
        try {
          const url = new URL(`${API_BASE}/api/v1/frameworks/components`);
          if (framework) {
            url.searchParams.append('framework', framework);
          }

          const response = await fetch(url.toString(), {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken') || 'dev-token'}`,
              'Content-Type': 'application/json'
            }
          });

          if (!response.ok) {
            throw new Error(`Failed to load components: ${response.statusText}`);
          }

          const data = await response.json();
          const components: ComponentInfo[] = data.components || [];
          set({ components, componentsLoading: false });
        } catch (error) {
          console.error('Error loading components:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load components',
            componentsLoading: false 
          });
        }
      },

      refreshFrameworkHealth: async (framework: string) => {
        try {
          const response = await fetch(`${API_BASE}/api/v1/frameworks/${framework}/health-check`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken') || 'dev-token'}`,
              'Content-Type': 'application/json'
            }
          });

          if (!response.ok) {
            throw new Error(`Health check failed: ${response.statusText}`);
          }

          const healthData = await response.json();
          
          // Update the framework status in the store
          const frameworks = get().frameworks.map(f => 
            f.name === framework 
              ? { ...f, status: healthData.status, last_health_check: healthData.timestamp }
              : f
          );
          
          set({ frameworks });
        } catch (error) {
          console.error(`Error checking health for ${framework}:`, error);
          set({ 
            error: error instanceof Error ? error.message : `Health check failed for ${framework}`
          });
        }
      },

      switchComponentFramework: async (flowId: string, componentMappings: Record<string, {from: string, to: string}>) => {
        try {
          const response = await fetch(`${API_BASE}/api/v1/flows/${flowId}/switch-framework`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken') || 'dev-token'}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              component_mappings: componentMappings,
              preserve_connections: true,
              validate_compatibility: true
            })
          });

          if (!response.ok) {
            throw new Error(`Framework switching failed: ${response.statusText}`);
          }

          const result = await response.json();
          
          if (result.status === 'partial' && result.invalid_mappings) {
            const errorMsg = Object.entries(result.invalid_mappings)
              .map(([comp, error]) => `${comp}: ${error}`)
              .join(', ');
            throw new Error(`Partial success - some components failed: ${errorMsg}`);
          }

          // Success - could trigger a reload of the flow or show success message
          return result;
        } catch (error) {
          console.error(`Error switching frameworks for flow ${flowId}:`, error);
          set({ 
            error: error instanceof Error ? error.message : 'Framework switching failed'
          });
          throw error;
        }
      },

      setFlowFrameworkContext: (flowId: string, preferences: FrameworkPreferences) => {
        const currentContext = get().flowFrameworkContext;
        set({
          flowFrameworkContext: {
            ...currentContext,
            [flowId]: preferences
          }
        });
      },

      clearError: () => {
        set({ error: null });
      }
    }),
    {
      name: 'framework-store',
      // Only persist certain fields
      partialize: (state) => ({
        selectedFramework: state.selectedFramework,
        frameworkPreferences: state.frameworkPreferences,
        flowFrameworkContext: state.flowFrameworkContext
      })
    }
  )
);
