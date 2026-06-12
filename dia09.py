from datetime import datetime
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class SistemaCadastroTrabalhador:

    def __init__(self):
        self._console = Console()
        self._dados = dict()
        self._ano_atual = datetime.now().year

    def executar(self):
        self._console.print("[bold blue]:desktop_computer: Iniciando o Sistema de Cadastro de Trabalhador...[/]\n")
        
        self._cadastrar_dados_pessoais()
        
        if self._dados['ctps'] != 0:
            self._cadastrar_dados_trabalhistas()
            
        self._gerar_ficha_profissional()

    def _cadastrar_dados_pessoais(self):
        while True:
            try:
                self._console.print("[bold cyan]:bust_in_silhouette: Digite o nome do trabalhador:[/]")
                nome_input = input().strip()
                
                if not nome_input:
                    self._console.print("[bold red]:warning: O nome não pode ficar vazio. Tente novamente.[/]\n")
                    continue
                    
                self._dados['nome'] = nome_input
                break
            except Exception:
                self._console.print("[bold red]:x: Ocorreu um erro inesperado ao ler o nome. Tente novamente.[/]\n")

        while True:
            try:
                self._console.print("\n[bold cyan]:calendar: Digite o ano de nascimento:[/]")
                self._dados['nascimento'] = int(input())
                self._dados['idade'] = self._ano_atual - self._dados['nascimento']
                break
            except ValueError:
                self._console.print("[bold red]:x: Erro de digitação! Por favor, insira um número inteiro válido para o ano.[/]")

        while True:
            try:
                self._console.print("\n[bold cyan]:briefcase: Digite a Carteira de Trabalho (0 se não tiver):[/]")
                self._dados['ctps'] = int(input())
                break
            except ValueError:
                self._console.print("[bold red]:x: Erro de digitação! Por favor, insira apenas números inteiros para a CTPS.[/]")

    def _cadastrar_dados_trabalhistas(self):
        while True:
            try:
                self._console.print("\n[bold cyan]:hourglass_flowing_sand: Digite o ano de contratação:[/]")
                self._dados['contratacao'] = int(input())
                break
            except ValueError:
                self._console.print("[bold red]:x: Erro de digitação! Por favor, insira um número inteiro para o ano de contratação.[/]")

        while True:
            try:
                self._console.print("\n[bold cyan]:heavy_dollar_sign: Digite o salário (R$):[/]")
                self._dados['salario'] = float(input())
                break
            except ValueError:
                self._console.print("[bold red]:x: Erro de digitação! Por favor, insira um valor numérico válido para o salário.[/]")

        self._dados['aposentadoria'] = (self._dados['contratacao'] + 35) - self._dados['nascimento']

    def _gerar_ficha_profissional(self):
        print()
        
        with self._console.status("[bold green]:arrows_counterclockwise: Processando as informações e gerando a ficha...", spinner="dots"):
            sleep(2.5)

        tabela = Table(title="[bold magenta]:clipboard: Ficha do Trabalhador", show_header=True, header_style="bold yellow")
        tabela.add_column("Categoria", justify="right")
        tabela.add_column("Registro", justify="left")

        tabela.add_row(":bust_in_silhouette: Nome", self._dados['nome'])
        tabela.add_row(":calendar: Idade", f"{self._dados['idade']} anos")
        
        if self._dados['ctps'] != 0:
            tabela.add_row(":briefcase: CTPS", str(self._dados['ctps']))
            tabela.add_row(":hourglass_flowing_sand: Ano de Contratação", str(self._dados['contratacao']))
            tabela.add_row(":heavy_dollar_sign: Salário", f"R$ {self._dados['salario']:.2f}")
            tabela.add_row(":older_adult: Idade de Aposentadoria", f"{self._dados['aposentadoria']} anos")
        else:
            tabela.add_row(":briefcase: CTPS", "Não possui registro")

        painel = Panel(tabela, expand=False, border_style="cyan")
        
        self._console.print(painel)
        self._console.print("\n[bold green]:white_check_mark: Cadastro finalizado e salvo no dicionário da classe com sucesso![/]")


if __name__ == "__main__":
    sistema = SistemaCadastroTrabalhador()
    sistema.executar()
