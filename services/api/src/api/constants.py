# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

from typing import Optional

DEFAULT_APP_HOSTNAME: str = "localhost"
DEFAULT_APP_NUM_WORKERS: int = 2
DEFAULT_APP_PORT: int = 8000
DEFAULT_ASSETS_DIRECTORY: None = None
DEFAULT_DATASETS_ENABLE_PRIVATE: bool = False
DEFAULT_HF_AUTH_PATH: str = "/api/datasets/%s/auth-check"
DEFAULT_HF_ENDPOINT: str = "https://huggingface.co"
DEFAULT_HF_TOKEN: Optional[str] = None
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_MAX_AGE_LONG_SECONDS: int = 120  # 2 minutes
DEFAULT_MAX_AGE_SHORT_SECONDS: int = 10  # 10 seconds
DEFAULT_MONGO_CACHE_DATABASE: str = "datasets_server_cache"
DEFAULT_MONGO_QUEUE_DATABASE: str = "datasets_server_queue"
DEFAULT_MONGO_URL: str = "mongodb://localhost:27018"
