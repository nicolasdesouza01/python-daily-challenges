import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def leia_dinheiro(msg):
    """Valida a entrada de dados para aceitar apenas valores monetários."""
    while True:
        try:
            entrada = str(input(msg)).strip().replace(",", ".")
            if entrada == "" or entrada.isalpha():
                console.print(
                    "[bold red]:warning: ERRO: Digite um preço válido![/bold red]"
                )
                continue
            return float(entrada)
        except (ValueError, TypeError):
            console.print(
                "[bold red]:warning: ERRO: Entrada inválida. Tente novamente.[/bold red]"
            )
        except KeyboardInterrupt:
            console.print(
                "\n[bold yellow]:warning: Usuário preferiu não digitar o valor.[/bold yellow]"
            )
            return 0.0


def metade(preco=0, formato=False):
    res = preco / 2
    return moeda(res) if formato else res


def dobro(preco=0, formato=False):
    res = preco * 2
    return moeda(res) if formato else res


def aumentar(preco=0, taxa=0, formato=False):
    res = preco + (preco * taxa / 100)
    return moeda(res) if formato else res


def diminuir(preco=0, taxa=0, formato=False):
    res = preco - (preco * taxa / 100)
    return moeda(res) if formato else res


def moeda(preco=0, moeda_sigla="R$"):
    return f"{moeda_sigla} {preco:>8.2f}".replace(".", ",")


def resumo(preco=0, taxaa=10, taxar=5):
    """Gera uma tabela estilizada com o resumo estatístico do valor."""
    with Progress(
        SpinnerColumn("dots"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="[bold cyan]Processando dados financeiros...[/bold cyan]",
            total=None,
        )
        time.sleep(1.2)

    table = Table(
        title="[bold green]:bar_chart: RESUMO DO VALOR[/bold green]",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Descrição", justify="left", style="cyan")
    table.add_column("Valor", justify="right", style="green")

    table.add_row("Preço analisado:", moeda(preco))
    table.add_row("Dobro do preço:", dobro(preco, True))
    table.add_row("Metade do preço:", metade(preco, True))
    table.add_row(f"{taxaa}% de aumento:", aumentar(preco, taxaa, True))
    table.add_row(f"{taxar}% de redução:", diminuir(preco, taxar, True))

    console.print(Panel(table, expand=False, border_style="bold blue"))


try:
    console.print(
        Panel.fit(
            "[bold gold1]:rocket:SISTEMA DE ANÁLISE DE PREÇOS[/bold gold1]",
            border_style="bold yellow",
        )
    )
    print("\n")

    while True:
        p = leia_dinheiro("Digite o preço: ")
        print("\n")

        resumo(p, 35, 22)
        print("\n")


        while True:
            try:
                console.print(
                    Panel.fit(
                        "[bold white]Deseja continuar analisando valores? [bold green][S][/bold green] / [bold red][N][/bold red][/bold white]",
                        border_style="bold cyan",
                    )
                )
                resp = str(input("Sua opção: ")).strip().upper()
                
                if resp in ("S", "N"):
                    break
                
                console.print(
                    "[bold red]:warning: ERRO: Responda apenas com S ou N.[/bold red]\n"
                )
            except (ValueError, TypeError):
                console.print(
                    "[bold red]:warning: Entrada inválida. Tente novamente.[/bold red]\n"
                )
            except KeyboardInterrupt:
                resp = "N"
                break

        print("\n")
        if resp == "N":
            with Progress(
                SpinnerColumn("bounce"),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(
                    description="[bold red]Fechando o sistema...[/bold red]",
                    total=None,
                )
                time.sleep(1.0)
            break

except Exception as erro:
    console.print(
        f"[bold red]:cross_mark: Ocorreu um erro inesperado no sistema: {erro.__class__}[/bold red]"
    )

finally:
    console.print(
        Panel.fit(
            "[bold green]:white_check_mark: VOLTE SEMPRE! O sistema foi encerrado com segurança.[/bold green]",
            border_style="bold green",
        )
    )