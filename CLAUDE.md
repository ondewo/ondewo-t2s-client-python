# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Principles

Behavioral guidelines to reduce common mistakes. They bias toward caution over speed; for trivial tasks, use judgment.

### Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Surgical changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that _your_ changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### Goal-driven execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and
clarifying questions come before implementation rather than after mistakes.

## Logging

```python
from loguru import logger as log
```

- **Levels:** `log.trace()`, `log.debug()`, `log.info()`, `log.warning()`, `log.error()`, `log.exception()`. Choose by
  hotness/verbosity — `trace` for per-token / hot-path detail, `debug` for routine method entry/exit, `info` for notable
  lifecycle events, `warning` / `error` / `exception` for problems.
- **Interpolate with f-strings, not loguru's `{}` positional args.** Consistent with the Code Style rule, use
  `f"…{value}"`; only add the `f` prefix when the string actually interpolates (`"START: …"` with no params stays a
  plain string).
- **`START:` / `DONE:` bracketing.** Wrap a method (or other notable operation) with a `START:` line at entry and a
  `DONE:` line at exit, both naming `ClassName: method_name` (append `: param={value}` context where useful):

  ```python
  log.debug("START: IntentBertClassifier: predict")
  ...
  log.debug(f"DONE: IntentBertClassifier: predict. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

- **Timing uses `perf_counter()`, rendered `:.5f`.** Measure elapsed time with `time.perf_counter()` captured as a start
  value and subtracted at the `DONE:` line; always format the elapsed value with the `:.5f` spec:

  ```python
  from time import perf_counter

  start_time: float = perf_counter()
  ...
  log.info(f"DONE: SESSION SERVICER: DetectIntent. Elapsed time: {perf_counter() - start_time:.5f}")
  ```

  Never measure a duration with `time.time()` — reserve `time.time()` for wall-clock timestamps (epoch seconds persisted
  to a DB / proto, unique-id or filename stamps). `perf_counter()` has an undefined epoch and must not be stored or
  compared across processes.

## Docstrings

Google-style, triple double-quotes:

```python
"""
Short imperative summary line.

Args:
    param_name (type):
        Description of the parameter.

Returns:
    type:
        Description of the return value.

Raises:
    ExceptionType:
        When this exception is raised.
"""
```

## Git Commits

- **Never include Claude as author or co-author** in commit messages, PR descriptions, or any other text. Do not add
  `Co-Authored-By: Claude…` trailers, "Generated with Claude Code" footers, or any similar attribution.
- The user's own git author identity (already configured in git) is the only identity that should appear on commits.
- This rule overrides the default Claude Code commit-template guidance.
- **Never prepend the JIRA ticket ID** (e.g. `[OND211-2386]`) to the commit subject yourself. The `giticket` pre-commit
  hook reads the ticket from the branch name (`(feature|bugfix|support|hotfix)/<TICKET>-…`) and prepends `[<ticket>]`
  (with a trailing space) automatically. Writing the prefix manually produces a duplicate like
  `[OND211-2386] [OND211-2386] feat: …`. Write the subject as plain Conventional Commits (`feat: …`, `fix(scope): …`,
  `docs(types): …`) and let the hook add the prefix on commit.

## General Principles

- Follow existing patterns before introducing new abstractions.
- Keep changes minimal and consistent with surrounding code.
- Validate inputs early with descriptive, context-rich error messages.
- Use context managers for files, sockets, and thread pools.
- Prefer region comments for grouping methods in files that already use them.
- End edited Markdown and YAML files with a trailing newline.

## Toolchain: uv + ruff + mypy, all configured in `pyproject.toml`

There is no `setup.py`, `setup.cfg`, `mypy.ini`, `.flake8`, `requirements.txt` or
`requirements-dev.txt` here, and none of them may come back — `pyproject.toml` is the single
config file and `uv.lock` is the single pin. A re-created `mypy.ini` silently **shadows**
`[tool.mypy]`; a re-created `setup.py` conflicts with `[project]` under setuptools>=61.

- **Deps:** edit `[project.dependencies]` / `[project.optional-dependencies].dev`, then run
  `uv lock` and commit the lock **in the same commit** — CI syncs `--frozen` and a stale lock is a
  hard failure.
- **Build backend stays setuptools** (PyPI compatibility) but the build command is `uv build`.
  PEP 625 applies: the sdist is `ondewo_t2s_client-<v>.tar.gz` with an **underscore**.
- **Lint/format is ruff** (`[tool.ruff]`, line-length 120, `*_pb2*` excluded): `make ruff`,
  `make ruff_fix`, `make ruff_format`. There is no flake8, black or autopep8 target.
- **`[tool.mypy] python_version = "3.12"`** because mypy 2.x refuses `3.9` outright
  (`Python 3.9 is not supported (must be 3.10 or higher)`). The old justification about numpy's
  PEP 695 stubs is gone with numpy itself — the runtime deps are now only `dataclasses-json`,
  `grpcio`, `ondewo-client-utils`, `protobuf` and `requests`, which is every package the shipped
  `ondewo` tree actually imports.
- **`ondewo/t2s/py.typed` must exist.** `[tool.setuptools.package-data]` and `MANIFEST.in` both
  list it; without the file itself the shipped `text_to_speech_pb2.pyi` is invisible to a
  downstream mypy (PEP 561). Verify with `uv build` + a `zipfile` listing of the wheel.
- The release `git commit` uses `--no-verify`, so hooks never gate an automated release.

## CI — `.github/workflows/tests.yml` is a required gate

Job `unit-tests` on `ubuntu-latest`, triggered on **push to every branch** (`branches: ["**"]`) and
on every pull request. `actions/checkout@v5` → `astral-sh/setup-uv@v6` (cache on) →
`uv python install 3.12` → the four commands below. Reproduce them **verbatim**:

```bash
uv sync --extra dev --frozen
uv run --frozen ruff check .
uv run --frozen mypy ondewo
uv run --frozen pytest tests/unit -q \
    --cov \
    --cov-report=term-missing \
    --cov-report=xml \
    --cov-fail-under=100
