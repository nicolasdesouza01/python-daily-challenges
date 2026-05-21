import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def verificar_expressao(expressao):
    pilha = []
    
    for simbolo in expressao:
        if simbolo == '(':
            pilha.append('(')
        elif simbolo == ')':
            if len(pilha) > 0:
                pilha.pop()
            else:
                pilha.append(')')
                break
    
    return len(pilha) == 0

def interface_principal():
    console.clear()
    
    msg_boas_vindas = Panel(
        "Bem-vindo ao [bold cyan]Analisador de Expressões[/bold cyan]\n"
        "Este sistema verifica se seus parênteses estão equilibrados.",
        title="[bold yellow]EXPRESSÕES[/bold yellow]",
        border_style="blue"
    )
    console.print(msg_boas_vindas)

    try:
        entrada = input("Digite a expressão matemática: ")
        
        if not entrada.strip():
            raise ValueError("A expressão não pode estar vazia.")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processando análise...", total=None)
            time.sleep(1.5)

        if verificar_expressao(entrada):
            tabela = Table(title="Resultado", show_header=False, border_style="green")
            tabela.add_row(":white_check_mark: A expressão está correta!")
            console.print(tabela)
        else:
            tabela = Table(title="Resultado", show_header=False, border_style="red")
            tabela.add_row(":x: A expressão está incorreta!")
            console.print(tabela)

    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] Ocorreu um problema: {e}")

if __name__ == "__main__":
    interface_principal()