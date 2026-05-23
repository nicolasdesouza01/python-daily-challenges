import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()


def fatorial(n, show=False):
    """
    Calcula o fatorial de um número.
    :param n: O número a ser calculado.
    :param show: (opcional) Se True, mostra o processo do cálculo.
    :return: O valor do fatorial de n.
    """
    
    f = 1
    
    processo = []
    
    for c in range(n, 0, -1):
        
        if show:
            processo.append(str(c))
            
        f *= c
        
    if show:
        console.print(f"[bold cyan]Processo:[/bold cyan] {' x '.join(processo)} = [green]{f}[/green]")
        
    return f


try:
    
    console.print(Panel("[bold yellow]Calculadora de Fatorial[/bold yellow]", expand=False))
    
    num_str = console.input("[bold blue]Digite um número para o fatorial:[/bold blue] ")
    
    num = int(num_str)
    
    show_str = console.input("[bold blue]Deseja mostrar o cálculo? (S/N):[/bold blue] ").strip().upper()
    
    mostrar = True if show_str == 'S' else False
    
    
    with console.status("[bold green]Calculando...[/bold green]", spinner="dots"):
        
        time.sleep(1.5)
        
    
    resultado = fatorial(num, show=mostrar)
    
    
    tabela = Table(title="Resultado Final")
    
    tabela.add_column("Número", style="cyan")
    
    tabela.add_column("Fatorial", style="green")
    
    tabela.add_row(str(num), str(resultado))
    
    console.print(tabela)

except ValueError:
    
    console.print("[bold red]Erro:[/bold red] Por favor, digite apenas números inteiros válidos.")

except Exception as e:
    
    console.print(f"[bold red]Ocorreu um erro inesperado:[/bold red] {e}")

console.print("\n[bold magenta]:thumbs_up: Programa finalizado![/bold magenta]")