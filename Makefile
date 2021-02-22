install:
	pip install .


# GENERATE PYTHON FILES FROM PROTOS
ONDEWO_PROTOS_DIR=ondewo-t2s-api/ondewo/t2s
ONDEWO_APIS_DIR=ondewo-t2s-api
PROTO_OUTPUT_FOLDER= .

generate_ondewo_protos:
	for f in $$(find ${ONDEWO_PROTOS_DIR} -name '*.proto'); do \
		python -m grpc_tools.protoc -I ${ONDEWO_APIS_DIR} --python_out=${PROTO_OUTPUT_FOLDER} --mypy_out=${PROTO_OUTPUT_FOLDER} --grpc_python_out=${PROTO_OUTPUT_FOLDER} $$f; \
	done
