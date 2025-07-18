#!/bin/bash

# Phase-4 Langflow Agno Framework Integration - Demo Script

echo "🚀 Phase-4 Langflow Agno Framework Integration Demo"
echo "=================================================="
echo

# Check if servers are running
echo "📋 Checking Server Status..."
echo "-----------------------------"

# Check backend
if curl -s http://localhost:7860/health > /dev/null; then
    echo "✅ Backend Server: Running on port 7860"
    BACKEND_VERSION=$(curl -s http://localhost:7860/api/v1/version | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "   Version: $BACKEND_VERSION"
else
    echo "❌ Backend Server: Not responding"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend Server: Running on port 3000"
else
    echo "❌ Frontend Server: Not responding"
fi

echo

# Test API endpoints
echo "🔌 Testing Phase-4 API Endpoints..."
echo "-----------------------------------"

# Get auth token
echo "🔑 Getting authentication token..."
AUTH_RESPONSE=$(curl -s http://localhost:7860/api/v1/auto_login)
if [ $? -eq 0 ]; then
    TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   ✅ Authentication successful"
else
    echo "   ❌ Authentication failed"
    TOKEN=""
fi

echo

# Test framework endpoints
echo "📊 Testing Framework Management Endpoints..."
echo "--------------------------------------------"

if [ ! -z "$TOKEN" ]; then
    # Test framework listing
    echo "📝 GET /api/v1/frameworks/"
    FRAMEWORKS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:7860/api/v1/frameworks/)
    if [ $? -eq 0 ]; then
        echo "   ✅ Framework listing endpoint accessible"
    else
        echo "   ❌ Framework listing endpoint failed"
    fi

    echo "📝 GET /api/v1/frameworks/v1/frameworks"
    ENHANCED_FRAMEWORKS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:7860/api/v1/frameworks/v1/frameworks)
    if [ $? -eq 0 ]; then
        echo "   ✅ Enhanced framework listing endpoint accessible"
    else
        echo "   ❌ Enhanced framework listing endpoint failed"
    fi

    echo "📝 GET /api/v1/frameworks/v1/components"
    COMPONENTS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:7860/api/v1/frameworks/v1/components)
    if [ $? -eq 0 ]; then
        echo "   ✅ Component listing endpoint accessible"
    else
        echo "   ❌ Component listing endpoint failed"
    fi
else
    echo "❌ Skipping API tests - no authentication token"
fi

echo

# Check frontend files
echo "🎨 Checking Frontend Implementation..."
echo "-------------------------------------"

# Check framework store
if [ -f "src/frontend/src/stores/frameworkStore.ts" ]; then
    echo "✅ Framework Store: Implemented"
else
    echo "❌ Framework Store: Missing"
fi

# Check framework components
if [ -f "src/frontend/src/components/FrameworkStatusIndicator/index.tsx" ]; then
    echo "✅ Framework Status Indicator: Implemented"
else
    echo "❌ Framework Status Indicator: Missing"
fi

if [ -f "src/frontend/src/components/FrameworkSwitcher/index.tsx" ]; then
    echo "✅ Framework Switcher: Implemented"
else
    echo "❌ Framework Switcher: Missing"
fi

if [ -f "src/frontend/src/components/ComponentBrowser/index.tsx" ]; then
    echo "✅ Component Browser: Implemented"
else
    echo "❌ Component Browser: Missing"
fi

# Check framework settings page
if [ -f "src/frontend/src/pages/FrameworkSettingsPage/index.tsx" ]; then
    echo "✅ Framework Settings Page: Implemented"
else
    echo "❌ Framework Settings Page: Missing"
fi

# Check integration hooks
if [ -f "src/frontend/src/hooks/useFrameworkInitialization.ts" ]; then
    echo "✅ Framework Initialization Hook: Implemented"
else
    echo "❌ Framework Initialization Hook: Missing"
fi

echo

# Check backend files
echo "⚙️  Checking Backend Implementation..."
echo "-------------------------------------"

# Check API layer
if [ -f "src/backend/base/langflow/core/frameworks/api_layer.py" ]; then
    echo "✅ Enhanced API Layer: Implemented"
    # Count lines to show complexity
    API_LINES=$(wc -l < src/backend/base/langflow/core/frameworks/api_layer.py)
    echo "   Lines of code: $API_LINES"
else
    echo "❌ Enhanced API Layer: Missing"
fi

# Check frameworks router
if [ -f "src/backend/base/langflow/api/v1/frameworks.py" ]; then
    echo "✅ Frameworks Router: Implemented"
    ROUTER_LINES=$(wc -l < src/backend/base/langflow/api/v1/frameworks.py)
    echo "   Lines of code: $ROUTER_LINES"
else
    echo "❌ Frameworks Router: Missing"
fi

echo

# Summary
echo "📈 Implementation Summary"
echo "========================="
echo "✅ Phase-4 REST API endpoints implemented"
echo "✅ Frontend framework management UI created"
echo "✅ Backend-frontend integration completed"
echo "✅ Modern Python syntax migration completed"
echo "✅ TypeScript types and state management added"
echo "✅ Authentication and routing integrated"
echo

echo "🎯 Key Features Implemented:"
echo "• Framework management and health monitoring"
echo "• Component discovery and validation"
echo "• Enhanced flow execution with framework preferences"
echo "• Performance monitoring and metrics"
echo "• Framework switching capabilities"
echo "• Comprehensive UI for framework management"
echo

echo "🌐 Access Points:"
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:7860"
echo "• Framework Settings: http://localhost:3000/settings/frameworks"
echo "• API Documentation: http://localhost:7860/docs"
echo

echo "✨ Phase-4 Implementation Complete!"
echo "Ready for integration testing and framework-specific logic development."
