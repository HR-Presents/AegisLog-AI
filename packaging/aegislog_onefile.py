from __future__ import annotations

import sys

from aegislog.entry import app


def main() -> None:
    # A customer double-clicking AegisLog.exe should land directly in the
    # interactive terminal experience. Advanced users can still pass any
    # normal CLI command, for example: AegisLog.exe dashboard auth.log
    if len(sys.argv) == 1:
        sys.argv.append("start")
    app()


if __name__ == "__main__":
    main()
