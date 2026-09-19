from pathlib import Path

from interface import AplicacaoTerminal


def principal() -> None:
    arquivo_dados = Path(__file__).parent / "dados" / "banco.json"
    AplicacaoTerminal(arquivo_dados).executar()


if __name__ == "__main__":
    principal()
