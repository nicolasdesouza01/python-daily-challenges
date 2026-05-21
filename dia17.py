import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

console = Console()

def exibir_cabecalho():
    console.print(Panel("[bold cyan]BEM-VINDO AO BANCO NÍCK[/bold cyan]", subtitle="Sistema de Saque Contínuo"))

def processar_saque(valor):
    cedulas = [50, 20, 10, 1]
    total = valor
    
    with Progress() as progress:
        task = progress.add_task("[green]Contando notas...", total=100)
        while not progress.finished:
            progress.update(task, advance=25)
            time.sleep(0.1)

    resultado = Table(title=f"Saque de R$ {valor:.2f}")
    resultado.add_column("Cédula", style="green")
    resultado.add_column("Quantidade", justify="center")

    for cedula in cedulas:
        if total >= cedula:
            total_cedulas = total // cedula
            total %= cedula
            if total_cedulas > 0:
                resultado.add_row(f"R$ {cedula}", str(total_cedulas))

    console.print(resultado)
    console.print(":white_check_mark: [bold green]Operação concluída![/bold green]")

def main():
    exibir_cabecalho()
    
    while True:
        try:
            entrada = console.input("\n[yellow]Quanto deseja sacar? (ou digite 'sair' para encerrar): [/yellow]")
            
            if entrada.lower() == 'sair':
                console.print(":wave: [bold red]Sistema encerrado. Até mais![/bold red]")
                break
                
            valor = int(entrada)
            
            if valor <= 0:
                console.print(":warning: [bold red]Valor inválido. Tente novamente.[/bold red]")
                continue
                
            processar_saque(valor)
            
        except ValueError:
            console.print(":x: [bold red]Erro: Digite apenas números inteiros.[/bold red]")
        except Exception as e:
            console.print(f":exclamation: [bold red]Erro inesperado: {e}[/bold red]")

if __name__ == "__main__":
    main()