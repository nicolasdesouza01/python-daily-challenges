import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()
turma = []


class Aluno:

    def __init__(self, nome, n1, n2):
        self._nome = nome
        self._n1 = n1
        self._n2 = n2

    @property
    def nome(self):
        return self._nome

    @property
    def n1(self):
        return self._n1

    @property
    def n2(self):
        return self._n2

    @property
    def media(self):
        return (self._n1 + self._n2) / 2

    def retornar_detalhes(self):
        """Cria o painel individual para a consulta"""
        info = f"Nota 1: [bold]{self._n1}[/]\nNota 2: [bold]{self._n2}[/]\nMédia: [cyan]{self.media:.1f}[/]"
        return Panel(info, title=f"[green]{self._nome}[/]", expand=False)


console.print(
    Panel.fit(
        "[bold magenta]:mortar_board: SISTEMA DE GESTÃO DE NOTAS :mortar_board:[/]",
        border_style="magenta",
    )
)

while True:
    nome = Prompt.ask("[bold white]Nome do Aluno[/]")

    while True:
        try:
            n1 = float(Prompt.ask(f"[bold white]Nota 1 de {nome}[/]"))
            if 0 <= n1 <= 10:
                break
            console.print(
                "[bold red]:warning: Erro: A nota deve estar entre 0 e 10![/]"
            )
        except ValueError:
            console.print(
                "[bold red]:warning: Erro: Digite um número válido para a nota![/]"
            )

    while True:
        try:
            n2 = float(Prompt.ask(f"[bold white]Nota 2 de {nome}[/]"))
            if 0 <= n2 <= 10:
                break
            console.print(
                "[bold red]:warning: Erro: A nota deve estar entre 0 e 10![/]"
            )
        except ValueError:
            console.print(
                "[bold red]:warning: Erro: Digite um número válido para a nota![/]"
            )

    with console.status(
        "[bold green]Salvando dados do aluno... :floppy_disk:[/]"
    ):
        time.sleep(1)

    turma.append(Aluno(nome, n1, n2))

    while True:
        continuar = Prompt.ask("Quer continuar? [bold cyan](s/n)[/]").lower()
        if continuar in ["s", "n"]:
            break
        console.print(
            "[bold red]:warning: Opção inválida! Digite 's' para sim ou 'n' para não.[/]"
        )

    if continuar == "n":
        break

with console.status("[bold magenta]Compilando boletim geral... :bar_chart:[/]"):
    time.sleep(1.5)

tabela = Table(title="BOLETIM FINAL", header_style="bold magenta")
tabela.add_column("ID", justify="center", style="cyan")
tabela.add_column("NOME", style="white")
tabela.add_column("MÉDIA", justify="right", style="green")

for i, aluno in enumerate(turma):
    tabela.add_row(str(i), aluno.nome, f"{aluno.media:.1f}")

console.print(tabela)

while True:
    try:
        entrada = Prompt.ask(
            "\n[bold white]Mostrar notas de qual aluno? (999 interrompe)[/]"
        )
        opc = int(entrada)

        if opc == 999:
            break

        if 0 <= opc < len(turma):
            with console.status(
                "[bold yellow]Buscando registros... :mag:[/]"
            ):
                time.sleep(0.8)
            console.print(turma[opc].retornar_detalhes())
        else:
            console.print(
                "[bold red]:warning: ID inválido! Aluno não encontrado.[/]"
            )

    except ValueError:
        console.print(
            "[bold red]:warning: Erro: Por favor, digite um número inteiro correspondente ao ID ou 999![/]"
        )

console.print("\n[bold yellow]:wave: PROGRAMA FINALIZADO. ATÉ MAIS![/]\n")
