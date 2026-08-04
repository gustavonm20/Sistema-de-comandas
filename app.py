# =========================
# CLASSES
# =========================

class Product:
    def __init__(self, product_id, name, price, category):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.active = True


# =========================
# LISTAS DO SISTEMA
# =========================

products = []


# =========================
# MENUS
# =========================

def show_menu():
    print("\n=====================")
    print("Sistema de comandas")
    print("1 - Produtos")
    print("2 - Comandas")
    print("3 - Histórico de vendas")
    print("4 - Resumo")
    print("0 - Encerrar sistema")
    print("=====================")


def show_product_menu():
    print("\n=====================")
    print("Área de produtos")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Pesquisar produto")
    print("4 - Editar produto")
    print("5 - Desativar produto")
    print("0 - Voltar ao menu principal")
    print("=====================")


def show_order_menu():
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


def show_history_menu():
    print("\n=====================")
    print("Histórico de vendas")
    print("1 - Listar todas as vendas")
    print("2 - Pesquisar venda")
    print("0 - Voltar ao menu principal")
    print("=====================")


def show_summary_menu():
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

def read_option():
    while True:
        try:
            option = int(input("Escolha uma opção: "))
            return option

        except ValueError:
            print("Entrada inválida, digite apenas números.")


def read_price():
    while True:
        try:
            price = input("Digite o preço do produto: R$ ")

            # Troca a vírgula por ponto para o Python reconhecer o decimal
            price = price.replace(",", ".")

            price = float(price)

            if price <= 0:
                print("O preço deve ser maior que zero.")
                continue

            return price

        except ValueError:
            print("Preço inválido. Digite apenas números.")


def format_currency(value):
    formatted_value = f"R$ {value:.2f}"
    return formatted_value.replace(".", ",")


def pause():
    input("\nPressione ENTER para continuar...")


def find_product_by_id(product_id):
    for product in products:
        if product.product_id == product_id:
            return product

    return None


# =========================
# FUNÇÕES DE PRODUTOS
# =========================

def register_product():
    print("\n=====================")
    print("Cadastro de produto")
    print("=====================")

    name = input("Digite o nome do produto: ").strip()
    category = input("Digite a categoria do produto: ").strip()
    price = read_price()

    product_id = len(products) + 1

    product = Product(
        product_id,
        name,
        price,
        category
    )

    products.append(product)

    print("\nProduto cadastrado com sucesso!")
    print(f"Código: {product.product_id}")
    print(f"Nome: {product.name}")
    print(f"Preço: {format_currency(product.price)}")
    print(f"Categoria: {product.category}")


def list_products():
    print("\nLista de produtos")
    print("=====================")

    if not products:
        print("Nenhum produto cadastrado.")
        return

    for product in products:
        status = "Ativo" if product.active else "Desativado"

        print(
            f"\nCódigo: {product.product_id} | "
            f"Nome: {product.name} | "
            f"Preço: {format_currency(product.price)} | "
            f"Categoria: {product.category} | "
            f"Status: {status}"
        )


def search_product():
    print("\nPesquisa de produto")
    print("=====================")

    if not products:
        print("Nenhum produto cadastrado.")
        return

    searched_name = input("Digite o nome do produto: ").strip().lower()

    found_products = []

    for product in products:
        if searched_name in product.name.lower():
            found_products.append(product)

    if not found_products:
        print("Nenhum produto encontrado.")
        return

    print("\nProdutos encontrados:")

    for product in found_products:
        status = "Ativo" if product.active else "Desativado"

        print(
            f"\nCódigo: {product.product_id} | "
            f"Nome: {product.name} | "
            f"Preço: {format_currency(product.price)} | "
            f"Categoria: {product.category} | "
            f"Status: {status}"
        )


def edit_product():
    print("\nEdição de produto")
    print("=====================")

    if not products:
        print("Nenhum produto cadastrado.")
        return

    try:
        product_id = int(input("Digite o código do produto: "))

    except ValueError:
        print("Código inválido. Digite apenas números.")
        return

    product = find_product_by_id(product_id)

    if product is None:
        print("Produto não encontrado.")
        return

    print("\nProduto encontrado:")
    print(f"Nome atual: {product.name}")
    print(f"Preço atual: {format_currency(product.price)}")
    print(f"Categoria atual: {product.category}")

    new_name = input("\nDigite o novo nome: ").strip()
    new_category = input("Digite a nova categoria: ").strip()
    new_price = read_price()

    product.name = new_name
    product.category = new_category
    product.price = new_price

    print("\nProduto editado com sucesso!")


def deactivate_product():
    print("\nDesativação de produto")
    print("=====================")

    if not products:
        print("Nenhum produto cadastrado.")
        return

    try:
        product_id = int(input("Digite o código do produto: "))

    except ValueError:
        print("Código inválido. Digite apenas números.")
        return

    product = find_product_by_id(product_id)

    if product is None:
        print("Produto não encontrado.")
        return

    if not product.active:
        print("Esse produto já está desativado.")
        return

    print(f"\nProduto: {product.name}")

    confirmation = input(
        "Deseja realmente desativar este produto? (S/N): "
    ).strip().lower()

    if confirmation == "s":
        product.active = False
        print("Produto desativado com sucesso.")

    else:
        print("Desativação cancelada.")


# =========================
# ÁREA DE PRODUTOS
# =========================

def product_view():
    while True:
        show_product_menu()
        option = read_option()

        match option:
            case 1:
                register_product()

            case 2:
                list_products()

            case 3:
                search_product()

            case 4:
                edit_product()

            case 5:
                deactivate_product()

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pause()

# =========================
# ÁREA DE COMANDAS
# =========================

def order_view():
    while True:
        show_order_menu()
        option = read_option()

        match option:
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

        pause()


# =========================
# ÁREA DE HISTÓRICO
# =========================

def historic_view():
    while True:
        show_history_menu()
        option = read_option()

        match option:
            case 1:
                print("\nLista de vendas selecionada.")

            case 2:
                print("\nPesquisa de venda selecionada.")

            case 0:
                print("\nVoltando ao menu principal...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")

        pause()


# =========================
# ÁREA DE RESUMOS
# =========================

def summary_view():
    while True:
        show_summary_menu()
        option = read_option()

        match option:
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

        pause()


# =========================
# PROGRAMA PRINCIPAL
# =========================

def start_system():
    while True:
        show_menu()
        option = read_option()

        match option:
            case 1:
                product_view()

            case 2:
                order_view()

            case 3:
                historic_view()

            case 4:
                summary_view()

            case 0:
                print("\nEncerrando sistema...")
                break

            case _:
                print("\nOpção inválida, tente novamente.")
                pause()


# Verifica se este é o arquivo principal antes de iniciar o sistema
if __name__ == "__main__":
    start_system()

