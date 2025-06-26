import grpc
from concurrent import futures
import sys
import socket
import portmapper_pb2 as pb2
import portmapper_pb2_grpc as pb2_grpc
import registry_pb2 as reg_pb2
import registry_pb2_grpc as reg_pb2_grpc

class portmapper(pb2_grpc.PortMapper):
    def __init__(self, port, registry_stub=None):
        self.registry_stub = registry_stub
        self.mutex1 = False #como se fosse um mutex
        self.port = port 
        self.port_table = {}   
        self.service_table = {}  
        self.next_port = 1025
        

    #recebe como parâmetros um nome de um serviço e um valor de ponto flutuante que deve ser associado ao string
    def register_service(self, request, _):
        name = request.name
        value = request.value

        if name in self.service_table:
            port, _ = self.service_table[name]
            self.service_table[name] = (port, value)
        else:#se o servico ainda nao tiver sido registrado, cria ele
            port = self.next_port
            self.service_table[name] = (port, value)
            self.port_table[port] = name
            self.next_port += 1

        if self.registry_stub:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:#pega o ip do google
                s.connect(('8.8.8.8', 80)) 
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()

            locator = f"{ip}:{self.port}"#manda o endereco do portmapper
            try:
                self.registry_stub.map(reg_pb2.entrada_registry(name=name, locator=locator))
            except Exception:
                pass  

        return pb2.port_resposta(port=port)
    
    #recebe como parâmetro um inteiro que identifica o porto que deve ter sido associado anteriormente a um serviço e remove a entrada relacionada a ele, retornando zero se a operação foi bem sucedida, ou -1, caso não tenha sido identificado um serviço associado àquele porto;
    def unregister_service(self, request, _):
        port = request.port
        if port in self.port_table:
            name = self.port_table.pop(port)
            self.service_table.pop(name)
            #se o servico ta no registry, remove ele
            if self.registry_stub:
                try:
                    self.registry_stub.unmap(reg_pb2.nome_servidor(name=name))
                except Exception:
                    pass
            #se o porto for o ultimo, reseta o proximo porto
            return pb2.status_resposta(status=0)
        else:
            return pb2.status_resposta(status=-1)

    #recebe como parâmetro um nome de um serviço e retorna o número do porto  e o valor de ponto flutuante a ele associado, caso o serviço exista
    def get_service_info(self, request, _):
        name = request.name
        if name in self.service_table:
            port, value = self.service_table[name]
            return pb2.info_resposta(port=port, value=value)
        else:
            return pb2.info_resposta(port=-1, value=0.0)
        
    #um procedimento sem parâmetros que indica que o servidor deve terminar sua execução
    def terminate(self, request, _):
        self.mutex1 = True
        return pb2.terminate_resposta(count=len(self.service_table))

def serve(port, registry_locator=None):
    port = int(port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    #se tem registry, cria o stub do registry
    if registry_locator:
        channel = grpc.insecure_channel(registry_locator)
        registry_stub = reg_pb2_grpc.ServiceRegistryStub(channel)
    else:
        registry_stub = None
    #serviço do portmapper
    service = portmapper(port=port, registry_stub=registry_stub)
    pb2_grpc.add_PortMapperServicer_to_server(service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    try:
        while (1): #espera o mutex ser ativado
            if service.mutex1:
                break
    finally:
        server.stop(0)
#
if __name__ == "__main__":
    if len(sys.argv) == 2:
        serve(sys.argv[1])
    elif len(sys.argv) == 3:
        serve(sys.argv[1], sys.argv[2])
    else:
        sys.exit(1)
