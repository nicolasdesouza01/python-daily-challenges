from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()
turma = []

class Aluno:
    def __init__(self, nome, n1, n2):
        self.nome = nome
        self.n1 = n1
        self.n2 = n2

    @property
    def media(self):
        return (self.n1 + self.n2) / 2

    def retornar_detalhes(self):
        """Cria o painel individual para a consulta"""
        info = f"Nota 1: [bold]{self.n1}[/]\nNota 2: [bold]{self.n2}[/]\nMédia: [cyan]{self.media:.1f}[/]"
        return Panel(info, title=f"[green]{self.nome}[/]", expand=False)
    
while True:
    nome = Prompt.ask("Nome do Aluno")
    n1 = float(Prompt.ask(f"Nota 1 de {nome}"))
    n2 = float(Prompt.ask(f"Nota 2 de {nome}"))
    
    turma.append(Aluno(nome, n1, n2))
    
    while True:
        continuar = Prompt.ask("Quer continuar? [bold cyan](s/n)[/]").lower()
        if continuar in ['s', 'n']:
            break
        console.print("[bold red]Opção inválida! Digite 's' para sim ou 'n' para não.[/]")   
    if continuar == "n":
        break

tabela = Table(title="BOLETIM FINAL", header_style="bold magenta")
tabela.add_column("ID", justify="center")
tabela.add_column("NOME")
tabela.add_column("MÉDIA", justify="right")

for i, aluno in enumerate(turma):
    tabela.add_row(str(i), aluno.nome, f"{aluno.media:.1f}")

console.print(tabela)

while True:
    opc = int(Prompt.ask("Mostrar notas de qual aluno? (999 interrompe)"))
    if opc == 999:
        break
    if opc < len(turma):
        console.print(turma[opc].retornar_detalhes())
    else:
        console.print("[red]ID Inválido![/]")

console.print("[bold yellow]PROGRAMA FINALIZADO. ATÉ MAIS![/]")
    
