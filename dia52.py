import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class LeitorNumerico:

    def __init__(self):
        self._valor_inteiro = 0
        self._valor_real = 0.0
        self._console = Console()

    def ler_inteiro(self, mensagem):
        while True:
            try:
                self._console.print(Panel(f"[bold blue]:arrow_right: {mensagem}[/bold blue]"), justify="center")
                entrada = input().strip()
                
                self._valor_inteiro = int(entrada)
                
                with self._console.status("[bold yellow]Validando número inteiro... :hourglass_flowing_sand:[/bold yellow]"):
                    time.sleep(1)
                    
                return self._valor_inteiro
                
            except (ValueError, TypeError):
                self._console.print("\n[bold red]:warning: ERRO: Por favor, digite um número inteiro válido.[/bold red]\n", justify="center")
                
            except KeyboardInterrupt:
                self._console.print("\n[bold orange3]:warning: O usuário preferiu não digitar esse número.[/bold orange3]\n", justify="center")
                self._valor_inteiro = 0
                return self._valor_inteiro

    def ler_real(self, mensagem):
        while True:
            try:
                self._console.print(Panel(f"[bold magenta]:arrow_right: {mensagem}[/bold magenta]"), justify="center")
                entrada = input().strip()
                
                entrada = entrada.replace(',', '.')
                self._valor_real = float(entrada)
                
                with self._console.status("[bold yellow]Validando número real... :hourglass_flowing_sand:[/bold yellow]"):
                    time.sleep(1)
                    
                return self._valor_real
                
            except (ValueError, TypeError):
                self._console.print("\n[bold red]:warning: ERRO: Por favor, digite um número real válido.[/bold red]\n", justify="center")
                
            except KeyboardInterrupt:
                self._console.print("\n[bold orange3]:warning: O usuário preferiu não digitar esse número.[/bold orange3]\n", justify="center")
                self._valor_real = 0.0
                return self._valor_real

    def mostrar_resultados(self):
        with self._console.status("[bold cyan]Gerando relatório final... :rocket:[/bold cyan]"):
            time.sleep(1.5)
            
        tabela = Table(title=":bar_chart: Valores Armazenados", title_style="bold cyan", show_lines=True)
        
        tabela.add_column("Tipo de Dado", justify="center", style="bold green")
        tabela.add_column("Valor Digitado", justify="center", style="bold white")
        
        tabela.add_row("Inteiro", str(self._valor_inteiro))
        tabela.add_row("Real", f"{self._valor_real:.2f}")
        
        self._console.print("\n")
        self._console.print(tabela, justify="center")
        self._console.print("\n")


if __name__ == "__main__":
    console_principal = Console()
    console_principal.clear()
    
    console_principal.print(Panel.fit("[bold green]  SISTEMA DE LEITURA DE DADOS  [/bold green]", subtitle="POO & Rich Interface"), justify="center")
    console_principal.print("\n")
    
    leitor = LeitorNumerico()
    
    leitor.ler_inteiro("Digite um valor Inteiro")
    console_principal.print("\n")
    
    leitor.ler_real("Digite um valor Real")
    console_principal.print("\n")
    
    leitor.mostrar_resultados()