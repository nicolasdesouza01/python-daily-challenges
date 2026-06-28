import time
from datetime import date
from rich.console import Console
from rich.panel import Panel

console = Console()


class Atleta:

    def __init__(self, ano_nascimento):
        self._ano_nascimento = ano_nascimento
        self._ano_atual = date.today().year
        self._idade = self._calcular_idade()

    def _calcular_idade(self):
        return self._ano_atual - self._ano_nascimento

    def obter_classificacao(self):
        if self._idade <= 9:
            return "MIRIM"
        elif self._idade <= 14:
            return "INFANTIL"
        elif self._idade <= 19:
            return "JUNIOR"
        elif self._idade <= 25:
            return "SÊNIOR"
        else:
            return "MASTER"

    @property
    def idade(self):
        return self._idade


def executar_sistema():
    console.clear()

    console.print(
        Panel.fit(
            " [bold blue]:running_shirt: SISTEMA DE CLASSIFICAÇÃO DE ATLETAS[/bold blue] ",
            border_style="blue",
        )
    )

    console.print()

    while True:
        try:
            entrada = input("Qual sua data de nascimento (Apenas números): ")
            ano_nascimento = int(entrada)

            ano_atual = date.today().year

            if ano_nascimento > ano_atual or ano_nascimento < 1900:
                raise ValueError

            break

        except ValueError:
            console.print()
            console.print(
                "[bold red]:warning: Erro: Por favor, insira um ano válido com 4 dígitos.[/bold red]"
            )
            console.print()

    console.print()

    with console.status(
        "[bold green]Processando dados do atleta...[/bold green]",
        spinner="dots",
    ):
        time.sleep(1.5)

    atleta = Atleta(ano_nascimento)
    idade = atleta.idade
    classificacao = atleta.obter_classificacao()

    resultado_texto = (
        f"[bold white]Idade do Atleta:[/bold white] [cyan]{idade} anos[/cyan]\n"
        f"[bold white]Classificação:[/bold white] [bold yellow]:trophy: {classificacao}[/bold yellow]"
    )

    console.print()

    console.print(
        Panel(
            resultado_texto,
            title="[bold green]:clipboard: ANÁLISE CONCLUÍDA[/bold green]",
            border_style="green",
            expand=False,
        )
    )

    console.print()


if __name__ == "__main__":
    executar_sistema()