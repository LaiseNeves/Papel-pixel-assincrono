from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_rota_inicial():
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "API Papel & Pixel funcionando. Sistema de compras assíncronas ativo."


def test_criar_compra_sem_token_deve_bloquear():
    resposta = client.post(
        "/compras",
        json={
            "nome_cliente": "Laise",
            "item": "Caneta colorida",
            "quantidade": 1
        }
    )

    assert resposta.status_code in [401, 403]


def test_criar_compra_com_quantidade_invalida():
    resposta = client.post(
        "/compras",
        headers={
            "Authorization": "Bearer token-laise-2026"
        },
        json={
            "nome_cliente": "Laise",
            "item": "Planner semanal",
            "quantidade": 0
        }
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A quantidade precisa ser maior que zero"