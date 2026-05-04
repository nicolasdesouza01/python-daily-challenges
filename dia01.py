from rich.console import Console
from rich.panel import Panel

console = Console()

console.print(Panel.fit("[bold cyan]Desafio 038: Comparador de Números[/bold cyan]", border_style="magenta"))

n1 = int(input('Primeiro número: '))
n2 = int(input('Segundo número: '))

if n1 > n2:
    console.print(f"[bold green]O PRIMEIRO valor ({n1}) é maior.[/bold green] :arrow_up:")
elif n2 > n1:
    console.print(f"[bold blue]O SEGUNDO valor ({n2}) é maior.[/bold blue] :arrow_up:")
else:
    console.print("[bold yellow]Os dois são IGUAIS.[/bold yellow] :balance_scale:")