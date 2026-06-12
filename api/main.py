from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pika
import json
import uuid
from memoria import compras

app = FastAPI(
    title="API Papel & Pixel - Compras Assíncronas",
    description="API para simular compras de uma papelaria online com processamento assíncrono via RabbitMQ.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN_API = "token-laise-2026"
NOME_FILA = "fila_papelaria"

security = HTTPBearer()


class CompraEntrada(BaseModel):
    nome_cliente: str
    item: str
    quantidade: int


def validar_acesso(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TOKEN_API:
        raise HTTPException(status_code=401, detail="Token inválido ou não informado")


def enviar_para_fila(mensagem: dict):
    try:
        conexao = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )

        canal = conexao.channel()
        canal.queue_declare(queue=NOME_FILA, durable=True)

        canal.basic_publish(
            exchange="",
            routing_key=NOME_FILA,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        conexao.close()

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Não foi possível enviar a compra para a fila: {erro}"
        )


@app.get("/")
def inicio():
    return {
        "mensagem": "API Papel & Pixel funcionando. Sistema de compras assíncronas ativo."
    }


@app.post("/compras", status_code=201)
def criar_compra(
    compra: CompraEntrada,
    autenticado: None = Depends(validar_acesso)
):
    if compra.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade precisa ser maior que zero"
        )

    compra_id = str(uuid.uuid4())

    compras[compra_id] = {
        "id": compra_id,
        "nome_cliente": compra.nome_cliente,
        "item": compra.item,
        "quantidade": compra.quantidade,
        "situacao": "Aguardando processamento"
    }

    enviar_para_fila({
        "id": compra_id,
        "nome_cliente": compra.nome_cliente,
        "item": compra.item,
        "quantidade": compra.quantidade
    })

    return {
        "mensagem": "Compra registrada e enviada para processamento.",
        "compra": compras[compra_id]
    }


@app.get("/compras/{compra_id}")
def consultar_compra(
    compra_id: str,
    autenticado: None = Depends(validar_acesso)
):
    if compra_id not in compras:
        raise HTTPException(status_code=404, detail="Compra não encontrada")

    return compras[compra_id]


@app.patch("/compras/{compra_id}/situacao")
def atualizar_situacao(
    compra_id: str,
    situacao: str,
    autenticado: None = Depends(validar_acesso)
):
    if compra_id not in compras:
        raise HTTPException(status_code=404, detail="Compra não encontrada")

    compras[compra_id]["situacao"] = situacao

    return {
        "mensagem": "Situação da compra atualizada com sucesso.",
        "compra": compras[compra_id]
    }