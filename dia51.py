from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
import math
import time

class VerificadorPrimo:
    def __init__(self):
        self._console = Console()
        self._numero = 0
        self._divisores_totais = 0

    def _solicitar_entrada(self):
        while True:
            try:
                entrada = self._console.input("[bold blue]Digite um número inteiro:[/bold blue] ")
                self._numero = int(entrada)
                if self._numero < 1:
                    raise ValueError
                break
            except ValueError:
                self._console.print("[bold red]Entrada inválida! Por favor, digite um número inteiro maior que 0.[/bold red]")

    def _processar_calculo(self):
        with self._console.status("[bold green]Processando análise matemática...", spinner="dots"):
            time.sleep(1.5)
            self._divisores_totais = 0
            for c in range(1, self._numero + 1):
                if self._numero % c == 0:
                    self._divisores_totais += 1

    def _exibir_resultado(self):
        tabela = Table(title=f"Divisores de {self._numero}", show_header=False)
        
        for c in range(1, self._numero + 1):
            cor = "green" if self._numero % c == 0 else "red"
            tabela.add_column(f"[{cor}]{c}[/{cor}]")
        
        self._console.print(Panel(tabela, title="[bold]Análise de Divisibilidade[/bold]"))
        
        self._console.print(f"\nO número {self._numero} foi divisível {self._divisores_totais} vezes.")
        
        if self._divisores_totais == 2:
            self._console.print("[bold green]E por isso ele É PRIMO :white_check_mark:[/bold green]")
        else:
            self._console.print("[bold red]E por isso ele NÃO É PRIMO :cross_mark:[/bold red]")

    def rodar(self):
        self._console.print(Panel("[bold]Verificador de Números Primos[/bold]", style="cyan"))
        
        self._solicitar_entrada()
        
        self._processar_calculo()
        
        self._exibir_resultado()

if __name__ == "__main__":
    programa = VerificadorPrimo()
    programa.rodar()