from pathlib import Path

from ui import TerminalApp


def main() -> None:
    data_file = Path(__file__).parent / "data" / "database.json"
    TerminalApp(data_file).run()


if __name__ == "__main__":
    main()
