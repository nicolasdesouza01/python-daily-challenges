import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

console = Console()


def limpar_tela():
    console.clear()


def exibir_cabecalho():
    limpar_tela()
    texto_cabecalho = (
        "[bold cyan]:sparkles: DETECTOR DE PALÍNDROMOS :sparkles:[/bold cyan]\n"
        "[dim]Verifique se uma frase é igual de trás para frente[/dim]"
    )
    painel = Panel(texto_cabecalho, expand=False, border_style="bold blue")
    console.print(painel)
    console.print("\n")


def simulacao_loading():
    exibir_cabecalho()
    for _ in track(
        range(5),
        description="[bold yellow]Analisando a estrutura da frase...[/bold yellow]",
    ):
        time.sleep(0.3)
    console.print("\n")


def verificar_palindromo(frase):
    frase_limpa = "".join(frase.split()).lower()

    caracteres_invalidos = [",", ".", "!", "?", "-", "_", "(", ")"]
    for char in caracteres_invalidos:
        frase_limpa = frase_limpa.replace(char, "")

    frase_invertida = frase_limpa[::-1]
    eh_palindromo = frase_limpa == frase_invertida

    return frase_limpa, frase_invertida, eh_palindromo


def exibir_resultado(frase_original, frase_limpa, frase_invertida, resultado):
    tabela = Table(title="[bold white]Análise Textual[/bold white]")

    tabela.add_column("Métrica", justify="right", style="cyan", no_wrap=True)
    tabela.add_column("Valor", style="white")

    tabela.add_row("Frase Original", frase_original)
    tabela.add_row("Frase Junta", frase_limpa)
    tabela.add_row("Frase Invertida", frase_invertida)

    console.print(tabela)
    console.print("\n")

    if resultado:
        mensagem = (
            "[bold green]:white_check_mark: É UM PALÍNDROMO! :white_check_mark:[/bold green]\n\n"
            f"A frase '{frase_original}' lida de trás para frente é idêntica."
        )
        cor_borda = "green"
    else:
        mensagem = (
            "[bold red]:x: NÃO É UM PALÍNDROMO! :x:[/bold red]\n\n"
            f"A frase '{frase_original}' não forma a mesma sequência invertida."
        )
        cor_borda = "red"

    painel_resultado = Panel(mensagem, expand=False, border_style=cor_borda)
    console.print(painel_resultado)
    console.print("\n")


def executar_desafio():
    while True:
        exibir_cabecalho()

        try:
            entrada = console.input(
                "[bold white]Digite a frase para analisar (ou digite [bold red]sair[/bold red] para encerrar): [/bold white]"
            )

            if not entrada:
                raise ValueError(
                    "A entrada não pode estar vazia. Por favor, digite uma frase."
                )

            frase = entrada.strip()

            if frase.lower() == "sair":
                limpar_tela()
                console.print(
                    "\n[bold yellow]:wave: Programa encerrado com sucesso. Até a próxima![/bold yellow]\n"
                )
                break

            simulacao_loading()

            frase_limpa, frase_invertida, resultado = verificar_palindromo(
                frase
            )

            exibir_resultado(
                frase, frase_limpa, frase_invertida, resultado
            )

            console.input(
                "[dim]Pressione [Enter] para fazer uma nova verificação...[/dim]"
            )

        except ValueError as erro:
            console.print(f"\n[bold red]:warning: Erro de Entrada: {erro}[/bold red]\n")
            time.sleep(2)

        except Exception as erro_inesperado:
            console.print(
                f"\n[bold red]:fire: Ocorreu um erro inesperado: {erro_inesperado}[/bold red]\n"
            )
            time.sleep(2)


if __name__ == "__main__":
    executar_desafio()