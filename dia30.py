import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

while True:
    console.print(
        Panel.fit(
            " [bold cyan] ANÁLISE DE DADOS EM TUPLA [/bold cyan] ",
            style="bold magenta",
            subtitle="Curso em Vídeo"
        )
    )
    console.print("\n" * 1)

    numeros_lista = []
    contador = 1

    while contador <= 4:
        try:
            entrada = console.input(f"[bold yellow]:Input: Digite o {contador}º número: [/bold yellow]")
            numero = int(entrada)
            numeros_lista.append(numero)
            contador += 1
        except ValueError:
            console.print("\n[bold red]:exclamation: Erro: Por favor, digite apenas números inteiros válidos![/bold red]\n")
        except Exception:
            console.print("\n[bold red]:cross_mark: Ocorreu um erro inesperado. Tente novamente.[/bold red]\n")

    numeros = tuple(numeros_lista)

    console.print("\n" * 1)
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold green]:hourglass_not_done: Analisando os dados inseridos...[/bold green]"),
        transient=True
    ) as progress:
        progress.add_task("loading", total=None)
        time.sleep(2)

    tabela = Table(title="[bold magenta]:bar_chart: RESULTADOS DA ANÁLISE[/bold magenta]", show_header=True, header_style="bold cyan")
    tabela.add_column("Critério Avaliado", justify="left", style="white")
    tabela.add_column("Resultado Obtido", justify="center", style="bold green")

    tabela.add_row("Tupla Completa", str(numeros))

    tabela.add_row(
        "Vezes que o 9 apareceu", 
        f"[bold yellow]{numeros.count(9)}x[/bold yellow]"
    )

    if 3 in numeros:
        posicao_tres = numeros.index(3) + 1
        tabela.add_row("Posição do primeiro 3", f"[bold cyan]{posicao_tres}ª posição[/bold cyan]")
    else:
        tabela.add_row("Posição do primeiro 3", "[bold red]O valor 3 não foi digitado[/bold red]")

    pares = [str(n) for n in numeros if n % 2 == 0]

    if pares:
        tabela.add_row("Números pares digitados", ", ".join(pares))
    else:
        tabela.add_row("Números pares digitados", "[bold red]Nenhum número par[/bold red]")

    console.print(tabela)
    console.print("\n" * 1)

    while True:
        resposta = console.input("[bold cyan]:question_mark: Deseja continuar? [S/N]: [/bold cyan]").strip().upper()
        if resposta in ("S", "N"):
            break
        console.print("\n[bold red]:exclamation: Resposta inválida! Digite apenas 'S' para Sim ou 'N' para Não.[/bold red]\n")

    if resposta == "N":
        console.print("\n" * 1)
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold red]:door: Encerrando o sistema...[/bold red]"),
            transient=True
        ) as progress:
            progress.add_task("loading", total=None)
            time.sleep(1.5)
        
        console.print(
            Panel.fit(
                " [bold green]:check_mark_button: Programa finalizado com sucesso! Até a próxima! :rocket:[/bold green] ",
                style="bold white"
            )
        )
        break
    else:
        console.print("\n" * 1)
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold blue]:arrows_counterclockwise: Reiniciando para nova análise...[/bold blue]"),
            transient=True
        ) as progress:
            progress.add_task("loading", total=None)
            time.sleep(1.5)
        console.print("\n" * 2)