from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from modelos import Pedido, Produto, Venda
from servicos import ErroNegocio, ServicoComandas


def formatar_dinheiro(centavos: int) -> str:
    valor = centavos / 100
    formatado = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatado}"


def converter_dinheiro(texto: str) -> int:
    normalizado = texto.strip().replace("R$", "").replace(" ", "")
    if not normalizado:
        raise ValueError
    if "," in normalizado:
        normalizado = normalizado.replace(".", "").replace(",", ".")
    valor = float(normalizado)
    centavos = round(valor * 100)
    if valor < 0:
        raise ValueError
    return centavos


class AplicacaoTerminal:
    def __init__(instancia, arquivo_dados: Path) -> None:
        instancia.servico = ServicoComandas(arquivo_dados)

    def executar(instancia) -> None:
        while True:
            instancia.limpar()
            situacao_sessao = "ABERTO" if instancia.servico.sessao_caixa_atual else "FECHADO"
            instancia.titulo(f"FLUXOPAG — SISTEMA DE COMANDAS | DIA {situacao_sessao}")
            print("1 - Produtos")
            print("2 - Comandas")
            print("3 - Histórico de vendas")
            print("4 - Resumo")
            print("5 - Caixa")
            print("0 - Encerrar sistema")
            match instancia.ler_opcao():
                case 1: instancia.menu_produtos()
                case 2: instancia.menu_comandas()
                case 3: instancia.historico_vendas()
                case 4: instancia.menu_resumos()
                case 5: instancia.menu_caixa()
                case 0:
                    print("Sistema encerrado com segurança.")
                    return
                case _: instancia.mensagem("Opção inválida.")

    def menu_produtos(instancia) -> None:
        while True:
            instancia.limpar(); instancia.titulo("PRODUTOS")
            print("1 - Cadastrar produto\n2 - Listar produtos\n3 - Pesquisar produto")
            print("4 - Editar produto\n5 - Desativar produto\n0 - Voltar")
            opcao = instancia.ler_opcao()
            if opcao == 0: return
            try:
                match opcao:
                    case 1: instancia.criar_produto()
                    case 2: instancia.exibir_produtos(instancia.servico.produtos)
                    case 3: instancia.pesquisar_produto()
                    case 4: instancia.editar_produto()
                    case 5: instancia.desativar_produto()
                    case _: instancia.mensagem("Opção inválida.")
            except ErroNegocio as erro: instancia.mensagem(str(erro))

    def criar_produto(instancia) -> None:
        instancia.titulo("CADASTRAR PRODUTO")
        produto = instancia.servico.adicionar_produto(input("Nome: "), instancia.ler_dinheiro("Preço: R$ "), input("Categoria: "))
        instancia.mensagem(f"Produto {produto.id_produto} cadastrado com sucesso.")

    def exibir_produtos(instancia, produtos: list[Produto], pausar: bool = True) -> None:
        instancia.titulo("LISTA DE PRODUTOS")
        if not produtos: print("Nenhum produto encontrado.")
        for produto in produtos:
            situacao = "Ativo" if produto.ativo else "Desativado"
            print(f"Código: {produto.id_produto} | Nome: {produto.nome} | Preço: {formatar_dinheiro(produto.preco_centavos)} | Categoria: {produto.categoria} | Status: {situacao}")
        if pausar: instancia.pausar()

    def pesquisar_produto(instancia) -> None:
        instancia.exibir_produtos(instancia.servico.pesquisar_produtos(input("Nome ou categoria: ")))

    def editar_produto(instancia) -> None:
        produto = instancia.servico.encontrar_produto(instancia.ler_inteiro_positivo("Código do produto: "))
        print("Informe os novos dados.")
        instancia.servico.editar_produto(produto.id_produto, input("Nome: "), instancia.ler_dinheiro("Preço: R$ "), input("Categoria: "))
        instancia.mensagem("Produto atualizado com sucesso.")

    def desativar_produto(instancia) -> None:
        id_produto = instancia.ler_inteiro_positivo("Código do produto: ")
        produto = instancia.servico.encontrar_produto(id_produto)
        if instancia.confirmar(f"Desativar '{produto.nome}'?"):
            instancia.servico.desativar_produto(id_produto); instancia.mensagem("Produto desativado.")

    def menu_comandas(instancia) -> None:
        while True:
            instancia.limpar(); instancia.titulo("COMANDAS")
            print("1 - Abrir comanda\n2 - Listar comandas\n3 - Adicionar produto")
            print("4 - Remover produto\n5 - Visualizar comanda\n6 - Fechar comanda\n0 - Voltar")
            opcao = instancia.ler_opcao()
            if opcao == 0: return
            try:
                match opcao:
                    case 1: instancia.abrir_pedido()
                    case 2: instancia.listar_pedidos()
                    case 3: instancia.adicionar_item_pedido()
                    case 4: instancia.remover_item_pedido()
                    case 5: instancia.visualizar_pedido()
                    case 6: instancia.fechar_pedido()
                    case _: instancia.mensagem("Opção inválida.")
            except ErroNegocio as erro: instancia.mensagem(str(erro))

    def abrir_pedido(instancia) -> None:
        pedido = instancia.servico.abrir_pedido(instancia.ler_inteiro_positivo("Número da comanda: "))
        instancia.mensagem(f"Comanda {pedido.numero_comanda} aberta com sucesso.")

    def listar_pedidos(instancia) -> None:
        instancia.titulo("SITUAÇÃO DAS COMANDAS")
        numeros_abertos = {pedido.numero_comanda for pedido in instancia.servico.pedidos}
        for numero in range(1, instancia.servico.MAXIMO_COMANDAS + 1):
            print(f"Comanda {numero:02d}: {'Aberta' if numero in numeros_abertos else 'Disponível'}")
        instancia.pausar()

    def adicionar_item_pedido(instancia) -> None:
        numero = instancia.ler_inteiro_positivo("Número da comanda: ")
        instancia.exibir_produtos([item for item in instancia.servico.produtos if item.ativo], pausar=False)
        instancia.servico.adicionar_item(numero, instancia.ler_inteiro_positivo("Código do produto: "), instancia.ler_inteiro_positivo("Quantidade: "))
        instancia.mensagem("Produto adicionado à comanda.")

    def remover_item_pedido(instancia) -> None:
        numero = instancia.ler_inteiro_positivo("Número da comanda: ")
        instancia.exibir_pedido(instancia.servico.encontrar_pedido(numero))
        instancia.servico.remover_item(numero, instancia.ler_inteiro_positivo("Código do produto: "), instancia.ler_inteiro_positivo("Quantidade a remover: "))
        instancia.mensagem("Produto removido da comanda.")

    def visualizar_pedido(instancia) -> None:
        instancia.exibir_pedido(instancia.servico.encontrar_pedido(instancia.ler_inteiro_positivo("Número da comanda: ")))
        instancia.pausar()

    def fechar_pedido(instancia) -> None:
        numero = instancia.ler_inteiro_positivo("Número da comanda: ")
        pedido = instancia.servico.encontrar_pedido(numero); instancia.exibir_pedido(pedido)
        print("\n1 - Dinheiro | 2 - Pix | 3 - Crédito | 4 - Débito")
        pagamento = str(instancia.ler_opcao("Forma de pagamento: "))
        if not instancia.confirmar(f"Confirmar fechamento da comanda {numero} por {formatar_dinheiro(pedido.total_centavos)}?"):
            instancia.mensagem("Fechamento cancelado."); return
        venda = instancia.servico.fechar_pedido(numero, pagamento)
        instancia.mensagem(f"Venda {venda.id_venda} concluída. A comanda {numero} está disponível novamente.")

    def exibir_pedido(instancia, pedido: Pedido) -> None:
        instancia.titulo(f"COMANDA {pedido.numero_comanda:02d}")
        if not pedido.itens: print("Comanda sem produtos.")
        for item in pedido.itens:
            print(f"{item.quantidade}x {item.nome_produto} | {formatar_dinheiro(item.preco_unitario_centavos)} | Subtotal: {formatar_dinheiro(item.subtotal_centavos)}")
        print(f"TOTAL: {formatar_dinheiro(pedido.total_centavos)}")

    def historico_vendas(instancia) -> None:
        instancia.limpar(); instancia.titulo("HISTÓRICO DE VENDAS")
        if not instancia.servico.vendas: print("Nenhuma venda concluída.")
        for venda in reversed(instancia.servico.vendas): instancia.exibir_venda(venda)
        instancia.pausar()

    def exibir_venda(instancia, venda: Venda) -> None:
        quando = datetime.fromisoformat(venda.fechado_em).strftime("%d/%m/%Y %H:%M")
        print(f"Venda #{venda.id_venda} | Comanda {venda.numero_comanda:02d} | {quando} | {venda.forma_pagamento} | {formatar_dinheiro(venda.total_centavos)}")

    def menu_resumos(instancia) -> None:
        while True:
            instancia.limpar(); instancia.titulo("RESUMOS")
            print("1 - Resumo do dia\n2 - Resumo da semana\n3 - Resumo do mês\n0 - Voltar")
            match instancia.ler_opcao():
                case 1: instancia.exibir_resumo("dia", "DIA")
                case 2: instancia.exibir_resumo("semana", "SEMANA")
                case 3: instancia.exibir_resumo("mes", "MÊS")
                case 0: return
                case _: instancia.mensagem("Opção inválida.")

    def exibir_resumo(instancia, periodo: str, rotulo: str) -> None:
        resumo = instancia.servico.resumo_periodo(periodo)
        instancia.limpar(); instancia.titulo(f"RESUMO DO {rotulo}")
        print(f"Período: {resumo['inicio'].strftime('%d/%m/%Y')} a {resumo['fim'].strftime('%d/%m/%Y')}")
        print(f"Vendas concluídas: {resumo['quantidade_vendas']}")
        print(f"Faturamento: {formatar_dinheiro(resumo['total_centavos'])}")
        print(f"Ticket médio: {formatar_dinheiro(resumo['media_centavos'])}")
        print("\nPor forma de pagamento:")
        pagamentos = resumo["pagamentos"]
        if not pagamentos: print("  Sem vendas no período.")
        for metodo, total in pagamentos.items(): print(f"  {metodo}: {formatar_dinheiro(total)}")
        print("\nProdutos mais vendidos:")
        produtos_mais_vendidos = resumo["produtos_mais_vendidos"]
        if not produtos_mais_vendidos: print("  Sem produtos vendidos no período.")
        for nome, quantidade in produtos_mais_vendidos: print(f"  {nome}: {quantidade} unidade(s)")
        variacao = resumo["variacao_percentual"]
        print("\nComparação com o período anterior:")
        print(f"  Anterior: {formatar_dinheiro(resumo['total_anterior_centavos'])}")
        if variacao is None: print("  Variação: indisponível (período anterior sem vendas)")
        else: print(f"  Variação: {variacao:+.1f}%")
        instancia.pausar()

    def menu_caixa(instancia) -> None:
        instancia.limpar(); instancia.titulo("CAIXA")
        sessao = instancia.servico.sessao_caixa_atual
        if sessao is None:
            print("O dia está fechado.\n1 - Iniciar dia\n0 - Voltar")
            if instancia.ler_opcao() == 1:
                try:
                    sessao = instancia.servico.abrir_caixa(instancia.ler_dinheiro("Saldo inicial do caixa: R$ "))
                    instancia.mensagem(f"Dia iniciado às {datetime.fromisoformat(sessao.aberto_em).strftime('%H:%M')}.")
                except ErroNegocio as erro: instancia.mensagem(str(erro))
            return
        print(f"Dia iniciado em {datetime.fromisoformat(sessao.aberto_em).strftime('%d/%m/%Y às %H:%M')}")
        print(f"Saldo inicial: {formatar_dinheiro(sessao.saldo_inicial_centavos)}")
        print(f"Comandas abertas: {len(instancia.servico.pedidos)}")
        print("\n1 - Finalizar dia\n0 - Voltar")
        if instancia.ler_opcao() != 1: return
        if instancia.servico.pedidos:
            numeros = ", ".join(str(pedido.numero_comanda) for pedido in instancia.servico.pedidos)
            instancia.mensagem(f"Fechamento bloqueado. Feche as comandas: {numeros}."); return
        obtido = instancia.ler_dinheiro("Valor contado em dinheiro no caixa: R$ ")
        if not instancia.confirmar("Esta ação encerrará definitivamente o dia. Confirmar?"):
            instancia.mensagem("Fechamento cancelado."); return
        try:
            fechado = instancia.servico.fechar_caixa(obtido)
            instancia.limpar(); instancia.titulo("DIA FINALIZADO")
            print(f"Valor esperado: {formatar_dinheiro(fechado.caixa_esperado_centavos or 0)}")
            print(f"Valor contado: {formatar_dinheiro(fechado.caixa_contado_centavos or 0)}")
            print(f"Diferença: {formatar_dinheiro(fechado.diferenca_centavos or 0)}")
            instancia.pausar()
        except ErroNegocio as erro: instancia.mensagem(str(erro))

    @staticmethod
    def titulo(texto: str) -> None:
        print(f"\n{'=' * 72}\n{texto}\n{'=' * 72}")

    @staticmethod
    def limpar() -> None:
        os.system("classe" if os.name == "nt" else "clear")

    @staticmethod
    def pausar() -> None:
        input("\nPressione ENTER para continuar...")

    def mensagem(instancia, texto: str) -> None:
        print(f"\n{texto}"); instancia.pausar()

    @staticmethod
    def ler_opcao(solicitacao: str = "Escolha uma opção: ") -> int:
        try: return int(input(solicitacao))
        except ValueError: return -1

    @staticmethod
    def ler_inteiro_positivo(solicitacao: str) -> int:
        while True:
            try:
                valor = int(input(solicitacao))
                if valor > 0: return valor
            except ValueError: pass
            print("Digite um número inteiro maior que zero.")

    @staticmethod
    def ler_dinheiro(solicitacao: str) -> int:
        while True:
            try: return converter_dinheiro(input(solicitacao))
            except ValueError: print("Digite um valor válido, como 10,50.")

    @staticmethod
    def confirmar(pergunta: str) -> bool:
        return input(f"{pergunta} (S/N): ").strip().casefold() == "s"
