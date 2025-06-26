import grpc
from concurrent import futures
import sys
import registry_pb2 as pb2
import registry_pb2_grpc as pb2_grpc
import portmapper_pb2 

class Registry(pb2_grpc.ServiceRegistryServicer):
    def __init__(self):
        self.registry = {} #guarda ip:porta
        self.mutex = False  

    # map: recebe como parâmetro o string de nome de um serviço e o string localizador do portmapper associado e retorna o número de serviços que foram mapeados até o momento;
    def map(self, request, _):
        self.registry[request.name] = request.locator
        return pb2.map_resposta(count=len(self.registry))

    #unmap: recebe como parâmetro o string de nome de um serviço e o remove do registro, se ele existir, retornando zero em caso de sucesso e -1 se o registro não foi encontrado;
    def unmap(self, request, _):
        if request.name in self.registry:
            del self.registry[request.name]
            return pb2.status_resposta(status=0)
        else:
            return pb2.status_resposta(status=-1)
    #query: recebe como parâmetro o string de nome de um serviço, consulta o seu registro e retorna o string localizador do portmapper que anunciou aquele serviço, ou um string vazio, caso não encontre tal servidor;
    def query(self, request, _):
        locator = self.registry.get(request.name, "")
        return pb2.locator_resposta(locator=locator)
    #finalize: encerra a operação do service registry apenas, retorna o número de serviços que estavam registrados e termina.
    def finalize(self, request,_):
        count = len(self.registry)
        self.mutex = True
        return portmapper_pb2.terminate_resposta(count=count)

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    service = Registry()
    pb2_grpc.add_ServiceRegistryServicer_to_server(service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    try:
        while (1):
            if service.mutex:
                break
    finally:
        server.stop(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    serve(sys.argv[1])