```

- **Keep `--frozen`.** It installs exactly what `uv.lock` pins and fails when the lock is stale
  relative to `pyproject.toml`. Without it uv re-resolves in memory and you test a dependency set
  CI never installs.
- **The `--cov` really is bare — do not re-add `--cov=<dotted.module>` arguments.** That older form
  made the gate **fail open**: pytest-cov only measures a dotted target the suite actually imports,
  so an untested module emitted `CoverageWarning: module-not-imported`, vanished from the table, and
  the run still printed `Required test coverage of 100% reached` and exited 0. Measured here: the
  dotted gate reported 100% over 220 statements while both service wrappers sat at 40%. The
  measured set now lives in `pyproject.toml` as `[tool.coverage.run] source = ["ondewo"]`, a
  **filesystem** scan — 393 statements at 100%, and a new untested file under `ondewo/` drops the
  total below 100 and fails the run (verified: 98.50%).
- **`include_namespace_packages = true` (under `[tool.coverage.report]`, not `[run]`) is
  load-bearing.** `ondewo/t2s/scripts/` has no `__init__.py`, so coverage's package walk skips such
  directories entirely — the same fail-open shape in a different disguise. Putting the option under
  `[run]` only emits `CoverageWarning: Unrecognized option`.
- **Only two `omit` entries, both argued in place:** the generated `*_pb2*.py` stubs, and
  `ondewo/t2s/scripts/generate_services.py`. The latter is developer-only codegen **and cannot
  reach 100% at all**: `proto_stem_to_file_name` opens with a bare `return stem`, so the six lines
  under it are unreachable. Do not add a third entry to make a red gate green — write the test.
- **`mypy` prints `note: unused section(s): module = ['soundfile.*']` on a clean run.** It is a
  note, the step still exits 0. `soundfile` is imported only by `examples/`, which the pre-commit
  mypy hook covers but `mypy ondewo` does not reach. Do not delete that override.
- **`.python-version` (`3.12`) is load-bearing — do not delete it.** `uv python install 3.12` only
  guarantees 3.12 on a fresh runner; on a developer machine uv prefers its newest managed CPython,
  and before this file existed the venv was built on 3.14 while CI ran 3.12 — producing
  `30 failed, 84 passed, 25 errors`, every one an `AttributeError: 'ServicesContainer' object has
  no attribute '__annotations__'` from `ondewo-client-utils`' `BaseClient.disconnect`, with nothing
  to do with the change under test.
- **The SDK really is broken on Python ≥ 3.13, so the pin is honest.** Under PEP 649 a dataclass no
  longer materialises `__annotations__` into its class `__dict__`, so the `self.services.__annotations__`
  lookup in `BaseClient.disconnect` no longer resolves. `requires-python` is `>=3.9` and the trove
  classifiers stop at 3.12: **3.12 is the tested interpreter.** Raising that ceiling is a real port.
- **CI does not check out submodules** (`actions/checkout@v5` with no `submodules:` key), so
  `ondewo-t2s-api/` and `ondewo-proto-compiler/` are absent there. Nothing in the four gates may
  depend on them: ruff already excludes both and the unit suite must never read a `.proto`.

## pre-commit: hook ORDER at the commit-msg stage is the whole game

pre-commit runs hooks in declaration order. `giticket` rewrites the subject to
`[OND221-2830] feat: …`, which is no longer valid Conventional Commits — so with `giticket` first,
**every** commit on a ticket branch fails and can only land with `--no-verify`.
`conventional-pre-commit` is therefore declared **before** `giticket`: validate first, decorate
second. Do not reorder them, and do not let a second `conventional-pre-commit` block reappear after
`giticket` — one did, which made the earlier reordering a no-op for two releases.

Write the plain subject (`feat: …`, `fix(scope): …`) and let `giticket` add the prefix; typing it
yourself yields `[OND221-2830] [OND221-2830] …`. The regex here is `OND`-anchored:
`(?:(?:feature|bugfix|support|hotfix)/)?(OND[0-9]{3}-[0-9]{1,5})[_-][\w-]+`.

Other hook facts worth not re-deriving:

- **The mypy hook names its environment; do not shorten its `entry` back to `mypy`.** It is
  `language: system` on purpose (so mypy sees the `types-*` packages installed in `.venv`), and
  `language: system` means pre-commit resolves the entry from `PATH`. A bare `entry: mypy` therefore
  passes under `uv run pre-commit` but fails under `uvx pre-commit run --all-files` with
  `Executable 'mypy' not found`, because `uvx` runs pre-commit in an ephemeral env that cannot see
  `.venv`. `entry: uv run --frozen --extra dev mypy` makes all three front-ends
  (`uvx pre-commit`, `uv run --frozen pre-commit`, `make precommit_hooks_run_all_files`) behave
  identically and type-check with the same interpreter and packages as
  `.github/workflows/tests.yml`. `--extra dev` is required because mypy lives in the `dev`
  _extra_, which is not a default group: in a fresh checkout `uv run --frozen mypy` dies with
  `Failed to spawn: 'mypy'` (measured), while `--extra dev` installs the extra first. It does not
  evict anything from an already-synced `.venv`.
- **`MD053` must stay `false` in `.markdownlint-cli2.yaml`.** Its auto-fix deletes
  `[comment]: <>` reference-definition markers that the release tooling greps for.
- **`RELEASE.md` structure is machine-read.** `CURRENT_RELEASE_NOTES` slices from
  `Release ONDEWO T2S Python Client ${ONDEWO_T2S_VERSION}` to the next `^\*{5}`, so the
  `## Release …` headings and the `*****************` separators must survive any reformat. The
  terminator is `^\*{5}` and **not** `/\*\*/`, which used to match the first inline `**bold**`
  span and silently truncate the notes with no error from `gh release create`.
