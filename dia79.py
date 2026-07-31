from abc import ABC, abstractmethod
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table


class ItemVenda:
    """Representa um item individual do carrinho."""

    def __init__(self, nome: str, preco: float, qtd: int = 1) -> None:
        """Inicializa o item com seus dados básicos."""
        self._nome, self._preco, self._qtd = nome, preco, qtd

    @property
    def nome(self) -> str:
        """Retorna o nome do produto."""
        return self._nome

    @property
    def preco(self) -> float:
        """Retorna o preço unitário."""
        return self._preco

    @property
    def qtd(self) -> int:
        """Retorna a quantidade do produto."""
        return self._qtd

    @property
    def subtotal(self) -> float:
        """Calcula o subtotal acumulado do item."""
        return self._preco * self._qtd


class CarrinhoCompras:
    """Gerencia a coleção de itens e operações do carrinho."""

    def __init__(self) -> None:
        """Inicializa a lista de itens do carrinho."""
        self._itens: List[ItemVenda] = []

    @property
    def itens(self) -> List[ItemVenda]:
        """Retorna a lista de itens cadastrados."""
        return self._itens

    @property
    def total_bruto(self) -> float:
        """Calcula a soma de todos os subtotais."""
        return sum(item.subtotal for item in self._itens)

    def adicionar(self, item: ItemVenda) -> None:
        """Insere um novo item no carrinho."""
        self._itens.append(item)

    def remover(self, indice: int) -> Optional[ItemVenda]:
        """Remove e retorna um item pelo índice informado."""
        return self._itens.pop(indice) if 0 <= indice < len(self._itens) else None

    def limpar(self) -> None:
        """Esvazia totalmente o carrinho de compras."""
        self._itens.clear()


class FormaPagamento(ABC):
    """Classe base abstrata para modalidades de pagamento."""

    def __init__(self, nome: str, desc: float) -> None:
        """Configura a forma de pagamento e sua porcentagem de desconto."""
        self._nome, self._desc = nome, desc

    @property
    def nome(self) -> str:
        """Retorna o nome da modalidade."""
        return self._nome

    @property
    def desc(self) -> float:
        """Retorna o percentual de desconto."""
        return self._desc

    @abstractmethod
    def calcular_total(self, bruto: float) -> float:
        """Calcula o valor final após aplicar o desconto."""
        pass


class PagamentoPixDinheiro(FormaPagamento):
    """Modalidade Pix ou Dinheiro com 10% de desconto."""

    def __init__(self) -> None:
        """Define Pix/Dinheiro com 10% de desconto."""
        super().__init__("Pix / Dinheiro à Vista", 10.0)

    def calcular_total(self, bruto: float) -> float:
        """Aplica 10% de abatimento no valor bruto."""
        return bruto * 0.90


class PagamentoDebito(FormaPagamento):
    """Modalidade Cartão de Débito com 5% de desconto."""

    def __init__(self) -> None:
        """Define Cartão de Débito com 5% de desconto."""
        super().__init__("Cartão de Débito", 5.0)

    def calcular_total(self, bruto: float) -> float:
        """Aplica 5% de abatimento no valor bruto."""
        return bruto * 0.95


class PagamentoCredito(FormaPagamento):
    """Modalidade Cartão de Crédito sem desconto."""

    def __init__(self) -> None:
        """Define Cartão de Crédito sem desconto."""
        super().__init__("Cartão de Crédito à Vista", 0.0)

    def calcular_total(self, bruto: float) -> float:
        """Retorna o valor bruto integral."""
        return bruto


class PagamentoGerencial(FormaPagamento):
    """Modalidade com desconto personalizado autorizado pela gerência."""

    def __init__(self, desc: float) -> None:
        """Configura a modalidade com taxa customizada."""
        super().__init__(f"Desconto Gerencial ({desc:.1f}%)", desc)

    def calcular_total(self, bruto: float) -> float:
        """Aplica a taxa manual de desconto sobre o valor bruto."""
        return bruto * (1.0 - (self._desc / 100.0))


class Venda:
    """Consolida os dados da transação financeira e troco."""

    def __init__(self, carrinho: CarrinhoCompras, forma: FormaPagamento, recebido: float = 0.0) -> None:
        """Inicializa e calcula o fechamento da venda."""
        self._carrinho, self._forma = carrinho, forma
        self._bruto = carrinho.total_bruto
        self._liquido = forma.calcular_total(self._bruto)
        self._recebido = recebido

    @property
    def bruto(self) -> float:
        """Retorna o valor total bruto."""
        return self._bruto

    @property
    def liquido(self) -> float:
        """Retorna o valor total com desconto."""
        return self._liquido

    @property
    def desconto(self) -> float:
        """Retorna o valor economizado pelo cliente."""
        return self._bruto - self._liquido

    @property
    def forma(self) -> FormaPagamento:
        """Retorna a forma de pagamento selecionada."""
        return self._forma

    @property
    def troco(self) -> float:
        """Calcula o valor do troco a ser devolvido."""
        return max(0.0, self._recebido - self._liquido)


