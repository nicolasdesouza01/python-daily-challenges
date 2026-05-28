import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def leiaInt(mensagem):
    while True:
        try:
            entrada = Prompt.ask(mensagem)

            with console.status(
                "[bold blue]Analisando os dados...:hourglass_not_done:",
                spinner="dots",
            ):
                time.sleep(1)

            if entrada.strip() == "":
                raise ValueError("O campo não pode ficar vazio.")

            if not entrada.strip().isdigit() and not (
                entrada.strip().startswith("-") and entrada.strip()[1:].isdigit()
            ):
                raise ValueError("O valor digitado não é um número inteiro.")

            numero_validado = int(entrada)
            return numero_validado

        except ValueError as erro:
            console.print("\n")

            painel_erro = Panel(
                f"[bold red]ERRO, {erro}\n[white]Por favor, digite um número inteiro válido.",
                title="[bold red]Entrada Inválida",
                border_style="red",
                expand=False,
            )

            console.print(painel_erro)
            console.print("\n")


console.print("\n")

painel_inicio = Panel(
    "[bold green]VALIDANDO ENTRADA DE DADOS:victory_hand:",
    subtitle="[italic white]Desenvolvido com Rich",
    border_style="green",
    expand=False,
)

console.print(painel_inicio)
console.print("\n")

n = leiaInt("[bold yellow]Digite um número inteiro")

console.print("\n")

painel_resultado = Panel(
    f"[bold green]Sucesso!\n\n[white]Você acabou de digitar o número: [bold cyan]{n}",
    title="[bold cyan]Resultado Final",
    border_style="cyan",
    expand=False,
)

console.print(painel_resultado)
console.print("\n")