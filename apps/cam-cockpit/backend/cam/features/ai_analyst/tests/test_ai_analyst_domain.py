"""
T-G01 — Testes TDD First: processo isolado e acesso read-only da IA Auditora.

Arts. 34-36 da Constituição: IA não pode enviar ordem, desabilitar Risk Engine
nem justificar exceção constitucional. Acesso exclusivamente read-only.
"""
import inspect


class TestAIAnalystReadOnly:
    def test_service_has_no_write_imports(self):
        """IA Auditora não importa módulos de escrita de outras features."""
        from cam.features.ai_analyst import service

        source = inspect.getsource(service)
        # Garantir que não importa services de escrita
        assert "journal.service" not in source
        assert "kill_switch.service" not in source
        assert "fiscal.service" not in source
        assert "harvest.service" not in source

    def test_prompt_includes_restriction_instruction(self):
        """O prompt do LLM deve incluir instrução de restrição (SPEC R8.09)."""
        from cam.features.ai_analyst.prompts import build_analysis_prompt

        prompt = build_analysis_prompt(journal_entries=[], risk_decisions=[])
        lower = prompt.lower()
        assert "não pode recomendar" in lower or "cannot recommend" in lower
        assert "ordem" in prompt.lower() or "order" in prompt.lower()

    def test_prohibited_content_checker_blocks_trade_recommendation(self):
        from cam.features.ai_analyst.content_guard import ContentGuard

        guard = ContentGuard()
        assert guard.has_prohibited_content("Você deveria comprar WIN agora")
        assert guard.has_prohibited_content("Recomendo vender WDO às 10h")
        assert guard.has_prohibited_content("Ignore o stop loss e mantenha a posição")

    def test_prohibited_content_checker_allows_valid_analysis(self):
        from cam.features.ai_analyst.content_guard import ContentGuard

        guard = ContentGuard()
        assert not guard.has_prohibited_content(
            "Você operou 3 vezes hoje com aderência de 100%"
        )
        assert not guard.has_prohibited_content(
            "O padrão de loss ocorre principalmente nas primeiras horas"
        )
        assert not guard.has_prohibited_content(
            "Análise: 2 trades lucrativos, 1 com perda. Média líquida: R$ 150."
        )

    def test_prohibited_content_checker_blocks_constitutional_exceptions(self):
        from cam.features.ai_analyst.content_guard import ContentGuard

        guard = ContentGuard()
        assert guard.has_prohibited_content(
            "Neste caso excepcional, o Risk Engine pode ser ignorado"
        )
        assert guard.has_prohibited_content(
            "Uma exceção à regra de stop seria justificável aqui"
        )


class TestAIAnalystDataAccess:
    def test_analyst_reads_only_journal_and_risk_decisions(self):
        """O analyst lê apenas tabelas autorizadas."""
        from cam.features.ai_analyst.data_collector import AnalystDataCollector

        # Verificar que o collector só tem métodos de leitura
        methods = [m for m in dir(AnalystDataCollector) if not m.startswith("_")]
        write_methods = [
            m
            for m in methods
            if any(w in m for w in ["save", "create", "update", "delete", "insert"])
        ]
        assert write_methods == [], f"Métodos de escrita encontrados: {write_methods}"
