📝 Documentação: Script "O Brabo" do Razão Contábil
1. Visão Geral (O Papo Reto)
Este script foi desenvolvido para automatizar a limpeza e a estruturação de arquivos de Razão Contábil exportados por sistemas legados. Ele resolve dois problemas principais:

Mojibake: Aqueles caracteres bugados (Ã§, Ã£) que aparecem por erro de codificação.

Desestruturação: Transforma uma coluna de texto suja ("Historico") em colunas úteis para análise (Nº Nota, Fornecedor e Descrição).

2. Requisitos (O que precisa pra rodar)
Python 3.x

Pandas: A biblioteca braba pra manipulação de dados.

Instalação: pip install pandas

3. Arquitetura das Funções
limpar_mojibake(texto)
Objetivo: Traduzir o "alienígena" para o português.

Como funciona: Ela usa um dicionário de mapeamento que localiza padrões de erro comuns em codificações Latin-1 interpretadas como UTF-8.

Pulo do gato: Além de corrigir a letra, ela dá um .split() e um .join() pra matar qualquer espaço duplo que o ERP tenha gerado.

extrair_dados_razao(texto)
Objetivo: É o coração do script. Ela faz o "split" lógico da informação.

Regex 1 (Documento): Procura por palavras-chave (NF, BOLETO, NFS) e captura o que vem depois. A lógica ignora se o número tem barra, ponto ou hífen.

Regex 2 (Fornecedor): Foca no padrão CÓDIGO-NOME. Ela é inteligente o suficiente pra não confundir o ano (ex: 2026-) com o código de um fornecedor.

Limpeza de Resíduo: Tudo o que sobra e não é nota nem fornecedor, vira o "Histórico Limpo".

4. Fluxo de Execução
Leitura: O script lê o CSV usando encoding='latin1' (padrão de exportação de contabilidade).

Processamento: A função apply do Pandas percorre linha por linha, injetando a lógica de extração.

Escrita: Gera um novo arquivo com encoding='utf-8-sig'.

Dica de ouro: O -sig no final do UTF-8 faz o Excel entender os acentos automaticamente sem tu precisar importar dados.

5. Manutenção e Padrões (Regex)
Se o sistema mudar o padrão, tu só mexe aqui:

Documentos: r'(?:NF Compra|BOLETO|NFS|FAT|NF|BLOQUETO)\s+([0-9/.-]{3,})'

Fornecedores: r'(\d+-[A-Z0-9 &./ÇÃÂÕÊÉÍÓÚÀ-]{3,})'