from rich.console import Console
from rich.panel import Panel

console = Console()

def area(larg, comp):
    total = larg * comp
    console.print(f"\nA área do terreno [yellow]{larg}m[/yellow] x [yellow]{comp}m[/yellow] é de [bold cyan]{total:.2f}m²[/bold cyan].")

def leia_float(msg):
    while True:
        try:
            n = float(input(msg))
            return n
        except:
            console.print("[bold red]Entrada inválida![/bold red] Digite um número real.")

console.print(Panel.fit("SISTEMA DE TERRENOS", style="bold magenta"))

l = leia_float("Largura (m): ")
c = leia_float("Comprimento (m): ")

area(l, c)