import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

console.print("\n")
console.print(Panel("[bold cyan]:rocket: SISTEMA DE TABUADA v3.0 :rocket:[/bold cyan]", subtitle="Interface Premium", expand=False))

while True:
    try:
        console.print("\n")
        entrada_usuario = console.input("[bold yellow]Qual número você quer ver na tabuada? [/bold yellow]")
        numero = int(entrada_usuario)
        
        console.print("\n")
        with console.status("[bold magenta]Buscando resultados na matriz... :hourglass_not_done:[/bold magenta]") as status:
            time.sleep(1.5)
            
        tabela = Table(title=f"[bold blue]TABUADA DO {numero}[/bold blue]", show_lines=True)
        
        tabela.add_column("Operação", justify="center", style="cyan")
        tabela.add_column("Resultado", justify="center", style="bold green")

        for i in range(1, 11):
            resultado = numero * i
            tabela.add_row(f"{numero} [bold yellow]x[/] {i}", f"{resultado}")

        console.print(tabela)
        console.print("\n")

        while True:
            resposta = console.input("[bold white]Deseja continuar na tabuada? [S/N]: [/bold white]").strip().upper()
            if resposta in ('S', 'N'):
                break
            console.print("[bold red]:warning: Resposta inválida! Digite apenas 'S' ou 'N'.[/bold red]")

        if resposta == 'N':
            console.print("\n")
            with console.status("[bold red]Encerrando sistema...[/bold red]") as status:
                time.sleep(1.0)
            break

    except ValueError:
        console.print("\n")
        console.print(Panel("[bold red]:warning: ERRO: Por favor, digite apenas números inteiros![/bold red]", border_style="red", expand=False))

console.print("\n")
console.print(Panel("[bold green]:sparkles: Obrigado por usar nossa tabuada! Até a próxima! :sparkles:[/bold green]", expand=False))
console.print("\n")