"""
Importador de CSV exportado pelo Profit/Nelogica (F2).

Formato esperado (separador ponto-e-vírgula):
    Data;Hora;Ativo;Operacao;Contratos;Preco Entrada;Preco Saida;Resultado

Deduplicação: hash SHA-256 gerado por concatenação de
    Data + Hora + Ativo + Resultado.
Reimportação do mesmo arquivo detecta duplicatas pelo hash.

Art. 31º: todo registro importado deve gerar JournalEntry.
"""
import csv
import hashlib
from decimal import Decimal, InvalidOperation
from io import StringIO


class ProfitCSVImporter:
    """
    Parseia CSV exportado pelo Profit e retorna lista de dicts normalizados.

    Cada entry contém:
        asset       str              — "WIN" | "WDO"
        direction   str              — "LONG" | "SHORT"
        contracts   int
        entry_price Decimal
        exit_price  Decimal
        result_gross Decimal
        date        str              — "YYYY-MM-DD"
        time        str              — "HH:MM:SS"
        hash        str              — SHA-256 hex (64 chars) para deduplicação
    """

    def parse(self, file_obj: StringIO) -> list[dict]:
        """
        Parseia o arquivo CSV e retorna lista de entradas normalizadas.

        Linhas vazias ou com campos faltando são silenciosamente ignoradas.
        """
        reader = csv.DictReader(file_obj, delimiter=";")
        entries = []

        for row in reader:
            # Ignora linhas completamente vazias
            if not any(v.strip() for v in row.values() if v):
                continue

            # Campos obrigatórios
            ativo = (row.get("Ativo") or "").strip()
            if not ativo:
                continue

            # Hash de deduplicação (imutável por linha — baseado em campos-chave)
            raw_date = (row.get("Data") or "").strip()
            raw_hora = (row.get("Hora") or "").strip()
            raw_resultado = (row.get("Resultado") or "").strip()
            content = f"{raw_date}{raw_hora}{ativo}{raw_resultado}"
            row_hash = hashlib.sha256(content.encode()).hexdigest()

            # Direção: "Compra" → LONG, qualquer outra coisa → SHORT
            operacao = (row.get("Operacao") or "").strip()
            direction = "LONG" if operacao == "Compra" else "SHORT"

            # Decimais — substituição de vírgula por ponto (locale BR)
            def to_decimal(val: str) -> Decimal:
                try:
                    return Decimal(val.replace(",", ".").strip())
                except (InvalidOperation, AttributeError):
                    return Decimal("0")

            entries.append({
                "asset": ativo,
                "direction": direction,
                "contracts": int((row.get("Contratos") or "1").strip()),
                "entry_price": to_decimal(row.get("Preco Entrada") or "0"),
                "exit_price": to_decimal(row.get("Preco Saida") or "0"),
                "result_gross": to_decimal(raw_resultado),
                "date": raw_date,
                "time": raw_hora,
                "hash": row_hash,
            })

        return entries
