import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Search, Filter, RefreshCw, Loader2, Package, Code } from "lucide-react";
import { useFrameworkStore } from "../../stores/frameworkStore";
import { ComponentInfo } from "../../types/zustand/framework";

interface ComponentBrowserProps {
  onComponentSelect?: (component: ComponentInfo) => void;
  selectedFramework?: string;
}

export const ComponentBrowser: React.FC<ComponentBrowserProps> = ({
  onComponentSelect,
  selectedFramework
}) => {
  const {
    components,
    frameworks,
    componentsLoading,
    error,
    loadComponents,
    clearError
  } = useFrameworkStore();

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [filterFramework, setFilterFramework] = useState<string>(selectedFramework || "all");

  // Ensure components and frameworks are always arrays
  const safeComponents = Array.isArray(components) ? components : [];
  const safeFrameworks = Array.isArray(frameworks) ? frameworks : [];

  useEffect(() => {
    loadComponents(filterFramework === "all" ? undefined : filterFramework);
  }, [filterFramework, loadComponents]);

  const filteredComponents = safeComponents.filter(component => {
    const matchesSearch = searchTerm === "" || 
      component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      component.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === "all" || component.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(safeComponents.map(c => c.category))).sort();

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'model':
        return <Package className="w-4 h-4" />;
      case 'tool':
        return <Code className="w-4 h-4" />;
      default:
        return <Package className="w-4 h-4" />;
    }
  };

  const getFrameworkColor = (framework: string) => {
    switch (framework.toLowerCase()) {
      case 'agno':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'langflow':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5" />
            <span>Component Browser</span>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => loadComponents(filterFramework === "all" ? undefined : filterFramework)}
            disabled={componentsLoading}
          >
            {componentsLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </Button>
        </CardTitle>
        
        {error && (
          <div className="flex items-center justify-between bg-red-50 border border-red-200 rounded-md p-3">
            <span className="text-red-700 text-sm">{error}</span>
            <Button size="sm" variant="outline" onClick={clearError}>
              Dismiss
            </Button>
          </div>
        )}
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Search and Filters */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search components..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">Framework</label>
              <Select value={filterFramework} onValueChange={setFilterFramework}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Frameworks</SelectItem>
                  {safeFrameworks.map((framework) => (
                    <SelectItem key={framework.name} value={framework.name}>
                      {framework.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-xs font-medium text-gray-700 mb-1 block">Category</label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      <div className="flex items-center space-x-2">
                        {getCategoryIcon(category)}
                        <span className="capitalize">{category}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Results Summary */}
        <div className="flex items-center justify-between text-sm text-gray-600 border-b pb-2">
          <span>
            {filteredComponents.length} component{filteredComponents.length !== 1 ? 's' : ''} found
          </span>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4" />
            <span>
              {searchTerm && `"${searchTerm}"`}
              {selectedCategory !== "all" && ` in ${selectedCategory}`}
              {filterFramework !== "all" && ` from ${filterFramework}`}
            </span>
          </div>
        </div>

        {/* Component List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {componentsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="ml-2">Loading components...</span>
            </div>
          ) : filteredComponents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Package className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div>No components found</div>
              <div className="text-xs">Try adjusting your search or filters</div>
            </div>
          ) : (
            filteredComponents.map((component) => (
              <div
                key={component.id}
                className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => onComponentSelect?.(component)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      {getCategoryIcon(component.category)}
                      <span className="font-medium">{component.name}</span>
                      <Badge variant="outline" className={getFrameworkColor(component.framework)}>
                        {component.framework}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{component.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {component.inputs.length > 0 && (
                        <span>Inputs: {component.inputs.slice(0, 3).join(", ")}{component.inputs.length > 3 ? "..." : ""}</span>
                      )}
                      {component.outputs.length > 0 && (
                        <span>Outputs: {component.outputs.slice(0, 3).join(", ")}{component.outputs.length > 3 ? "..." : ""}</span>
                      )}
                    </div>
                  </div>
                  <Badge variant="outline" className="capitalize">
                    {component.status}
                  </Badge>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
