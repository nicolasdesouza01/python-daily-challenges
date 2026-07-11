import math
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class AnalisadorTrigonometrico:

    def __init__(self):
        self.console = Console()
        self._angulo = 0.0
        self._seno = 0.0
        self._cosseno = 0.0
        self._tangente = 0.0

    def iniciar(self):
        self.console.clear()
        self.console.print(Panel("[bold cyan]:triangular_ruler: ANALISADOR TRIGONOMÉTRICO :triangular_ruler:[/bold cyan]", expand=False))
        
        try:
            entrada = self.console.input("\n[bold yellow]Digite o ângulo que deseja: [/bold yellow]")
            self._angulo = float(entrada)
            
            with self.console.status("[bold green]Realizando cálculos...[/bold green]", spinner="aesthetic"):
                time.sleep(1.2)
                self._calcular_trigonometria()
            
            self._apresentar_resultados()
            
        except ValueError:
            self.console.print("\n[bold red]:warning: Erro: Por favor, digite apenas números válidos para o ângulo.[/bold red]\n")
        except Exception as erro:
            self.console.print(f"\n[bold red]:warning: Ocorreu um erro inesperado: {erro}[/bold red]\n")

    def _calcular_trigonometria(self):
        radiano = math.radians(self._angulo)
        self._seno = math.sin(radiano)
        self._cosseno = math.cos(radiano)
        self._tangente = math.tan(radiano)

    def _apresentar_resultados(self):
        tabela = Table(title=f"Análise do Ângulo: {self._angulo}°", title_style="bold magenta")
        
        tabela.add_column("Grandeza", justify="left", style="blue")
        tabela.add_column("Valor Formatado", justify="right", style="green")
        
        tabela.add_row("Seno", f"{self._seno:.2f}")
        tabela.add_row("Cosseno", f"{self._cosseno:.2f}")
        tabela.add_row("Tangente", f"{self._tangente:.2f}")
        
        self.console.print("\n")
        self.console.print(tabela)
        self.console.print("\n[bold green]:white_check_mark: Processo finalizado com sucesso![/bold green]\n")


if __name__ == "__main__":
    analisador = AnalisadorTrigonometrico()
    analisador.iniciar()