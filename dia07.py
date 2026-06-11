import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress


class CalculadorPintura:

    def __init__(self):
        self._console = Console()
        self._largura = 0.0
        self._altura = 0.0
        self._area = 0.0
        self._tinta = 0.0

    def _exibir_cabecalho(self):
        header = Panel("[bold cyan]CALCULADOR DE PINTURA V1.3[/bold cyan]", border_style="blue")
        self._console.print(header, justify="center")

    def _obter_medida(self, mensagem):
        while True:
            try:
                entrada = self._console.input(f"[bold white]{mensagem}: [/bold white]").strip()
                valor_convertido = float(entrada.replace(',', '.'))
                
                if valor_convertido <= 0:
                    self._console.print(Panel("[bold red]ERRO DE ENTRADA[/bold red]\nO valor deve ser maior que zero.", border_style="red", expand=False))
                    continue
                    
                return valor_convertido
                
            except ValueError:
                self._console.print(Panel("[bold red]ERRO DE ENTRADA[/bold red]\nUse apenas números e vírgulas/pontos.", border_style="red", expand=False))
            except (KeyboardInterrupt, SystemExit):
                self._console.print("\n[bold yellow]Execução interrompida de forma segura.[/bold yellow]")
                exit()

    def _calcular(self):
        self._area = self._largura * self._altura
        self._tinta = self._area / 2

    def _exibir_loading(self):
        with Progress() as progress:
            tarefa = progress.add_task("[yellow]Calculando... :hourglass_flowing_sand:", total=100)
            while not progress.finished:
                progress.update(tarefa, advance=20)
                time.sleep(0.15)

    def _exibir_resultados(self):
        area_formatada = f"{self._area:.2f}".replace('.', ',')
        tinta_formatada = f"{self._tinta:.2f}".replace('.', ',')

        tabela = Table(title="[bold magenta]Resumo do Cálculo[/bold magenta]", border_style="green")
        tabela.add_column("Item", style="cyan")
        tabela.add_column("Resultado", justify="right", style="bold yellow")

        tabela.add_row("Área Total", f"{area_formatada} m²")
        tabela.add_row("Tinta Necessária", f"{tinta_formatada} L")

        self._console.print("\n")
        self._console.print(tabela, justify="center")
        self._console.print(Panel("[bold green]Processamento concluído com sucesso! :white_check_mark:[/bold green]", expand=False), justify="center")

    def executar(self):
        self._exibir_cabecalho()
        self._largura = self._obter_medida("Largura da parede (m)")
        self._altura = self._obter_medida("Altura da parede (m)")
        
        self._calcular()
        self._exibir_loading()
        self._exibir_resultados()


if __name__ == "__main__":
    calculador = CalculadorPintura()
    calculador.executar()
