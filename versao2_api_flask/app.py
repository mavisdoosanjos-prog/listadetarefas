# -*- coding: utf-8 -*-
"""
Projeto Integrador - Sistema de Lista de Tarefas e Hábitos (API REST com Flask)

Como executar:
    pip install flask
    python app.py
A API sobe em http://127.0.0.1:5000

Endpoints:
    GET     /                          -> informações da API
    GET     /tarefas                   -> lista itens (filtros: ?tipo=, ?concluida=, ?prioridade=)
    GET     /tarefas/<id>              -> busca um item
    POST    /tarefas                   -> cria tarefa ou hábito
    PUT     /tarefas/<id>              -> atualiza um item
    PATCH   /tarefas/<id>/concluir     -> marca uma tarefa como concluída
    POST    /habitos/<id>/registros    -> registra que o hábito foi cumprido hoje
    DELETE  /tarefas/<id>              -> remove um item
    GET     /resumo                    -> estatísticas gerais
"""

from datetime import date, datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------
# 1. DADOS EM MEMÓRIA (sem banco de dados)
# ---------------------------------------------------------
TIPOS_VALIDOS = ("tarefa", "habito")
PRIORIDADES_VALIDAS = ("baixa", "media", "alta")

itens = [
    {
        "id": 1,
        "titulo": "Entregar Projeto Integrador",
        "descricao": "Finalizar documentos e API",
        "tipo": "tarefa",
        "prioridade": "alta",
        "prazo": "2026-10-15",
        "concluida": False,
        "registros": [],
        "criada_em": datetime.now().isoformat(timespec="seconds"),
    },
    {
        "id": 2,
        "titulo": "Beber 2 litros de água",
        "descricao": "Hábito diário de hidratação",
        "tipo": "habito",
        "prioridade": "media",
        "prazo": None,
        "concluida": False,
        "registros": [],
        "criada_em": datetime.now().isoformat(timespec="seconds"),
    },
]
proximo_id = 3


# ---------------------------------------------------------
# 2. FUNÇÕES AUXILIARES
# ---------------------------------------------------------
def erro(mensagem, codigo):
    """Resposta de erro padronizada em JSON."""
    return jsonify({"erro": mensagem}), codigo


def buscar_item(id_item):
    return next((i for i in itens if i["id"] == id_item), None)


def validar_data(texto):
    """Retorna True se o texto estiver no formato AAAA-MM-DD."""
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def calcular_sequencia(registros):
    """Conta quantos dias seguidos o hábito foi cumprido (até hoje ou ontem)."""
    if not registros:
        return 0
    datas = {datetime.strptime(r, "%Y-%m-%d").date() for r in registros}
    dia = date.today()
    if dia not in datas:
        dia -= timedelta(days=1)
    sequencia = 0
    while dia in datas:
        sequencia += 1
        dia -= timedelta(days=1)
    return sequencia


def item_para_json(item):
    """Copia o item e adiciona a sequência quando for hábito."""
    dados = dict(item)
    if item["tipo"] == "habito":
        dados["sequencia_dias"] = calcular_sequencia(item["registros"])
    return dados


def validar_corpo(dados, parcial=False):
    """Valida os campos enviados. Retorna mensagem de erro ou None."""
    if not isinstance(dados, dict):
        return "Envie um corpo JSON válido."

    if not parcial or "titulo" in dados:
        titulo = dados.get("titulo")
        if not isinstance(titulo, str) or not titulo.strip():
            return "O campo 'titulo' é obrigatório."

    if "tipo" in dados and dados["tipo"] not in TIPOS_VALIDOS:
        return "O campo 'tipo' deve ser 'tarefa' ou 'habito'."

    if "prioridade" in dados and dados["prioridade"] not in PRIORIDADES_VALIDAS:
        return "O campo 'prioridade' deve ser 'baixa', 'media' ou 'alta'."

    if dados.get("prazo") is not None and "prazo" in dados:
        if not validar_data(dados["prazo"]):
            return "O campo 'prazo' deve estar no formato AAAA-MM-DD."

    return None


# ---------------------------------------------------------
# 3. ENDPOINTS
# ---------------------------------------------------------
@app.get("/")
def raiz():
    return jsonify({
        "api": "Lista de Tarefas e Hábitos",
        "versao": "1.0",
        "documentacao": "Veja a lista de endpoints no topo do arquivo app.py",
    })


