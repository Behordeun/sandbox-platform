from typing import Any, List, Optional

from app.models.config import (
    ConfigCreate,
    ConfigDiff,
    ConfigHistory,
    ConfigResponse,
    ConfigStatus,
    ConfigType,
    ConfigUpdate,
)
from app.services.config_manager import config_manager
from fastapi import APIRouter, HTTPException, Query

CONFIGURATION_ERROR = "Configuration not found"

router = APIRouter()


@router.post("/", response_model=ConfigResponse)
async def create_configuration(config_data: ConfigCreate) -> Any:
    """Create a new configuration."""
    try:
        config = await config_manager.create_config(config_data)
        return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ConfigResponse])
async def list_configurations(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    config_type: Optional[ConfigType] = Query(
        None, description="Filter by configuration type"
    ),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    include_deleted: bool = Query(False, description="Include soft-deleted configs"),
) -> Any:
    """List all configurations with optional filtering."""
    try:
        list_configs_kwargs = {
            "config_type": config_type.value if config_type else None,
            "tags": tags,
        }
        if environment is not None:
            list_configs_kwargs["environment"] = environment

        list_configs_kwargs["include_deleted"] = include_deleted
        configs = await config_manager.list_configs(**list_configs_kwargs)
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}", response_model=ConfigResponse)
async def get_configuration(
    config_id: str,
    decrypt_sensitive: bool = Query(True, description="Decrypt sensitive values"),
) -> Any:
    """Get a specific configuration by ID."""
    try:
        config = await config_manager.get_config(config_id, decrypt_sensitive)
        if not config:
            raise HTTPException(status_code=404, detail=CONFIGURATION_ERROR)
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_id}", response_model=ConfigResponse)
async def update_configuration(config_id: str, update_data: ConfigUpdate) -> Any:
    """Update an existing configuration."""
    try:
        config = await config_manager.update_config(config_id, update_data)
        if not config:
            raise HTTPException(status_code=404, detail=CONFIGURATION_ERROR)
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{config_id}")
async def delete_configuration(config_id: str) -> Any:
    """Delete a configuration."""
    try:
        success = await config_manager.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail=CONFIGURATION_ERROR)
        return {"message": "Configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}/history", response_model=ConfigHistory)
async def get_configuration_history(config_id: str) -> Any:
    """Get configuration version history."""
    try:
        history = await config_manager.get_config_history(config_id)
        if not history:
            raise HTTPException(
                status_code=404,
                detail="Configuration history not found or versioning not enabled",
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}/diff", response_model=ConfigDiff)
async def get_configuration_diff(
    config_id: str,
    version1: int = Query(..., description="First version to compare"),
    version2: int = Query(..., description="Second version to compare"),
) -> Any:
    """Get difference between two configuration versions."""
    try:
        diff = await config_manager.get_config_diff(config_id, version1, version2)
        if not diff:
            raise HTTPException(
                status_code=404, detail="Configuration versions not found"
            )
        return diff
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}/data")
async def get_configuration_data(
    config_id: str,
    key: Optional[str] = Query(None, description="Specific key to retrieve"),
    decrypt_sensitive: bool = Query(True, description="Decrypt sensitive values"),
) -> Any:
    """Get configuration data (or specific key) in raw format."""
    try:
        config = await config_manager.get_config(config_id, decrypt_sensitive)
        if not config:
            raise HTTPException(status_code=404, detail=CONFIGURATION_ERROR)

        if key:
            # Return specific key
            if key in config.data:
                return {"key": key, "value": config.data[key]}
            else:
                raise HTTPException(status_code=404, detail=f"Key '{key}' not found")

        # Return all data
        return config.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{config_id}/status")
async def update_configuration_status(config_id: str, status: ConfigStatus) -> Any:
    """Update configuration status."""
    try:
        update_data = ConfigUpdate(status=status)
        config = await config_manager.update_config(config_id, update_data)
        if not config:
            raise HTTPException(status_code=404, detail=CONFIGURATION_ERROR)
        return {"message": f"Configuration status updated to {status.value}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
