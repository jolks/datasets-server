# Developer guide

This document is intended for developers who want to install, test or contribute to the code.

## Install

To start working on the project:

```bash
git clone git@github.com:huggingface/datasets-server.git
cd datasets-server
```

Install docker (see https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository and https://docs.docker.com/engine/install/linux-postinstall/)

```
make install
make start-from-local-code
```

To use the docker images already compiled using the CI:

```
make start-from-remote-images
```

To install a single library (in [libs](./libs)) or service (in [services](./services)), install Python 3.9 (consider [pyenv](https://github.com/pyenv/pyenv)) and [poetry](https://python-poetry.org/docs/master/#installation) (don't forget to add `poetry` to the `PATH` environment variable).

If you use pyenv:

```bash
cd libs/libutils/
pyenv install 3.9.6
pyenv local 3.9.6
poetry env use python3.9
```

then:

```
make install
```

It will create a virtual environment in a `./.venv/` subdirectory.

If you use VSCode, it might be useful to use the ["monorepo" workspace](./.vscode/monorepo.code-workspace) (see a [blogpost](https://medium.com/rewrite-tech/visual-studio-code-tips-for-monorepo-development-with-multi-root-workspaces-and-extension-6b69420ecd12) for more explanations). It is a multi-root workspace, with one folder for each library and service (note that we hide them from the ROOT to avoid editing there). Each folder has its own Python interpreter, with access to the dependencies installed by Poetry. You might have to manually select the interpreter in every folder though on first access, then VSCode stores the information in its local storage.

## Architecture

The repository is structured as a monorepo, with Python applications in [services/](./services/) and Python libraries in [libs/](./libs/).

If you have access to the internal HF notion, see https://www.notion.so/huggingface2/Datasets-server-464848da2a984e999c540a4aa7f0ece5.

The application is distributed in several components.

[api](./services/api) is a web server that exposes the [API endpoints](https://huggingface.co/docs/datasets-server). Apart from some endpoints (`valid`, `is-valid`), all the responses are served from pre-computed responses. That's the main point of this project: generating these responses takes time, and the API server provides this service to the users.

The precomputed responses are stored in a Mongo database called "cache" (see [libcache](./libs/libcache)). They are computed by workers ([worker](./services/worker)) which take their jobs from a job queue stored in a Mongo database called "queue" (see [libqueue](./libs/libqueue)), and store the results (error or valid response) into the "cache".

The API service exposes the `/webhook` endpoint which is called by the Hub on every creation, update or deletion of a dataset on the Hub. On deletion, the cached responses are deleted. On creation or update, a new job is appended in the "queue" database.

Note that two job queues exist:

- `splits`: the job is to refresh a dataset, namely to get the list of [config](https://huggingface.co/docs/datasets/v2.1.0/en/load_hub#select-a-configuration) and [split](https://huggingface.co/docs/datasets/v2.1.0/en/load_hub#select-a-split) names, then to create a new job for every split
- `first-rows`: the job is to get the columns and the first 100 rows of the split

Note also that the workers create local files when the dataset contains images or audios. A shared directory (`ASSETS_DIRECTORY`) must therefore be provisioned with sufficient space for the generated files. The `/first-rows` endpoint responses contain URLs to these files, served by the API under the `/assets/` endpoint.

Hence, the working application has:

- one instance of the API service which exposes a port
- M instances of the `splits` worker and N instances of the `first-rows` worker (N should generally be higher than M)
- a Mongo server with two databases: "cache" and "queue"
- a shared directory for the assets

The application also has:

- a reverse proxy in front of the API to serve static files and proxy the rest to the API server
- an admin server to serve technical endpoints

The following environments contain all the modules: reverse proxy, API server, admin API server, workers, and the Mongo database.

| Environment              | URL                                                  | Type              | How to deploy                                                           |
| ------------------------ | ---------------------------------------------------- | ----------------- | ----------------------------------------------------------------------- |
| Production               | https://datasets-server.huggingface.co               | Helm / Kubernetes | `make upgrade-prod` in [chart](./chart)                                 |
| Development              | https://datasets-server.us.dev.moon.huggingface.tech | Helm / Kubernetes | `make upgrade-dev` in [chart](./chart)                                  |
| Local from remote images | http://localhost:8100                                | Docker compose    | `make start-from-remote-images` (fetches docker images from Docker Hub) |
| Local build              | http://localhost:8000                                | Docker compose    | `make start-from-local-code` (builds docker images)                     |

## Quality

The CI checks the quality of the code through a [GitHub action](./.github/workflows/quality.yml). To manually format the code of a library or a service:

```bash
make style
```

To check the quality (which includes checking the style, but also security vulnerabilities):

```bash
make quality
```

## Tests

The CI checks the tests a [GitHub action](./.github/workflows/unit-tests.yml). To manually test a library or a service:

```bash
make test
```

Note that it requires the resources to be ready, ie. mongo and the storage for assets.

To launch the end to end tests:

```bash
make e2e
```

## Poetry

### Versions

We version the [libraries](./libs) as they are dependencies of the [services](./services). To update a library:

- change the version in its pyproject.yaml file
- build with `make build`
- version the new files in `dist/`

And then update the library version in the services that require the update, for example if the library is `libcache`:

```
poetry update libcache
```

If service is updated, we don't update its version in the `pyproject.yaml` file. But we have to update the [docker images file](./chart/docker-images.yaml) with the new image tag. Then the CI will test the new docker images, and we will be able to deploy them to the infrastructure.

## Pull requests

All the contributions should go through a pull request. The pull requests must be "squashed" (ie: one commit per pull request).

## GitHub Actions

You can use [act](https://github.com/nektos/act) to test the GitHub Actions (see [.github/workflows/](.github/workflows/)) locally. It reduces the retroaction loop when working on the GitHub Actions, avoid polluting the branches with empty pushes only meant to trigger the CI, and allows to only run specific actions.

For example, to launch the build and push of the docker images to Docker Hub:

```
act -j build-and-push-image-to-docker-hub --secret-file my.secrets
```

with `my.secrets` a file with the secrets:

```
DOCKERHUB_USERNAME=xxx
DOCKERHUB_PASSWORD=xxx
GITHUB_TOKEN=xxx
```

## Mac OS

To install the [worker service](./services/worker) on Mac OS, you can follow the next steps.

### First: as an administrator

Install brew:

```bash
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install ICU:

```bash
$ brew install icu4c


==> Caveats
icu4c is keg-only, which means it was not symlinked into /opt/homebrew,
because macOS provides libicucore.dylib (but nothing else).

If you need to have icu4c first in your PATH, run:
  echo 'export PATH="/opt/homebrew/opt/icu4c/bin:$PATH"' >> ~/.zshrc
  echo 'export PATH="/opt/homebrew/opt/icu4c/sbin:$PATH"' >> ~/.zshrc

For compilers to find icu4c you may need to set:
  export LDFLAGS="-L/opt/homebrew/opt/icu4c/lib"
  export CPPFLAGS="-I/opt/homebrew/opt/icu4c/include"
```

### Then: as a normal user

Add ICU to the path:

```bash
$ echo 'export PATH="/opt/homebrew/opt/icu4c/bin:$PATH"' >> ~/.zshrc
$ echo 'export PATH="/opt/homebrew/opt/icu4c/sbin:$PATH"' >> ~/.zshrc
```

Install pyenv:

```bash
$ curl https://pyenv.run | bash
```

append the following lines to ~/.zshrc:

```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Logout and login again.

Install Python 3.9.6:

```bash
$ pyenv install 3.9.6
```

Check that the expected local version of Python is used:

```bash
$ cd services/workers
$ python --version
Python 3.9.6
```

Install poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

append the following lines to ~/.zshrc:

```bash
export PATH="/Users/slesage2/.local/bin:$PATH"
```

Install rust:

```bash
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
$ source $HOME/.cargo/env
```

Set the python version to use with poetry:

```bash
poetry env use 3.9.6
```

Avoid an issue with Apache beam (https://github.com/python-poetry/poetry/issues/4888#issuecomment-1208408509):

```bash
poetry config experimental.new-installer false
```

Install the dependencies:

```bash
make install
```
