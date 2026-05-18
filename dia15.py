import pydoc
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def ajuda_interativa(comando):
    """Busca o manual da função e exibe na tela de forma segura."""
    with console.status(
        "[bold cyan]Acessando o manual... :hourglass_not_done:", spinner="earth"
    ):
        time.sleep(0.8)

    try:
        texto_ajuda = pydoc.render_doc(comando, renderer=pydoc.plaintext)

        console.print("\n")
        painel_titulo = Panel(
            f"[bold gold1]MANUAL DO COMANDO: '{comando}'[/]",
            style="bright_white on blue",
            expand=False,
        )
        console.print(painel_titulo)
        console.print(f"\n[white]{texto_ajuda}[/\n")

    except Exception:
        console.print("\n")
        painel_aviso = Panel(
            f"[bold white]Não encontrei manual para: '{comando}' :warning:[/]",
            style="black on yellow",
            expand=False,
        )
        console.print(painel_aviso)
        console.print("\n")


def exibir_cabecalho():
    """Exibe o título principal alinhado corretamente."""
    tabela_titulo = Table(show_header=False, padding=(1, 5), box=None)
    tabela_titulo.add_column(justify="center")
    tabela_titulo.add_row("[bold white]SISTEMA DE AJUDA PYHELP :bright_button:[/]")

    painel_principal = Panel(
        tabela_titulo, style="black on green", expand=False
    )
    console.print(painel_principal)


def blankets_limpeza():
    """Apenas adiciona um respiro visual no terminal."""
    console.print("\n")


def encerrar_sistema():
    """Finaliza o programa com animação."""
    with console.status(
        "[bold red]Finalizando o PyHelp... :bright_button:", spinner="dots"
    ):
        time.sleep(0.8)

    painel_fim = Panel(
        "[bold white]ATÉ LOGO! :wave:[/]", style="black on red", expand=False
    )
    console.print(painel_fim)


while True:
    try:
        exibir_cabecalho()

        console.print(
            "\n[bold white]Função ou Biblioteca (ou 'FIM' para sair) > [/]",
            end="",
        )
        resposta = input()

        resposta_limpa = resposta.strip()

        if not resposta_limpa:
            with console.status(
                "[bold yellow]Entrada vazia. Tente novamente... :warning:",
                spinner="simpleDots",
            ):
                time.sleep(0.8)
            blankets_limpeza()
            continue

        if resposta_limpa.upper() == "FIM":
            encerrar_sistema()
            break

        ajuda_interativa(resposta_limpa.lower())

    except KeyboardInterrupt:
        blankets_limpeza()
        encerrar_sistema()
        break

    except Exception as erro:
        blankets_limpeza()
        painel_erro = Panel(
            f"[bold white]Erro no sistema: {erro} :cross_mark:[/]",
            title="[bold red]ERRO[/]",
            expand=False,
        )
        console.print(painel_erro)
        blankets_limpeza()
        time.sleep(2)