# Exemplo de uso da BIBLIOTECA


    import os
    from sascar import SascarAPI

    # Exemplo
    if __name__ == "__main__":
        # Configurações de conexão
        USERNAME = os.getenv('USERNAME')
        PASSWORD = os.getenv('PASSWORD')
        
        try:
            # Criar instância da API
            sascar = SascarAPI( USERNAME, PASSWORD)
            
            print("\n=== EXEMPLOS ===")
            # Lista de Exemplo
            #cliente = sascar.obterClientes()
            #veiculos = sascar.obterVeiculos()
            #obterPacotePosicoes = sascar.obterPacotePosicoes()
            #deltaTelemetria = sascar.obterDeltaTelemetriaIntegracao(1231226,'2025-05-20 00:00:00', '2025-05-20 12:59:59')
            #eventosTelemetria = sascar.obterEventoTelemetriaIntegracao(1231226,'2025-05-20 00:00:00', '2025-05-20 12:59:59')
            #telemetriaDataChegada = sascar.obterEventoTelemetriaIntegracaoDataChegada(1231226,'2025-05-21 00:00:00', '2025-05-21 23:59:59')
            #obterStatusComando = sascar.obterStatusComando(0)
            #obterPacote = sascar.obterPacotePosicaoMotoristaPorRangeJSON(0, 0)
            #sascar.export([], 'nomeDoArquivo', 'csv')
            
        except Exception as e:
            print(f"Erro: {str(e)}")

## Biblioteca api sascar com ssl para python

### Em Desenvolvimento
