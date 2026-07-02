import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

class ControleQualidade:

    def __init__(self):
        self._amostra = []
        self._limite_minimo = 6.0
        self._console = Console()

    def obter_dados(self):
        self._console.clear()
        self._console.print(Panel(Align.center("[bold blue]:factory: SISTEMA DE CONTROLE DE QUALIDADE :factory:[/bold blue]\n\nInsira a nota de conformidade (0.0 a 10.0) para os 5 itens coletados."), border_style="blue"))
        
        self._amostra.clear()
        contador = 1
        
        while contador <= 5:
            try:
                valor_input = input(f"\nDigite a nota do item {contador}: ").strip()
                
                if not valor_input:
                    self._console.print("[bold red]:warning: Erro: O campo não pode ficar vazio.[/bold red]")
                    continue
                    
                valor = float(valor_input)
                
                if 0 <= valor <= 10:
                    self._amostra.append(valor)
                    contador += 1
                else:
                    self._console.print("[bold red]:warning: Erro: A nota deve ser um número entre 0 e 10.[/bold red]")
                    
            except ValueError:
                self._console.print("[bold red]:warning: Erro: Entrada inválida. Digite apenas números números decimais ou inteiros.[/bold red]")

    def analisar_lote(self):
        if not self._amostra:
            self._console.print("[bold red]:warning: Erro: Nenhuma amostra foi registrada para análise.[/bold red]")
            return

        self._console.print("")
        with self._console.status("[bold yellow]Processando amostragem estatística e verificando limites...[/bold yellow]", spinner="aesthetic"):
            time.sleep(2.5)

        maior = max(self._amostra)
        menor = min(self._amostra)
        
        lote_aprovado = menor >= self._limite_minimo
        
        cor_resultado = "green" if lote_aprovado else "red"
        status_texto = "[bold green]:white_check_mark: LOTE APROVADO[/bold green]" if lote_aprovado else "[bold red]:x: LOTE BLOQUEADO PARA INSPEÇÃO[/bold red]"

        tabela = Table(title="Métricas dos Itens Avaliados", title_style="bold magenta", expand=False)
        tabela.add_column("Item Coletado", justify="center", style="cyan")
        tabela.add_column("Nota de Conformidade", justify="center", style="bold white")

        for indice, nota in enumerate(self._amostra, 1):
            tabela.add_row(f"Item 0{indice}", f"{nota:.1f}")

        self._console.clear()
        self._console.print(tabela)
        self._console.print("")

        painel_conteudo = f"Maior índice de conformidade encontrado: [bold cyan]{maior:.1f}[/bold cyan]\n"
        painel_conteudo += f"Menor índice de conformidade encontrado: [bold magenta]{menor:.1f}[/bold magenta]\n\n"
        painel_conteudo += f"Veredicto Final: {status_texto}"

        self._console.print(Panel(painel_conteudo, title="[bold]Relatório Técnico de Amostragem[/bold]", border_style=cor_resultado, expand=False))

if __name__ == "__main__":
    try:
        gerenciador = ControleQualidade()
        gerenciador.obter_dados()
        gerenciador.analisar_lote()
    except KeyboardInterrupt:
        print("\n\nOperação interrompida pelo usuário de forma segura.")