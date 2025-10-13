"""
fragua.core.config
------------------
Minimal configuration helpers. Start small; can be extended to YAML/ENV.
"""

from dataclasses import dataclass
import os


@dataclass
class FraguaConfig:
    """
    Basic configuration dataclass.
    Extend with more fields as needed.
    """

    tmp_dir: str = "/tmp/fragua"
    default_encoding: str = "utf-8"
    log_level: str = "INFO"


def load_config() -> FraguaConfig:
    """
    Load configuration from environment variables (fallback to defaults).
    """
    tmp_dir = os.getenv("FRAGUA_TMP_DIR", FraguaConfig.tmp_dir)
    default_encoding = os.getenv("FRAGUA_ENCODING", FraguaConfig.default_encoding)
    log_level = os.getenv("FRAGUA_LOG_LEVEL", FraguaConfig.log_level)
    return FraguaConfig(
        tmp_dir=tmp_dir, default_encoding=default_encoding, log_level=log_level
    )
