import math
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class AnalisadorNumerico:

    def __init__(self):
        self.console = Console()
        self._numero_usuario = 0.0

    def _truncar_numero(self):
        return math.trunc(self._numero_usuario)

    def _calcular_fracao(self):
        return self._numero_usuario - self._truncar_numero()

    def _exibir_carregamento(self):
        with self.console.status("[bold cyan]Coletando dados do número... :hourglass_flowing_sand:") as status:
            time.sleep(1.0)
            status.update("[bold magenta]Separando a parte inteira... :scissors:")
            time.sleep(1.0)
            status.update("[bold green]Finalizando análise técnica... :white_check_mark:")
            time.sleep(0.8)

    def _gerar_tabela_resultados(self, inteiro, fracao):
        tabela = Table(title="[bold white]ANÁLISE DETALHADA[/bold white]", show_header=True, header_style="bold magenta")
        
        tabela.add_column("Métrica", style="cyan", justify="left")
        tabela.add_column("Resultado", style="green", justify="right")
        
        tabela.add_row("Número Informado", f"{self._numero_usuario}")
        tabela.add_row("Parte Inteira (Truncada)", f"{inteiro}")
        tabela.add_row("Parte Fracionária", f"{fracao:.4f}")
        
        paridade = "Par :heavy_check_mark:" if inteiro % 2 == 0 else "Ímpar :heavy_check_mark:"
        tabela.add_row("Paridade do Inteiro", paridade)
        
        return tabela

    def iniciar(self):
        while True:
            try:
                self.console.clear()
                
                self.console.print(
                    Panel(
                        "[bold yellow]:rocket: SISTEMA DE ANÁLISE NUMÉRICA :rocket:[/bold yellow]",
                        subtitle="[italic white]Desenvolvido em Python[/italic white]",
                        expand=False
                    )
                )
                
                entrada = self.console.input("\n[bold cyan]Digite um número real (ou 'sair'): [/bold cyan]").strip()
                
                if entrada.lower() == 'sair':
                    self.console.print("\n[bold green]Encerrando o sistema de forma segura... :wave:[/bold green]\n")
                    break
                
                self._numero_usuario = float(entrada)
                
                self._exibir_carregamento()
                
                parte_inteira = self._truncar_numero()
                parte_fracionaria = self._calcular_chem = self._calcular_fracao()
                
                tabela_final = self._gerar_tabela_resultados(parte_inteira, parte_fracionaria)
                
                self.console.print("\n")
                self.console.print(Panel(tabela_final, expand=False))
                self.console.print("\n")
                
                self.console.input("[bold white]Pressione [Enter] para realizar uma nova análise...[/bold white]")
                
            except ValueError:
                self.console.print("\n[bold red]:warning: Erro: Entrada inválida! Digite apenas números reais (use ponto para decimais).[/bold red]\n")
                time.sleep(2.5)
                
            except Exception as erro:
                self.console.print(f"\n[bold red]:warning: Ocorreu um erro inesperado: {erro}[/bold red]\n")
                time.sleep(2.5)

if __name__ == "__main__":
    analisador = AnalisadorNumerico()
    analisador.iniciar()