import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiofiles
import redis
from app.core.config import settings
from app.core.encryption import config_encryption
from app.models.config import (
    ConfigCreate,
    ConfigDiff,
    ConfigHistory,
    ConfigResponse,
    ConfigStatus,
    ConfigUpdate,
)


class ConfigStorage:
    """Abstract base class for configuration storage."""

    async def get(self, config_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    async def set(self, config_id: str, data: Dict[str, Any]) -> bool:
        raise NotImplementedError

    async def delete(self, config_id: str) -> bool:
        raise NotImplementedError

    async def list_all(self) -> List[str]:
        raise NotImplementedError

    async def exists(self, config_id: str) -> bool:
        raise NotImplementedError


class MemoryStorage(ConfigStorage):
    """In-memory configuration storage."""

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}

    async def get(self, config_id: str) -> Optional[Dict[str, Any]]:
        return self._storage.get(config_id)

    async def set(self, config_id: str, data: Dict[str, Any]) -> bool:
        self._storage[config_id] = data
        return True

    async def delete(self, config_id: str) -> bool:
        if config_id in self._storage:
            del self._storage[config_id]
            return True
        return False

    async def list_all(self) -> List[str]:
        return list(self._storage.keys())

    async def exists(self, config_id: str) -> bool:
        return config_id in self._storage


class RedisStorage(ConfigStorage):
    """Redis-based configuration storage."""

    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.key_prefix = "sandbox:config:"

    async def get(self, config_id: str) -> Optional[Dict[str, Any]]:
        try:
            # Since redis_client.get is synchronous, call it in a thread executor
            import asyncio

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self.redis_client.get, f"{self.key_prefix}{config_id}"
            )
            if data:
                if isinstance(data, bytes):
                    return json.loads(data.decode())
                elif isinstance(data, str):
                    return json.loads(data)
                else:
                    return None
            return None
        except Exception:
            return None

    async def set(self, config_id: str, data: Dict[str, Any]) -> bool:
        try:
            self.redis_client.set(
                f"{self.key_prefix}{config_id}", json.dumps(data, default=str)
            )
            return True
        except Exception:
            return False

    async def delete(self, config_id: str) -> bool:
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.redis_client.delete, f"{self.key_prefix}{config_id}"
            )
            return int(result or 0) > 0
        except Exception:
            return False

    async def list_all(self) -> List[str]:
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            keys = await loop.run_in_executor(
                None, self.redis_client.keys, f"{self.key_prefix}*"
            )
            if keys is None:
                return []
            return [key.decode().replace(self.key_prefix, "") for key in keys]
        except Exception:
            return []

    async def exists(self, config_id: str) -> bool:
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.redis_client.exists, f"{self.key_prefix}{config_id}"
            )
            return int(result or 0) > 0
        except Exception:
            return False


class FileStorage(ConfigStorage):
    """File-based configuration storage."""

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_file_path(self, config_id: str) -> str:
        return os.path.join(self.base_path, f"{config_id}.json")

    async def get(self, config_id: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = self._get_file_path(config_id)
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, "r") as f:
                    content = await f.read()
                    return json.loads(content)
            return None
        except Exception:
            return None

    async def set(self, config_id: str, data: Dict[str, Any]) -> bool:
        try:
            file_path = self._get_file_path(config_id)
            async with aiofiles.open(file_path, "w") as f:
                await f.write(json.dumps(data, indent=2, default=str))
            return True
        except Exception:
            return False

    async def delete(self, config_id: str) -> bool:
        try:
            file_path = self._get_file_path(config_id)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    async def list_all(self) -> List[str]:
        try:
            files = [
                f.replace(".json", "")
                for f in os.listdir(self.base_path)
                if f.endswith(".json")
            ]
            return files
        except Exception:
            return []

    async def exists(self, config_id: str) -> bool:
        file_path = self._get_file_path(config_id)
        return os.path.exists(file_path)


