# Release History

*****************

## Release ONDEWO T2S Python Client 6.6.2

### Bug Fixes

* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **A client could silently authenticate as a different user.** `get_keycloak_token_provider` keyed its shared-provider registry on `id(config)` — the memory address of the `ClientConfig`. The service interfaces keep only the grpc channel, so the config passed to the usual `Client(config=ClientConfig(...))` becomes unreachable the moment the client is built; CPython then reuses that address for the next `ClientConfig`, and the `WeakValueDictionary` handed the new client the previous user's still-alive token provider. The second client authenticated as the first user — including when its own credentials were wrong or belonged to nobody at all. Any process that builds more than one client with different identities was affected, and the failure is silent: calls succeed, they are simply made as the wrong principal. The registry is now keyed by a SHA-256 of the credential set (`keycloak_url`, `realm`, `client_id`, username, `password`, `token_expiration_in_s`, `keycloak_verify_ssl`), so two configs share a provider exactly when a shared provider would behave identically for both, and never otherwise. The digest is hashed rather than stored as a plain tuple so the password does not end up in a module-level dict or in that frame's locals, where a traceback renderer printing locals would expose it. Same fix as `ondewo-nlu-client` 7.0.2, `ondewo-csi-client` 5.4.1 and `ondewo-s2t-client` 7.4.1.

*****************

## Release ONDEWO T2S Python Client 6.6.1

### Bug Fixes

* [[OND211-2418]](https://ondewo.atlassian.net/browse/OND211-2418) **`ClientConfig` printed its credentials in clear text.** `@dataclass` generates a `__repr__` that renders every field, so `log.debug(f"...{config}")` — or any traceback carrying locals — wrote the Keycloak `password` and the gRPC certificate to the logs. That is not hypothetical: a repository-wide sweep in ondewo-vtsi found this class among its leaking dataclasses, and the real staging password was observed on a developer console this way. `repr()` and `str()` now render `password` and `grpc_cert` as `***REDACTED***`. An unset or empty secret still renders as `None` / `''` rather than as the marker: `***REDACTED***` reads as "this is set and sensitive", which is actively misleading when the real fault is that nobody set it — usually the very thing being debugged.
* **Behaviour change** for anyone who parsed the repr: read the attribute (`config.password`, `config.grpc_cert`) instead. Only the rendered text changed — the fields themselves, equality and `dataclasses.asdict()` are untouched.

*****************

## Release ONDEWO T2S Python Client 6.6.0

### Improvements

* Tracking API Version [6.6.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.6.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.5.0

### Improvements

* Tracking API Version [6.5.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.5.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.4.2

### Improvements

* Tracking API Version [6.4.2](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.4.2) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.4.1

### Improvements

* Tracking API Version [6.4.1](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.4.1) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.4.0

### Improvements

* Tracking API Version [6.4.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.4.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.2.0

### Improvements

* Tracking API Version [6.2.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.2.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.1.1

### Improvements

* `streaming_synthesize` and `list_t2s_normalization_pipelines` in the client

*****************

## Release ONDEWO T2S Python Client 6.1.0

### Improvements

* Tracking API
  Version [6.1.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.1.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 6.0.0

### Improvements

* Tracking API
  Version [6.0.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/6.0.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 5.4.0

### Improvements

* Tracking API
  Version [5.4.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/5.4.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 5.3.1

### Improvements

* Added functionality to pass grpc options to grpc clients based
  on [ONDEWO CLIENT UTILS PYTHON 2.0.0](https://github.com/ondewo/ondewo-client-utils-python/releases/tag/2.0.0)

*****************

## Release ONDEWO T2S Python Client 5.3.0

### Improvements

* Tracking API
  Version [5.3.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/5.3.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 5.2.0

### Improvements

* Tracking API
  Version [5.2.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/5.2.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 5.0.0

### Improvements

* Tracking API
  Version [5.0.0](https://github.com/ondewo/ondewo-t2s-api/releases/tag/5.0.0) ( [Documentation](https://ondewo.github.io/ondewo-t2s-api/) )

*****************

## Release ONDEWO T2S Python Client 4.4.0

### Improvements

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) - added pre-commit hooks and adjusted files to them
* Updated API to 4.3.0

*****************

## Release ONDEWO T2S Python Client 4.3.0

### New features

* [[OND211-2039]](https://ondewo.atlassian.net/browse/OND211-2039) - Automated Release Process

*****************

## Release ONDEWO T2S Python Client 4.2.2

### New features

* Add normalizer to synthesize message

*****************

## Release ONDEWO T2S Python Client 4.1.0

### New features

* Refactor Makefile, dockerize packaging.
* Update grpc libraries and other requirements.

*****************

## Release ONDEWO T2S Python Client 4.0.5

### New features

* Delegate generation of proto files to proto-compoiler image.
* Add NormalizeText endpoint, that allows for text normalization without speech synthesis.

*****************

## Release ONDEWO T2S Python Client 4.0.4

### Breaking Changes

* Add field T2SCustomLengthScales to T2SNormalizePipeline.

*****************

## Release ONDEWO T2S Python Client 4.0.3

### New Features

* [[OND232-348]](https://ondewo.atlassian.net/browse/OND232-348) - Add field normalized_text to SynthesizeResponse.

*****************

## Release ONDEWO T2S Python Client 4.0.2

### Breaking Changes

* [[OND232-343]](https://ondewo.atlassian.net/browse/OND232-343) - Rename oneof attributes and merged custom-phonemizer
  proto into text-to-speech proto

*****************

## Release ONDEWO T2S Python Client 4.0.1

### Breaking Changes

* [[OND231-343]](https://ondewo.atlassian.net/browse/OND231-343) - Rename oneof attributes and merged custom-phonemizer
  proto into text-to-speech proto

*****************

## Release ONDEWO T2S Python Client 3.1.1

* Added batch_synthesis endpoint to T2S client

*****************

## Release ONDEWO T2S Python Client 3.1.0

* Added list_t2s_pipelines, get_service_info, list_t2s_languages, list_t2s_domains endpoints to T2S client

*****************

## Release ONDEWO T2S Python Client 3.0.1

### Breaking Changes

* [[OND231-334]](https://ondewo.atlassian.net/browse/OND231-334) - Rename Description, GetServiceInfoResponse, Inference
  and Normalization messages to include T2S

*****************

## Release ONDEWO T2S Python Client 1.5.0

### New Features

* Abstracted GRPC from the client to be easier to use

*****************

## Release ONDEWO T2S Python Client 1.4.1

### New Features

* push to pypi

*****************

## Release ONDEWO T2S Python Client 1.4.0

### New Features

* First public version

### Improvements

* Open source

### Known issues not covered in this release

* CI/CD Integration is missing
* Extend the README.md with an examples usage
