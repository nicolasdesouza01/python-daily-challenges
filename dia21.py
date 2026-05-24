import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

numeros = list()

console.print(
    Panel.fit(
        "     [bold cyan]SISTEMA DE CADASTRO DE VALORES[/bold cyan]     ",
        border_style="cyan"
    )
)

while True:
    try:
        console.print("\n:arrow_right: [bold white]Digite um valor numérico inteiro:[/bold white] ", end="")
        entrada = input().strip()
        
        valor = int(entrada)
        
        if valor not in numeros:
            numeros.append(valor)
            console.print("[bold green]:white_check_mark: Valor adicionado com sucesso!...[/bold green]")
        else:
            console.print("[bold yellow]:warning: Valor duplicado! Não vou adicionar...[/bold yellow]")
            
    except ValueError:
        console.print("[bold red]:x: Erro! Por favor, digite apenas números inteiros válidos.[/bold red]")
        continue
    except Exception as erro:
        console.print(f"[bold red]:x: Ocorreu um erro inesperado: {erro}[/bold red]")
        continue

    while True:
        console.print("\n:question: [bold white]Quer continuar? [S/N]:[/bold white] ", end="")
        resposta = input().strip().upper()
        
        if resposta in ("S", "N"):
            break
        console.print("[bold red]:x: Resposta inválida! Digite apenas 'S' para Sim ou 'N' para Não.[/bold red]")

    if resposta == "N":
        break

print()
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    transient=True
) as progress:
    task = progress.add_task(description="[cyan]Processando e ordenando dados...[/cyan]", total=None)
    time.sleep(1.5)

numeros.sort()

tabela = Table(title="[bold magenta]Valores Cadastrados[/bold magenta]", border_style="magenta")
tabela.add_column("Posição", justify="center", style="cyan", no_wrap=True)
tabela.add_column("Valor Guardado", justify="center", style="green")

for indice, num in enumerate(numeros):
    tabela.add_row(f"{indice + 1}º", str(num))

console.print("\n")
console.print(tabela)

console.print(
    Panel.fit(
        " [bold green]:wave: Programa finalizado com sucesso! Até a próxima![/bold green] ",
        border_style="green"
    )
)