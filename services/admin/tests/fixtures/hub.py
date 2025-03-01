# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

# Adapted from https://github.com/huggingface/datasets/blob/main/tests/fixtures/hub.py

import time
from contextlib import contextmanager, suppress
from typing import Dict, Iterable, Literal, Optional, TypedDict

import pytest
import requests
from huggingface_hub.hf_api import (  # type: ignore
    REPO_TYPES,
    REPO_TYPES_URL_PREFIXES,
    HfApi,
    HfFolder,
    _raise_for_status,
)

# see https://github.com/huggingface/moon-landing/blob/main/server/scripts/staging-seed-db.ts
CI_HUB_USER = "__DUMMY_DATASETS_SERVER_USER__"
CI_HUB_USER_API_TOKEN = "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"

CI_HUB_ENDPOINT = "https://hub-ci.huggingface.co"
CI_HUB_DATASETS_URL = CI_HUB_ENDPOINT + "/datasets/{repo_id}/resolve/{revision}/{path}"


def update_repo_settings(
    hf_api: HfApi,
    repo_id: str,
    *,
    private: Optional[bool] = None,
    gated: Optional[bool] = None,
    token: Optional[str] = None,
    organization: Optional[str] = None,
    repo_type: Optional[str] = None,
    name: str = None,
) -> Dict[str, bool]:
    """Update the settings of a repository.
    Args:
        repo_id (`str`, *optional*):
            A namespace (user or an organization) and a repo name separated
            by a `/`.
            <Tip>
            Version added: 0.5
            </Tip>
        private (`bool`, *optional*, defaults to `None`):
            Whether the repo should be private.
        gated (`bool`, *optional*, defaults to `None`):
            Whether the repo should request user access.
        token (`str`, *optional*):
            An authentication token (See https://huggingface.co/settings/token)
        repo_type (`str`, *optional*):
            Set to `"dataset"` or `"space"` if uploading to a dataset or
            space, `None` or `"model"` if uploading to a model. Default is
            `None`.
    Returns:
        The HTTP response in json.
    <Tip>
    Raises the following errors:
        - [`~huggingface_hub.utils.RepositoryNotFoundError`]
            If the repository to download from cannot be found. This may be because it doesn't exist,
            or because it is set to `private` and you do not have access.
    </Tip>
    """
    if repo_type not in REPO_TYPES:
        raise ValueError("Invalid repo type")

    organization, name = repo_id.split("/") if "/" in repo_id else (None, repo_id)

    token, name = hf_api._validate_or_retrieve_token(token, name, function_name="update_repo_settings")

    if organization is None:
        namespace = hf_api.whoami(token)["name"]
    else:
        namespace = organization

    path_prefix = f"{hf_api.endpoint}/api/"
    if repo_type in REPO_TYPES_URL_PREFIXES:
        path_prefix += REPO_TYPES_URL_PREFIXES[repo_type]

    path = f"{path_prefix}{namespace}/{name}/settings"

    json = {}
    if private is not None:
        json["private"] = private
    if gated is not None:
        json["gated"] = gated

    r = requests.put(
        path,
        headers={"authorization": f"Bearer {token}"},
        json=json,
    )
    _raise_for_status(r)
    return r.json()


@pytest.fixture
def set_ci_hub_access_token() -> Iterable[None]:
    _api = HfApi(endpoint=CI_HUB_ENDPOINT)
    _api.set_access_token(CI_HUB_USER_API_TOKEN)
    HfFolder.save_token(CI_HUB_USER_API_TOKEN)
    yield
    HfFolder.delete_token()
    _api.unset_access_token()


@pytest.fixture(scope="session")
def hf_api():
    return HfApi(endpoint=CI_HUB_ENDPOINT)


@pytest.fixture(scope="session")
def hf_token(hf_api: HfApi) -> Iterable[str]:
    hf_api.set_access_token(CI_HUB_USER_API_TOKEN)
    HfFolder.save_token(CI_HUB_USER_API_TOKEN)
    yield CI_HUB_USER_API_TOKEN
    with suppress(requests.exceptions.HTTPError):
        hf_api.unset_access_token()


@pytest.fixture
def cleanup_repo(hf_api: HfApi):
    def _cleanup_repo(repo_id):
        hf_api.delete_repo(repo_id=repo_id, token=CI_HUB_USER_API_TOKEN, repo_type="dataset")

    return _cleanup_repo


@pytest.fixture
def temporary_repo(cleanup_repo):
    @contextmanager
    def _temporary_repo(repo_id):
        try:
            yield repo_id
        finally:
            cleanup_repo(repo_id)

    return _temporary_repo


def create_unique_repo_name(prefix: str, user: str) -> str:
    repo_name = f"{prefix}-{int(time.time() * 10e3)}"
    return f"{user}/{repo_name}"


def create_hf_dataset_repo(
    hf_api: HfApi, hf_token: str, prefix: str, *, private=False, gated=False, user=CI_HUB_USER
) -> str:
    repo_id = create_unique_repo_name(prefix, user)
    hf_api.create_repo(repo_id=repo_id, token=hf_token, repo_type="dataset", private=private)
    if gated:
        update_repo_settings(hf_api, repo_id, token=hf_token, gated=gated, repo_type="dataset")
    return repo_id


# https://docs.pytest.org/en/6.2.x/fixture.html#yield-fixtures-recommended
@pytest.fixture(scope="session", autouse=True)
def hf_public_dataset_repo_empty(hf_api: HfApi, hf_token: str) -> Iterable[str]:
    repo_id = create_hf_dataset_repo(hf_api=hf_api, hf_token=hf_token, prefix="repo_empty")
    yield repo_id
    with suppress(requests.exceptions.HTTPError, ValueError):
        hf_api.delete_repo(repo_id=repo_id, token=hf_token, repo_type="dataset")


@pytest.fixture(scope="session", autouse=True)
def hf_gated_dataset_repo_empty(hf_api: HfApi, hf_token: str) -> Iterable[str]:
    repo_id = create_hf_dataset_repo(hf_api=hf_api, hf_token=hf_token, prefix="repo_empty", gated=True)
    yield repo_id
    with suppress(requests.exceptions.HTTPError, ValueError):
        hf_api.delete_repo(repo_id=repo_id, token=hf_token, repo_type="dataset")


@pytest.fixture(scope="session", autouse=True)
def hf_private_dataset_repo_empty(hf_api: HfApi, hf_token: str) -> Iterable[str]:
    repo_id = create_hf_dataset_repo(hf_api=hf_api, hf_token=hf_token, prefix="repo_empty", private=True)
    yield repo_id
    with suppress(requests.exceptions.HTTPError, ValueError):
        hf_api.delete_repo(repo_id=repo_id, token=hf_token, repo_type="dataset")


class DatasetRepos(TypedDict):
    public: str
    private: str
    gated: str


DatasetReposType = Literal["public", "private", "gated"]


@pytest.fixture(scope="session", autouse=True)
def hf_dataset_repos_csv_data(
    hf_public_dataset_repo_empty,
    hf_gated_dataset_repo_empty,
    hf_private_dataset_repo_empty,
) -> DatasetRepos:
    return {
        "public": hf_public_dataset_repo_empty,
        "private": hf_private_dataset_repo_empty,
        "gated": hf_gated_dataset_repo_empty,
    }
