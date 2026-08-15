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
  thing being debugged. The `__repr__` therefore redacts only a *truthy* value.
- **A new secret field must join `SECRET_FIELD_NAMES` in the same commit.** That frozenset is the entire
  policy; nothing infers sensitivity from a field name.
- **Redaction covers `repr()` / `str()` only.** Measured on the sibling class: `to_json()`, `to_dict()` and
  `dataclasses.asdict()` still return the plaintext password, and `to_json()` renders the certificate as a
  byte array. That is deliberate, because `@dataclass_json` has to round-trip through `from_json` — so
  never log a serialized config, and do not "fix" it by redacting there.
- **The guard is behavioural.** `tests/unit/test_client_config_redacts_secrets.py` builds a `ClientConfig`
  with distinctive planted values and reads its `repr`. It does not grep for `__repr__`, because a grep
  passes just as well for a `__repr__` that prints the secret anyway. It also asserts each secret is really
  **on the object** (`config.password == PASSWORD`) before asserting it is absent from the repr — reading
  only the repr would pass vacuously against unfixed code. The certificate is compared against
  `GRPC_CERT.encode()`, since `BaseClientConfig.__post_init__` encodes it to `bytes`; comparing to the
  `str` would fail while the redaction it guards worked perfectly.

Run it with `python -m pytest tests/unit/test_client_config_redacts_secrets.py -q` — 5 tests. (This repo
still builds from `setup.py` with `mypy.ini` / flake8 / black / autopep8; it has no `pyproject.toml`, so
the `uv run pytest` invocation the other four clients use does not apply here.)

**The fix is unreleased.** `git tag --contains HEAD` is empty here (newest tag `6.6.0`), and ondewo-vtsi
pins `ondewo-t2s-client==6.6.0` by exact version, so the redaction cannot reach it until this package cuts
a release.

## This repo has NO Conventional-Commits hook — only `giticket`

Unlike the nlu, sip, csi and vtsi clients, `.pre-commit-config.yaml` here declares exactly one `commit-msg`
hook: `giticket`, which prepends `[<TICKET>] ` to whatever subject you typed. There is no
`conventional-pre-commit` block, so **nothing validates the subject in this repo** — a message that the
other four clients reject commits cleanly here. Its `giticket` regex is also the looser one,
`([A-Z]{3}[0-9]{3}-[0-9]{1,5})` instead of the `OND`-anchored `(OND[0-9]{3}-[0-9]{1,5})` the others use, so
it accepts any three-letter project key.

If a `conventional-pre-commit` hook is ever added here, it **must be listed before `giticket`**. pre-commit
runs hooks in file order, and `giticket` rewrites the subject to `[OND211-2418] <subject>`, which is not a
valid Conventional Commit; with `giticket` first the validator is handed the prefix the other hook just
added and rejects it, so no conforming commit message exists at all. That exact ordering bug was live in
the sip, csi and vtsi clients and forced their authors onto `--no-verify`. Write the plain subject and let
`giticket` decorate it — never type the `[TICKET]` prefix yourself, which yields
`[OND211-2418] [OND211-2418] …`.
