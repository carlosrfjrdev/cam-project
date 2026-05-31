"""
conftest.py raiz do backend — CaM Cockpit.

Configura o SelectorEventLoop no Windows antes de qualquer teste.
psycopg3 async é incompatível com ProactorEventLoop (padrão no Windows
desde Python 3.8). WindowsSelectorEventLoopPolicy força o loop correto
para todos os testes que usam asyncio, incluindo asyncio.run() direto.
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
