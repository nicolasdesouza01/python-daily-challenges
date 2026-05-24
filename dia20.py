import math
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def main():
    console.print("\n")
    painel_inicio = Panel(
        "[bold white]Calculadora Contínua\n"
        "Calcule o dobro, triplo e raiz de quantos números quiser.\n"
        "Para encerrar o programa, digite [bold yellow]999[/bold yellow] ou [bold yellow]sair[/bold yellow].[/bold white]",
        title="Curso em Vídeo - Python",
        border_style="bold magenta",
        expand=False
    )
    console.print(painel_inicio, justify="center")
    
    while True:
        console.print("\n")
        try:
            entrada = console.input("[bold cyan]Digite um número (ou '999' para sair): [/bold cyan]").strip().lower()

            if not entrada:
                raise ValueError("Nenhum dado foi inserido.")

            if entrada == "999" or entrada == "sair":
                console.print("\n")
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="[bold red]Encerrando o sistema com segurança...[/bold red]", total=None)
                    time.sleep(1.5)
                
                painel_fim = Panel(
                    "[bold yellow]Programa finalizado com sucesso. Até a próxima! :wave:[/bold yellow]",
                    title="Desconexão",
                    border_style="bold yellow",
                    expand=False
                )
                console.print(painel_fim, justify="center")
                console.print("\n")
                break

            numero = float(entrada)

            console.print("\n")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="[yellow]Processando cálculos matemáticos...[/yellow]", total=None)
                time.sleep(1.2)

            if numero < 0:
                raise ArithmeticError("Não é possível calcular a raiz quadrada de um número negativo no conjunto dos reais.")

            dobro = numero * 2
            triplo = numero * 3
            raiz = math.sqrt(numero)

            resultados = (
                f"[white]Número analisado:[/white] [bold blue]{numero}[/bold blue]\n\n"
                f"[white]O dobro de {numero} é:[/white] [bold green]{dobro}[/bold green]\n"
                f"[white]O triplo de {numero} é:[/white] [bold green]{triplo}[/bold green]\n"
                f"[white]A raiz quadrada de {numero} é:[/white] [bold green]{raiz:.2f}[/bold green]"
            )

            painel_resultado = Panel(
                resultados,
                title=" :checkered_flag: Resultados Obtidos :checkered_flag:",
                border_style="bold green",
                expand=False
            )
            console.print(painel_resultado, justify="center")

        except ValueError as erro:
            console.print("\n")
            mensagem_erro = "[bold red]Erro: Entrada inválida! :warning:\n\n"
            if "Nenhum dado" in str(erro):
                mensagem_erro += "Você não digitou nada. O sistema precisa de um valor para operar.[/bold red]"
            else:
                mensagem_erro += "Por favor, digite apenas números válidos ou '999' para sair.[/bold red]"
                
            painel_erro = Panel(mensagem_erro, title="Falha na Entrada", border_style="bold red", expand=False)
            console.print(painel_erro, justify="center")

        except ArithmeticError as erro_matematico:
            console.print("\n")
            painel_negativo = Panel(
                f"[bold red]Erro de Cálculo: :warning:\n\n{erro_matematico}[/bold red]",
                title="Erro Matemático",
                border_style="bold red",
                expand=False
            )
            console.print(painel_negativo, justify="center")

        except KeyboardInterrupt:
            console.print("\n\n")
            painel_interrupcao = Panel(
                "[bold yellow]O programa foi fechado abruptamente via teclado. :wave:[/bold yellow]",
                title="Programa Interrompido",
                border_style="bold yellow",
                expand=False
            )
            console.print(painel_interrupcao, justify="center")
            console.print("\n")
            break

if __name__ == "__main__":
    main()