- Hook revs as of this pass: markdownlint-cli2 `v0.23.2`, ruff-pre-commit `v0.16.6`, mirrors-mypy
  `v2.3.1`, pre-commit-hooks `v6.0.0`, uv-pre-commit `0.12.10` (**no** leading `v` — that is the
  real tag spelling), giticket `'1.92'` (**keep the quotes**; unquoted it is a YAML float),
  conventional-pre-commit `v4.4.0`. The ruff and mypy revs are only half the story: ruff runs from
  `uv.lock` in CI, and the mypy hook being `language: system` means its rev is documentation only —
  bump `uv.lock` with `uv lock --upgrade-package ruff --upgrade-package mypy` or the hook and the
  gate silently diverge.

## Submodules and the proto-compiler pin

Two submodules, both pinned twice — as a gitlink **and** as a Makefile variable
(`ONDEWO_T2S_API_GIT_BRANCH`, `ONDEWO_PROTO_COMPILER_GIT_BRANCH`). `make
checkout_defined_submodule_versions` checks out the _variable_, so if the two disagree it silently
**downgrades** the submodule before codegen. Move both together:

```bash
git -C ondewo-proto-compiler fetch --tags origin
git -C ondewo-proto-compiler checkout <VERSION>
git add ondewo-proto-compiler
# ONDEWO_PROTO_COMPILER_GIT_BRANCH=tags/<VERSION> in the Makefile
git submodule status          # must print <VERSION> for both lines
```

