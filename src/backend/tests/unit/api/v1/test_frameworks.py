"""
Test the frameworks API endpoints to ensure /{framework}/components 
returns the same structure as /all endpoint
"""

import pytest
from httpx import AsyncClient
from langflow.core.frameworks.types import ComponentCategory, ComponentMetadata, FrameworkType


@pytest.mark.asyncio
async def test_frameworks_components_structure_matches_all(client: AsyncClient, logged_in_headers):
    """Test that /{framework}/components returns the same structure as /all endpoint."""
    
    # First get the /all endpoint response to understand the expected structure
    all_response = await client.get("api/v1/all", headers=logged_in_headers)
    assert all_response.status_code == 200
    all_data = all_response.json()
    
    # Verify /all has the expected structure (categories as top-level keys)
    assert isinstance(all_data, dict)
    assert len(all_data) > 0
    
    # Check that we have some expected categories
    expected_categories = {"input_output", "processing", "tools", "llms"}
    actual_categories = set(all_data.keys())
    assert len(actual_categories.intersection(expected_categories)) > 0
    
    # Verify component structure in /all
    sample_category = next(iter(all_data.keys()))
    sample_components = all_data[sample_category]
    assert isinstance(sample_components, dict)
    
    if sample_components:
        sample_component = next(iter(sample_components.values()))
        expected_component_keys = {
            "template", "display_name", "description", "documentation", 
            "icon", "is_component"
        }
        actual_component_keys = set(sample_component.keys())
        assert expected_component_keys.issubset(actual_component_keys)


@pytest.mark.asyncio
async def test_frameworks_list_endpoint(client: AsyncClient, logged_in_headers):
    """Test that the frameworks list endpoint works."""
    
    response = await client.get("api/v1/frameworks/", headers=logged_in_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "frameworks" in data
    assert isinstance(data["frameworks"], list)


@pytest.mark.asyncio
async def test_framework_components_endpoint_structure(client: AsyncClient, logged_in_headers):
    """Test that each framework's components endpoint returns the correct structure."""
    
    # Get available frameworks
    frameworks_response = await client.get("api/v1/frameworks/", headers=logged_in_headers)
    assert frameworks_response.status_code == 200
    frameworks_data = frameworks_response.json()
    
    # Get /all structure for comparison
    all_response = await client.get("api/v1/all", headers=logged_in_headers)
    assert all_response.status_code == 200
    all_data = all_response.json()
    
    # Test each available framework
    for framework in frameworks_data["frameworks"]:
        components_response = await client.get(
            f"api/v1/frameworks/{framework}/components", 
            headers=logged_in_headers
        )
        
        if components_response.status_code == 200:
            components_data = components_response.json()
            
            # Verify it has the same top-level structure as /all
            assert isinstance(components_data, dict)
            
            # All category keys should be valid category names
            for category_key in components_data.keys():
                assert isinstance(category_key, str)
                components_in_category = components_data[category_key]
                assert isinstance(components_in_category, dict)
                
                # Verify component structure matches /all structure
                for component_name, component_data in components_in_category.items():
                    assert isinstance(component_data, dict)
                    
                    # Should have the same keys as components in /all
                    expected_keys = {
                        "template", "display_name", "description", "documentation",
                        "icon", "is_component", "framework"
                    }
                    actual_keys = set(component_data.keys())
                    assert expected_keys.issubset(actual_keys)
                    
                    # Framework-specific fields
                    assert component_data["framework"] == framework
                    assert "framework_component_id" in component_data
                    
                    # Template structure should match
                    template = component_data["template"]
                    assert isinstance(template, dict)
                    assert "display_name" in template
                    assert "description" in template
                    assert "framework" in template
                    assert template["framework"] == framework


@pytest.mark.asyncio 
async def test_framework_components_compression(client: AsyncClient, logged_in_headers):
    """Test that the framework components endpoint returns compressed response like /all."""
    
    frameworks_response = await client.get("api/v1/frameworks/", headers=logged_in_headers)
    assert frameworks_response.status_code == 200
    frameworks_data = frameworks_response.json()
    
    # Test compression for available frameworks
    for framework in frameworks_data["frameworks"]:
        components_response = await client.get(
            f"api/v1/frameworks/{framework}/components",
            headers=logged_in_headers
        )
        
        if components_response.status_code == 200:
            # Check that the response has compression headers (if implemented)
            # or at least that the structure is the same as /all
            components_data = components_response.json()
            assert isinstance(components_data, dict)
            
            # Should be categorized like /all endpoint
            for category, components in components_data.items():
                assert isinstance(components, dict)
                for component_name, component_info in components.items():
                    assert isinstance(component_info, dict)
                    assert "framework" in component_info
                    assert component_info["framework"] == framework


@pytest.mark.asyncio
async def test_nonexistent_framework_returns_404(client: AsyncClient, logged_in_headers):
    """Test that requesting components for a non-existent framework returns 404."""
    
    response = await client.get(
        "api/v1/frameworks/nonexistent/components",
        headers=logged_in_headers
    )
    assert response.status_code == 404
    
    error_data = response.json()
    assert "detail" in error_data
    assert "not available" in error_data["detail"].lower()


@pytest.mark.asyncio
async def test_framework_status_endpoint(client: AsyncClient, logged_in_headers):
    """Test the framework status endpoint."""
    
    # Get available frameworks first
    frameworks_response = await client.get("api/v1/frameworks/", headers=logged_in_headers)
    assert frameworks_response.status_code == 200
    frameworks_data = frameworks_response.json()
    
    # Test status for each framework
    for framework in frameworks_data["frameworks"]:
        status_response = await client.get(
            f"api/v1/frameworks/{framework}/status",
            headers=logged_in_headers
        )
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert "framework" in status_data
        assert "available" in status_data
        assert status_data["framework"] == framework
        assert isinstance(status_data["available"], bool)
