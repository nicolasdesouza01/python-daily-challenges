import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

class ComparadorValores:

    def __init__(self):
        self._primeiro_numero = 0
        self._segundo_numero = 0

    def configurar_valores(self, valor1: int, valor2: int):
        self._primeiro_numero = valor1
        self._segundo_numero = valor2

    def analisar_maior(self) -> tuple[str, str, str]:
        if self._primeiro_numero > self._segundo_numero:
            return (
                "primeiro",
                f"O PRIMEIRO valor ({self._primeiro_numero}) é maior.",
                "green"
            )
        
        elif self._segundo_numero > self._primeiro_numero:
            return (
                "segundo",
                f"O SEGUNDO valor ({self._segundo_numero}) é maior.",
                "blue"
            )
        
        else:
            return (
                "iguais",
                "Os dois valores são IGUAIS.",
                "yellow"
            )


def iniciar_sistema():
    console = Console()

    console.print()
    console.print(
        Panel.fit(
            " [bold cyan]Analisador de Grandezas Numéricas[/bold cyan] ",
            border_style="magenta",
            subtitle="[bold white]POO & Rich[/bold white]"
        )
    )
    console.print()

    while True:
        try:
            entrada_1 = Prompt.ask("[bold white]Digite o primeiro número inteiro[/bold white]")
            n1 = int(entrada_1)
            break
        except ValueError:
            console.print()
            console.print("[bold red]:warning: Erro: Tipo de dado inválido. Digite apenas números inteiros.[/bold red]")
            console.print()

    while True:
        try:
            entrada_2 = Prompt.ask("[bold white]Digite o segundo número inteiro[/bold white]")
            n2 = int(entrada_2)
            break
        except ValueError:
            console.print()
            console.print("[bold red]:warning: Erro: Tipo de dado inválido. Digite apenas números inteiros.[/bold red]")
            console.print()

    analisador = ComparadorValores()
    analisador.configurar_valores(n1, n2)

    console.print()
    with console.status("[bold magenta]Processando e comparando os dados...[/bold magenta]", spinner="aesthetic"):
        time.sleep(1.8)
    console.print()

    status, mensagem, cor_painel = analisador.analisador_maior()

    if status == "iguais":
        icone = ":balance_scale:"
    else:
        icone = ":arrow_up:"

    console.print(
        Panel(
            f"[bold {cor_painel}]{mensagem}[/bold {cor_painel}] {icone}",
            title="[bold white]Resultado da Verificação[/bold white]",
            border_style=cor_painel,
            expand=False
        )
    )
    console.print()


if __name__ == "__main__":
    iniciar_sistema()
