import requests
from datetime import date

# 1. API EXTERNA (BrasilAPI - Feriados nacionais)
def obter_proximo_feriado():
    """Busca na internet o próximo feriado nacional do ano."""
    ano = date.today().year
    url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            hoje = date.today().isoformat()
            for feriado in resposta.json():
                if feriado["date"] >= hoje:
                    return feriado["name"], feriado["date"]
        return None
    except Exception:
        return None


# 2. DADOS EM MEMÓRIA (sem banco de dados)
tarefas = [
    {"id": 1, "titulo": "Entregar Projeto Integrador", "concluida": False},
    {"id": 2, "titulo": "Beber 2 litros de água", "concluida": False},
]
proximo_id = 3


# 3. FUNÇÕES DO SISTEMA
def listar_tarefas():
    print("\n--- SUAS TAREFAS ---")
    feriado = obter_proximo_feriado()
    if feriado:
        nome, data = feriado
        data_br = f"{data[8:10]}/{data[5:7]}/{data[:4]}"
        print(f"📅 Próximo feriado (obtido via API): {nome} - {data_br}\n")
    else:
        print("⚠️ Não foi possível obter o próximo feriado.\n")

    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
        return

    for t in tarefas:
        status = "✅ Concluída" if t["concluida"] else "⏳ Pendente"
        print(f"{t['id']:<3} | {t['titulo']:<35} | {status}")


def adicionar_tarefa():
    global proximo_id
    print("\n--- NOVA TAREFA ---")
    titulo = input("Digite a tarefa ou hábito: ").strip()
    if not titulo:
        print("❌ O título não pode ficar vazio.")
        return
    tarefas.append({"id": proximo_id, "titulo": titulo, "concluida": False})
    proximo_id += 1
    print(f"✅ '{titulo}' adicionada com sucesso!")


def concluir_tarefa():
    listar_tarefas()
    try:
        id_tarefa = int(input("\nDigite o ID da tarefa concluída: "))
    except ValueError:
        print("❌ Digite um número válido.")
        return
    tarefa = next((t for t in tarefas if t["id"] == id_tarefa), None)
    if not tarefa:
        print("❌ Tarefa não encontrada!")
        return
    tarefa["concluida"] = True
    print(f"🎉 Tarefa '{tarefa['titulo']}' marcada como concluída!")


def apagar_tarefa():
    listar_tarefas()
    try:
        id_tarefa = int(input("\nDigite o ID da tarefa a apagar: "))
    except ValueError:
        print("❌ Digite um número válido.")
        return
    tarefa = next((t for t in tarefas if t["id"] == id_tarefa), None)
    if not tarefa:
        print("❌ Tarefa não encontrada!")
        return
    tarefas.remove(tarefa)
    print(f"🗑️ Tarefa '{tarefa['titulo']}' apagada!")


# 4. MENU PRINCIPAL
def menu():
    while True:
        print("\n====================================")
        print("   LISTA DE TAREFAS E HÁBITOS")
        print("====================================")
        print("1. Listar tarefas")
        print("2. Adicionar tarefa")
        print("3. Marcar tarefa como concluída")
        print("4. Apagar tarefa")
        print("5. Sair")
        opcao = input("Escolha uma opção (1-5): ").strip()
        if opcao == "1":
            listar_tarefas()
        elif opcao == "2":
            adicionar_tarefa()
        elif opcao == "3":
            concluir_tarefa()
        elif opcao == "4":
            apagar_tarefa()
        elif opcao == "5":
            print("\nEncerrando o sistema... Até logo!")
            break
        else:
            print("❌ Opção inválida! Digite um número de 1 a 5.")


menu()
