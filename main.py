"""Launch the EldhoAi desktop application."""
from gui import EldhoAiApp


def main() -> None:
    app = EldhoAiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
