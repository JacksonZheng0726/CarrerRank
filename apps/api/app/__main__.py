from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        proxy_headers=True,
        loop="app.core.platform:psycopg_compatible_loop_factory",
    )


if __name__ == "__main__":
    main()
