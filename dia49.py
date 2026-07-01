import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class SistemaCheckout:

    def __init__(self):
        self._preco_compras = 0.0
        self._opcao_escolhida = 0
        self._total_final = 0.0
        self._quantidade_parcelas = 0
        self._valor_parcela = 0.0

    def executar(self):
        console.clear()
        console.print(
            Panel.fit(
                " LOJAS GUANABARA ",
                style="bold white on blue",
                subtitle="Sistema de Checkout",
            )
        )

        self._coletar_preco()
        self._exibir_opcoes_pagamento()
        self._coletar_opcao_pagamento()

        if self._processar_fluxo_pagamento():
            self._exibir_recibo_final()

    def _coletar_preco(self):
        while True:
            try:
                entrada = console.input(
                    "\n[bold green]:money_bag: Preço das compras: R$ [/]"
                )
                self._preco_compras = float(entrada)

                if self._preco_compras <= 0:
                    console.print(
                        "[bold red]:warning: O valor das compras deve ser maior que zero.[/]"
                    )
                    continue

                break
            except ValueError:
                console.print(
                    "[bold red]:warning: Entrada inválida. Por favor, digite um valor numérico válido.[/]"
                )

    def _exibir_opcoes_pagamento(self):
        tabela = Table(title="\nFORMAS DE PAGAMENTO", title_style="bold cyan")
        tabela.add_column("Opção", justify="center", style="bold magenta")
        tabela.add_column("Descrição do Método", style="white")

        tabela.add_row(
            "1", "À vista / Dinheiro / Cheque [green](10% de desconto)[/]"
        )
        tabela.add_row("2", "À vista no cartão [green](5% de desconto)[/]")
        tabela.add_row("3", "2x no cartão [yellow](Preço normal da etiqueta)[/]")
        tabela.add_row("4", "3x ou mais no cartão [red](20% de juros)[/]")

        console.print(tabela)

    def _coletar_opcao_pagamento(self):
        while True:
            try:
                entrada = console.input(
                    "\n[bold green]:credit_card: Qual a opção desejada (1 a 4)? [/]"
                )
                self._opcao_escolhida = int(entrada)

                if 1 <= self._opcao_escolhida <= 4:
                    break

                console.print(
                    "[bold red]:warning: Opção incorreta. Escolha apenas números entre 1 e 4.[/]"
                )
            except ValueError:
                console.print(
                    "[bold red]:warning: Entrada inválida. Digite um número inteiro de 1 a 4.[/]"
                )

    def _processar_fluxo_pagamento(self):
        with console.status(
            "[bold yellow]:hourglass_flowing_sand: Calculando condições...[/]",
            spinner="dots",
        ):
            time.sleep(1.2)

        if self._opcao_escolhida == 1:
            self._total_final = self._preco_compras - (
                self._preco_compras * 10 / 100
            )

        elif self._opcao_escolhida == 2:
            self._total_final = self._preco_compras - (
                self._preco_compras * 5 / 100
            )

        elif self._opcao_escolhida == 3:
            self._total_final = self._preco_compras
            self._valor_parcela = self._total_final / 2
            console.print(
                f"\n[bold blue]:white_check_mark: Compra autorizada e parcelada em 2x de R${self._valor_parcela:.2f} sem juros.[/]"
            )

        elif self._opcao_escolhida == 4:
            self._total_final = self._preco_compras + (
                self._preco_compras * 20 / 100
            )

            while True:
                try:
                    entrada = console.input(
                        "\n[bold green]:stopwatch: Quantas parcelas deseja? [/]"
                    )
                    self._quantidade_parcelas = int(entrada)

                    if self._quantidade_parcelas >= 3:
                        break

                    console.print(
                        "[bold red]:warning: Quantidade inválida para esta opção. O mínimo são 3 parcelas.[/]"
                    )
                except ValueError:
                    console.print(
                        "[bold red]:warning: Entrada inválida. Digite um número inteiro para a quantidade de parcelas.[/]"
                    )

            self._valor_parcela = self._total_final / self._quantidade_parcelas
            console.print(
                f"\n[bold red]:exclamation: Compra parcelada em {self._quantidade_parcelas}x de R${self._valor_parcela:.2f} COM JUROS.[/]"
            )

        return True

    def _exibir_recibo_final(self):
        conteudo_recibo = (
            f"Valor Inicial das Compras: [cyan]R${self._preco_compras:.2f}[/]\n"
            f"Total a pagar no método escolhido: [bold yellow]R${self._total_final:.2f}[/]"
        )

        painel_resultado = Panel(
            conteudo_recibo,
            title="[bold green]:wrapped_gift: RESUMO DO PEDIDO[/]",
            expand=False,
            border_style="green",
        )

        console.print("\n")
        console.print(painel_resultado)
        console.print(
            "\n[bold magenta]:sparkles: Operação finalizada com sucesso! Volte sempre. :sparkles:\n"
        )


if __name__ == "__main__":
    checkout = SistemaCheckout()
    checkout.executar()