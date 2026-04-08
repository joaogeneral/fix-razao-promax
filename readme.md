# Documentacao - Tradutor de Razao Contabil

## Visao Geral
O projeto processa um CSV de razao contabil exportado por ERP legado e gera um novo arquivo com:
- Correcao de texto com mojibake no campo `Historico`.
- Extracao de documento em colunas separadas (`NF` e `Serie`).
- Extracao de fornecedor (`Fornecedor_Extraido`).
- Historico residual limpo (`Hist_Limpo`).

Arquivo padrao de entrada:
- `razao.csv`

Arquivo padrao de saida:
- `razao_processado_brabo.csv`

## Requisitos
- Python 3.10+
- `pandas`

Instalacao:

```bash
pip install pandas
```

## Como Executar

Execucao padrao:

```bash
python index.py
```

Com argumentos:

```bash
python index.py --input razao.csv --output razao_processado_brabo.csv --sep ";"
```

## Logica do Processamento
1. Le o CSV com `encoding='latin1'`, preservando dados como string.
2. Corrige mojibake no `Historico`.
3. Extrai numero de documento por regex (`NF`, `BOLETO`, `NFS`, `FAT`, etc.).
4. Separa documento em `NF` e `Serie` (exemplo: `36185/6` -> `NF=36185`, `Serie=6`).
5. Extrai fornecedor no padrao `codigo-nome`, ignorando falsos positivos de ano (`2026-...`).
6. Remove trechos extraidos do historico e limpa prefixos comuns.
7. Remove colunas `Unnamed` geradas por delimitador final no CSV.
8. Salva em `utf-8-sig` para abrir corretamente no Excel.

## Estrutura do Script (`index.py`)
- `limpar_mojibake`: corrige caracteres quebrados e normaliza espacos.
- `extrair_dados_razao`: retorna `(documento, fornecedor, historico_limpo)`.
- `separar_nf_serie`: separa documento em `NF` e `Serie`.
- `carregar_csv`: leitura padronizada do arquivo de entrada.
- `processar_razao`: aplica extracao no dataframe.
- `salvar_csv`: grava o CSV final.
- `main`: CLI e orquestracao.

## Observacoes de Manutencao
- Ajustes de regras de documento e fornecedor devem ser feitos nos regex globais:
  - `PADRAO_DOCUMENTO`
  - `PADRAO_FORNECEDOR`
- Ajustes de limpeza de prefixo devem ser feitos em `PADRAO_PREFIXO`.
- Caso o ERP mude formato, atualize os regex e valide com uma amostra real do CSV.

## Documentacao de Layouts
- `15.05.01.csv` (OBZ lancamentos Promax): ver `15.05.01.md`.
