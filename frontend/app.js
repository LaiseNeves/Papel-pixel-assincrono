const API_URL = "http://localhost:8000";
const TOKEN_API = "token-laise-2026";

const formCompra = document.getElementById("formCompra");
const areaResultado = document.getElementById("areaResultado");

const compraId = document.getElementById("compraId");
const compraCliente = document.getElementById("compraCliente");
const compraItem = document.getElementById("compraItem");
const compraQuantidade = document.getElementById("compraQuantidade");
const compraSituacao = document.getElementById("compraSituacao");

function exibirCompra(compra) {
  compraId.textContent = compra.id;
  compraCliente.textContent = compra.nome_cliente;
  compraItem.textContent = compra.item;
  compraQuantidade.textContent = compra.quantidade;
  compraSituacao.textContent = compra.situacao;

  compraSituacao.className = "etiqueta";

  if (compra.situacao === "Aguardando processamento") {
    compraSituacao.classList.add("aguardando");
  }

  if (compra.situacao === "Pedido confirmado") {
    compraSituacao.classList.add("confirmado");
  }

  if (compra.situacao === "Pedido recusado") {
    compraSituacao.classList.add("recusado");
  }

  areaResultado.classList.remove("escondido");
}

async function consultarCompra(id) {
  const resposta = await fetch(`${API_URL}/compras/${id}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${TOKEN_API}`
    }
  });

  const compra = await resposta.json();
  exibirCompra(compra);

  return compra.situacao;
}

async function acompanharProcessamento(id) {
  let tentativas = 0;
  const limiteTentativas = 8;

  const intervalo = setInterval(async function () {
    tentativas++;

    const situacaoAtual = await consultarCompra(id);

    if (
      situacaoAtual === "Pedido confirmado" ||
      situacaoAtual === "Pedido recusado" ||
      tentativas >= limiteTentativas
    ) {
      clearInterval(intervalo);
    }
  }, 2000);
}

formCompra.addEventListener("submit", async function (evento) {
  evento.preventDefault();

  const nomeCliente = document.getElementById("nomeCliente").value;
  const item = document.getElementById("item").value;
  const quantidade = Number(document.getElementById("quantidade").value);

  const resposta = await fetch(`${API_URL}/compras`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${TOKEN_API}`
    },
    body: JSON.stringify({
      nome_cliente: nomeCliente,
      item: item,
      quantidade: quantidade
    })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert("Não foi possível registrar a compra: " + JSON.stringify(dados));
    return;
  }

  exibirCompra(dados.compra);
  acompanharProcessamento(dados.compra.id);
});