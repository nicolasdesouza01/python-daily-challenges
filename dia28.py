import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def exibir_loading_analise():
    with console.status("[bold cyan]Varrendo o texto... :mag:[/bold cyan]", spinner="bouncingBar"):
        time.sleep(1.5)
    with console.status("[bold purple]Contando ocorrências de 'A'... :abacus:[/bold purple]", spinner="point"):
        time.sleep(1.2)

def exibir_loading_fim():
    with console.status("[bold red]Limpando o buffer e fechando as conexões... :coffin:[/bold red]", spinner="earth"):
        time.sleep(2)

def analisar_frase():
    while True:
        console.clear()
        
        painel_titulo = Panel(
            "[bold magenta]:sparkles: ANÁLISE DE TEXTO SUPERIOR :sparkles:[/bold magenta]",
            expand=False,
            border_style="magenta"
        )
        console.print(painel_titulo)
        console.print("")  

        try:
            frase = Prompt.ask("[bold yellow]Digite uma frase[/bold yellow]").strip()

            if not frase:
                raise ValueError("O texto não pode ficar em branco para ser analisado.")

            exibir_loading_analise()

            frase_maiuscula = frase.upper()
            
            frase_tratada = frase_maiuscula.replace('Á', 'A').replace('À', 'A').replace('Ã', 'A').replace('Â', 'A')

            quantidade_a = frase_tratada.count('A')
            primeira_posicao = frase_tratada.find('A') + 1
            ultima_posicao = frase_tratada.rfind('A') + 1

            tabela_resultados = Table(title="[bold green]:bar_chart: Relatório Estatístico :bar_chart:[/bold green]", border_style="cyan")
            
            tabela_resultados.add_column("Métrica", justify="left", style="bold white")
            tabela_resultados.add_column("Valor Encontrado", justify="center", style="bold green")

            tabela_resultados.add_row("Frase processada", f'"{frase}"')
            tabela_resultados.add_row("Frequência da letra 'A'", str(quantidade_a))
            
            if quantidade_a > 0:
                tabela_resultados.add_row("Primeira ocorrência", f"Posição {primeira_posicao}")
                tabela_resultados.add_row("Última ocorrência", f"Posição {ultima_posicao}")
            else:
                tabela_resultados.add_row("Primeira ocorrência", "[bold red]Inexistente :x:[/bold red]")
                tabela_resultados.add_row("Última ocorrência", "[bold red]Inexistente :x:[/bold red]")

            console.print("")  
            console.print(tabela_resultados)
            console.print("")  

        except ValueError as erro_vazio:
            console.print("")  
            console.print(Panel(f"[bold red]:warning: Erro de entrada: {erro_vazio}[/bold red]", border_style="red"))
            console.print("")  
            
        except Exception as erro_inesperado:
            console.print("")  
            console.print(Panel(f"[bold red]:fire: Erro crítico: {erro_inesperado}[/bold red]", border_style="red"))
            console.print("")  

        while True:
            resposta = Prompt.ask("[bold blue]Quer continuar? [S/N][/bold blue]").strip().upper()
            if resposta in ('S', 'N'):
                break
            console.print("[bold red]Opção inválida! Digite apenas S para Sim ou N para Não. :no_entry:[/bold red]")
            console.print("")

        if resposta == 'N':
            console.print("")
            exibir_loading_fim()
            console.print("")
            console.print(Panel("[bold green]:checkered_flag: Sistema encerrado!:wave:[/bold green]", border_style="green"))
            console.print("")
            break

if __name__ == "__main__":
    analisar_frase()