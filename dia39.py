import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class AnalisadorTexto:
    def __init__(self):
        self.console = Console()
        self._texto_usuario = ""

    def executar(self):
        try:
            self.console.clear()
            self.console.print(
                Panel.fit(
                    "[bold blue]Analisador de Dados V2.0[/bold blue] :rocket:", 
                    subtitle="Interface Profissional"
                )
            )
            
            self._texto_usuario = input("\nDigite algo para analisar: ")
            
            if not self._texto_usuario:
                self.console.print(
                    "\n[yellow]:warning: Entrada vazia detectada. Prosseguindo com a análise mesmo assim...[/yellow]\n"
                )
            
            self._exibir_loading()
            self._gerar_relatorio()
            
        except KeyboardInterrupt:
            self.console.print(
                "\n\n[bold red]:x: Operação cancelada pelo usuário. Até logo![/bold red]\n"
            )
        except Exception as erro:
            self.console.print(
                f"\n\n[bold red]:boom: Ocorreu um erro inesperado no sistema: {erro}[/bold red]\n"
            )

    def _exibir_loading(self):
        with self.console.status("[bold green]Mapeando propriedades do texto... :hourglass:[/bold green]") as status:
            time.sleep(1.5)

    def _gerar_relatorio(self):
        tabela = Table(title="[bold magenta]Resultado da Investigação[/bold magenta]", title_justify="left")
        
        tabela.add_column("Propriedade", style="cyan", no_wrap=True)
        tabela.add_column("Status / Resposta", justify="center")

        tipo_nome = str(type(self._texto_usuario).__name__)
        tabela.add_row("Tipo primitivo", f"[bold yellow]{tipo_nome}[/bold yellow]")
        
        tabela.add_row(
            "Só tem espaços?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.isspace() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "É um número?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.isnumeric() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "É alfabético?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.isalpha() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "É alfanumérico?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.isalnum() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "Está em maiúsculas?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.isupper() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "Está em minúsculas?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.islower() else "[red]Não :x:[/red]"
        )
        tabela.add_row(
            "Está capitalizada?", 
            "[green]Sim :heavy_check_mark:[/green]" if self._texto_usuario.istitle() else "[red]Não :x:[/red]"
        )

        self.console.print(tabela)
        self.console.print("\n[bold green]:sparkles: Análise concluída com sucesso![/bold green]\n")

if __name__ == "__main__":
    analisador = AnalisadorTexto()
    analisador.executar()