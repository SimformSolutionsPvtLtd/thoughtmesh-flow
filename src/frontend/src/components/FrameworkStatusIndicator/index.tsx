import React from "react";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { CheckCircle, AlertCircle, XCircle, Settings } from "lucide-react";
import { useFrameworkStore } from "../../stores/frameworkStore";
import { FrameworkSwitcher } from "../FrameworkSwitcher";

export const FrameworkStatusIndicator: React.FC = () => {
  const { frameworks, selectedFramework, frameworkPreferences } = useFrameworkStore();

  // Ensure frameworks is always an array
  const safeFrameworks = Array.isArray(frameworks) ? frameworks : [];
  
  const activeFramework = safeFrameworks.find(f => f.name === selectedFramework);
  const preferredFrameworks = Object.entries(frameworkPreferences || {})
    .filter(([_, preference]) => preference === 'preferred')
    .map(([name, _]) => name);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="w-3 h-3 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="w-3 h-3 text-red-500" />;
      default:
        return <AlertCircle className="w-3 h-3 text-gray-500" />;
    }
  };

  const getOverallStatus = () => {
    const healthyCount = safeFrameworks.filter(f => f.status === 'healthy').length;
    const totalCount = safeFrameworks.length;
    
    if (totalCount === 0) return 'unknown';
    if (healthyCount === totalCount) return 'healthy';
    if (healthyCount > 0) return 'degraded';
    return 'unhealthy';
  };

  const overallStatus = getOverallStatus();

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center space-x-2">
          {getStatusIcon(overallStatus)}
          <span className="text-xs">
            {activeFramework ? activeFramework.name : 'No Framework'}
          </span>
          <Settings className="w-3 h-3" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="end">
        <div className="space-y-3">
          <div>
            <h4 className="font-medium text-sm">Framework Status</h4>
            <div className="mt-2 space-y-1">
              {safeFrameworks.map((framework) => (
                <div key={framework.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(framework.status)}
                    <span>{framework.name}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Badge variant="outline" className="text-xs px-1 py-0">
                      {framework.component_count}
                    </Badge>
                    {preferredFrameworks.includes(framework.name) && (
                      <Badge variant="default" className="text-xs px-1 py-0">
                        Preferred
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="pt-2 border-t">
            <FrameworkSwitcher compact={true} />
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};