- **A pin bump regenerates nothing.** It changes which image `make build` would build; the
  committed `_pb2*.py` stubs are untouched. Never write "Regenerated with ondewo-proto-compiler
  X.Y.Z" in `RELEASE.md` unless you ran `make build` and committed the result — the 6.6.3 entry
  says exactly that while the pin at the time was 5.12.0.
- `ondewo-proto-compiler` 5.11.0→5.14.0 contains **only** Angular/JS/Node/TS codegen fixes;
  `git diff 5.11.0..5.14.0 -- python/` is empty. For this repo the bump is pin hygiene.
- `.gitmodules` declares `[submodule "ondewo-proto-compiler"]` **twice** (identical path and url).
  Harmless today, pre-existing, and not this task's to fix — but do not be surprised by it.

## Testing

`tests/unit` is the gated suite; `tests/e2e` needs a live T2S server and CI never runs it.
`make test_unit`, `make test_unit_client`, `make test_unit_async_client`, `make test_e2e`.

- **`make test_unit_coverage` is not the CI gate** — it passes `--cov=ondewo/t2s/client` (a _path_),
  so it reports a different, smaller number than the `--cov` gate. Trust the workflow command.
- The service wrappers under `ondewo/t2s/client/services/` are one-line stub delegations. They are
  tested by driving every method through a patched `Text2SpeechStub` and asserting the RPC name, the
  forwarded `metadata=` (that is where the Keycloak bearer token rides) and the returned object. The
  async side uses `AsyncMock` stubs, which is also what would catch a `await` dropped by the perl
  rewrites in `make create_async_services`. Both test tables carry a guard test asserting the table
  covers every public method on the class, so a newly generated method cannot ship untested.
- Async tests drive their own loop via `asyncio.run` (`_run(...)` in `tests/unit/test_async_client.py`);
  there is no `asyncio_mode` configured, so do not write bare `async def test_…`.

## `ClientConfig` must not print its secrets

`@dataclass` generates a `__repr__` that prints **every** field, so `log.debug(f"…{config}")` — or any
traceback carrying locals — wrote the ROPC `password` and the PEM `grpc_cert` to the log in clear text.
Downstream consumers really do log config objects: a repository-wide sweep in ondewo-vtsi found this class
among the leakers, alongside thirteen of its own dataclasses. All five ONDEWO Python clients had the same
defect and all five now carry the same fix.

`ondewo/t2s/client/client_config.py` names the secrets once and renders around them:

```python
SECRET_FIELD_NAMES: ClassVar[FrozenSet[str]] = frozenset({"password", "grpc_cert"})
```

Four properties are load-bearing:

- **An empty secret renders as `''`, never as `***REDACTED***`.** The marker reads as "this is set and
  sensitive", which is actively misleading when the real fault is that nobody set it — usually the very
  thing being debugged. The `__repr__` therefore redacts only a _truthy_ value.
