# Exemplo de uso da API


    import os
    from sascar import SascarAPI


    # Exemplo de uso da API
    if __name__ == "__main__":
        # Configurações de conexão
        WSDL_URL = 'https://sasintegra.sascar.com.br/SasIntegra/SasIntegraWSService?wsdl'
        USERNAME = os.getenv('USERNAME')
        PASSWORD = os.getenv('PASSWORD')
        
        try:
            # Criar instância da API
            sascar = SascarAPI( USERNAME, PASSWORD)
            
            print("\n=== METODOS ===")
            # Lista de Exemplo
            veiculos = sascar.obterVeiculos()
            #deltaTelemetria = sascar.obterDeltaTelemetriaIntegracao(1231226,'2025-05-20 00:00:00', '2025-05-20 12:59:59')
            #eventosTelemetria = sascar.obterEventoTelemetriaIntegracao(1231226,'2025-05-20 00:00:00', '2025-05-20 12:59:59')
            #telemetriaDataChegada = sascar.obterEventoTelemetriaIntegracaoDataChegada(1231226,'2025-05-21 00:00:00', '2025-05-21 23:59:59')
            #obterStatusComando = sascar.obterStatusComando(0)
            #print('telemetria',veiculos[:1])
            #obterPacote = sascar.obterPacotePosicaoMotoristaPorRangeJSON(0, 0)
            sascar.export(veiculos, 'veiculos', 'csv')
            
        except Exception as e:
            print(f"Erro: {str(e)}")

