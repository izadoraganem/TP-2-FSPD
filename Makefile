PORTMAPPER_PROTO=portmapper.proto
REGISTRY_PROTO=registry.proto

PORTMAPPER_PB=portmapper_pb2.py portmapper_pb2_grpc.py
REGISTRY_PB=registry_pb2.py registry_pb2_grpc.py

all: $(PORTMAPPER_PB) $(REGISTRY_PB)

portmapper_pb2.py portmapper_pb2_grpc.py: $(PORTMAPPER_PROTO)
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $(PORTMAPPER_PROTO)

registry_pb2.py registry_pb2_grpc.py: $(REGISTRY_PROTO)
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. $(REGISTRY_PROTO)

run_portmapper_1:
	python svc_pm.py $(arg)

run_portmapper_2:
	python svc_pm.py $(arg1) $(arg2)

run_cli_portmapper:
	python cln_pm.py $(arg)

run_registry:
	python svc_reg.py $(arg)

run_cli_registry:

	python cln_reg.py $(arg)

clean:
	rm -f portmapper_pb2.py portmapper_pb2_grpc.py registry_pb2.py registry_pb2_grpc.py