class SistemaPDV:
    """Orquestra a interface do terminal e os fluxos operacionais do caixa."""

    def __init__(self) -> None:
        """Inicializa o ambiente do console e o carrinho do PDV."""
        self._console = Console()
        self._carrinho = CarrinhoCompras()

    def _cabecalho(self) -> None:
        """Exibe o painel superior fixo no terminal."""
        self._console.clear()
        self._console.print(Panel("[bold white]SISTEMA DE CAIXA PDV[/bold white]\n[dim]Módulo Operacional de Vendas[/dim]", expand=False, border_style="cyan"))

    def _mostrar_carrinho(self) -> None:
        """Exibe a tabela visual contendo todos os itens atuais."""
        if not self._carrinho.itens:
            self._console.print("\n[dim yellow]Carrinho vazio.[/dim yellow]\n")
            return

        t = Table(title="[bold cyan]CARRINHO DE COMPRAS[/bold cyan]", show_header=True)
        t.add_column("Item", justify="center", style="dim white")
        t.add_column("Descrição", style="bold white")
        t.add_column("Qtd", justify="center", style="yellow")
        t.add_column("Preço Unit.", justify="right", style="cyan")
        t.add_column("Subtotal", justify="right", style="bold green")

        for i, item in enumerate(self._carrinho.itens, start=1):
            t.add_row(str(i), item.nome, str(item.qtd), f"R$ {item.preco:.2f}", f"R$ {item.subtotal:.2f}")

        self._console.print(t)
        self._console.print(f"[bold white]Itens: [cyan]{len(self._carrinho.itens)}[/cyan] | Total Bruto: [bold green]R$ {self._carrinho.total_bruto:.2f}[/bold green][/bold white]\n")

    def _modo_rapido_adicionar(self) -> None:
        """Executa o loop contínuo e rápido de registro de produtos."""
        self._console.print("\n[bold cyan]ENTRADA RÁPIDA DE PRODUTOS[/bold cyan] [dim](Pressione Enter no nome para finalizar)[/dim]\n")
        while True:
            try:
                nome = Prompt.ask("Descrição do Produto").strip()
                if not nome:
                    break
                preco = FloatPrompt.ask(f"Preço de '{nome}' R$")
                if preco <= 0:
                    self._console.print("[bold red]Erro: O preço deve ser maior que zero.[/bold red]")
                    continue
                qtd = IntPrompt.ask("Quantidade", default=1)
                if qtd <= 0:
                    self._console.print("[bold red]Erro: A quantidade deve ser de pelo menos 1 unidade.[/bold red]")
                    continue

                self._carrinho.adicionar(ItemVenda(nome, preco, qtd))
                self._console.print(f"[bold green]Adicionado: {qtd}x {nome} (R$ {preco * qtd:.2f})[/bold green]\n")
            except Exception:
                self._console.print("[bold red]Entrada inválida. Tente novamente.[/bold red]")

    def _remover_item(self) -> None:
        """Gerencia a exclusão de um produto do carrinho."""
        if not self._carrinho.itens:
            self._console.print("[bold red]Não há produtos para remover.[/bold red]")
            Prompt.ask("\nPressione Enter para continuar...")
            return
        self._mostrar_carrinho()
        try:
            idx = IntPrompt.ask("Número do item a remover (0 para cancelar)")
            if idx > 0 and (item := self._carrinho.remover(idx - 1)):
                self._console.print(f"[bold yellow]Item '{item.nome}' removido do carrinho.[/bold yellow]")
            elif idx != 0:
                self._console.print("[bold red]Número de item inválido.[/bold red]")
        except Exception:
            self._console.print("[bold red]Entrada inválida.[/bold red]")
        Prompt.ask("\nPressione Enter para continuar...")

    def _selecionar_pagamento(self) -> Optional[FormaPagamento]:
        """Exibe as opções de pagamento no fechamento e retorna a regra escolhida."""
        t = Table(title="[bold cyan]FORMAS DE PAGAMENTO[/bold cyan]")
        t.add_column("Opção", justify="center", style="cyan")
        t.add_column("Modalidade", style="white")
        t.add_column("Desconto", justify="right", style="green")
        t.add_row("1", "Pix / Dinheiro à Vista", "10%")
        t.add_row("2", "Cartão de Débito", "5%")
        t.add_row("3", "Cartão de Crédito à Vista", "0%")
        t.add_row("4", "Desconto Gerencial", "Manual")
        self._console.print(t)

        while True:
            try:
                op = IntPrompt.ask("Selecione a opção de pagamento (1-4)")
                if op == 1: return PagamentoPixDinheiro()
                if op == 2: return PagamentoDebito()
                if op == 3: return PagamentoCredito()
                if op == 4:
                    desc = FloatPrompt.ask("Percentual de Desconto Autorizado (%)")
                    if 0 <= desc <= 100: return PagamentoGerencial(desc)
                    self._console.print("[bold red]O desconto deve estar entre 0% e 100%.[/bold red]")
                else:
                    self._console.print("[bold red]Opção inválida. Escolha entre 1 e 4.[/bold red]")
            except Exception:
                self._console.print("[bold red]Entrada inválida.[/bold red]")

    def _checkout(self) -> None:
        """Realiza o procedimento de fechamento da compra e emissão do recibo."""
        if not self._carrinho.itens:
            self._console.print("[bold red]Não é possível finalizar com o carrinho vazio.[/bold red]")
            Prompt.ask("\nPressione Enter para continuar...")
            return

        self._cabecalho()
        self._mostrar_carrinho()
        forma = self._selecionar_pagamento()
        if not forma: return

        total_liquido = forma.calcular_total(self._carrinho.total_bruto)
        recebido = 0.0

        if isinstance(forma, PagamentoPixDinheiro):
            while True:
                try:
                    self._console.print(f"\n[bold cyan]Total a Pagar: R$ {total_liquido:.2f}[/bold cyan]")
                    recebido = FloatPrompt.ask("Valor Pago pelo Cliente R$", default=total_liquido)
                    if recebido >= total_liquido: break
                    self._console.print("[bold red]O valor pago é menor que o total da compra.[/bold red]")
                except Exception:
                    self._console.print("[bold red]Valor inválido.[/bold red]")

        venda = Venda(self._carrinho, forma, recebido)
        self._exibir_recibo(venda)
        self._carrinho.limpar()
        Prompt.ask("\n[bold green]Venda finalizada com sucesso.[/bold green] Pressione Enter para continuar...")

    def _exibir_recibo(self, v: Venda) -> None:
        """Exibe o cupom fiscal formatado com resumo de produtos e pagamento."""
        self._cabecalho()
        t = Table(title="[bold green]COMPROVANTE DE VENDA[/bold green]")
        t.add_column("Descrição", style="white")
        t.add_column("Qtd x Unit.", justify="center", style="dim white")
        t.add_column("Subtotal", justify="right", style="yellow")

        for i in self._carrinho.itens:
            t.add_row(i.nome, f"{i.qtd}x R$ {i.preco:.2f}", f"R$ {i.subtotal:.2f}")
        self._console.print(t)

        res = Table(show_header=False, box=None)
        res.add_row("Subtotal Bruto:", f"R$ {v.bruto:.2f}")
        res.add_row("Forma de Pagamento:", v.forma.nome)
        res.add_row("Desconto Aplicado:", f"- R$ {v.desconto:.2f}")
        res.add_row("[bold cyan]TOTAL LÍQUIDO:[/bold cyan]", f"[bold green]R$ {v.liquido:.2f}[/bold green]")
        if v.troco > 0:
            res.add_row("[bold yellow]Troco:[/bold yellow]", f"[bold yellow]R$ {v.troco:.2f}[/bold yellow]")

        self._console.print(Panel(res, title="[bold white]RESUMO FINANCEIRO[/bold white]", border_style="green"))

    def executar(self) -> None:
        """Inicia e mantém o menu principal interativo do PDV."""
        try:
            while True:
                self._cabecalho()
                self._mostrar_carrinho()
                self._console.print("[bold white]MENU OPERACIONAL[/bold white]")
                self._console.print(" [bold cyan]1.[/bold cyan] Registrar Produtos (Entrada Rápida)")
                self._console.print(" [bold cyan]2.[/bold cyan] Remover Produto do Carrinho")
                self._console.print(" [bold cyan]3.[/bold cyan] Finalizar Venda / Pagamento")
                self._console.print(" [bold cyan]4.[/bold cyan] Cancelar Venda Atual")
                self._console.print(" [bold cyan]5.[/bold cyan] Encerrar Sistema")

                try:
                    op = IntPrompt.ask("\nSelecione uma opção", choices=["1", "2", "3", "4", "5"])
                    if op == 1: self._modo_rapido_adicionar()
                    elif op == 2: self._remover_item()
                    elif op == 3: self._checkout()
                    elif op == 4:
                        if self._carrinho.itens and Prompt.ask("Confirmar cancelamento da venda?", choices=["s", "n"], default="n").lower() == "s":
                            self._carrinho.limpar()
                    elif op == 5:
                        self._console.print("\n[bold green]Sistema encerrado.[/bold green]\n")
                        break
                except Exception:
                    self._console.print("[bold red]Opção inválida.[/bold red]")
                    Prompt.ask("\nPressione Enter para continuar...")

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]Operação interrompida pelo usuário. Encerrando sistema...[/bold yellow]\n")
        except Exception as e:
            self._console.print(f"\n[bold red]Erro de execução: {e}[/bold red]\n")


if __name__ == "__main__":
    app = SistemaPDV()
    app.executar()