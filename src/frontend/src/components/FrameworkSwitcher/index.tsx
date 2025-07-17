import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Loader2, RefreshCw, Settings, CheckCircle, AlertCircle, XCircle } from "lucide-react";
import { useFrameworkStore } from "../../stores/frameworkStore";
import { FrameworkInfo } from "../../types/zustand/framework";

interface FrameworkSwitcherProps {
  flowId?: string;
  onFrameworkChange?: (framework: string) => void;
  compact?: boolean;
}

export const FrameworkSwitcher: React.FC<FrameworkSwitcherProps> = ({
  flowId,
  onFrameworkChange,
  compact = false
}) => {
  const {
    frameworks,
    selectedFramework,
    frameworkPreferences,
    loading,
    error,
    setSelectedFramework,
    updateFrameworkPreference,
    loadFrameworks,
    refreshFrameworkHealth,
    clearError
  } = useFrameworkStore();

  const [refreshingFramework, setRefreshingFramework] = useState<string | null>(null);
  
  // Ensure frameworks is always an array
  const safeFrameworks = Array.isArray(frameworks) ? frameworks : [];
  const safeFrameworkPreferences = frameworkPreferences || {};

  useEffect(() => {
    // Load frameworks on component mount
    loadFrameworks();
  }, [loadFrameworks]);

  const handleFrameworkSelect = (framework: string) => {
    setSelectedFramework(framework);
    onFrameworkChange?.(framework);
  };

  const handlePreferenceChange = (framework: string, preference: 'preferred' | 'fallback' | 'disabled') => {
    updateFrameworkPreference(framework, preference);
  };

  const handleRefreshHealth = async (framework: string) => {
    setRefreshingFramework(framework);
    await refreshFrameworkHealth(framework);
    setRefreshingFramework(null);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <Select value={selectedFramework || ""} onValueChange={handleFrameworkSelect}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Select Framework" />
          </SelectTrigger>
          <SelectContent>
            {safeFrameworks.map((framework) => (
              <SelectItem key={framework.name} value={framework.name}>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(framework.status)}
                  <span>{framework.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selectedFramework && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleRefreshHealth(selectedFramework)}
            disabled={refreshingFramework === selectedFramework}
          >
            {refreshingFramework === selectedFramework ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </Button>
        )}
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2">
          <Settings className="w-5 h-5" />
          <span>Framework Management</span>
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        </CardTitle>
        {error && (
          <div className="flex items-center justify-between bg-red-50 border border-red-200 rounded-md p-3">
            <div className="flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
            <Button size="sm" variant="outline" onClick={clearError}>
              Dismiss
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Active Framework
          </label>
          <Select value={selectedFramework || ""} onValueChange={handleFrameworkSelect}>
            <SelectTrigger>
              <SelectValue placeholder="Select a framework to use" />
            </SelectTrigger>
            <SelectContent>
              {safeFrameworks.map((framework) => (
                <SelectItem key={framework.name} value={framework.name}>
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(framework.status)}
                      <span>{framework.name}</span>
                      <span className="text-xs text-gray-500">v{framework.version}</span>
                    </div>
                    <Badge variant="outline" className={getStatusColor(framework.status)}>
                      {framework.component_count} components
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700 mb-3 block">
            Framework Preferences
          </label>
          <div className="space-y-3">
            {safeFrameworks.map((framework: FrameworkInfo) => (
              <div key={framework.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(framework.status)}
                  <div>
                    <div className="font-medium">{framework.name}</div>
                    <div className="text-xs text-gray-500">
                      {framework.description || `${framework.name} framework integration`}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Select
                    value={safeFrameworkPreferences[framework.name] || 'fallback'}
                    onValueChange={(value: 'preferred' | 'fallback' | 'disabled') =>
                      handlePreferenceChange(framework.name, value)
                    }
                  >
                    <SelectTrigger className="w-28">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="preferred">Preferred</SelectItem>
                      <SelectItem value="fallback">Fallback</SelectItem>
                      <SelectItem value="disabled">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleRefreshHealth(framework.name)}
                    disabled={refreshingFramework === framework.name}
                  >
                    {refreshingFramework === framework.name ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-2 border-t">
          <Button
            onClick={loadFrameworks}
            disabled={loading}
            variant="outline"
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Frameworks
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
