import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class GeradorFibonacci:

    def __init__(self):
        self._console = Console()
        self._termo_inicial = 0
        self._termo_segundo = 1


    def _calcular_sequencia(self, total_termos):
        if total_termos <= 0:
            return []

        if total_termos == 1:
            return [self._termo_inicial]

        sequencia = [self._termo_inicial, self._termo_segundo]
        t1 = self._termo_inicial
        t2 = self._termo_segundo

        for _ in range(3, total_termos + 1):
            t3 = t1 + t2
            sequencia.append(t3)
            t1, t2 = t2, t3

        return sequencia


    def _exibir_titulo(self):
        self._console.clear()

        titulo_texto = "[bold cyan]:sparkles: SEQUÊNCIA DE FIBONACCI :sparkles:[/bold cyan]\n[dim]Insira a quantidade de termos que deseja visualizar[/dim]"

        painel_titulo = Panel(
            titulo_texto,
            title="[bold magenta]Fibonacci System[/bold magenta]",
            border_style="cyan",
            expand=False
        )

        self._console.print(painel_titulo)
        self._console.print("")


    def iniciar(self):
        while True:
            self._exibir_titulo()

            entrada = Prompt.ask("[bold yellow]Quantos termos você quer mostrar? (ou digite 'PARAR' para sair)[/bold yellow]")

            if entrada.strip().upper() == "PARAR":
                self._console.print("")
                self._console.print(Panel("[bold green]Programa encerrado com sucesso. Até logo![/bold green]", border_style="green"))
                break

            try:
                quantidade = int(entrada)

                if quantidade <= 0:
                    self._console.print("")
                    self._console.print("[bold red]:warning: Erro: Por favor, digite um número inteiro maior que 0.[/bold red]")
                    time.sleep(2)
                    continue

            except ValueError:
                self._console.print("")
                self._console.print("[bold red]:warning: Erro: Entrada inválida! Digite um número inteiro ou 'PARAR'.[/bold red]")
                time.sleep(2)
                continue

            self._console.print("")

            with self._console.status("[bold green]Calculando termos... :hourglass_flowing_sand:[/bold green]", spinner="dots"):
                termos = self._calcular_sequencia(quantidade)
                time.sleep(1.5)

            self._console.print("")

            tabela_resultados = Table(title="[bold magenta]:chart_increasing: Termos Gerados[/bold magenta]", show_header=True, header_style="bold magenta")
            tabela_resultados.add_column("Posição", justify="center", style="cyan")
            tabela_resultados.add_column("Valor", justify="center", style="green")

            for indice, valor in enumerate(termos, start=1):
                tabela_resultados.add_row(f"{indice}º", str(valor))

            self._console.print(tabela_resultados)

            self._console.print("")

            sequencia_visual = " -> ".join(map(str, termos)) + " -> [bold red]FIM[/bold red]"

            painel_resultado = Panel(
                sequencia_visual,
                title="[bold green] :white_check_mark: Sequência Linear[/bold green]",
                border_style="green",
                expand=False
            )

            self._console.print(painel_resultado)

            self._console.print("")

            Prompt.ask("[bold white]Pressione [Enter] para continuar...[/bold white]")


if __name__ == "__main__":
    gerador = GeradorFibonacci()
    gerador.iniciar()