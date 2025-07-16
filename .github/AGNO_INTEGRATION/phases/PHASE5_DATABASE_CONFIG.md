# Phase 5: Database & Configuration Management (Week 9-10)

## 🎯 Objective
Implement comprehensive database migrations, persistent configuration management, and data persistence for framework components with environment-specific settings and secure credential management.

## 📋 Prerequisites
- Phase 1-4 completed with API layer functional
- Framework manager and component system operational
- REST API endpoints for framework management active
- Workflow orchestration system implemented

## 🗄️ Database Schema Design

### 1. Framework Metadata Tables

#### Frameworks Table
```sql
-- frameworks table
CREATE TABLE frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    adapter_class VARCHAR(200) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    configuration JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Framework capabilities
CREATE TABLE framework_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,
    capability VARCHAR(100) NOT NULL,
    supported BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    UNIQUE(framework_id, capability)
);

-- Framework health status
CREATE TABLE framework_health_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    health_data JSONB DEFAULT '{}',
    error_message TEXT,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Components Table
```sql
-- components table
CREATE TABLE framework_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(50),
    inputs JSONB DEFAULT '[]',
    outputs JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    schema JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'available',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(framework_id, name)
);

-- Component performance metrics
CREATE TABLE component_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID REFERENCES framework_components(id) ON DELETE CASCADE,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_execution_time DECIMAL(10,6) DEFAULT 0,
    min_execution_time DECIMAL(10,6) DEFAULT 0,
    max_execution_time DECIMAL(10,6) DEFAULT 0,
    last_execution_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Component execution logs
CREATE TABLE component_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID REFERENCES framework_components(id) ON DELETE CASCADE,
    execution_id VARCHAR(100),
    inputs JSONB,
    outputs JSONB,
    configuration JSONB,
    success BOOLEAN,
    execution_time DECIMAL(10,6),
    error_message TEXT,
    mode VARCHAR(50), -- 'real', 'simulated', 'hybrid'
    metadata JSONB DEFAULT '{}',
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Configuration Management Tables

#### Environment Configuration
```sql
-- configuration environments
CREATE TABLE configuration_environments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- framework configurations per environment
CREATE TABLE framework_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,
    environment_id UUID REFERENCES configuration_environments(id) ON DELETE CASCADE,
    configuration JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(framework_id, environment_id)
);

-- component-specific configurations
CREATE TABLE component_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_id UUID REFERENCES framework_components(id) ON DELETE CASCADE,
    environment_id UUID REFERENCES configuration_environments(id) ON DELETE CASCADE,
    configuration JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(component_id, environment_id)
);
```

#### Credential Management
```sql
-- secure credentials storage
CREATE TABLE framework_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES frameworks(id) ON DELETE CASCADE,
    environment_id UUID REFERENCES configuration_environments(id) ON DELETE CASCADE,
    credential_key VARCHAR(200) NOT NULL,
    encrypted_value TEXT NOT NULL,
    encryption_method VARCHAR(100) DEFAULT 'AES-256-GCM',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(framework_id, environment_id, credential_key)
);

-- credential audit log
CREATE TABLE credential_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id UUID REFERENCES framework_credentials(id) ON DELETE CASCADE,
    accessed_by VARCHAR(200),
    access_type VARCHAR(50), -- 'read', 'write', 'delete'
    ip_address INET,
    user_agent TEXT,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Workflow and Execution Persistence

#### Workflow Definitions
```sql
-- workflow definitions
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    framework_requirements JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- workflow executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    inputs JSONB,
    outputs JSONB,
    component_results JSONB DEFAULT '{}',
    framework_usage JSONB DEFAULT '{}',
    error_logs JSONB DEFAULT '[]',
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- workflow templates
CREATE TABLE workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    template_definition JSONB NOT NULL,
    default_configuration JSONB DEFAULT '{}',
    required_frameworks JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT false,
    created_by VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Configuration Management System

### 1. Configuration Provider (`config_system.py`)

