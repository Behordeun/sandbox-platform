from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ConfigType(str, Enum):
    """Configuration types."""

    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGING = "messaging"
    SECURITY = "security"
    MONITORING = "monitoring"
    CUSTOM = "custom"


class ConfigFormat(str, Enum):
    """Configuration formats."""

    JSON = "json"
    YAML = "yaml"
    PROPERTIES = "properties"
    ENV = "env"


class ConfigStatus(str, Enum):
    """Configuration status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


class ConfigBase(BaseModel):
    """Base configuration model."""

    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    config_type: ConfigType = Field(ConfigType.CUSTOM, description="Configuration type")
    environment: str = Field("development", description="Target environment")
    tags: List[str] = Field(default_factory=list, description="Configuration tags")

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Configuration name cannot be empty")
        if len(v) > 100:
            raise ValueError("Configuration name cannot exceed 100 characters")
        return v.strip()

    @validator("environment")
    def validate_environment(cls, v):
        from app.core.config import settings

        if v not in settings.supported_environments:
            raise ValueError(
                f"Environment must be one of: {settings.supported_environments}"
            )
        return v


class ConfigCreate(ConfigBase):
    """Configuration creation model."""

    data: Dict[str, Any] = Field(..., description="Configuration data")
    format: ConfigFormat = Field(ConfigFormat.JSON, description="Configuration format")
    encrypt_sensitive: bool = Field(True, description="Encrypt sensitive values")
    sensitive_keys: Optional[List[str]] = Field(None, description="Keys to encrypt")


class ConfigUpdate(BaseModel):
    """Configuration update model."""

    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[ConfigStatus] = None
    encrypt_sensitive: Optional[bool] = None
    sensitive_keys: Optional[List[str]] = None


class ConfigResponse(ConfigBase):
    """Configuration response model."""

    id: str = Field(..., description="Configuration ID")
    data: Dict[str, Any] = Field(..., description="Configuration data")
    format: ConfigFormat = Field(..., description="Configuration format")
    status: ConfigStatus = Field(..., description="Configuration status")
    version: int = Field(..., description="Configuration version")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Created by user")
    updated_by: Optional[str] = Field(None, description="Updated by user")

    class Config:
        from_attributes = True


class ConfigVersion(BaseModel):
    """Configuration version model."""

    version: int = Field(..., description="Version number")
    data: Dict[str, Any] = Field(..., description="Configuration data at this version")
    created_at: datetime = Field(..., description="Version creation timestamp")
    created_by: Optional[str] = Field(None, description="Version created by user")
    change_summary: Optional[str] = Field(None, description="Summary of changes")


class ConfigHistory(BaseModel):
    """Configuration history model."""

    config_id: str = Field(..., description="Configuration ID")
    versions: List[ConfigVersion] = Field(..., description="Configuration versions")


class ConfigTemplate(BaseModel):
    """Configuration template model."""

    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    config_type: ConfigType = Field(..., description="Configuration type")
    template_data: Dict[str, Any] = Field(..., description="Template structure")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    created_at: datetime = Field(..., description="Creation timestamp")


class ConfigValidationRule(BaseModel):
    """Configuration validation rule."""

    field_path: str = Field(..., description="JSON path to field")
    rule_type: str = Field(..., description="Validation rule type")
    rule_config: Dict[str, Any] = Field(..., description="Rule configuration")
    error_message: str = Field(..., description="Error message for validation failure")


class ConfigSchema(BaseModel):
    """Configuration schema for validation."""

    name: str = Field(..., description="Schema name")
    config_type: ConfigType = Field(..., description="Configuration type")
    schema_data: Dict[str, Any] = Field(..., description="JSON schema")
    validation_rules: List[ConfigValidationRule] = Field(
        default_factory=list, description="Custom validation rules"
    )
    created_at: datetime = Field(..., description="Creation timestamp")


class ConfigDiff(BaseModel):
    """Configuration difference model."""

    added: Dict[str, Any] = Field(default_factory=dict, description="Added keys")
    removed: Dict[str, Any] = Field(default_factory=dict, description="Removed keys")
    modified: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Modified keys with old/new values"
    )


class ConfigExport(BaseModel):
    """Configuration export model."""

    configs: List[ConfigResponse] = Field(..., description="Configurations to export")
    export_format: ConfigFormat = Field(ConfigFormat.JSON, description="Export format")
    include_sensitive: bool = Field(False, description="Include sensitive data")
    environment_filter: Optional[str] = Field(None, description="Filter by environment")


class ConfigImport(BaseModel):
    """Configuration import model."""

    configs: List[ConfigCreate] = Field(..., description="Configurations to import")
    overwrite_existing: bool = Field(False, description="Overwrite existing configs")
    validate_before_import: bool = Field(True, description="Validate before importing")
