import grpc
import sys
import socket
import registry_pb2 as registry_pb2
import portmapper_pb2 as portmapper_pb2
import registry_pb2_grpc as pb2_grpc
import portmapper_pb2_grpc as pb2_grpc_pm

def main(host_port):
    channel = grpc.insecure_channel(host_port)
    stub = pb2_grpc.ServiceRegistryStub(channel)
    #le comandos da entrada
    for line in sys.stdin:
        requisicao = line.strip().split()
        if not requisicao:
            continue
        command = requisicao[0]
        #comando Query do registry
        if command == 'Q' and len(requisicao) == 2:
            service = requisicao[1]
            locator_response = stub.query(portmapper_pb2.nome_servidor(name=service))
            locator = locator_response.locator
            if locator:
                #conecta no portmapper
                pm_channel = grpc.insecure_channel(locator)
                pm_stub = pb2_grpc_pm.PortMapperStub(pm_channel)
                resposta = pm_stub.get_service_info(portmapper_pb2.nome_servidor(name=service))
                if resposta.port != -1:
                    print(f"{resposta.port} {resposta.value:.6f}")

        #finaliza o registry
        elif command == 'F':
            resposta = stub.finalize(portmapper_pb2.empty())
            print(resposta.count)
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    main(sys.argv[1])
