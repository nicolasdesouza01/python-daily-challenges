import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

console = Console()

header = Panel("[bold cyan]CALCULADOR DE PINTURA V1.3[/bold cyan]", border_style="blue")
console.print(header, justify="center")

def obter_medida(mensagem):
    while True:
        entrada = console.input(f"[bold white]{mensagem}: [/bold white]")
        
        try:
            valor_convertido = float(entrada.replace(',', '.'))
            return valor_convertido
            
        except ValueError:
            console.print(Panel("[bold red]ERRO DE ENTRADA[/bold red]\nUse apenas números e vírgulas/pontos.", border_style="red", expand=False))

largura = obter_medida("Largura da parede (m)")
altura = obter_medida("Altura da parede (m)")

area = largura * altura
tinta = area / 2

with Progress() as progress:
    tarefa = progress.add_task("[yellow]Calculando...", total=100)
    while not progress.finished:
        progress.update(tarefa, advance=50)
        time.sleep(0.3)

area_formatada = f"{area:.2f}".replace('.', ',')
tinta_formatada = f"{tinta:.2f}".replace('.', ',')

tabela = Table(title="[bold magenta]Resumo do Cálculo[/bold magenta]", border_style="green")
tabela.add_column("Item", style="cyan")
tabela.add_column("Resultado", justify="right", style="bold yellow")

tabela.add_row("Área Total", f"{area_formatada} m²")
tabela.add_row("Tinta Necessária", f"{tinta_formatada} L")

console.print("\n")
console.print(tabela, justify="center")

console.print(Panel("[bold green]Processamento concluído com sucesso![/bold green]", expand=False), justify="center")