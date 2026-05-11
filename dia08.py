import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

class AnalistaDeIdentidade:

    def __init__(self):
        self.console = Console()
        self.nome_completo = ""
        self.fragmentos = []

    def exibir_banner(self):
        self.console.print(Panel.fit(
            "[bold magenta]NUCLEO DE PROCESSAMENTO NOMINAL[/bold magenta]\n"
            "[white]Engine de Extração e Estruturação de Dados[/white]",
            border_style="bright_magenta",
            padding=(1, 4)
        ))

    def carregar_sistema(self, mensagem="Acessando banco de dados..."):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=mensagem, total=None)
            time.sleep(1.2)

    def coletar_nome(self):
        while True:
            entrada = self.console.input("\n[bold cyan]Digite o nome completo para o registro:[/bold cyan] ").strip()

            if not entrada:
                self.console.print("[bold red]Erro: A entrada não pode estar vazia.[/bold red]")
                continue
            
            if all(parte.isalpha() for parte in entrada.split()):
                self.nome_completo = entrada
                self.fragmentos = entrada.split()
                break
            else:
                self.console.print("[bold red]Erro: O sistema aceita apenas caracteres alfabéticos.[/bold red]")

    def gerar_relatorio(self):
        self.carregar_sistema("Mapeando fragmentos do nome...")
        
        tabela = Table(
            title="RELATÓRIO DE ESTRUTURA", 
            title_style="bold yellow", 
            show_lines=True,
            header_style="bold cyan"
        )
        
        tabela.add_column("Propriedade", justify="right")
        tabela.add_column("Conteúdo Identificado", style="bold white")

        tabela.add_row("Primeiro Nome", self.fragmentos[0].capitalize())
        tabela.add_row("Sobrenome Final", self.fragmentos[-1].capitalize())
        tabela.add_row("Total de Termos", str(len(self.fragmentos)))

        self.console.print("\n")
        self.console.print(tabela)
        
        self.console.print(Panel(
            f"[bold green]Objeto processado com sucesso: {self.nome_completo.upper()}[/bold green]",
            border_style="green"
        ))

    def executar(self):
        self.exibir_banner()
        self.coletar_nome()
        self.gerar_relatorio()


if __name__ == "__main__":
    app = AnalistaDeIdentidade()
    app.executar()