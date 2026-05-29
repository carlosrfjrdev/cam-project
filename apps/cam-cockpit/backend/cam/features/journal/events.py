"""
Eventos publicados pela feature journal.

JournalEntryCreated é consumido por:
- fiscal/ (atualiza provisão fiscal em tempo real — SPEC R3.08)
- harvest/ (snapshot de buckets pós-pagamento)
"""
from dataclasses import dataclass

from cam._shared.events import DomainEvent


@dataclass
class JournalEntryCreated(DomainEvent):
    """
    Publicado após persistência de um JournalEntry.

    Contém os valores em string para evitar dependência de Money nos consumidores.
    Art. 25º: result_net e tax_provisioned SEMPRE presentes no evento.
    """

    entry_id: str
    result_gross_brl: str      # resultado bruto como string (Decimal seguro)
    result_net_brl: str        # resultado líquido — Art. 25º
    tax_provisioned_brl: str   # imposto provisionado — Art. 24º
    asset: str                 # WIN | WDO
