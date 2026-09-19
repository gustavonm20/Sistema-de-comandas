"""Verifica destinos locais, imagens e âncoras Markdown sem acessar a rede."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def anchors(text):
    result = set()
    counts = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", title.replace("`", "").lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        result.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return result


def main():
    paths = subprocess.check_output(["git", "ls-files", "-z", "*.md"], cwd=ROOT).decode().split("\0")
    errors = []
    checked = 0
    for relative in filter(None, paths):
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        links = re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text)
        links += re.findall(r'(?:src|href)="([^"]+)"', text)
        for target in links:
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            checked += 1
            destination = path.parent / unquote(url.path) if url.path else path
            if not destination.exists():
                errors.append(f"{relative}: destino ausente: {target}")
            elif url.fragment and destination.suffix == ".md":
                if unquote(url.fragment) not in anchors(destination.read_text(encoding="utf-8")):
                    errors.append(f"{relative}: âncora ausente: {target}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"{checked} links locais e imagens verificados em {len(list(filter(None, paths)))} arquivos Markdown.")


if __name__ == "__main__":
    main()
