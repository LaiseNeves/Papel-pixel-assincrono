import pika
import json
import time
import random
import requests

NOME_FILA = "fila_papelaria"
TOKEN_API = "token-laise-2026"
URL_API = "http://localhost:8000"


def atualizar_situacao(compra_id, situacao):
    url = f"{URL_API}/compras/{compra_id}/situacao"

    headers = {
        "Authorization": f"Bearer {TOKEN_API}"
    }

    params = {
        "situacao": situacao
    }

    resposta = requests.patch(url, headers=headers, params=params)

    if resposta.status_code == 200:
        print(f"Compra {compra_id} atualizada para: {situacao}")
    else:
        print(f"Erro ao atualizar compra {compra_id}: {resposta.text}")


def processar_compra(ch, method, properties, body):
    dados = json.loads(body)

    compra_id = dados["id"]
    cliente = dados["nome_cliente"]
    item = dados["item"]
    quantidade = dados["quantidade"]

    print("----------------------------------------")
    print(f"Compra recebida: {compra_id}")
    print(f"Cliente: {cliente}")
    print(f"Item: {item}")
    print(f"Quantidade: {quantidade}")
    print("Separando item no estoque da papelaria...")

    time.sleep(5)

    situacao_final = random.choice([
        "Pedido confirmado",
        "Pedido recusado"
    ])

    atualizar_situacao(compra_id, situacao_final)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def iniciar_processador():
    print("Conectando ao RabbitMQ...")
    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

    canal = conexao.channel()
    canal.queue_declare(queue=NOME_FILA, durable=True)
    canal.basic_qos(prefetch_count=1)

    canal.basic_consume(
        queue=NOME_FILA,
        on_message_callback=processar_compra
    )

    print("Processador iniciado. Aguardando compras da Papel & Pixel...")
    canal.start_consuming()


if __name__ == "__main__":
    iniciar_processador()