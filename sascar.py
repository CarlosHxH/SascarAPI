from datetime import datetime
import pandas as pd
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault
import json
from requests import Session
from requests.adapters import HTTPAdapter
import ssl
import urllib3

# Configurações de segurança para HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SascarAPI:
    def __init__(self, SASCAR_USERNAME, SASCAR_PASSWORD):
        """
        Inicializa a conexão com o Web Service Sascar
        
        Args:
            username (str): Nome de usuário para autenticação
            password (str): Senha para autenticação
        """
        if not SASCAR_USERNAME or not SASCAR_PASSWORD:
            raise Exception('ERROR', 'username or password not defined')

        self.wsdl_url = 'https://sasintegra.sascar.com.br/SasIntegra/SasIntegraWSService?wsdl'
        self.username = SASCAR_USERNAME
        self.password = SASCAR_PASSWORD
        self.client = self.configurar_cliente_sascar()
    
    def configurar_cliente_sascar(self):
        """Configura e retorna o cliente SOAP para a API Sascar com conexão segura"""
        try:
            # Configuração do contexto SSL para TLSv1.2
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Configuração da sessão com autenticação e SSL
            session = Session()
            session.verify = True  # Validação do certificado do servidor
            
            # Adaptador de transporte com suporte a retry
            adapter = HTTPAdapter(
                max_retries=urllib3.Retry(
                    total=3,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504]
                )
            )
            session.mount('https://', adapter)
            
            settings = Settings(
                strict=False,
                xml_huge_tree=True,
                extra_http_headers={
                    'Content-Type': 'text/xml; charset=utf-8',
                    'User-Agent': 'SascarIntegracaoAPI/1.0'
                }
            )
            
            transport = Transport(session=session, timeout=30, operation_timeout=30)
            
            return Client(self.wsdl_url, settings=settings, transport=transport)
        except Exception as e:
            raise Exception(f"Erro ao configurar cliente SOAP seguro: {str(e)}")
    
    def zeep_to_dict(self, zeep_obj):
        """
        Converte um objeto Zeep para dicionário Python
        
        Args:
            zeep_obj: Objeto retornado pela API Zeep
            
        Returns:
            dict: Dicionário com os dados do objeto
        """
        try:
            # Tenta diferentes métodos para extrair dados do objeto Zeep
            
            # Método 1: Usar __values__ se disponível (estrutura comum do Zeep)
            if hasattr(zeep_obj, '__values__'):
                if zeep_obj.__values__:
                    return dict(zeep_obj.__values__)
            
            # Método 2: Usar __dict__ e filtrar atributos internos
            if hasattr(zeep_obj, '__dict__'):
                result = {}
                for key, value in zeep_obj.__dict__.items():
                    # Pular atributos internos do Zeep
                    if key.startswith('_'):
                        continue
                    
                    if isinstance(value, datetime):
                        result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif hasattr(value, '__values__') or hasattr(value, '__dict__'):
                        result[key] = self.zeep_to_dict(value)
                    elif isinstance(value, list):
                        result[key] = [self.zeep_to_dict(item) if (hasattr(item, '__values__') or hasattr(item, '__dict__')) else item for item in value]
                    else:
                        result[key] = value
                
                if result:  # Se encontrou dados válidos
                    return result
            
            # Método 3: Tentar acessar diretamente as propriedades do objeto
            # Isso funciona para alguns tipos de objetos Zeep
            if hasattr(zeep_obj, '__class__'):
                result = {}
                # Tentar obter todos os atributos não privados
                for attr_name in dir(zeep_obj):
                    if not attr_name.startswith('_') and not callable(getattr(zeep_obj, attr_name)):
                        try:
                            attr_value = getattr(zeep_obj, attr_name)
                            if isinstance(attr_value, datetime):
                                result[attr_name] = attr_value.strftime('%Y-%m-%d %H:%M:%S')
                            elif hasattr(attr_value, '__values__') or hasattr(attr_value, '__dict__'):
                                result[attr_name] = self.zeep_to_dict(attr_value)
                            elif isinstance(attr_value, list):
                                result[attr_name] = [self.zeep_to_dict(item) if (hasattr(item, '__values__') or hasattr(item, '__dict__')) else item for item in attr_value]
                            else:
                                result[attr_name] = attr_value
                        except:
                            continue
                
                if result:
                    return result
            
            # Se nenhum método funcionou, retornar string representation
            return {'raw_data': str(zeep_obj)}
            
        except Exception as e:
            return {'error': f'Erro ao converter objeto Zeep: {str(e)}', 'raw_data': str(zeep_obj)}
    
    def process_response(self, response):
        """
        Processa a resposta da API convertendo objetos Zeep para dicionários
        
        Args:
            response: Resposta da API
            
        Returns:
            list: Lista de dicionários
        """
        if not response:
            return []
        
        processed_data = []
        for item in response:
            if hasattr(item, '__dict__'):
                processed_data.append(self.zeep_to_dict(item))
            else:
                processed_data.append(item)
        
        return processed_data
     
    def atualizar_senha(self, senha_atual, nova_senha):
        """
        Método para atualizar a senha do usuário
        
        Args:
            senha_atual (str): Senha atual
            nova_senha (str): Nova senha
            
        Returns:
            str: Mensagem de confirmação
        """
        try:
            response = self.client.service.atualizarSenha(
                usuario=self.username,
                senhaAtual=senha_atual,
                novaSenha=nova_senha
            )
            return response
        except Fault as e:
            raise Exception(f"Erro ao atualizar senha: {str(e)}")
    
    def obter_grupo_atuadores(self):
        """
        Obtém a lista de sensores, atuadores e eventos disponíveis
        
        Returns:
            list: Lista de dicionários com informações dos atuadores
        """
        try:
            response = self.client.service.obterGrupoAtuadores(
                usuario=self.username,
                senha=self.password
            )
            return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter grupo de atuadores: {str(e)}")
    
    def obterClientes(self, quantidade=1, id_cliente=0):
        """
        Obtém informações sobre os clientes
        
        Args:
            quantidade (int, optional): Quantidade máxima de registros
            id_cliente (int, optional): ID de um cliente específico
            
        Returns:
            list: Lista de dicionários com informações dos clientes
        """
        try:
            response = self.client.service.obterClientes(
                usuario=self.username,
                senha=self.password,
                quantidade=quantidade,
                idCliente=id_cliente
            )
            return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter clientes: {str(e)}")
    
    def debug_zeep_object(self, obj, max_depth=2, current_depth=0):
        """
        Método para debug - mostra a estrutura interna de um objeto Zeep
        
        Args:
            obj: Objeto a ser analisado
            max_depth: Profundidade máxima para análise
            current_depth: Profundidade atual (usado internamente)
        """
        indent = "  " * current_depth
        #print(f"{indent}Tipo: {type(obj)}")
        
        if hasattr(obj, '__dict__'):
            print(f"{indent}__dict__ keys: {list(obj.__dict__.keys())}")
            if current_depth < max_depth:
                for key, value in obj.__dict__.items():
                    print(f"{indent}  {key}: {type(value)}")
                    if hasattr(value, '__dict__') and current_depth < max_depth - 1:
                        self.debug_zeep_object(value, max_depth, current_depth + 2)
        
        if hasattr(obj, '__values__'):
            print(f"{indent}__values__: {obj.__values__}")
        
        if hasattr(obj, 'keys'):
            print(f"{indent}keys(): {list(obj.keys()) if callable(obj.keys) else 'not callable'}")
        
        # Tentar listar todos os atributos não privados
        attrs = [attr for attr in dir(obj) if not attr.startswith('_') and not callable(getattr(obj, attr, None))]
        if attrs:
            print(f"{indent}Atributos públicos: {attrs[:10]}...")  # Mostrar apenas os primeiros 10

    
    def obterVeiculos(self, json_format=False, debug=False):
        """
        Obtém informações sobre os veículos
        
        Args:
            json_format (bool): Se True, usa o método que retorna JSON
            debug (bool): Se True, mostra informações de debug
            
        Returns:
            list: Lista de dicionários com informações dos veículos
        """
        try:
            if json_format:
                response = self.client.service.obterVeiculosJson(
                    usuario=self.username,
                    senha=self.password,
                    quantidade=0
                )
                # O retorno já vem em JSON, então podemos converter diretamente
                return json.loads(response) if response else []
            else:
                response = self.client.service.obterVeiculos(
                    usuario=self.username,
                    senha=self.password,
                    quantidade=0,
                )
                # Verificar se há dados
                if response:
                    print(f"Total de veículos encontrados: {len(response)}")
                
                if debug and response:
                    print(f"Tipo da resposta: {type(response)}")
                    print(f"Quantidade de itens: {len(response) if hasattr(response, '__len__') else 'N/A'}")
                    if len(response) > 0:
                        print("Estrutura do primeiro item:")
                        self.debug_zeep_object(response[0])
                
                return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter veículos: {str(e)}")


    def obterPacotePosicoes(self, quantidade=3000, motorista=False, com_placa=False):
        """
        Obtém pacotes de posições dos veículos
        
        Args:
            quantidade (int): Quantidade máxima de registros (default 3000)
            motorista (bool): Se True, inclui informações do motorista
            com_placa (bool): Se True, inclui a placa do veículo
            
        Returns:
            list: Lista de dicionários com informações dos pacotes de posição
        """
        try:
            if motorista:
                if com_placa:
                    response = self.client.service.obterPacotePosicoesMotoristaComPlaca(
                        usuario=self.username,
                        senha=self.password,
                        quantidade=quantidade
                    )
                else:
                    response = self.client.service.obterPacotePosicoesMotorista(
                        usuario=self.username,
                        senha=self.password,
                        quantidade=quantidade
                    )
            else:
                response = self.client.service.obterPacotePosicoes(
                    usuario=self.username,
                    senha=self.password,
                    quantidade=quantidade
                )
            
            return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter pacotes de posições: {str(e)}")
    
    def obterPacotePosicaoMotoristaPorRangeJSON(self, id_inicio, id_final, quantidade=3000, motorista=False, json_format=False):
        """
        Obtém pacotes de posições por range de IDs
        
        Args:
            id_inicio (int): ID do primeiro pacote
            id_final (int): ID do último pacote
            quantidade (int): Quantidade máxima de registros (default 3000)
            motorista (bool): Se True, inclui informações do motorista
            json_format (bool): Se True, usa o método que retorna JSON
            
        Returns:
            list: Lista de dicionários com informações dos pacotes de posição
        """
        try:
            if json_format:
                if motorista:
                    response = self.client.service.obterPacotePosicaoMotoristaPorRangeJSON(
                        usuario=self.username,
                        senha=self.password,
                        idInicio=id_inicio,
                        idFinal=id_final,
                        quantidade=quantidade
                    )
                else:
                    response = self.client.service.obterPacotePosicaoPorRangeJSON(
                        usuario=self.username,
                        senha=self.password,
                        idInicio=id_inicio,
                        idFinal=id_final,
                        quantidade=quantidade
                    )
                
                # O retorno já vem em JSON, então podemos converter diretamente
                return json.loads(response) if response else []
            else:
                if motorista:
                    response = self.client.service.obterPacotePosicaoMotoristaPorRange(
                        usuario=self.username,
                        senha=self.password,
                        idInicio=id_inicio,
                        idFinal=id_final,
                        quantidade=quantidade
                    )
                else:
                    response = self.client.service.obterPacotePosicaoPorRange(
                        usuario=self.username,
                        senha=self.password,
                        idInicio=id_inicio,
                        idFinal=id_final,
                        quantidade=quantidade
                    )
                
                return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter pacotes de posições por range: {str(e)}")

    
    def obterStatusComando(self, ticket=None, ticket_sascar=False):
        """
        Obtém o status de um comando enviado
        
        Args:
            ticket (int): Número do ticket do comando
            ticket_sascar (bool): Se True, usa o ticket interno da Sascar
            
        Returns:
            list: Lista de dicionários com status do comando
        """
        try:
            if ticket_sascar:
                response = self.client.service.obterStatusComandoTicketSascar(
                    usuario=self.username,
                    senha=self.password,
                    ticket=ticket
                )
            else:
                response = self.client.service.obterStatusComando(
                    usuario=self.username,
                    senha=self.password,
                    ticket=ticket
                )
            
            return self.process_response(response)
        except Fault as e:
            raise Exception(f"Erro ao obter status do comando: {str(e)}")
    
    
    def obterEventoTelemetriaIntegracao(self, idVeiculo, dataInicio, dataFinal):
        """
        Obtém eventos de telemetria para um veículo em um intervalo específico
        
        Args:
            idVeiculo (int): Número do ticket do comando
            dataInicio (str): Data de início no formato 'YYYY-MM-DD HH:MM:SS'
            dataFinal (str): Data final no formato 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            list: Lista de dicionários com eventos telemetria
        """
        try:
            if not all([idVeiculo, dataInicio, dataFinal]):
                raise ValueError('Parametros pendentes')
            
            # Garante que as datas estejam no formato correto para a API
            if isinstance(dataInicio, datetime):
                dataInicio = dataInicio.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(dataFinal, datetime):
                dataFinal = dataFinal.strftime('%Y-%m-%d %H:%M:%S')
            
            resultado = self.client.service.obterEventoTelemetriaIntegracao(
                usuario=self.username,
                senha=self.password,
                idVeiculo=idVeiculo,
                dataInicio=dataInicio,
                dataFinal=dataFinal,
            )
            
            return resultado or []
        except Exception as e:
            raise Exception(f"Erro ao obter eventos de telemetria: {str(e)}")
        
    
    def obterEventoTelemetriaIntegracaoDataChegada(self, idVeiculo, dataInicio=None, dataFinal=None,idEventoList=None):
        """
        Obtém eventos de telemetria
        
        Args:
            idVeiculo (int): Número do ID do veiculo
            idEventoList (int): Número do ID do evento
            data_inicio (str, optional): Data de início no formato 'YYYY-MM-DD HH:MM:SS'
            data_final (str, optional): Data final no formato 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            list: Lista de dicionários com eventos de telemetria data chegada
        """
        try:
            if not all([idVeiculo, dataInicio, dataFinal]):
                raise ValueError('Parametros pendentes')
            
            # Garante que as datas estejam no formato correto para a API
            if isinstance(dataInicio, datetime):
                dataInicio = dataInicio.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(dataFinal, datetime):
                dataFinal = dataFinal.strftime('%Y-%m-%d %H:%M:%S')
            
            response = self.client.service.obterEventoTelemetriaIntegracaoDataChegada(
                usuario=self.username,
                senha=self.password,
                idVeiculo=idVeiculo,
                dataInicio=dataInicio,
                dataFinal=dataFinal,
                dataChegadaInicio=dataInicio,
                dataChegadaFinal=dataFinal,
                idEventoList=idEventoList,
            )
            return self.process_response(response)
        except Exception as e:
            raise Exception(f"Erro ao obter eventos de telemetria: {str(e)}")
    
    def obterDeltaTelemetriaIntegracao(self, idVeiculo, dataInicio, dataFinal):
        """
        Obtém todos os Delta Telemetria disponíveis
        
        Args:
            idVeiculo (int): Número do ID do veiculo
            data_inicio (str, optional): Data de início no formato 'YYYY-MM-DD HH:MM:SS'
            data_final (str, optional): Data final no formato 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            list: Lista de dicionários com eventos de telemetria integração
        """
        try:
            resultado = self.client.service.obterDeltaTelemetriaIntegracao(
                usuario=self.username,
                senha=self.password,
                dataInicio=dataInicio,
                dataFinal=dataFinal,
                idVeiculo=idVeiculo,
            )
            return self.process_response(resultado)
        except Exception as e:
            raise Exception(f"Erro ao obter Delta Telemetria Integracao: {str(e)}")
    
    # Em desenvolvimento
    def to_excel_multisheet(self, data_dict, nome_arquivo):
        """Exporta múltiplos conjuntos de dados para planilhas diferentes"""
        with pd.ExcelWriter(nome_arquivo) as writer:
            for sheet_name, data in data_dict.items():
                pd.DataFrame(data).to_excel(writer, sheet_name=sheet_name, index=False)
    
    def export(self, data, nome_arquivo="file", formato='excel'or'csv'or'json'):
        """
        Exporta dados em múltiplos formatos
        
        Args:
            data (str): dados que serão exportados
            nome_arquivo (str, optional): Nome do arquivo que será exportado, nome padrão 'file'
            formato (str, 'excel'|'csv'|'json', optional): formato de exportação do arquivo
        """
        if formato == 'excel':
            """Exporta os dados para um arquivo Excel"""
            #return self.to_excel(data, nome_arquivo+".xlsx")
            return pd.DataFrame(data).to_excel(nome_arquivo+".xlsx", index=False, sheet_name=nome_arquivo)
        elif formato == 'csv':
            """Exporta os dados para um arquivo csv"""
            return pd.DataFrame(data).to_csv(nome_arquivo+".csv", index=False)
        elif formato == 'json':
            """Exporta os dados para um arquivo json"""
            with open(nome_arquivo+".json", 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
    
    def formatar_data(self, data_zeep):
        """Formata datas do objeto Zeep para string"""
        if data_zeep is None:
            return ''
        if isinstance(data_zeep, datetime):
            return data_zeep.strftime('%Y-%m-%d %H:%M:%S')
        return str(data_zeep)