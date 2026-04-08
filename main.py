from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

PADRAO_DOCUMENTO = re.compile(
    r"\b(?:NF\s+COMPRA|BOLETO|NFS|FAT|NF|BLOQUETO)\s+([0-9][0-9./-]{2,})",
    re.IGNORECASE,
)
PADRAO_FORNECEDOR = re.compile(
    r"\b(?P<codigo>\d{2,6})-(?P<nome>[\w &./-]{3,})",
    re.IGNORECASE,
)
PADRAO_PREFIXO = re.compile(
    r"^(?:NF\s+COMPRA|ENTRADA\s+BLOQUETO\s+BANCAR|ENTRADA\s+A\s+VISTA|0?\s*VR\s+REF(?:\s+A)?)\b\s*",
    re.IGNORECASE,
)
PADRAO_INICIO_SUJO = re.compile(r"^[\s\-:/(),.]+")
PADRAO_FORNECEDOR_RB = re.compile(r"^\s*0\s+VR\b", re.IGNORECASE)


def limpar_mojibake(texto: object) -> str:
    if not isinstance(texto, str):
        return ""

    texto_corrigido = texto
    for _ in range(2):
        if not any(marcador in texto_corrigido for marcador in ("\u00c3", "\u00c2", "\ufffd")):
            break
        try:
            texto_corrigido = texto_corrigido.encode("latin1").decode("utf-8")
        except UnicodeError:
            break

    return " ".join(texto_corrigido.split())


def _extrair_fornecedor(texto: str) -> tuple[str, tuple[int, int] | None]:
    for resultado in PADRAO_FORNECEDOR.finditer(texto):
        codigo = resultado.group("codigo")
        nome = resultado.group("nome").strip()
        if len(codigo) == 4 and 1900 <= int(codigo) <= 2099:
            continue
        return f"{codigo}-{nome}", resultado.span()
    return "", None


def _remover_spans(texto: str, spans: Iterable[tuple[int, int]]) -> str:
    texto_limpo = texto
    for inicio, fim in sorted(spans, reverse=True):
        texto_limpo = f"{texto_limpo[:inicio]} {' ' * (fim - inicio)}{texto_limpo[fim:]}"
    return texto_limpo


def extrair_dados_razao(texto: object) -> tuple[str, str, str]:
    texto_limpo = limpar_mojibake(texto)
    fornecedor_forcado_rb = bool(PADRAO_FORNECEDOR_RB.search(texto_limpo))

    documento = ""
    fornecedor = ""
    spans_para_remover: list[tuple[int, int]] = []

    resultado_documento = PADRAO_DOCUMENTO.search(texto_limpo)
    if resultado_documento:
        documento = resultado_documento.group(1)
        spans_para_remover.append(resultado_documento.span())

    fornecedor, span_fornecedor = _extrair_fornecedor(texto_limpo)
    if span_fornecedor:
        spans_para_remover.append(span_fornecedor)

    if fornecedor_forcado_rb:
        fornecedor = "RB"

    historico = _remover_spans(texto_limpo, spans_para_remover)
    historico = PADRAO_PREFIXO.sub("", historico)
    historico = PADRAO_INICIO_SUJO.sub("", historico)
    historico = " ".join(historico.split())

    return documento, fornecedor, historico


def separar_nf_serie(documento: str) -> tuple[str, str]:
    doc = (documento or "").strip()
    if not doc:
        return "", ""

    resultado = re.match(r"^(?P<nf>\d+)(?:[./-](?P<serie>[A-Za-z0-9]+))?$", doc)
    if resultado:
        return resultado.group("nf") or "", resultado.group("serie") or ""

    partes = re.split(r"[./-]", doc, maxsplit=1)
    if len(partes) == 2:
        return partes[0].strip(), partes[1].strip()
    return doc, ""


def carregar_csv(caminho: Path, separador: str) -> pd.DataFrame:
    return pd.read_csv(
        caminho,
        sep=separador,
        encoding="latin1",
        dtype=str,
        keep_default_na=False,
    )


def processar_razao(df: pd.DataFrame) -> pd.DataFrame:
    if "Historico" not in df.columns:
        raise KeyError("A coluna 'Historico' nao foi encontrada no arquivo de entrada.")

    saida = df.copy()
    saida = saida.loc[:, ~saida.columns.str.match(r"^Unnamed: ?\d+$")]

    extraidos = saida["Historico"].map(extrair_dados_razao).tolist()
    saida[["_NF_Documento", "Fornecedor_Extraido", "Hist_Limpo"]] = pd.DataFrame(
        extraidos,
        index=saida.index,
    )

    nf_serie = saida["_NF_Documento"].map(separar_nf_serie).tolist()
    saida[["NF", "Serie"]] = pd.DataFrame(nf_serie, index=saida.index)
    saida = saida.drop(columns=["_NF_Documento"])
    return saida


def salvar_csv(df: pd.DataFrame, caminho: Path, separador: str) -> None:
    df.to_csv(caminho, index=False, sep=separador, encoding="utf-8-sig")


def construir_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa arquivo de razao contabil e extrai documento/fornecedor/historico limpo."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="razao.csv",
        help="Arquivo CSV de entrada (padrao: razao.csv).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="razao_processado_brabo.csv",
        help="Arquivo CSV de saida (padrao: razao_processado_brabo.csv).",
    )
    parser.add_argument(
        "-s",
        "--sep",
        default=";",
        help="Separador do CSV (padrao: ';').",
    )
    return parser.parse_args()


def main() -> None:
    args = construir_args()
    arquivo_input = Path(args.input)
    arquivo_output = Path(args.output)

    if not arquivo_input.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {arquivo_input}")

    df = carregar_csv(arquivo_input, args.sep)
    df_processado = processar_razao(df)
    salvar_csv(df_processado, arquivo_output, args.sep)

    print(f"Arquivo '{arquivo_output}' gerado com sucesso.")


if __name__ == "__main__":
    main()
