from datetime import date
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def voto(ano_nascimento):
    ano_atual = 2026
    idade = ano_atual - ano_nascimento
    
    if idade < 0:
        return ":alien: [bold red]ANO INVÁLIDO[/bold red]"
    
    if idade < 16:
        return f"Com {idade} anos: :prohibited: VOTO NEGADO."
    elif 16 <= idade < 18 or idade >= 70:
        return f"Com {idade} anos: :envelope_with_arrow: VOTO OPCIONAL."
    else:
        return f"Com {idade} anos: :heavy_check_mark: VOTO OBRIGATÓRIO."


console.print(Panel(":computer: [bold blue]SISTEMA DE CONSULTA ELEITORAL PROFISSIONAL[/bold blue] :computer:", expand=False))

while True:
    try:
        print("\n" + "—" * 60)
        entrada = input("Digite o ano de nascimento (ou 'S' para sair): ").strip()

        if entrada.upper() == 'S':
            console.print("\n:wave: [bold cyan]Encerrando o sistema. Até a próxima![/bold cyan]\n")
            break

        if not entrada:
            console.print("\n:warning: [bold yellow]Atenção: Nenhuma informação foi digitada![/bold yellow]")
            continue
        
        nascimento = int(entrada)

        with console.status("[bold green]Consultando base de dados...[/bold green]", spinner="aesthetic"):
            sleep(1.2)

        resultado = voto(nascimento)

        tabela = Table(title="[bold magenta]BOLETIM INFORMATIVO[/bold magenta]", show_header=True, header_style="bold yellow")
        
        tabela.add_column("Critério", justify="center", style="cyan")
        tabela.add_column("Resultado do Sistema", justify="center", style="bright_white")

        tabela.add_row("Status Eleitoral", resultado)

        console.print("\n")
        console.print(tabela)
        console.print("\n")

    except ValueError:
        console.print("\n:x: [bold red]ERRO DE ENTRADA:[/bold red] Por favor, insira um ano válido com 4 dígitos ou 'S' para sair.")

    except Exception as erro:
        console.print(f"\n:warning: [bold red]OCORREU UM PROBLEMA:[/bold red] {erro}")