```python
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import yaml
import json
from cryptography.fernet import Fernet
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

class ConfigurationSource(Enum):
    DATABASE = "database"
    FILE = "file"
    ENVIRONMENT = "environment"
    REMOTE = "remote"

@dataclass
class ConfigurationItem:
    key: str
    value: Any
    source: ConfigurationSource
    environment: str
    framework: Optional[str] = None
    component: Optional[str] = None
    encrypted: bool = False
    metadata: Dict[str, Any] = None

class ConfigurationManager:
    """Centralized configuration management system"""
    
    def __init__(self, database_url: str, encryption_key: str = None):
        self.database_url = database_url
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.config_cache: Dict[str, ConfigurationItem] = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize configuration system"""
        # Ensure default environment exists
        await self.ensure_default_environment()
        
        # Load base configurations
        await self.load_configurations()
        
        # Set up configuration watchers
        await self.setup_configuration_watchers()
    
    async def get_framework_configuration(
        self, 
        framework_name: str, 
        environment: str = "default"
    ) -> Dict[str, Any]:
        """Get configuration for a specific framework"""
        
        async with self._get_db_session() as session:
            query = """
                SELECT fc.configuration, f.name as framework_name
                FROM framework_configurations fc
                JOIN frameworks f ON fc.framework_id = f.id
                JOIN configuration_environments ce ON fc.environment_id = ce.id
                WHERE f.name = $1 AND ce.name = $2 AND fc.is_active = true
            """
            
            result = await session.fetchrow(query, framework_name, environment)
            
            if result:
                config = result['configuration']
                
                # Decrypt sensitive values
                config = await self._decrypt_configuration(config)
                
                # Merge with environment variables
                config = self._merge_environment_variables(config, framework_name)
                
                return config
            
            return {}
    
    async def set_framework_configuration(
        self,
        framework_name: str,
        configuration: Dict[str, Any],
        environment: str = "default"
    ):
        """Set configuration for a framework"""
        
        # Encrypt sensitive values
        encrypted_config = await self._encrypt_sensitive_values(configuration)
        
        async with self._get_db_session() as session:
            # Get framework and environment IDs
            framework_id = await self._get_framework_id(session, framework_name)
            environment_id = await self._get_environment_id(session, environment)
            
            # Upsert configuration
            query = """
                INSERT INTO framework_configurations 
                (framework_id, environment_id, configuration, updated_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (framework_id, environment_id)
                DO UPDATE SET configuration = $3, updated_at = NOW()
            """
            
            await session.execute(query, framework_id, environment_id, json.dumps(encrypted_config))
            await session.commit()
        
        # Clear cache
        cache_key = f"framework:{framework_name}:{environment}"
        self.config_cache.pop(cache_key, None)
    
    async def get_component_configuration(
        self,
        framework_name: str,
        component_name: str,
        environment: str = "default"
    ) -> Dict[str, Any]:
        """Get configuration for a specific component"""
        
        # Start with framework configuration
        framework_config = await self.get_framework_configuration(framework_name, environment)
        
        # Get component-specific overrides
        async with self._get_db_session() as session:
            query = """
                SELECT cc.configuration
                FROM component_configurations cc
                JOIN framework_components fc ON cc.component_id = fc.id
                JOIN frameworks f ON fc.framework_id = f.id
                JOIN configuration_environments ce ON cc.environment_id = ce.id
                WHERE f.name = $1 AND fc.name = $2 AND ce.name = $3 AND cc.is_active = true
            """
            
            result = await session.fetchrow(query, framework_name, component_name, environment)
            
            if result:
                component_config = result['configuration']
                component_config = await self._decrypt_configuration(component_config)
                
                # Merge configurations (component overrides framework)
                merged_config = {**framework_config, **component_config}
                return merged_config
            
            return framework_config
    
    async def create_environment(self, name: str, description: str = None, is_default: bool = False):
        """Create a new configuration environment"""
        
        async with self._get_db_session() as session:
            # If this is default, unset other defaults
            if is_default:
                await session.execute("UPDATE configuration_environments SET is_default = false")
            
            query = """
                INSERT INTO configuration_environments (name, description, is_default)
                VALUES ($1, $2, $3)
                ON CONFLICT (name) DO UPDATE SET 
                description = $2, is_default = $3, updated_at = NOW()
            """
            
            await session.execute(query, name, description, is_default)
            await session.commit()
    
    async def clone_environment(self, source_env: str, target_env: str, description: str = None):
        """Clone configuration from one environment to another"""
        
        async with self._get_db_session() as session:
            # Create target environment
            await self.create_environment(target_env, description)
            
            source_env_id = await self._get_environment_id(session, source_env)
            target_env_id = await self._get_environment_id(session, target_env)
            
            # Clone framework configurations
            clone_framework_query = """
                INSERT INTO framework_configurations (framework_id, environment_id, configuration)
                SELECT framework_id, $2, configuration
                FROM framework_configurations
                WHERE environment_id = $1
            """
            
            await session.execute(clone_framework_query, source_env_id, target_env_id)
            
            # Clone component configurations
            clone_component_query = """
                INSERT INTO component_configurations (component_id, environment_id, configuration)
                SELECT component_id, $2, configuration
                FROM component_configurations
                WHERE environment_id = $1
            """
            
            await session.execute(clone_component_query, source_env_id, target_env_id)
            
            # Clone credentials
            clone_credentials_query = """
                INSERT INTO framework_credentials 
                (framework_id, environment_id, credential_key, encrypted_value, encryption_method, metadata)
                SELECT framework_id, $2, credential_key, encrypted_value, encryption_method, metadata
                FROM framework_credentials
                WHERE environment_id = $1
            """
            
            await session.execute(clone_credentials_query, source_env_id, target_env_id)
            await session.commit()
    
    async def manage_credentials(
        self,
        framework_name: str,
        credential_key: str,
        credential_value: str = None,
        environment: str = "default",
        operation: str = "set"
    ) -> Optional[str]:
        """Manage framework credentials securely"""
        
        async with self._get_db_session() as session:
            framework_id = await self._get_framework_id(session, framework_name)
            environment_id = await self._get_environment_id(session, environment)
            
            if operation == "set":
                encrypted_value = self.cipher.encrypt(credential_value.encode()).decode()
                
                query = """
                    INSERT INTO framework_credentials 
                    (framework_id, environment_id, credential_key, encrypted_value, updated_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (framework_id, environment_id, credential_key)
                    DO UPDATE SET encrypted_value = $4, updated_at = NOW()
                """
                
                await session.execute(query, framework_id, environment_id, credential_key, encrypted_value)
                await session.commit()
                
                # Log access
                await self._log_credential_access(session, framework_id, environment_id, credential_key, "write")
                
                return "Credential set successfully"
                
            elif operation == "get":
                query = """
                    SELECT encrypted_value FROM framework_credentials
                    WHERE framework_id = $1 AND environment_id = $2 AND credential_key = $3
                """
                
                result = await session.fetchval(query, framework_id, environment_id, credential_key)
                
                if result:
                    # Log access
                    await self._log_credential_access(session, framework_id, environment_id, credential_key, "read")
                    
                    decrypted_value = self.cipher.decrypt(result.encode()).decode()
                    return decrypted_value
                
                return None
                
            elif operation == "delete":
                query = """
                    DELETE FROM framework_credentials
                    WHERE framework_id = $1 AND environment_id = $2 AND credential_key = $3
                """
                
                await session.execute(query, framework_id, environment_id, credential_key)
                await session.commit()
                
                # Log access
                await self._log_credential_access(session, framework_id, environment_id, credential_key, "delete")
                
                return "Credential deleted successfully"
    
    async def get_configuration_templates(self) -> List[Dict[str, Any]]:
        """Get available configuration templates"""
        
        async with self._get_db_session() as session:
            query = """
                SELECT name, description, category, template_definition, 
                       default_configuration, required_frameworks, tags
                FROM workflow_templates
                WHERE is_public = true
                ORDER BY name
            """
            
            results = await session.fetch(query)
            
            return [
                {
                    "name": row['name'],
                    "description": row['description'],
                    "category": row['category'],
                    "template": row['template_definition'],
                    "default_config": row['default_configuration'],
                    "required_frameworks": row['required_frameworks'],
                    "tags": row['tags']
                }
                for row in results
            ]
    
    async def validate_configuration(
        self,
        framework_name: str,
        configuration: Dict[str, Any],
        environment: str = "default"
    ) -> Dict[str, Any]:
        """Validate configuration against framework requirements"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Get framework schema for validation
        async with self._get_db_session() as session:
            query = """
                SELECT metadata FROM frameworks WHERE name = $1
            """
            
            result = await session.fetchval(query, framework_name)
            
            if result and 'configuration_schema' in result:
                schema = result['configuration_schema']
                
                # Validate against schema
                try:
                    import jsonschema
                    jsonschema.validate(configuration, schema)
                except jsonschema.ValidationError as e:
                    validation_result["valid"] = False
                    validation_result["errors"].append(str(e))
                except Exception as e:
                    validation_result["warnings"].append(f"Schema validation error: {str(e)}")
        
        # Check for required credentials
        required_credentials = self._extract_credential_requirements(configuration)
        for cred_key in required_credentials:
            credential_value = await self.manage_credentials(
                framework_name, cred_key, environment=environment, operation="get"
            )
            if not credential_value:
                validation_result["errors"].append(f"Missing required credential: {cred_key}")
                validation_result["valid"] = False
        
        return validation_result
    
    async def _encrypt_sensitive_values(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration values"""
        encrypted_config = configuration.copy()
        sensitive_keys = ['api_key', 'secret', 'password', 'token', 'credential']
        
        def encrypt_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        if isinstance(value, str):
                            obj[key] = {
                                "__encrypted__": True,
                                "value": self.cipher.encrypt(value.encode()).decode()
                            }
                    elif isinstance(value, (dict, list)):
                        encrypt_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    encrypt_recursive(item)
        
        encrypt_recursive(encrypted_config)
        return encrypted_config
    
    async def _decrypt_configuration(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive configuration values"""
        decrypted_config = configuration.copy()
        
        def decrypt_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict) and value.get("__encrypted__"):
                        try:
                            obj[key] = self.cipher.decrypt(value["value"].encode()).decode()
                        except Exception:
                            obj[key] = value["value"]  # Fallback to encrypted value
                    elif isinstance(value, (dict, list)):
                        decrypt_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    decrypt_recursive(item)
        
        decrypt_recursive(decrypted_config)
        return decrypted_config
    
    def _merge_environment_variables(self, config: Dict[str, Any], framework_name: str) -> Dict[str, Any]:
        """Merge configuration with environment variables"""
        merged_config = config.copy()
        
        # Check for framework-specific environment variables
        env_prefix = f"{framework_name.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                merged_config[config_key] = value
        
        return merged_config
```

