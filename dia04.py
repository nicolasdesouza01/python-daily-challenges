from rich import print
from rich.console import Console
from time import sleep
console = Console()
while True:
    nome = str(console.input("[white on blue]Digite seu nome completo: [/]")).strip().lower()
    if nome in "silva":
        console.print("[green]Percebi que seu nome tem Silva, então você é um Silva![/]")
    else:
        console.print("[red]Parece que seu nome não tem Silva, então você não é um Silva.[/]")
    continuar = console.input("[blue]Deseja continuar? (s/n): [/]").strip().lower()
    if continuar != 's':
        console.print("[green]Encerrando o programa. Até mais![/]")
        for i in range(3, 0, -1):
            if i == 1:
                console.print(f"[yellow]Saindo em {i} segundo...[/]")
            else:                
                console.print(f"[yellow]Saindo em {i} segundos...[/]")
            sleep(1)
        print("Programa encerrado!")
        break
    console.print("[yellow]Digite outro nome![/]")