@app.get("/tarefas")
def listar():
    """GET - lista itens, com filtros opcionais."""
    resultado = itens

    tipo = request.args.get("tipo")
    if tipo:
        resultado = [i for i in resultado if i["tipo"] == tipo]

    prioridade = request.args.get("prioridade")
    if prioridade:
        resultado = [i for i in resultado if i["prioridade"] == prioridade]

    concluida = request.args.get("concluida")
    if concluida:
        valor = concluida.lower() == "true"
        resultado = [i for i in resultado if i["concluida"] == valor]

    return jsonify([item_para_json(i) for i in resultado]), 200


@app.get("/tarefas/<int:id_item>")
def obter(id_item):
    """GET - busca um item pelo ID."""
    item = buscar_item(id_item)
    if not item:
        return erro("Item não encontrado.", 404)
    return jsonify(item_para_json(item)), 200


@app.post("/tarefas")
def criar():
    """POST - cria uma nova tarefa ou hábito."""
    global proximo_id
    dados = request.get_json(silent=True)

    mensagem = validar_corpo(dados)
    if mensagem:
        return erro(mensagem, 400)

    novo = {
        "id": proximo_id,
        "titulo": dados["titulo"].strip(),
        "descricao": dados.get("descricao", ""),
        "tipo": dados.get("tipo", "tarefa"),
        "prioridade": dados.get("prioridade", "media"),
        "prazo": dados.get("prazo"),
        "concluida": False,
        "registros": [],
        "criada_em": datetime.now().isoformat(timespec="seconds"),
    }
    itens.append(novo)
    proximo_id += 1
    return jsonify(item_para_json(novo)), 201


@app.put("/tarefas/<int:id_item>")
def atualizar(id_item):
    """PUT - atualiza os dados de um item existente."""
    item = buscar_item(id_item)
    if not item:
        return erro("Item não encontrado.", 404)

    dados = request.get_json(silent=True)
    mensagem = validar_corpo(dados)
    if mensagem:
        return erro(mensagem, 400)

    item["titulo"] = dados["titulo"].strip()
    item["descricao"] = dados.get("descricao", item["descricao"])
    item["tipo"] = dados.get("tipo", item["tipo"])
    item["prioridade"] = dados.get("prioridade", item["prioridade"])
    item["prazo"] = dados.get("prazo", item["prazo"])
    return jsonify(item_para_json(item)), 200


@app.patch("/tarefas/<int:id_item>/concluir")
def concluir(id_item):
    """PATCH - marca uma tarefa como concluída."""
    item = buscar_item(id_item)
    if not item:
        return erro("Item não encontrado.", 404)
    if item["tipo"] == "habito":
        return erro("Hábitos não são concluídos; use POST /habitos/<id>/registros.", 400)
    if item["concluida"]:
        return erro("A tarefa já está concluída.", 409)

    item["concluida"] = True
    return jsonify(item_para_json(item)), 200


@app.post("/habitos/<int:id_item>/registros")
def registrar_habito(id_item):
    """POST - registra que o hábito foi cumprido hoje."""
    item = buscar_item(id_item)
    if not item:
        return erro("Item não encontrado.", 404)
    if item["tipo"] != "habito":
        return erro("Este item é uma tarefa, não um hábito.", 400)

    hoje = date.today().isoformat()
    if hoje in item["registros"]:
        return erro("Hábito já registrado hoje.", 409)

    item["registros"].append(hoje)
    return jsonify(item_para_json(item)), 201


@app.delete("/tarefas/<int:id_item>")
def remover(id_item):
    """DELETE - remove um item."""
    item = buscar_item(id_item)
    if not item:
        return erro("Item não encontrado.", 404)
    itens.remove(item)
    return jsonify({"mensagem": "Item removido com sucesso."}), 200


@app.get("/resumo")
def resumo():
    """GET - estatísticas gerais do sistema."""
    tarefas = [i for i in itens if i["tipo"] == "tarefa"]
    habitos = [i for i in itens if i["tipo"] == "habito"]
    concluidas = [t for t in tarefas if t["concluida"]]
    hoje = date.today().isoformat()

    return jsonify({
        "total_itens": len(itens),
        "tarefas": {
            "total": len(tarefas),
            "concluidas": len(concluidas),
            "pendentes": len(tarefas) - len(concluidas),
        },
        "habitos": {
            "total": len(habitos),
            "cumpridos_hoje": sum(1 for h in habitos if hoje in h["registros"]),
        },
    }), 200


# ---------------------------------------------------------
# 4. EXECUÇÃO
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
