import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class AnalisadorRegistros:

    def __init__(self):
        self._console = Console()
        self._a = 0
        self._b = 0
        self._c = 0
        self._menor = 0
        self._maior = 0


    def _obter_leitura_segura(self, ordem):
        while True:
            try:
                valor = int(self._console.input(f"[bold yellow]Digite o {ordem} valor: [/bold yellow]"))
                return valor
            except ValueError:
                self._console.print("\n:warning: [bold red]Entrada inválida![/bold red] Por favor, digite apenas números inteiros.\n")


    def _coletar_dados(self):
        self._console.print(Panel(":bar_chart: [bold cyan]MÓDULO DE ENTRADA DE DADOS[/bold cyan]\n\nInsira três medições sequenciais para extração de picos e extremos.", border_style="cyan"))
        self._console.print("\n")
        
        self._a = self._obter_leitura_segura("primeiro")
        self._b = self._obter_leitura_segura("segundo")
        self._c = self._obter_leitura_segura("terceiro")


    def _processar_extremos(self):
        a = self._a
        b = self._b
        c = self._c

        menor = a
        if b < a and b < c:
            menor = b
        if c < a and c < b:
            menor = c

        maior = a
        if b > a and b > c:
            maior = b
        if c > a and c > b:
            maior = c

        self._menor = menor
        self._maior = maior


    def _exibir_resultados(self):
        tabela = Table(title=":clipboard: Resumo das Leituras Coletadas", title_style="bold magenta")
        tabela.add_column("Leitura", justify="center", style="cyan")
        tabela.add_column("Valor Registrado", justify="center", style="white")

        tabela.add_row("Primeira", str(self._a))
        tabela.add_row("Segunda", str(self._b))
        tabela.add_row("Terceira", str(self._c))

        self._console.print("\n")
        self._console.print(tabela)
        self._console.print("\n")

        painel_conclusao = Panel(
            f"[bold blue]O menor valor digitado foi[/bold blue] [bold white]{self._menor}[/bold white]\n"
            f":small_red_triangle: [bold red]O Maior valor digitado foi[/bold red] [bold white]{self._maior}[/bold white]",
            title="[bold green]:white_check_mark: Diagnóstico Final[/bold green]",
            border_style="green"
        )
        self._console.print(painel_conclusao)
        self._console.print("\n")


    def _deseja_continuar(self):
        while True:
            resposta = self._console.input("[bold cyan]Deseja continuar? [S/N]: [/bold cyan]").strip().upper()
            
            if resposta in ("S", "N"):
                return resposta == "S"
            
            self._console.print("\n:warning: [bold red]Opção inválida![/bold red] Digite apenas S para Sim ou N para Não.\n")


    def executar(self):
        while True:
            self._console.clear()
            self._console.print(Panel.fit("[bold magenta]SISTEMA DE ANÁLISE DE VARIÁVEIS[/bold magenta]", border_style="magenta"))
            self._console.print("\n")

            self._coletar_dados()
            self._console.print("\n")

            with self._console.status("[bold text] :hourglass_flowing_sand: Sincronizando registros e computando extremos...", spinner="aesthetic"):
                time.sleep(1.8)

            self._processar_extremos()
            self._exibir_resultados()

            if not self._deseja_continuar():
                self._console.print("\n:wave: [bold magenta]Encerrando o sistema. Até mais![/bold magenta]\n")
                break


if __name__ == "__main__":
    analisador = AnalisadorRegistros()
    analisador.executar()