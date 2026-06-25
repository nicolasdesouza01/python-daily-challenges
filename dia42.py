import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box


class SuperCalculadora:

    def __init__(self):
        self._console = Console()

    def _mostrar_loading(self, texto_status):
        with self._console.status(texto_status, spinner="aesthetic"):
            time.sleep(1.2)

    def _ler_inteiro(self, mensagem):
        while True:
            try:
                entrada = Prompt.ask(mensagem).strip()
                return int(entrada)
            except ValueError:
                self._console.print(
                    "[bold red]:warning: Entrada inválida! Por favor, insira apenas números inteiros nas perguntas.[/bold red]"
                )

    def _executar_adicao(self):
        try:
            n1 = self._ler_inteiro("Digite o primeiro número (parcela 1)")
            n2 = self._ler_inteiro("Digite o segundo número (parcela 2)")

            self._mostrar_loading("[yellow]Somando os valores...[/yellow]")

            resultado = n1 + n2

            tabela = Table(box=box.ROUNDED, show_lines=True)
            tabela.add_column("Operação Solicitada", justify="center", style="bold cyan")
            tabela.add_column("Resultado Final", justify="center", style="bold green")
            tabela.add_row(f"{n1} :heavy_plus_sign: {n2}", f"{resultado}")

            self._console.print(tabela)

        except Exception as erro:
            self._console.print(
                f"[bold red]:warning: Erro inesperado ao somar: {erro}[/bold red]"
            )

    def _executar_subtracao(self):
        try:
            n1 = self._ler_inteiro("Digite o número base (minuendo)")
            n2 = self._ler_inteiro("Digite o valor a ser subtraído (subtraendo)")

            self._mostrar_loading("[yellow]Subtraindo os valores...[/yellow]")

            resultado = n1 - n2

            tabela = Table(box=box.ROUNDED, show_lines=True)
            tabela.add_column("Operação Solicitada", justify="center", style="bold cyan")
            tabela.add_column("Resultado Final", justify="center", style="bold green")
            tabela.add_row(f"{n1} :heavy_minus_sign: {n2}", f"{resultado}")

            self._console.print(tabela)

        except Exception as erro:
            self._console.print(
                f"[bold red]:warning: Erro inesperado ao subtrair: {erro}[/bold red]"
            )

    def _executar_multiplicacao(self):
        try:
            num = self._ler_inteiro("Deseja gerar a tabuada de qual número?")
            inicio = self._ler_inteiro("Começar a multiplicação a partir de")
            fim = self._ler_inteiro("Terminar a multiplicação em")

            if inicio > fim:
                self._console.print(
                    Panel(
                        "[bold red]:warning: O valor inicial da tabuada não pode ser maior que o final![/bold red]"
                    )
                )
                return

            self._mostrar_loading("[yellow]Construindo a tabuada...[/yellow]")

            tabela = Table(
                title=f"Tabuada de Multiplicação: {num}", box=box.ROUNDED, show_lines=True
            )
            tabela.add_column("Expressão", justify="center", style="bold cyan")
            tabela.add_column("Resultado", justify="center", style="bold green")

            for c in range(inicio, fim + 1):
                tabela.add_row(f"{num} :heavy_multiplication_x: {c}", f"{num * c}")

            self._console.print(tabela)

        except Exception as erro:
            self._console.print(
                f"[bold red]:warning: Erro inesperado na multiplicação: {erro}[/bold red]"
            )

    def _executar_divisao(self):
        try:
            num = self._ler_inteiro("Deseja gerar a tabela de divisão para qual número?")
            inicio = self._ler_inteiro("Começar a divisão pelo divisor")
            fim = self._ler_inteiro("Terminar a divisão no divisor")

            if inicio > fim:
                self._console.print(
                    Panel(
                        "[bold red]:warning: O divisor inicial não pode ser maior que o final![/bold red]"
                    )
                )
                return

            self._mostrar_loading("[yellow]Construindo a tabela de divisão...[/yellow]")

            tabela = Table(
                title=f"Tabela de Divisão: {num}", box=box.ROUNDED, show_lines=True
            )
            tabela.add_column("Expressão", justify="center", style="bold cyan")
            tabela.add_column("Resultado", justify="center", style="bold green")

            for c in range(inicio, fim + 1):
                if c == 0:
                    tabela.add_row(
                        f"{num} :heavy_division_sign: {c}",
                        "[bold red]Erro: Divisão por 0[/bold red]",
                    )
                else:
                    tabela.add_row(
                        f"{num} :heavy_division_sign: {c}", f"{num / c:.2f}"
                    )

            self._console.print(tabela)

        except Exception as erro:
            self._console.print(
                f"[bold red]:warning: Erro inesperado na divisão: {erro}[/bold red]"
            )

    def iniciar(self):
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold blue]SISTEMA MATEMÁTICO INTERATIVO[/bold blue]",
                subtitle="Ambiente Profissional :rocket:",
            )
        )

        while True:
            try:
                self._console.print(
                    "\n[bold yellow]Selecione a Operação Desejada:[/bold yellow]"
                )
                self._console.print("1. Multiplicação (Formato Tabuada) :heavy_multiplication_x:")
                self._console.print("2. Adição (Cálculo Direto) :heavy_plus_sign:")
                self._console.print("3. Subtração (Cálculo Direto) :heavy_minus_sign:")
                self._console.print("4. Divisão (Formato Tabela) :heavy_division_sign:")
                self._console.print("5. Sair do Programa :door:")

                while True:
                    opcao = Prompt.ask("\nEscolha uma opção").strip()

                    if opcao in ["1", "2", "3", "4", "5"]:
                        break

                    self._console.print(
                        "[bold red]:warning: Opção inválida! Por favor, escolha um número de 1 a 5.[/bold red]"
                    )

                if opcao == "5":
                    self._mostrar_loading("[red]Fechando o sistema...[/red]")
                    self._console.print(
                        Panel(
                            "[bold green]Obrigado por usar o sistema! Até a próxima! :wave:[/bold green]"
                        )
                    )
                    break

                if opcao == "1":
                    self._executar_multiplicacao()
                elif opcao == "2":
                    self._executar_adicao()
                elif opcao == "3":
                    self._executar_subtracao()
                elif opcao == "4":
                    self._executar_divisao()

                while True:
                    recomecar = Prompt.ask("\nDeseja realizar outro cálculo? (s/n)").lower().strip()

                    if recomecar in ["s", "n"]:
                        break

                    self._console.print(
                        "[bold red]:warning: Resposta inválida! Digite apenas 's' para sim ou 'n' para não.[/bold red]"
                    )

                if recomecar == "n":
                    self._mostrar_loading("[red]Fechando o sistema...[/red]")
                    self._console.print(
                        Panel(
                            "[bold green]Obrigado por usar o sistema! Até a próxima! :wave:[/bold green]"
                        )
                    )
                    break

            except Exception as erro:
                self._console.print(
                    Panel(
                        f"[bold red]:warning: Ocorreu um erro inesperado no sistema: {erro}[/bold red]"
                    )
                )


if __name__ == "__main__":
    app = SuperCalculadora()
    app.iniciar()