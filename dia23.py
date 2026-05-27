import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

console = Console()

def carregar(mensagem="Processando..."):
    with Live(Spinner("dots", text=f"[bold blue]{mensagem}"), refresh_per_second=10):
        time.sleep(1.5)

def main():
    galera = []
    soma = 0
    
    console.print(Panel("[bold cyan]Cadastro de Pessoas - Sistema Profissional[/bold cyan]", expand=False))

    while True:
        try:
            nome = str(console.input("[bold yellow]Nome:[/bold yellow] ")).strip()
            if not nome:
                raise ValueError("O nome não pode ficar em branco!")

            while True:
                sexo = str(console.input("[bold yellow]Sexo [M/F]:[/bold yellow] ")).strip().upper()
                if sexo in 'MF':
                    break
                console.print("[red]ERRO! Digite apenas M ou F.[/red]")

            while True:
                try:
                    idade = int(console.input("[bold yellow]Idade:[/bold yellow] "))
                    break
                except ValueError:
                    console.print("[red]ERRO! Por favor, digite um número inteiro.[/red]")

            soma += idade
            galera.append({'nome': nome, 'sexo': sexo, 'idade': idade})

            while True:
                resp = str(console.input("[bold yellow]Quer continuar [S/N]? [/bold yellow]")).strip().upper()
                if resp in 'SN':
                    break
                console.print("[red]ERRO! Responda apenas S ou N.[/red]")
            
            if resp == 'N':
                break
                
        except Exception as e:
            console.print(f"[bold red]Erro inesperado:[/bold red] {e}")

    carregar("Analisando dados...")

    console.print(f"\n[bold green]Total de {len(galera)} pessoas cadastradas.[/bold green]")
    media = soma / len(galera)
    console.print(f"[bold]Média de idade:[/bold] {media:.2f} anos\n")


    tabela_mulheres = Table(title="Mulheres Cadastradas", header_style="bold magenta", expand=False)
    tabela_mulheres.add_column("Nome", min_width=25)
    for p in galera:
        if p['sexo'] == 'F':
            tabela_mulheres.add_row(p['nome'])
    console.print(tabela_mulheres)

    tabela_media = Table(title="Acima da Média de Idade", header_style="bold yellow", expand=False)
    tabela_media.add_column("Nome", min_width=15)
    tabela_media.add_column("Idade", min_width=10)
    for p in galera:
        if p['idade'] >= media:
            tabela_media.add_row(p['nome'], str(p['idade']))
    console.print(tabela_media)

    console.print(Panel("[bold green]:thumbs_up: ENCERRANDO O PROGRAMA![/bold green]"))

if __name__ == "__main__":
    main()