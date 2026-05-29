"""
T-A02 — Testes de validação do docker-compose.yml.
"""
from pathlib import Path

import yaml


def test_docker_compose_valid_yaml():
    compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"
    with open(compose_file) as f:
        config = yaml.safe_load(f)
    assert "services" in config
    assert "db" in config["services"]
    db = config["services"]["db"]
    assert "timescale/timescaledb" in db["image"]
    assert any("5433" in str(p) for p in db.get("ports", []))


def test_docker_compose_has_volume():
    compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"
    with open(compose_file) as f:
        config = yaml.safe_load(f)
    assert "volumes" in config
    assert "pgdata" in config["volumes"]
