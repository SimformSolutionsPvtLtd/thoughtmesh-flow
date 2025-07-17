import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, Search, Activity } from "lucide-react";
import { FrameworkSwitcher } from "../../components/FrameworkSwitcher";
import { ComponentBrowser } from "../../components/ComponentBrowser";

export default function FrameworkSettingsPage(): JSX.Element {
  return (
    <div className="flex h-full w-full flex-col space-y-8 p-8">
      <div>
        <div className="flex items-center space-x-2 mb-2">
          <Settings className="w-6 h-6" />
          <h1 className="text-2xl font-bold">Framework Management</h1>
        </div>
        <p className="text-gray-600">
          Configure and manage AI frameworks for your flows. Switch between frameworks, 
          set preferences, and browse available components.
        </p>
      </div>

      <Tabs defaultValue="frameworks" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="frameworks" className="flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Frameworks</span>
          </TabsTrigger>
          <TabsTrigger value="components" className="flex items-center space-x-2">
            <Search className="w-4 h-4" />
            <span>Components</span>
          </TabsTrigger>
          <TabsTrigger value="monitoring" className="flex items-center space-x-2">
            <Activity className="w-4 h-4" />
            <span>Monitoring</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="frameworks" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Framework Configuration</CardTitle>
              <CardDescription>
                Manage framework preferences, check health status, and configure execution settings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FrameworkSwitcher />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="components" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Component Browser</CardTitle>
              <CardDescription>
                Explore and search components across all available frameworks.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ComponentBrowser />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitoring" className="space-y-6 mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>
                  Monitor framework performance and execution statistics.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <div>Performance monitoring coming soon</div>
                  <div className="text-xs">Track execution times, success rates, and resource usage</div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Health Dashboard</CardTitle>
                <CardDescription>
                  Real-time health status and alerts for all frameworks.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <div>Health dashboard coming soon</div>
                  <div className="text-xs">Monitor framework health and receive alerts</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
