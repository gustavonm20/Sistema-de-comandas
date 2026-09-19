# =========================
# CLASSES
# =========================

class Produto:
    def __init__(instancia, id_produto, nome, preco, categoria):
        instancia.id_produto = id_produto
        instancia.nome = nome
        instancia.preco = preco
        instancia.categoria = categoria
        instancia.ativo = True


# =========================
# LISTAS DO SISTEMA
# =========================

produtos = []


# =========================
# MENUS
# =========================

def exibir_menu():
    print("\n=====================")
    print("Sistema de comandas")
    print("1 - Produtos")
    print("2 - Comandas")
    print("3 - Histórico de vendas")
    print("4 - Resumo")
    print("0 - Encerrar sistema")
    print("=====================")


def exibir_menu_produtos():
    print("\n=====================")
    print("Área de produtos")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Pesquisar produto")
    print("4 - Editar produto")
    print("5 - Desativar produto")
    print("0 - Voltar ao menu principal")
    print("=====================")


def exibir_menu_comandas():
    print("\n=====================")
    print("Área de comandas")
    print("1 - Abrir comanda")
    print("2 - Listar comandas")
    print("3 - Adicionar produto")
    print("4 - Remover produto")
    print("5 - Visualizar comanda")
    print("6 - Fechar comanda")
    print("0 - Voltar ao menu principal")
    print("=====================")


def exibir_menu_historico():
    print("\n=====================")
    print("Histórico de vendas")
    print("1 - Listar todas as vendas")
    print("2 - Pesquisar venda")
    print("0 - Voltar ao menu principal")
    print("=====================")


def exibir_menu_resumos():
    print("\n=====================")
    print("Resumo de vendas")
    print("1 - Resumo diário")
    print("2 - Resumo semanal")
    print("3 - Resumo mensal")
    print("0 - Voltar ao menu principal")
    print("=====================")


# =========================
# FUNÇÕES AUXILIARES
# =========================

def ler_opcao():
    while True:
        try:
            opcao = int(input("Escolha uma opção: "))
            return opcao

        except ValueError:
            print("Entrada inválida, digite apenas números.")


def ler_preco():
    while True:
        try:
            preco = input("Digite o preço do produto: R$ ")

            # Troca a vírgula por ponto para o Python reconhecer o decimal
            preco = preco.replace(",", ".")

            preco = float(preco)

            if preco <= 0:
                print("O preço deve ser maior que zero.")
                continue

            return preco

        except ValueError:
            print("Preço inválido. Digite apenas números.")


def formatar_moeda(valor):
    valor_formatado = f"R$ {valor:.2f}"
    return valor_formatado.replace(".", ",")


def pausar():
    input("\nPressione ENTER para continuar...")


def encontrar_produto_por_id(id_produto):
    for produto in produtos:
        if produto.id_produto == id_produto:
            return produto

    return None


# =========================
# FUNÇÕES DE PRODUTOS
# =========================

def cadastrar_produto():
    print("\n=====================")
    print("Cadastro de produto")
    print("=====================")

    nome = input("Digite o nome do produto: ").strip()
    categoria = input("Digite a categoria do produto: ").strip()
    preco = ler_preco()

    id_produto = len(produtos) + 1

    produto = Produto(
        id_produto,
        nome,
        preco,
        categoria
    )

    produtos.append(produto)

    print("\nProduto cadastrado com sucesso!")
    print(f"Código: {produto.id_produto}")
    print(f"Nome: {produto.nome}")
    print(f"Preço: {formatar_moeda(produto.preco)}")
    print(f"Categoria: {produto.categoria}")


def listar_produtos():
    print("\nLista de produtos")
    print("=====================")

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    for produto in produtos:
        situacao = "Ativo" if produto.ativo else "Desativado"

        print(
            f"\nCódigo: {produto.id_produto} | "
            f"Nome: {produto.nome} | "
            f"Preço: {formatar_moeda(produto.preco)} | "
            f"Categoria: {produto.categoria} | "
            f"Status: {situacao}"
        )


