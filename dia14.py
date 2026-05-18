import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

console.print(
    Panel(
        "[bold cyan]:wave:VÁRIOS NÚMEROS COM FLAG :wave:[/bold cyan]\n\n"
        "Digite quantos números inteiros quiser. \n"
        "Para encerrar o programa e ver o resultado, digite [bold red]999[/bold red].",
        title="[bold main]Curso em Vídeo D66[/bold main]",
        border_style="cyan",
        expand=False
    )
)

soma = 0
contador = 0

while True:
    try:
        entrada = input("Digite um valor (999 para parar): ").strip()

        if not entrada:
            console.print("[bold yellow]:warning: Nenhuma informação foi digitada. Tente novamente![/bold yellow]\n")
            continue

        numero = int(entrada)

        if numero == 999:
            break

        soma += numero
        contador += 1

    except ValueError:
        console.print("[bold red]:x: Erro! Por favor, digite apenas números inteiros válidos.[/bold red]\n")


console.print("\n")

with console.status("[bold magenta]Processando e somando os valores... :bar_chart:[/bold magenta]", spinner="bounce"):
    time.sleep(2)


tabela = Table(
    title="[bold green]:checkered_flag: ANÁLISE DOS DADOS DOS NÚMEROS :checkered_flag:[/bold green]", 
    border_style="green",
    padding=(0, 2)
)

tabela.add_column("Análise", justify="left", style="bold white")
tabela.add_column("Resultado", justify="center", style="bold gold1")

tabela.add_row("Total de números digitados", str(contador))
tabela.add_row("Soma de todos os valores", str(soma))


console.print(tabela)

console.print("\n")

console.print(
    Panel(
        "[bold green]:star: Código executado com sucesso e flag acionado perfeitamente! :star:[/bold green]", 
        border_style="green", 
        expand=False
    )
)