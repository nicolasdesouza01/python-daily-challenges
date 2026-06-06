import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Tabuada:

    def __init__(self, numero):
        """
        Construtor: Aqui inicializamos o 'estado' do nosso objeto.
        """
        self._numero = numero

    def calcular_e_exibir(self):
        """
        Método que encapsula a lógica de exibição.
        """
        with console.status(
            "[bold cyan]Gerando os dados da tabuada... :hourglass_flowing_sand:",
            spinner="dots",
        ):
            time.sleep(1.2)

        tabela = Table(
            title=f"[bold magenta]Tabuada do {self._numero}[/bold magenta]",
            show_header=True,
            header_style="bold violet",
            expand=True,
        )

        tabela.add_column("Operação", justify="center", style="cyan")
        tabela.add_column("Resultado", justify="center", style="bold green")

        for i in range(1, 11):
            resultado = self._numero * i
            tabela.add_row(f"{self._numero} x {i:2}", f"{resultado}")

        console.print()
        console.print(
            Panel(
                tabela,
                border_style="magenta",
                title="[bold white]Visualização Efetuada :sparkles:[/bold white]",
            )
        )
        console.print()


# --- Fluxo Principal (Main) ---
if __name__ == "__main__":
    console.print()
    console.print(
        Panel.fit(
            "[bold deep_sky_blue1]SISTEMA DE TABUADAS :rocket:[/bold deep_sky_blue1]",
            border_style="deep_sky_blue1",
        )
    )
    console.print()

    while True:
        try:
            num_input = console.input(
                "[bold yellow]Digite um número para ver sua tabuada: [/bold yellow]"
            )

            num = int(num_input)

            minha_tabuada = Tabuada(num)

            minha_tabuada.calcular_e_exibir()

        except ValueError:
            console.print()
            console.print(
                Panel(
                    "[bold red]Erro: Por favor, digite um número inteiro válido. :warning:[/bold red]",
                    border_style="red",
                    title="[bold red]Entrada Inválida[/bold red]",
                )
            )
            console.print()

        except Exception as erro:
            console.print()
            console.print(
                Panel(
                    f"[bold red]Ocorreu um erro inesperado: {erro} :warning:[/bold red]",
                    border_style="red",
                )
            )
            console.print()

        while True:
            resposta = (
                console.input("[bold purple]Quer continuar? [S/N]: [/bold purple]")
                .strip()
                .upper()
            )

            if resposta in ("S", "N"):
                break

            console.print(
                "[bold red]Resposta inválida! Digite apenas S ou N. :thinking_face:[/bold red]"
            )

        if resposta == "N":
            console.print()
            console.print(
                Panel.fit(
                    "[bold green]Obrigado por usar o sistema! Até logo! :wave:[/bold green]",
                    border_style="green",
                )
            )
            console.print()
            break