def pesquisar_produto():
    print("\nPesquisa de produto")
    print("=====================")

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    nome_pesquisado = input("Digite o nome do produto: ").strip().lower()

    produtos_encontrados = []

    for produto in produtos:
        if nome_pesquisado in produto.nome.lower():
            produtos_encontrados.append(produto)

    if not produtos_encontrados:
        print("Nenhum produto encontrado.")
        return

    print("\nProdutos encontrados:")

    for produto in produtos_encontrados:
        situacao = "Ativo" if produto.ativo else "Desativado"

        print(
            f"\nCódigo: {produto.id_produto} | "
            f"Nome: {produto.nome} | "
            f"Preço: {formatar_moeda(produto.preco)} | "
            f"Categoria: {produto.categoria} | "
            f"Status: {situacao}"
        )


def editar_produto():
    print("\nEdição de produto")
    print("=====================")

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    try:
        id_produto = int(input("Digite o código do produto: "))

    except ValueError:
        print("Código inválido. Digite apenas números.")
        return

    produto = encontrar_produto_por_id(id_produto)

    if produto is None:
        print("Produto não encontrado.")
        return

    print("\nProduto encontrado:")
    print(f"Nome atual: {produto.nome}")
    print(f"Preço atual: {formatar_moeda(produto.preco)}")
    print(f"Categoria atual: {produto.categoria}")

    novo_nome = input("\nDigite o novo nome: ").strip()
    nova_categoria = input("Digite a nova categoria: ").strip()
    novo_preco = ler_preco()

    produto.nome = novo_nome
    produto.categoria = nova_categoria
    produto.preco = novo_preco

    print("\nProduto editado com sucesso!")


def desativar_produto():
    print("\nDesativação de produto")
    print("=====================")

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    try:
        id_produto = int(input("Digite o código do produto: "))

    except ValueError:
        print("Código inválido. Digite apenas números.")
        return

    produto = encontrar_produto_por_id(id_produto)

    if produto is None:
        print("Produto não encontrado.")
        return

    if not produto.ativo:
        print("Esse produto já está desativado.")
        return

    print(f"\nProduto: {produto.nome}")

    confirmacao = input(
        "Deseja realmente desativar este produto? (S/N): "
    ).strip().lower()

    if confirmacao == "s":
        produto.ativo = False
        print("Produto desativado com sucesso.")

    else:
        print("Desativação cancelada.")


# =========================
# ÁREA DE PRODUTOS
# =========================

def tela_produtos():
    while True:
        exibir_menu_produtos()
        opcao = ler_opcao()

        match opcao:
            case 1:
                cadastrar_produto()

            case 2:
                listar_produtos()

            case 3:
                pesquisar_produto()

            case 4:
                editar_produto()

            case 5:
                desativar_produto()

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pausar()

# =========================
# ÁREA DE COMANDAS
# =========================

def tela_comandas():
    while True:
        exibir_menu_comandas()
        opcao = ler_opcao()

        match opcao:
            case 1:
                print("\nAbertura de comanda selecionada.")

            case 2:
                print("\nLista de comandas selecionada.")

            case 3:
                print("\nAdição de produto selecionada.")

            case 4:
                print("\nRemoção de produto selecionada.")

            case 5:
                print("\nVisualização de comanda selecionada.")

            case 6:
                print("\nFechamento de comanda selecionado.")

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pausar()


# =========================
# ÁREA DE HISTÓRICO
# =========================

def tela_historico():
    while True:
        exibir_menu_historico()
        opcao = ler_opcao()

        match opcao:
            case 1:
                print("\nLista de vendas selecionada.")

            case 2:
                print("\nPesquisa de venda selecionada.")

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pausar()


# =========================
# ÁREA DE RESUMOS
# =========================

def tela_resumos():
    while True:
        exibir_menu_resumos()
        opcao = ler_opcao()

        match opcao:
            case 1:
                print("\nResumo diário selecionado.")

            case 2:
                print("\nResumo semanal selecionado.")

            case 3:
                print("\nResumo mensal selecionado.")

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pausar()


# =========================
# PROGRAMA PRINCIPAL
# =========================

def iniciar_sistema():
    while True:
        exibir_menu()
        opcao = ler_opcao()

        match opcao:
            case 1:
                tela_produtos()

            case 2:
                tela_comandas()

            case 3:
                tela_historico()

            case 4:
                tela_resumos()

            case 0:
                print("\nEncerrando sistema...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")
                pausar()


# Verifica se este é o arquivo principal antes de iniciar o sistema
if __name__ == "__main__":
    iniciar_sistema()
