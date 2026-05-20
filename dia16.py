import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

console = Console()

def exibir_loading():
    for _ in track(range(10), description="[bold blue]Processando dados..."):
        time.sleep(0.1)

def calcular_dobro_triplo_raiz():
    
    console.print(Panel("[bold yellow]DESAFIO 07: Cálculos Matemáticos[/bold yellow]", expand=False))
    
    while True:
        try:
            entrada = console.input("[bold green]Digite um número:[/bold green] ")
            
            if not entrada.strip():
                console.print("[bold red]Erro:[/bold red] Você não digitou nada. Tente novamente.")
                continue
                
            numero = float(entrada)
            
            exibir_loading()
            
            dobro = numero * 2
            triplo = numero * 3
            raiz = numero ** 0.5
            
            tabela = Table(title=f"Resultados para {numero}")
            tabela.add_column("Operação", style="cyan")
            tabela.add_column("Resultado", style="magenta")
            
            tabela.add_row("Dobro", f"{dobro:.2f}")
            tabela.add_row("Triplo", f"{triplo:.2f}")
            tabela.add_row("Raiz Quadrada", f"{raiz:.2f}")
            
            console.print(tabela)
            
            continuar = console.input("\n[bold yellow]Deseja calcular outro número? (S/N):[/bold yellow] ").strip().upper()
            
            if continuar == "N":
                console.print("[bold blue]Encerrando o programa...[/bold blue] :wave:")
                break
            
        except ValueError:
            console.print("[bold red]Erro:[/bold red] O valor digitado não é um número válido. :warning:")
            
        except Exception as e:
            console.print(f"[bold red]Ocorreu um erro inesperado:[/bold red] {e}")
            break

if __name__ == "__main__":
    try:
        calcular_dobro_triplo_raiz()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Programa encerrado pelo usuário.[/bold yellow] :wave:")