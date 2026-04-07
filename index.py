import pandas as pd
import re

def limpar_mojibake(texto):
    """Corrige os erros de acentuação comuns em arquivos latinos."""
    if not isinstance(texto, str): return ""
    # Mapa de correções para os bugs mais chatos
    correcoes = {
        'Ã‡ÃƒO': 'ÇÃO', 'Ã‡': 'Ç', 'Ã„': 'Ã', 'Ãƒ': 'Ã', 'Ã‚': 'Â', 
        'ÃŠ': 'Ê', 'Ã‰': 'É', 'Ã': 'Í', 'Ã“': 'Ó', 'Ãš': 'Ú', 
        'Ã•': 'Õ', 'Ãª': 'ê', 'Ã©': 'é', 'Ã¡': 'á', 'Ã³': 'ó', 
        'Ãº': 'ú', 'Âª': 'ª', 'Â°': '°'
    }
    for errado, certo in correcoes.items():
        texto = texto.replace(errado, certo)
    return " ".join(texto.split()) # Remove espaços extras

def extrair_dados_razao(texto):
    """Extrai NF/Boleto, Fornecedor e limpa o histórico."""
    texto_limpo = limpar_mojibake(texto)
    nf = ""
    fornecedor = ""
    
    # 1. Busca o número do documento (NF, Boleto, Fatura)
    # Procura por números/barras após palavras-chave
    padrao_doc = re.search(r'(?:NF Compra|BOLETO|NFS|FAT|NF|BLOQUETO)\s+([0-9/.-]{3,})', texto_limpo, re.IGNORECASE)
    if padrao_doc:
        nf = padrao_doc.group(1)

    # 2. Busca o Fornecedor (Padrão: Código-Nome)
    # Procura por uma sequência de números, um hífen e o nome em maiúsculas
    padrao_forn = re.search(r'(\d+-[A-Z0-9 &./ÇÃÂÕÊÉÍÓÚÀ-]{3,})', texto_limpo)
    if padrao_forn:
        val = padrao_forn.group(1).strip()
        # Evita pegar datas no formato 2026-NOME
        fornecedor = val.split('-', 1)[1].strip() if re.match(r'^\d{4}-', val) else val

    # 3. Gera o histórico limpo removendo o que já extraímos
    hist_final = texto_limpo
    if nf: hist_final = hist_final.replace(nf, "")
    if fornecedor: hist_final = hist_final.replace(fornecedor, "")
    
    # Remove prefixos inúteis do início
    prefixos = ["NF COMPRA", "ENTRADA BLOQUETO BANCAR", "ENTRADA A VISTA", "VR REF A", "VR REF", "0 VR REF"]
    for p in prefixos:
        if hist_final.upper().startswith(p):
            hist_final = hist_final[len(p):].strip()
            
    hist_final = re.sub(r'^[ -:/(),]+', '', hist_final).strip()
    
    return pd.Series([nf, fornecedor, hist_final])

# --- EXECUÇÃO PRINCIPAL ---
arquivo_input = 'razao.csv' # Bota o nome do seu arquivo original
arquivo_output = 'razao_processado_brabo.csv'

# Carrega o CSV (usando latin1 que é o padrão de muito ERP antigo)
df = pd.read_csv(arquivo_input, sep=';', encoding='latin1')

# Aplica a mágica
df[['NF_Documento', 'Fornecedor_Extraido', 'Hist_Limpo']] = df['Historico'].apply(extrair_dados_razao)

# Salva o resultado em UTF-8 pra nunca mais ver mojibake na vida
df.to_csv(arquivo_output, index=False, sep=';', encoding='utf-8-sig')

print(f"Tá na mão, chefia! Arquivo '{arquivo_output}' gerado com sucesso.")