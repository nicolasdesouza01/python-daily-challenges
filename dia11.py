from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import time

console = Console()

class BoasVindas:
    def __init__(self):
        self.nome = ""

    def exibir_loading(self, tarefa):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=tarefa, total=None)
            time.sleep(1.5)

    def mostrar_cabecalho(self):
        tabela = Table(show_header=False, border_style="blue")
        tabela.add_column("Info")
        tabela.add_row(":computer: [bold white]SISTEMA DE IDENTIFICAÇÃO v2.0[/bold white]")
        
        console.print(Panel(tabela, expand=False, title="[bold cyan]Desafio 002[/bold cyan]"))

    def coletar_nome(self):
        while True:
            try:
                entrada = Prompt.ask("\n:bust_in_silhouette: [bold yellow]Digite seu nome[/bold yellow]")
                if not entrada.strip():
                    raise ValueError("O nome não pode estar vazio.")
                
                if any(char.isdigit() for char in entrada):
                    raise ValueError("Nomes geralmente não contêm números.")

                self.nome = entrada.strip()
                break

            except ValueError as e:
                console.print(f"\n[bold red]:warning: ERRO:[/bold red] {e}")
                console.print("[italic]Tente novamente...[/italic]\n")
            except Exception:
                console.print("\n[bold red]:x: Ocorreu um erro inesperado.[/bold red]")

    def saudar_usuario(self):
        self.exibir_loading(":hourglass_flowing_sand: Processando dados...")
        
        mensagem = f":sparkles: Olá [bold green]{self.nome}[/bold green]!\n\nÉ um grande prazer te conhecer!"
        
        console.print(
            Panel(
                mensagem,
                title="[bold magenta]:wave: BOAS-VINDAS[/bold magenta]",
                border_style="green",
                padding=(1, 2)
            )
        )

    def executar(self):
        try:
            self.mostrar_cabecalho()
            self.coletar_nome()
            self.saudar_usuario()
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]:door: Programa encerrado pelo usuário.[/bold yellow]")
        finally:
            console.print("\n[dim]Finalizando execução...[/dim]")

if __name__ == "__main__":
    app =  BoasVindas()
    app.executar()
