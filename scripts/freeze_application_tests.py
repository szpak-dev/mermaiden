from pathlib import Path

from tests.repository.application_policy import ApplicationTestCheck


class ApplicationTestFreezeWriter:
    def write(self) -> None:
        root = Path(__file__).resolve().parents[1]
        freeze = ApplicationTestCheck(root).current_freeze()
        path = root / "tests" / "application-suite.freeze.json"
        path.write_text(freeze.model_dump_json(indent=2) + "\n", encoding="utf-8")
        print(f"Application test freeze written: {path.relative_to(root)}")


if __name__ == "__main__":
    ApplicationTestFreezeWriter().write()