class ConfigManager:
    """Configuration management service."""

    def __init__(self):
        self.storage = self._create_storage()
        self.version_storage = self._create_storage("versions")

    def _create_storage(self, suffix: str = "") -> ConfigStorage:
        """Create storage instance based on configuration."""
        storage_type = settings.storage_type

        if storage_type == "redis":
            return RedisStorage(settings.redis_url)
        elif storage_type == "file":
            path = settings.config_file_path
            if suffix:
                path = os.path.join(path, suffix)
            return FileStorage(path)
        else:
            return MemoryStorage()

    async def create_config(
        self, config_data: ConfigCreate, created_by: Optional[list[str]] = None
    ) -> ConfigResponse:
        """Create a new configuration."""
        config_id = str(uuid.uuid4())
        now = datetime.now()

        # Process configuration data
        processed_data = config_data.data.copy()

        # Encrypt sensitive values if requested
        if config_data.encrypt_sensitive:
            processed_data = config_encryption.encrypt_config(
                processed_data, config_data.sensitive_keys
            )

        # Create configuration record
        config_record = {
            "id": config_id,
            "name": config_data.name,
            "description": config_data.description,
            "config_type": config_data.config_type,
            "environment": config_data.environment,
            "tags": config_data.tags,
            "data": processed_data,
            "format": config_data.format,
            "status": ConfigStatus.ACTIVE,
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
            "updated_by": created_by,
        }

        # Store configuration
        await self.storage.set(config_id, config_record)

        # Store initial version
        if settings.versioning_enabled:
            created_by_str = ""
            if isinstance(created_by, list):
                created_by_str = ", ".join(created_by)
            elif created_by is not None:
                created_by_str = created_by
            await self._store_version(config_id, 1, processed_data, created_by_str)

        return ConfigResponse(**config_record)

    async def get_config(
        self, config_id: str, decrypt_sensitive: bool = True
    ) -> Optional[ConfigResponse]:
        """Get configuration by ID."""
        config_record = await self.storage.get(config_id)
        if not config_record:
            return None

        # Decrypt sensitive values if requested
        if decrypt_sensitive:
            config_record["data"] = config_encryption.decrypt_config(
                config_record["data"]
            )

        return ConfigResponse(**config_record)

    async def update_config(
        self,
        config_id: str,
        update_data: ConfigUpdate,
        updated_by: Optional[str] = None,
    ) -> Optional[ConfigResponse]:
        """Update an existing configuration."""
        config_record = await self.storage.get(config_id)
        if not config_record:
            return None

        now = datetime.now()
        old_version = config_record["version"]
        new_version = old_version + 1

        # Update fields
        if update_data.description is not None:
            config_record["description"] = update_data.description

        if update_data.tags is not None:
            config_record["tags"] = update_data.tags

        if update_data.status is not None:
            config_record["status"] = update_data.status

        if update_data.data is not None:
            # Process new data
            processed_data = update_data.data.copy()

            # Encrypt sensitive values if requested
            encrypt_sensitive = update_data.encrypt_sensitive
            if encrypt_sensitive is None:
                # Check if original data had encrypted values
                encrypt_sensitive = any(
                    config_encryption.is_encrypted_value(v)
                    for v in config_record["data"].values()
                    if isinstance(v, dict)
                )

            if encrypt_sensitive:
                processed_data = config_encryption.encrypt_config(
                    processed_data, update_data.sensitive_keys
                )

            config_record["data"] = processed_data
            config_record["version"] = new_version

        config_record["updated_at"] = now
        config_record["updated_by"] = updated_by

        # Store updated configuration
        await self.storage.set(config_id, config_record)

        # Store new version
        if settings.versioning_enabled and update_data.data is not None:
            await self._store_version(
                config_id, new_version, config_record["data"], updated_by or ""
            )

        # Decrypt for response
        config_record["data"] = config_encryption.decrypt_config(config_record["data"])

        return ConfigResponse(**config_record)

    async def delete_config(self, config_id: str) -> bool:
        """Delete a configuration."""
        success = await self.storage.delete(config_id)

        # Also delete versions
        if settings.versioning_enabled:
            await self.version_storage.delete(config_id)

        return success

    async def list_configs(
        self,
        environment: Optional[str] = None,
        config_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[ConfigResponse]:
        """List configurations with optional filtering."""
        config_ids = await self.storage.list_all()
        configs = []

        for config_id in config_ids:
            config_record = await self.storage.get(config_id)
            if not config_record:
                continue

            # Apply filters
            if environment and config_record["environment"] != environment:
                continue

            if config_type and config_record["config_type"] != config_type:
                continue

            if tags:
                config_tags = set(config_record.get("tags", []))
                if not set(tags).intersection(config_tags):
                    continue

            # Decrypt sensitive values
            config_record["data"] = config_encryption.decrypt_config(
                config_record["data"]
            )

            configs.append(ConfigResponse(**config_record))

        return configs

    async def get_config_history(self, config_id: str) -> Optional[ConfigHistory]:
        """Get configuration version history."""
        if not settings.versioning_enabled:
            return None

        version_record = await self.version_storage.get(config_id)
        if not version_record:
            return None

        return ConfigHistory(**version_record)

    async def get_config_diff(
        self, config_id: str, version1: int, version2: int
    ) -> Optional[ConfigDiff]:
        """Get difference between two configuration versions."""
        history = await self.get_config_history(config_id)
        if not history:
            return None

        # Find versions
        v1_data = None
        v2_data = None

        for version in history.versions:
            if version.version == version1:
                v1_data = version.data
            elif version.version == version2:
                v2_data = version.data

        if v1_data is None or v2_data is None:
            return None

        return self._calculate_diff(v1_data, v2_data)

    async def _store_version(
        self,
        config_id: str,
        version: int,
        data: Dict[str, Any],
        created_by: Optional[str] = None,
    ):
        """Store a configuration version."""
        version_record = await self.version_storage.get(config_id)

        if not version_record:
            version_record = {"config_id": config_id, "versions": []}

        # Add new version
        new_version = {
            "version": version,
            "data": data,
            "created_at": datetime.now(),
            "created_by": created_by,
        }

        version_record["versions"].append(new_version)

        # Limit number of versions
        if len(version_record["versions"]) > settings.max_versions:
            version_record["versions"] = version_record["versions"][
                -settings.max_versions :
            ]

        await self.version_storage.set(config_id, version_record)

    def _calculate_diff(
        self, data1: Dict[str, Any], data2: Dict[str, Any]
    ) -> ConfigDiff:
        """Calculate difference between two configuration data sets."""
        added = {}
        removed = {}
        modified = {}

        # Find added and modified keys
        for key, value in data2.items():
            if key not in data1:
                added[key] = value
            elif data1[key] != value:
                modified[key] = {"old": data1[key], "new": value}

        # Find removed keys
        for key, value in data1.items():
            if key not in data2:
                removed[key] = value

        return ConfigDiff(added=added, removed=removed, modified=modified)


# Global config manager instance
config_manager = ConfigManager()
