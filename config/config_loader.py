"""
Configuration Loader for Sandbox Platform
Loads and merges YAML configuration files with environment variable support
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigLoader:
    """Load and manage YAML configuration files with environment variable substitution."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.base_config_file = "config.yaml"
        self._config_cache = {}

    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration for specified environment."""
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")

        # Check cache first
        cache_key = f"{environment}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        # Load base configuration
        base_config = self._load_yaml_file(self.base_config_file)

        # Load environment-specific configuration
        env_config_file = f"environments/{environment}.yaml"
        env_config = self._load_yaml_file(env_config_file)

        # Merge configurations (environment overrides base)
        merged_config = self._deep_merge(base_config, env_config)

        # Substitute environment variables
        final_config = self._substitute_env_vars(merged_config)

        # Cache the result
        self._config_cache[cache_key] = final_config

        return final_config

    def get_service_config(
        self, service_name: str, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        config = self.load_config(environment)

        # Try to get from services section first
        if "services" in config and service_name in config["services"]:
            return config["services"][service_name]

        # Try to get from sandbox section
        if "sandbox" in config and service_name in config["sandbox"]:
            return config["sandbox"][service_name]

        # Return empty dict if service not found
        return {}

    def get_database_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get database configuration."""
        config = self.load_config(environment)
        return config.get("database", {})

    def get_provider_config(
        self, provider_name: str, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get external provider configuration."""
        config = self.load_config(environment)

        if "providers" in config and provider_name in config["providers"]:
            return config["providers"][provider_name]

        return {}

    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file and return its contents."""
        file_path = self.config_dir / filename

        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {filename}: {e}")
        except Exception as e:
            raise ValueError(f"Error reading file {filename}: {e}")

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in configuration."""
        if isinstance(config, dict):
            return {
                key: self._substitute_env_vars(value) for key, value in config.items()
            }
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            # Extract environment variable name
            env_var = config[2:-1]
            default_value = None

            # Handle default values: ${VAR_NAME:default_value}
            if ":" in env_var:
                env_var, default_value = env_var.split(":", 1)

            return os.getenv(env_var, default_value)
        else:
            return config


# Global configuration loader instance
config_loader = ConfigLoader()


def get_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """Get the full configuration for the specified environment."""
    return config_loader.load_config(environment)


def get_service_config(
    service_name: str, environment: Optional[str] = None
) -> Dict[str, Any]:
    """Get configuration for a specific service."""
    return config_loader.get_service_config(service_name, environment)


def get_database_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """Get database configuration."""
    return config_loader.get_database_config(environment)


def get_provider_config(
    provider_name: str, environment: Optional[str] = None
) -> Dict[str, Any]:
    """Get external provider configuration."""
    return config_loader.get_provider_config(provider_name, environment)