### 2. Database Migration System

```python
# migrations/framework_migrations.py
from typing import List
from sqlalchemy import text
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

class FrameworkMigration:
    """Framework-specific database migration utilities"""
    
    @staticmethod
    def create_framework_tables():
        """Create all framework-related tables"""
        
        # Frameworks table
        op.create_table(
            'frameworks',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('name', sa.String(100), unique=True, nullable=False),
            sa.Column('version', sa.String(50), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('adapter_class', sa.String(200), nullable=False),
            sa.Column('status', sa.String(50), server_default='active'),
            sa.Column('configuration', postgresql.JSONB(), server_default='{}'),
            sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'))
        )
        
        # Framework components table
        op.create_table(
            'framework_components',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('framework_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frameworks.id', ondelete='CASCADE'), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('category', sa.String(100), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('version', sa.String(50)),
            sa.Column('inputs', postgresql.JSONB(), server_default='[]'),
            sa.Column('outputs', postgresql.JSONB(), server_default='[]'),
            sa.Column('dependencies', postgresql.JSONB(), server_default='[]'),
            sa.Column('schema', postgresql.JSONB(), server_default='{}'),
            sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
            sa.Column('status', sa.String(50), server_default='available'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.UniqueConstraint('framework_id', 'name')
        )
        
        # Configuration environments
        op.create_table(
            'configuration_environments',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('name', sa.String(100), unique=True, nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('is_default', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'))
        )
        
        # Framework configurations
        op.create_table(
            'framework_configurations',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('framework_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frameworks.id', ondelete='CASCADE'), nullable=False),
            sa.Column('environment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('configuration_environments.id', ondelete='CASCADE'), nullable=False),
            sa.Column('configuration', postgresql.JSONB(), nullable=False, server_default='{}'),
            sa.Column('is_active', sa.Boolean(), server_default='true'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.UniqueConstraint('framework_id', 'environment_id')
        )
        
        # Credentials table
        op.create_table(
            'framework_credentials',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('framework_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('frameworks.id', ondelete='CASCADE'), nullable=False),
            sa.Column('environment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('configuration_environments.id', ondelete='CASCADE'), nullable=False),
            sa.Column('credential_key', sa.String(200), nullable=False),
            sa.Column('encrypted_value', sa.Text(), nullable=False),
            sa.Column('encryption_method', sa.String(100), server_default='AES-256-GCM'),
            sa.Column('metadata', postgresql.JSONB(), server_default='{}'),
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
            sa.UniqueConstraint('framework_id', 'environment_id', 'credential_key')
        )
    
    @staticmethod
    def seed_default_data():
        """Seed database with default framework data"""
        
        # Create default environment
        op.execute(text("""
            INSERT INTO configuration_environments (name, description, is_default)
            VALUES ('default', 'Default configuration environment', true)
            ON CONFLICT (name) DO NOTHING
        """))
        
        # Insert Agno framework
        op.execute(text("""
            INSERT INTO frameworks (name, version, description, adapter_class, metadata)
            VALUES (
                'agno',
                '2.0.0',
                'Agno AI framework integration with 45+ components',
                'langflow.core.frameworks.real_agno_adapter.RealAgnoAdapter',
                '{"component_count": 45, "categories": ["model", "tool", "vector_store", "knowledge_base", "embedder", "memory", "storage", "reranker", "chunking", "document_reader", "agent", "team", "workflow"]}'
            )
            ON CONFLICT (name) DO UPDATE SET
                version = EXCLUDED.version,
                description = EXCLUDED.description,
                metadata = EXCLUDED.metadata,
                updated_at = NOW()
        """))
        
        # Insert Langflow framework
        op.execute(text("""
            INSERT INTO frameworks (name, version, description, adapter_class, metadata)
            VALUES (
                'langflow',
                '1.0.0',
                'Native Langflow components and workflows',
                'langflow.core.frameworks.langflow_adapter.LangflowAdapter',
                '{"native": true, "built_in": true}'
            )
            ON CONFLICT (name) DO NOTHING
        """))
```

