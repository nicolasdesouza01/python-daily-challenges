import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

total_pessoas = 0
total_homens = 0
mulheres_menos_20 = 0
soma_idades = 0

with Progress(
    SpinnerColumn(),
    TextColumn("[bold cyan]{task.description}"),
    transient=True
) as progress:
    progress.add_task(description="Inicializando o sistema...", total=None)
    time.sleep(1.5)

while True:
    console.clear()
    
    console.print(
        Panel.fit(
            "  :clipboard: CADASTRO DE PESSOAS :clipboard:  ",
            style="bold white on blue",
            border_style="cyan"
        )
    )
    console.print("")

    while True:
        try:
            idade = int(console.input("[bold yellow]Digite a idade: [/]"))
            if idade < 0 or idade > 130:
                console.print("[bold red]:warning: Erro: Por favor, digite uma idade válida (0 a 130).[/]\n")
                continue
            break
        except ValueError:
            console.print("[bold red]:warning: Erro: Tipo de dado inválido. Digite um número inteiro para a idade.[/]\n")

    console.print("")

    while True:
        sexo = console.input("[bold yellow]Digite o sexo [M/F]: [/]").strip().upper()
        if sexo in ("M", "F"):
            break
        console.print("[bold red]:warning: Erro: Entrada inválida. Por favor, digite apenas 'M' ou 'F'.[/]\n")

    total_pessoas += 1
    soma_idades += 1
    
    if sexo == "M":
        total_homens += 1
        
    if sexo == "F" and idade < 20:
        mulheres_menos_20 += 1

    console.print("")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}"),
        transient=True
    ) as progress:
        progress.add_task(description="Salvando dados no sistema...", total=None)
        time.sleep(1)

    console.print("[bold green]:white_check_mark: Dados registrados com sucesso![/]")
    console.print("")

    while True:
        continuar = console.input("[bold magenta]Deseja continuar cadastrando? [S/N]: [/]").strip().upper()
        if continuar in ("S", "N"):
            break
        console.print("[bold red]:warning: Erro: Entrada inválida. Digite apenas 'S' ou 'N'.[/]\n")

    if continuar == "N":
        break

console.clear()

with Progress(
    SpinnerColumn(),
    TextColumn("[bold magenta]{task.description}"),
    transient=True
) as progress:
    progress.add_task(description="Gerando relatório final...", total=None)
    time.sleep(2)

media_idade = soma_idades / total_pessoas if total_pessoas > 0 else 0

tabela = Table(title=":bar_chart: RESULTADOS DA ANÁLISE", title_style="bold magenta", border_style="cyan")

tabela.add_column("Métrica Analisada", justify="left", style="bold white")
tabela.add_column("Resultado", justify="center", style="bold green")

tabela.add_row("Total de pessoas cadastradas", str(total_pessoas))
tabela.add_row("Média de idade do grupo", f"{media_idade:.1f} anos")
tabela.add_row("Total de homens cadastrados", str(total_homens))
tabela.add_row("Mulheres com menos de 20 anos", str(mulheres_menos_20))

console.print("")
console.print(tabela)
console.print("")

console.print(
    Panel.fit(
        "  :wave: Programa encerrado com sucesso. Bom descanso!  ",
        style="bold white on green",
        border_style="bright_green"
    )
)
console.print("")