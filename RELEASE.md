# Release History

*****************
## Release ONDEWO APIS 4.2.2

### New features
* Add normalizer to synthesize message

*****************
## Release ONDEWO APIS 4.1.0

### New features
* Refactor Makefile, dockerize packaging.
* Update grpc libraries and other requirements.

*****************
## Release ONDEWO APIS 4.0.5

### New features
* Delegate generation of proto files to proto-compoiler image.
* Add NormalizeText endpoint, that allows for text normalization without speech synthesis.

*****************
## Release ONDEWO APIS 4.0.4

### Breaking Changes
* Add field T2SCustomLengthScales to T2SNormalizePipeline.

*****************
## Release ONDEWO APIS 4.0.3
### New Features
* [[OND232-348]] -
Add field normalized_text to SynthesizeResponse.
* 
*****************
## Release ONDEWO APIS 4.0.2
### Breaking Changes
* [[OND232-343]] -
Rename oneof attributes and merged custom-phonemizer proto into text-to-speech proto

*****************
## Release ONDEWO APIS 4.0.1

### Breaking Changes
* [[OND232-343]] -
Rename oneof attributes and merged custom-phonemizer proto into text-to-speech proto.

*****************
## Release ONDEWO APIS 3.1.1
* Added batch_synthesis endpoint to T2S client

*****************
## Release ONDEWO APIS 3.1.0
* Added list_t2s_pipelines, get_service_info, list_t2s_languages, list_t2s_domains endpoints to T2S client

*****************
## Release ONDEWO APIS 3.0.1

### Breaking Changes
* [[OND231-334]] -
Rename Description, GetServiceInfoResponse, Inference and Normalization messages to include T2S

*****************
## Release ONDEWO APIS 3.1.0
* Added list_t2s_pipelines, get_service_info, list_t2s_languages, list_t2s_domains endpoints to T2S client

*****************
## Release ONDEWO APIS 3.0.1

### Breaking Changes
* [[OND231-334]] -
Rename Description, GetServiceInfoResponse, Inference and Normalization messages to include T2S

*****************

## ONDEWO-T2S Python Client 1.5.0

### New Features
 * Abstracted GRPC from the client to be easier to use

*****************
## ONDEWO-T2S Python Client 1.4.1

### New Features
 * push to pypi

*****************

## ONDEWO-T2S Python Client 1.4.0

### New Features
 * First public version

### Improvements
 * Open source

### Known issues not covered in this release
 * CI/CD Integration is missing
 * Extend the README.md with an examples usage
