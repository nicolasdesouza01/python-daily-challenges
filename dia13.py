import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

lista_numeros = []

console.clear()
console.print(
    Panel.fit(
        " :vampire: [bold cyan]LISTA ORDENADA SEM SORT()[/] :vampire:\n"
        "[white]Digite 5 valores e veja a mágica da ordenação manual acontecer![/]",
        border_style="magenta",
        padding=(1, 2)
    )
)
console.print()

for c in range(0, 5):
    while True:
        try:
            console.print(f"[bold yellow]➔[/] [bold white]Digite o {c + 1}º valor:[/] ", end="")
            entrada = input().strip()
            
            if not entrada:
                raise ValueError("O campo não pode ficar vazio.")
                
            num = int(entrada)
            break
            
        except ValueError as erro:
            console.print()
            if "invalid literal for int()" in str(erro):
                console.print(
                    Panel(
                        " :warning: [bold red]Erro de Entrada:[/] Você precisa digitar um número inteiro válido!",
                        border_style="red"
                    )
                )
            else:
                console.print(
                    Panel(
                        f" :warning: [bold red]Erro de Entrada:[/] {erro}",
                        border_style="red"
                    )
                )
            console.print()

    console.print()
    with Progress(
        SpinnerColumn("dots"),
        TextColumn("[bold magenta]Analisando a melhor posição...[/]"),
        transient=True
    ) as progress:
        progress.add_task("loading", total=None)
        time.sleep(1.0)

    if c == 0 or num > lista_numeros[-1]:
        lista_numeros.append(num)
        console.print(f" :rocket: [bold green]Adicionado ao final da lista...[/]")
    
    else:
        posicao = 0
        while posicao < len(lista_numeros):
            if num <= lista_numeros[posicao]:
                lista_numeros.insert(posicao, num)
                console.print(f" :pushpin: [bold green]Adicionado na posição {posicao} da lista...[/]")
                break
            posicao += 1
            
    console.print()
    console.print("[dim]─" * 50 + "[/]")
    console.print()

console.print()
with Progress(
    SpinnerColumn("bounce"),
    TextColumn("[bold cyan]Formatando relatório final...[/]"),
    transient=True
) as progress:
    progress.add_task("loading", total=None)
    time.sleep(1.5)

tabela = Table(title="[bold magenta]RESULTADO DA LISTA ORDENADA[/]", border_style="cyan")
tabela.add_column("Posição", justify="center", style="yellow", no_wrap=True)
tabela.add_column("Valor Armazenado", justify="center", style="green")

for i, v in enumerate(lista_numeros):
    tabela.add_row(f"{i}º", str(v))

console.print(tabela)
console.print()

console.print(
    Panel.fit(
        f" :chequered_flag: [bold green]Programa finalizado com sucesso![/]\n"
        f"[bold white]Sua lista final ficou assim:[/] [cyan]{lista_numeros}[/]",
        border_style="green"
    )
)