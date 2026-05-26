import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


console.print(
    Panel.fit(
        "  [bold cyan]:bar_chart: ANALISADOR COMPLETO - DESAFIO 056 :bar_chart:[/bold cyan]  ",
        style="bold magenta",
        border_style="cyan",
    )
)
console.print()

soma_idade = 0
maior_idade_homem = 0
nome_homem_mais_velho = ""
mulheres_menos_20 = 0
dados_pessoas = []

for p in range(1, 5):
    console.print(
        f"[bold yellow]------------------- {p}ª PESSOA -------------------[/bold yellow]"
    )
    console.print()

    while True:
        nome = input("Nome: ").strip()
        if nome != "":
            break
        console.print(
            "[bold red]:warning: O nome não pode ficar vazio![/bold red]"
        )
        console.print()

    while True:
        try:
            idade = int(input("Idade: "))
            if idade >= 0:
                break
            console.print(
                "[bold red]:warning: A idade não pode ser negativa![/bold red]"
            )
            console.print()
        except ValueError:
            console.print(
                "[bold red]:warning: Erro! Digite um número inteiro válido para a idade.[/bold red]"
            )
            console.print()

    while True:
        sexo = input("Sexo [M/F]: ").strip().upper()
        if sexo in ("M", "F"):
            break
        console.print(
            "[bold red]:warning: Entrada inválida! Digite apenas 'M' para Masculino ou 'F' para Feminino.[/bold red]"
        )
        console.print()

    soma_idade += idade

    if sexo == "M":
        if p == 1 or idade > maior_idade_homem:
            maior_idade_homem = idade
            nome_homem_mais_velho = nome

    if sexo == "F" and idade < 20:
        mulheres_menos_20 += 1

    dados_pessoas.append({"nome": nome, "idade": idade, "sexo": sexo})
    console.print()

console.print()
with Progress(
    SpinnerColumn(spinner_name="dots"),
    TextColumn("[bold magenta]{task.description}"),
    transient=True,
) as progress:
    progress.add_task(description="Processando os dados do grupo...", total=None)
    time.sleep(2.5)

media_idade = soma_idade / 4

tabela = Table(
    title="[bold white]Dados Coletados[/bold white]",
    title_justify="center",
    border_style="magenta",
)
tabela.add_column("Nome", justify="left", style="cyan", no_wrap=True)
tabela.add_column("Idade", justify="center", style="green")
tabela.add_column("Sexo", justify="center", style="yellow")

for pessoa in dados_pessoas:
    tabela.add_row(pessoa["nome"], str(pessoa["idade"]), pessoa["sexo"])

console.print(tabela)
console.print()

resultado_texto = f"[bold white]A média de idade do grupo é de:[/bold white] [bold cyan]{media_idade:.1f} anos.[/bold cyan]\n\n"

if nome_homem_mais_velho != "":
    resultado_texto += f"[bold white]O homem mais velho é o:[/bold white] [bold green]{nome_homem_mais_velho}[/bold green] [bold white]com[/bold white] [bold green]{maior_idade_homem} anos.[/bold green]\n\n"
else:
    resultado_texto += (
        "[bold yellow]:information: Nenhum homem foi cadastrado.[/bold yellow]\n\n"
    )

if mulheres_menos_20 == 0:
    resultado_texto += "[bold white]Não há mulheres com menos de 20 anos no grupo.[/bold white]"
elif mulheres_menos_20 == 1:
    resultado_texto += "[bold white]Temos apenas[/bold white] [bold magenta]1 mulher[/bold magenta] [bold white]com menos de 20 anos.[/bold white]"
else:
    resultado_texto += f"[bold white]Ao todo são[/bold white] [bold magenta]{mulheres_menos_20} mulheres[/bold magenta] [bold white]com menos de 20 anos.[/bold white]"

console.print(
    Panel(
        resultado_texto,
        title="[bold green]:white_check_mark: RESULTADO FINAL :white_check_mark:[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
)
console.print()