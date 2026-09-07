<div align="center">
  <table>
    <tr>
      <td>
        <a href="https://ondewo.com/en/products/natural-language-understanding/">
            <img width="400px" src="https://raw.githubusercontent.com/ondewo/ondewo-logos/master/ondewo_we_automate_your_phone_calls.png"/>
        </a>
      </td>
    </tr>
    <tr>
        <td align="center">
          <a href="https://www.linkedin.com/company/ondewo "><img width="40px" src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png"></a>
          <a href="https://www.facebook.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
          <a href="https://twitter.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733579.png"> </a>
          <a href="https://www.instagram.com/ondewo.ai/"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/174/174855.png"></a>
        </td>
    </tr>
  </table>
  <h1>
  Ondewo T2S Client Python Library
  </h1>
</div>

This library facilitates the interaction between a user and a CAI server. It achieves this by providing a higher-level interface mediator.

This higher-level interface mediator is structured around a series of python files generated from protobuf files. These protobuf files specify the details of the interface, and can be used to generate code in 10+ high-level languages. They are found in the [ONDEWO T2S API](https://github.com/ondewo/ondewo-t2s-api) along with the older Google protobufs from Dialogueflow that were used at the start. The [ONDEWO PROTO-COMPILER](https://github.com/ondewo/ondewo-proto-compiler) will generate the needed files directly in this library.

## Python Installation

You can install the library by installing it directly from the PyPi:

```bash
pip install ondewo-t2s-client
```

Or, you could clone it and install the requirements:

```bash
git clone git@github.com:ondewo/ondewo-t2s-client-python.git
cd ondewo-t2s-client-python
make setup_developer_environment_locally
```

## Repository Structure

```
.
├── .github
│   └── workflows
│       └── tests.yml            <- the CI gate: ruff -> mypy -> pytest @ 100% coverage
├── examples
│   ├── configs
│   │   ├── insecure_grpc.json
│   │   └── secure_grpc_placeholder.json
│   ├── environment.env
│   ├── example_api.py
│   ├── __init__.py
│   ├── ondewo_t2s_with_certificate.ipynb
│   ├── requirements.txt
│   └── synthesize_with_keycloak.py
├── ondewo
│   ├── t2s
│   │   ├── client
│   │   │   ├── core
│   │   │   │   ├── async_services_interface.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── services_interface.py
│   │   │   ├── services
│   │   │   │   ├── async_text_to_speech.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── text_to_speech.py
│   │   │   ├── utils
│   │   │   │   ├── __init__.py
│   │   │   │   └── keycloak.py      <- headless Keycloak offline-token auth (D18)
│   │   │   ├── async_client.py
│   │   │   ├── async_services_container.py
│   │   │   ├── client_config.py
│   │   │   ├── client.py
│   │   │   ├── __init__.py
│   │   │   └── services_container.py
│   │   ├── scripts
│   │   │   └── generate_services.py <- codegen, run by `make generate_services`
│   │   ├── __init__.py
│   │   ├── py.typed                 <- PEP 561 marker; without it the .pyi below is ignored
│   │   ├── text_to_speech_pb2_grpc.py
│   │   ├── text_to_speech_pb2.py
│   │   └── text_to_speech_pb2.pyi
│   └── __init__.py
├── tests
│   ├── e2e                          <- needs a live T2S server; NOT run by CI
│   │   ├── __init__.py
│   │   └── test_synthesize_request.py
│   ├── unit                         <- what the coverage gate runs
│   │   ├── __init__.py
│   │   ├── test_async_client.py
│   │   ├── test_client_config_redacts_secrets.py
│   │   ├── test_client.py
│   │   ├── test_keycloak.py
│   │   ├── test_services_interface.py
│   │   └── test_synthesize_with_keycloak_example.py
│   ├── __init__.py
│   └── conftest.py
├── ondewo-proto-compiler            <- submodule, pinned in Makefile
├── ondewo-t2s-api                   <- submodule, pinned in Makefile
├── .markdownlint-cli2.yaml
├── .pre-commit-config.yaml
├── .python-version                  <- 3.12; load-bearing, see CLAUDE.md
├── CONTRIBUTING.md
├── Dockerfile.utils
├── LICENSE
├── Makefile
├── MANIFEST.in
├── pyproject.toml                   <- deps + ruff/mypy/coverage config (no setup.py)
├── README.md
├── RELEASE.md
└── uv.lock
```

## Build

The `make build` command is dependent on 2 `repositories` and their speciefied `version`:

- [ondewo-t2s-api](https://github.com/ondewo/ondewo-t2s-api) -- `ONDEWO_T2S_API_GIT_BRANCH` in `Makefile`
- [ondewo-proto-compiler](https://github.com/ondewo/ondewo-proto-compiler) -- `ONDEWO_PROTO_COMPILER_GIT_BRANCH` in `Makefile`

It will generate a `_pb2.py`, `_pb2.pyi` and `_pb2_grpc.py` file for every `.proto` in the api submodule.

> :warning: All Files in the `ondewo` folder that dont have `pb2` in their name are handwritten, and therefor need to be manually adjusted to any changes in the proto-code.

To move to a newer proto-compiler release, do both halves or `make build` will silently use the old
image: check the submodule out at the tag and set the Makefile variable to the same tag.

```bash
git -C ondewo-proto-compiler fetch --tags origin
git -C ondewo-proto-compiler checkout <VERSION>       # e.g. 5.14.0
git add ondewo-proto-compiler
# then set ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/<VERSION> in the Makefile
git submodule status                                  # must show <VERSION>
```

Bumping the pin does **not** rewrite a single committed stub - it only changes which image
`make build` would build. Say "pinned", not "regenerated", in `RELEASE.md` unless you actually ran
`make build` and committed the regenerated `_pb2*` files.

## Development

```bash
make setup_developer_environment_locally   # uv + .venv (runtime + dev) + pre-commit hooks
```

The four commands below are exactly what `.github/workflows/tests.yml` runs; all four must exit 0
before you push. Keep `--frozen` - it is what makes a stale `uv.lock` fail instead of being silently
re-resolved.

```bash
uv sync --extra dev --frozen
uv run --frozen ruff check .
uv run --frozen mypy ondewo
uv run --frozen pytest tests/unit -q --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=100
```

The bare `--cov` is deliberate: the measured set is `[tool.coverage.run] source = ["ondewo"]` in
`pyproject.toml`, a filesystem scan, so **a new file under `ondewo/` with no test fails the gate**.
Add a hand-written module and you must add its tests in the same commit.

Run the hooks with `uv run --frozen pre-commit run --all-files` (or `make
precommit_hooks_run_all_files`, or `uvx pre-commit run --all-files` - all three are equivalent).
The mypy hook stays `language: system` so it sees the `types-*` packages, but its `entry` is
`uv run --frozen --extra dev mypy`, so it finds the `.venv` mypy no matter which front-end started
pre-commit.

## Examples

The `/examples` folder provides a possible implementation of this library. To run an example, simple execute it like any other python file. To specify the server and credentials, you need to provide an environment file with the following variables:

- host `// The hostname of the Server - e.g. 127.0.0.1`
- port `// Port of the Server - e.g. 6600`
- user_name `// Username - same as you would use in AIM`
- password `// Password of the user`
- grpc_cert `// gRPC Certificate of the server`

### Keycloak bearer auth (D18)

The ONDEWO CCAI platform authenticates SDK calls with a Keycloak-issued JWT (D18). Configure the
client with the Keycloak fields:

```python
from ondewo.t2s.client.client import Client
from ondewo.t2s.client.client_config import ClientConfig
from ondewo.t2s.text_to_speech_pb2 import ListT2sPipelinesRequest

config = ClientConfig(
    host="127.0.0.1",
    port="50555",
    keycloak_url="https://keycloak.example.com/auth",
    realm="ondewo-ccai-platform",
    client_id="ondewo-nlu-cai-sdk-public",
    username="technical-user@ondewo.com",
    password="<password>",
)
client = Client(config=config, use_secure_channel=bool(config.grpc_cert))
response = client.services.text_to_speech.list_t2s_pipelines(ListT2sPipelinesRequest())
```

The SDK performs a headless Resource-Owner-Password-Credentials (ROPC) grant with
`scope=offline_access` against the **public** Keycloak client (`ondewo-nlu-cai-sdk-public` - no
client secret), auto-refreshes the short-lived access token in the background, and attaches it to
every gRPC call as the `Authorization: Bearer <jwt>` header. When the client is built from a
Keycloak config the generated convenience methods
(`client.services.text_to_speech.synthesize(...)`, `list_t2s_pipelines(...)`, ...) attach the
bearer token automatically; Envoy validates the bearer JWT (D5). See
[`examples/synthesize_with_keycloak.py`](examples/synthesize_with_keycloak.py) for a full working
example.

## Automatic Release Process

The entire process is automated to make development easier. The actual steps are simple:

TODO after Pull Request was merged in:

- Checkout master:

  ```shell
  git checkout master
  ```

- Pull the new stuff:

  ```shell
  git pull
  ```

- (If not already, run the `setup_developer_environment_locally` command):

  ```shell
  make setup_developer_environment_locally
  ```

- Update the `ONDEWO_T2S_VERSION` in the `Makefile`
- Add the new Release Notes in `RELEASE.md` in the format:

  ```
  ## Release ONDEWO T2S Python Client X.X.X       <---- Beginning of Notes

     ...<NOTES>...

  *****************                      <---- End of Notes
  ```

- Release:

  ```shell
  make ondewo_release
  ```

---

The release process can be divided into 6 Steps:

1. `build` specified version of the `ondewo-t2s-api`
2. `commit and push` all changes in code resulting from the `build`
3. Create and push the `release branch` e.g. `release/1.3.20`
4. Create and push the `release tag` e.g. `1.3.20`
5. Create a new `Release` on GitHub
6. Publish the built `dist` folder to `pypi.org`

> :warning: The Release Automation checks if the build has created all the proto-code files, but it does not check the code-integrity. Please build and test the generated code prior to starting the release process.
