from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.progress import track
from time import sleep


class Moeda:

    def __init__(self, preco=0, moeda='R$'):
        self._preco = preco
        self._moeda_simbolo = moeda

    def formatar(self, valor=None):
        v = valor if valor is not None else self._preco
        return f"{self._moeda_simbolo} {v:>8.2f}".replace('.', ',')

    def aumentar(self, taxa=0):
        res = self._preco + (self._preco * taxa / 100)
        return self.formatar(res)

    def disminuir(self, taxa=0):
        res = self._preco - (self._preco * taxa / 100)
        return self.formatar(res)

    def dobro(self):
        res = self._preco * 2
        return self.formatar(res)

    def metade(self):
        res = self._preco / 2
        return self.formatar(res)


console = Console()

print()
print(Panel.fit(
    "[bold white]SISTEMA DE GESTÃO FINANCEIRA[/bold white]",
    subtitle="v1.0.8",
    border_style="blue"
))
print()

try:
    entrada_usuario = console.input("[bold cyan]Digite o valor base (R$): [/bold cyan]")
    
    entrada_limpa = entrada_usuario.replace(',', '.')
    entrada = float(entrada_limpa)
    
    item = Moeda(entrada)

    print()
    for _ in track(range(10), description="[cyan]Processando cálculos..."):
        sleep(0.1)
    print()

    tabela = Table(title="RESULTADOS", title_style="bold white", border_style="blue")
    tabela.add_column("Descrição", style="cyan")
    tabela.add_column("Valor Formatado", justify="right", style="yellow")

    tabela.add_row("Valor Original", item.formatar())
    tabela.add_row("Metade do Valor", item.metade())
    tabela.add_row("Dobro do Valor", item.dobro())
    tabela.add_row("Aumento (10%)", item.aumentar(10))
    tabela.add_row("Redução (13%)", item.disminuir(13))

    console.print(tabela)
    
    sleep(0.5)
    print()
    print(Panel("[bold green]:white_check_mark: Processamento concluído com sucesso![/bold green]", border_style="green"))
    print()

except ValueError:
    print()
    print(Panel("[bold red]:x: ERRO: Entrada inválida. Utilize apenas números.[/bold red]", border_style="red"))
    print()

except KeyboardInterrupt:
    print()
    print(Panel("[bold yellow]:warning: Operação interrompida pelo usuário.[/bold yellow]", border_style="yellow"))
    print()

