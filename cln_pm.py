import grpc
import sys
import portmapper_pb2 as pb2
import portmapper_pb2_grpc as pb2_grpc

def main(host_port):
    channel = grpc.insecure_channel(host_port)
    stub = pb2_grpc.PortMapperStub(channel)

    #le comandos da entrada
    for line in sys.stdin:
        entrada = line.strip().split()
        if not entrada:
            continue

        command = entrada[0]

        #registra o servico
        if command == 'R' and len(entrada) == 3:
            name, value = entrada[1], float(entrada[2])
            response = stub.register_service(pb2.informacao_servidor(name=name, value=value))
            print(response.port)

        #remove o servico
        elif command == 'U' and len(entrada) == 2:
            port = int(entrada[1])
            response = stub.unregister_service(pb2.requisicao_porta(port=port))
            print(response.status)

        #realiza a consulta do servico
        elif command == 'G' and len(entrada) == 2:
            name = entrada[1]
            response = stub.get_service_info(pb2.nome_servidor(name=name))
            if response.port != -1:
                print(f"{response.port} {response.value:.6f}")

        #termina o servidor
        elif command == 'T':
            response = stub.terminate(pb2.empty())
            print(response.count)
            break  

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    main(sys.argv[1])
