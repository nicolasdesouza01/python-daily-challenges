import time
from rich.console import Console
from rich.panel import Panel

console = Console()


class VerificadorNome:

    def __init__(self, nome):
        """
        Construtor para inicializar o nome de forma encapsulada.
        """
        self._nome = nome

    def verificar_e_exibir(self):
        """
        Método que valida a presença do sobrenome Silva e exibe o resultado.
        """
        with console.status(
            "[bold cyan]Analisando o sobrenome... :hourglass_flowing_sand:",
            spinner="dots",
        ):
            time.sleep(1.2)

        nome_analise = self._nome.strip().lower()

        console.print()

        if "silva" in nome_analise:
            console.print(
                Panel(
                    "[bold green]Percebi que seu nome tem Silva, então você é um Silva! :white_check_mark:[/bold green]",
                    border_style="green",
                    title="[bold green]Resultado da Análise[/bold green]",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold yellow]Parece que seu nome não tem Silva, então você não é um Silva. :x:[/bold yellow]",
                    border_style="yellow",
                    title="[bold yellow]Resultado da Análise[/bold yellow]",
                )
            )

        console.print()


# --- Fluxo Principal (Main) ---
if __name__ == "__main__":
    console.print()
    console.print(
        Panel.fit(
            "[bold deep_sky_blue1]VERIFICADOR DE SOBRENOME :mag:[/bold deep_sky_blue1]",
            border_style="deep_sky_blue1",
        )
    )
    console.print()

    while True:
        try:
            nome_input = console.input(
                "[bold yellow]Digite seu nome completo: [/bold yellow]"
            )

            if not nome_input.strip():
                raise ValueError("O nome não pode ser enviado em branco. :thinking_face:")

            validador = VerificadorNome(nome_input)

            validador.verificar_e_exibir()

        except ValueError as erro_vazio:
            console.print()
            console.print(
                Panel(
                    f"[bold red]Erro: {erro_vazio}[/bold red]",
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
                console.input("[bold purple]Deseja continuar? [S/N]: [/bold purple]")
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
                    "[bold green]Encerrando o programa. Até mais! :wave:[/bold green]",
                    border_style="green",
                )
            )
            console.print()

            for i in range(3, 0, -1):
                segundo_texto = "segundo" if i == 1 else "segundos"
                console.print(
                    f"[bold orange3]Saindo em {i} {segundo_texto}... :hourglass:[/bold orange3]"
                )
                time.sleep(1)

            console.print()
            console.print(
                "[bold white]Programa encerrado! :checkered_flag:[/bold white]"
            )
            console.print()
            break

        console.print()
        console.print(
            "[bold cyan]Prepare-se para digitar outro nome! :arrow_down:[/bold cyan]"
        )
        console.print()
