"""Verifica destinos locais, imagens e âncoras Markdown sem acessar a rede."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


RAIZ = Path(__file__).resolve().parents[1]


def ancoras(texto):
    resultado = set()
    contagens = {}
    for titulo in re.findall(r"^#{1,6}\s+(.+)$", texto, flags=re.MULTILINE):
        identificador = re.sub(r"[^\w\- ]", "", titulo.replace("`", "").lower()).replace(" ", "-")
        contagem = contagens.get(identificador, 0)
        resultado.add(f"{identificador}-{contagem}" if contagem else identificador)
        contagens[identificador] = contagem + 1
    return resultado


def principal():
    caminhos = subprocess.check_output(["git", "ls-files", "-z", "*.md"], cwd=RAIZ).decode().split("\0")
    erros = []
    verificados = 0
    for relativo in filter(None, caminhos):
        caminho = RAIZ / relativo
        texto = caminho.read_text(encoding="utf-8")
        texto = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)
        ligacoes = re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", texto)
        ligacoes += re.findall(r'(?:src|href)="([^"]+)"', texto)
        for destino in ligacoes:
            endereco = urlsplit(destino)
            if endereco.scheme or endereco.netloc:
                continue
            verificados += 1
            destino = caminho.parent / unquote(endereco.path) if endereco.path else caminho
            if not destino.exists():
                erros.append(f"{relativo}: destino ausente: {destino}")
            elif endereco.fragment and destino.suffix == ".md":
                if unquote(endereco.fragment) not in ancoras(destino.read_text(encoding="utf-8")):
                    erros.append(f"{relativo}: âncora ausente: {destino}")
    if erros:
        raise SystemExit("\n".join(erros))
    print(f"{verificados} links locais e imagens verificados em {len(list(filter(None, caminhos)))} arquivos Markdown.")


if __name__ == "__main__":
    principal()
