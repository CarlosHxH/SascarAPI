## Uso/Exemplos

```python
    import os
    from sascar import SascarAPI


    # Exemplo de uso
    if __name__ == "__main__":
        # Configurações de conexão
        USERNAME = os.getenv('SASCAR_USERNAME')
        PASSWORD = os.getenv('SASCAR_PASSWORD')
        
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
            #print('telemetria',veiculos[:1])
            #obterPacote = sascar.obterPacotePosicaoMotoristaPorRangeJSON(0, 0)
            #sascar.export([], 'nomeDoArquivo', 'csv')
            
        except Exception as e:
            print(f"Erro: {str(e)}")
```
## Biblioteca api sascar com ssl para python


## Variáveis de Ambiente

Para rodar esse projeto, você vai precisar adicionar as seguintes variáveis de ambiente no seu .env

`SASCAR_USERNAME='seu_usuario'`

`SASCAR_PASSWORD='sua_senha'`


## Rodando localmente

Clone o projeto

```bash
  git clone https://github.com/CarlosHxH/SascarAPI.git
```

Entre no diretório do projeto

```bash
  cd SascarAPI
```

Instale as dependências

```bash
  python -m venv venv
  pip install -r requirements.txt
```

Usar a biblioteca

```bash
  python app.py
```

### Em Desenvolvimento