# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

from typing import Optional

DEFAULT_ASSETS_BASE_URL: str = "assets"
DEFAULT_ASSETS_DIRECTORY: None = None
DEFAULT_DATASETS_REVISION: str = "main"
DEFAULT_HF_ENDPOINT: str = "https://huggingface.co"
DEFAULT_HF_TOKEN: Optional[str] = None
DEFAULT_LOG_LEVEL: str = "INFO"
DEFAULT_MAX_JOB_RETRIES: int = 3
DEFAULT_MAX_JOBS_PER_DATASET: int = 1
DEFAULT_MAX_LOAD_PCT: int = 70
DEFAULT_MAX_MEMORY_PCT: int = 80
DEFAULT_MAX_SIZE_FALLBACK: int = 100_000_000
DEFAULT_MIN_CELL_BYTES: int = 100
DEFAULT_MONGO_CACHE_DATABASE: str = "datasets_server_cache"
DEFAULT_MONGO_QUEUE_DATABASE: str = "datasets_server_queue"
DEFAULT_MONGO_URL: str = "mongodb://localhost:27018"
DEFAULT_ROWS_MAX_BYTES: int = 1_000_000
DEFAULT_ROWS_MAX_NUMBER: int = 100
DEFAULT_ROWS_MIN_NUMBER: int = 10
DEFAULT_WORKER_SLEEP_SECONDS: int = 15
DEFAULT_WORKER_QUEUE: str = "splits_responses"
