"""
Launcher do backend CaM — força SelectorEventLoop no Windows.

uvicorn 0.48 usa ProactorEventLoop no Windows (sem subprocess), o que QUEBRA o
psycopg(async) do DB e o pyzmq(asyncio) da bridge. Aqui criamos o Server do uvicorn
e rodamos seu `serve()` com `loop_factory=SelectorEventLoop` (Python 3.13).

Uso:
  uv run python run_server.py [--host 127.0.0.1] [--port 8000]
"""
from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> None:
    ap = argparse.ArgumentParser(description="Sobe o backend CaM (SelectorEventLoop)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()

    from uvicorn import Config, Server

    config = Config("cam.api.main:app", host=a.host, port=a.port, loop="asyncio")
    server = Server(config)

    if sys.platform == "win32":
        # contorna o ProactorEventLoop forçado pelo uvicorn no Windows
        asyncio.run(server.serve(), loop_factory=asyncio.SelectorEventLoop)
    else:
        server.run()


if __name__ == "__main__":
    main()