## 📋 Implementation Checklist

### Database Schema
- [ ] Create framework metadata tables
- [ ] Implement component persistence tables
- [ ] Add configuration management tables
- [ ] Create credential storage with encryption
- [ ] Add workflow and execution tracking tables

### Configuration System
- [ ] Implement configuration manager with encryption
- [ ] Add environment-specific configuration support
- [ ] Create credential management with secure storage
- [ ] Add configuration validation and templates
- [ ] Implement configuration inheritance and overrides

### Database Migrations
- [ ] Create Alembic migration scripts
- [ ] Add seed data for default frameworks
- [ ] Implement rollback procedures
- [ ] Add data validation and integrity checks
- [ ] Create migration testing procedures

### Data Persistence
- [ ] Implement component execution logging
- [ ] Add performance metrics persistence
- [ ] Create workflow execution tracking
- [ ] Add configuration change auditing
- [ ] Implement data retention policies

## 🎯 Success Criteria

### Database Integration
- ✅ All framework data persisted in database
- ✅ Configuration management operational across environments
- ✅ Secure credential storage and access logging
- ✅ Workflow and execution history tracking
- ✅ Performance metrics data collection

### Configuration Management
- ✅ Environment-specific configurations working
- ✅ Credential encryption and secure access
- ✅ Configuration validation and templates
- ✅ Configuration inheritance and overrides
- ✅ Audit trails for all configuration changes

### Data Integrity
- ✅ Database migrations tested and reliable
- ✅ Data validation and constraint enforcement
- ✅ Backup and recovery procedures operational
- ✅ Performance optimization for large datasets
- ✅ Data retention and cleanup policies active

---

**🎯 Phase 5 Goal**: Establish robust data persistence and configuration management foundation that supports multi-environment deployments with secure credential handling and comprehensive audit trails.
