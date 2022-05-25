install:
	pip install .


# GENERATE PYTHON FILES FROM PROTOS
PROTO_OUTPUT_FOLDER=ondewo
PROTO_COMPILER_IMAGE_NAME=registry-dev.ondewo.com:5000/ondewo/ondewo-python-proto-compiler
PROTO_DIR=ondewo-t2s-api
TARGET_DIR=
INCLUDE_DIR=ondewo-t2s-api

generate_ondewo_protos:
	-mkdir ${PROTO_OUTPUT_FOLDER}
	docker run -it\
		--user ${shell id -u}:${shell id -g} \
		-v ${shell pwd}/${PROTO_OUTPUT_FOLDER}:/home/ondewo/ondewo-proto-compiler/output/${PROTO_OUTPUT_FOLDER} \
		-v ${shell pwd}/${PROTO_DIR}:/home/ondewo/ondewo-proto-compiler/protos/${shell basename ${PROTO_DIR}} \
		-e INTERNAL_TARGET_PROTO_DIR=${TARGET_DIR} \
		-e INCLUDE_DIR=${INCLUDE_DIR} \
		${PROTO_COMPILER_IMAGE_NAME}

push_to_pypi: build_package upload_package clear_package_data
	echo 'pushed to pypi : )'

build_package:
	python setup.py sdist bdist_wheel

upload_package:
	twine upload -r pypi dist/*

clear_package_data:
	rm -rf build dist ondewo_logging.egg-info
