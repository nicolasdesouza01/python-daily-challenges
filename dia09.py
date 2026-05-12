from datetime import datetime
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    dados = dict()
    ano_atual = datetime.now().year

    console.print("[bold blue]:desktop_computer: Iniciando o Sistema de Cadastro de Trabalhador...[/]\n")

    while True:
        try:
            console.print("[bold cyan]:bust_in_silhouette: Digite o nome do trabalhador:[/]")
            nome_input = input().strip()
            if not nome_input:
                console.print("[bold red]:warning: O nome não pode ficar vazio. Tente novamente.[/]\n")
                continue
            dados['nome'] = nome_input
            break
        except Exception:
            console.print("[bold red]:x: Ocorreu um erro inesperado ao ler o nome. Tente novamente.[/]\n")

    while True:
        try:
            console.print("\n[bold cyan]:calendar: Digite o ano de nascimento:[/]")
            dados['nascimento'] = int(input())
            dados['idade'] = ano_atual - dados['nascimento']
            break
        except ValueError:
            console.print("[bold red]:x: Erro de digitação! Por favor, insira um número inteiro válido para o ano.[/]")

    while True:
        try:
            console.print("\n[bold cyan]:briefcase: Digite a Carteira de Trabalho (0 se não tiver):[/]")
            dados['ctps'] = int(input())
            break
        except ValueError:
            console.print("[bold red]:x: Erro de digitação! Por favor, insira apenas números inteiros para a CTPS.[/]")

    if dados['ctps'] != 0:
        while True:
            try:
                console.print("\n[bold cyan]:hourglass_flowing_sand: Digite o ano de contratação:[/]")
                dados['contratacao'] = int(input())
                break
            except ValueError:
                console.print("[bold red]:x: Erro de digitação! Por favor, insira um número inteiro para o ano de contratação.[/]")

        while True:
            try:
                console.print("\n[bold cyan]:heavy_dollar_sign: Digite o salário (R$):[/]")
                dados['salario'] = float(input())
                break
            except ValueError:
                console.print("[bold red]:x: Erro de digitação! Por favor, insira um valor numérico válido para o salário.[/]")

        dados['aposentadoria'] = (dados['contratacao'] + 35) - dados['nascimento']

    print()

    with console.status("[bold green]:arrows_counterclockwise: Processando as informações e gerando a ficha...", spinner="dots"):
        sleep(2.5)

    tabela = Table(title="[bold magenta]:clipboard: Ficha do Trabalhador", show_header=True, header_style="bold yellow")
    tabela.add_column("Categoria", justify="right")
    tabela.add_column("Registro", justify="left")

    tabela.add_row(":bust_in_silhouette: Nome", dados['nome'])
    tabela.add_row(":calendar: Idade", f"{dados['idade']} anos")
    
    if dados['ctps'] != 0:
        tabela.add_row(":briefcase: CTPS", str(dados['ctps']))
        tabela.add_row(":hourglass_flowing_sand: Ano de Contratação", str(dados['contratacao']))
        tabela.add_row(":heavy_dollar_sign: Salário", f"R$ {dados['salario']:.2f}")
        tabela.add_row(":older_adult: Idade de Aposentadoria", f"{dados['aposentadoria']} anos")
    else:
        tabela.add_row(":briefcase: CTPS", "Não possui registro")

    painel = Panel(tabela, expand=False, border_style="cyan")
    
    console.print(painel)
    console.print("\n[bold green]:white_check_mark: Cadastro finalizado e salvo no dicionário com sucesso![/]")

if __name__ == "__main__":
    main()