- **A new secret field must join `SECRET_FIELD_NAMES` in the same commit.** That frozenset is the entire
  policy; nothing infers sensitivity from a field name.
- **Redaction covers `repr()` / `str()` only.** Measured on the sibling class: `to_json()`, `to_dict()` and
  `dataclasses.asdict()` still return the plaintext password, and `to_json()` renders the certificate as a
  byte array. That is deliberate, because `@dataclass_json` has to round-trip through `from_json` — so
  never log a serialized config, and do not "fix" it by redacting there. (That decorator is also why
  `dataclasses-json` stays a declared runtime dependency here while the s2t and nlu twins dropped it.)
- **The guard is behavioural.** `tests/unit/test_client_config_redacts_secrets.py` builds a `ClientConfig`
  with distinctive planted values and reads its `repr`. It does not grep for `__repr__`, because a grep
  passes just as well for a `__repr__` that prints the secret anyway. It also asserts each secret is really
  **on the object** (`config.password == PASSWORD`) before asserting it is absent from the repr — reading
  only the repr would pass vacuously against unfixed code. The certificate is compared against
  `GRPC_CERT.encode()`, since `BaseClientConfig.__post_init__` encodes it to `bytes`; comparing to the
  `str` would fail while the redaction it guards worked perfectly.

Run it with `uv run --frozen pytest tests/unit/test_client_config_redacts_secrets.py -q` — 5 tests.
Released in `6.6.1`; ondewo-vtsi pins `ondewo-t2s-client` by exact version, so raising that pin is what
carries the redaction downstream.

## Keycloak token provider — teardown runs during interpreter finalization

`KeycloakTokenProvider.__del__` calls `stop()`, so `stop()` can run while CPython is finalizing. It
must therefore guard on `sys.is_finalizing()` **and** catch `RuntimeError` around the join:
`Thread.join` raises `PythonFinalizationError` (a `RuntimeError` subclass) on CPython ≥ 3.13, and
because it is raised inside a deallocator the interpreter can only _print_ it — every process using
the SDK ended with an `Exception ignored while calling deallocator … PythonFinalizationError`
traceback. The refresh thread is a daemon and is reaped anyway, so the skipped join costs nothing.
`tests/unit/test_keycloak.py::TestInterpreterShutdownTeardown` guards both the guard and the catch,
plus a child-process probe asserting a clean stderr at exit.

The shared-provider registry is keyed by a **SHA-256 of the credential set**, never by
`id(config)` — the address-keyed version handed a new client the previous user's live token
provider, silently authenticating as the wrong principal (fixed in 6.6.2).

## Release process

`make ondewo_release` clones `ondewo-devops-accounts`, then `make release`: build → check_build →
a `--no-verify` commit → release branch → tag → GitHub release → PyPI.

- **`make TEST` masks its secrets** (`<set>` / `<unset>` for `GITHUB_GH_TOKEN` and
  `PYPI_PASSWORD`). It is on the automated path — `ondewo-t2s-api`'s `release_client` runs
  `make -C <client> TEST` — so a plain `@echo ${TOKEN}` there leaks into a release log. Every other
  token-bearing recipe line is `@`-prefixed; keep it that way and rotate any token you see printed.
- **Trust the registry, not the log.** The multi-client release wrapper swallows a failed client
  release into an "Already released …" line. After a release, check the GitHub release **and** PyPI
  directly.
- **Codegen must run TTY-free.** The `docker run` that invokes the proto-compiler must not pass
  `-it`; non-interactively it dies with `cannot attach stdin to a TTY-enabled container`.
- **The release image builds with `uv build`, not `python setup.py`.** `Dockerfile.utils`
  (`python:3.12-slim`) copies in `uv` and `pip install`s only `twine`; `make build_package` is a
  bare `uv build`, which provisions the `[build-system]` backend (`setuptools>=61.0`, `wheel`) in
  its own isolated PEP 517 environment. So no `pip install setuptools wheel build` is needed in the
  image — do not add one back on the theory that the slim base is missing it.
