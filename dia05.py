import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Terreno:

    def __init__(self, largura: float = 0.0, comprimento: float = 0.0):
        self._largura = largura
        self._comprimento = comprimento

    @property
    def largura(self) -> float:
        return self._largura

    @largura.setter
    def largura(self, valor: float):
        if valor <= 0:
            raise ValueError("A largura precisa ser um número maior que zero.")
        self._largura = valor

    @property
    def comprimento(self) -> float:
        return self._comprimento

    @comprimento.setter
    def comprimento(self, valor: float):
        if valor <= 0:
            raise ValueError(
                "O comprimento precisa ser um número maior que zero."
            )
        self._comprimento = valor

    def calcular_area(self) -> float:
        return self._largura * self._comprimento


def ler_dimensao_valida(mensagem: str) -> float:
    while True:
        try:
            entrada = console.input(mensagem).strip()

            if not entrada:
                raise ValueError(
                    "O campo não pode ficar vazio. Digite um valor."
                )

            valor = float(entrada)

            if valor <= 0:
                raise ValueError("O valor digitado deve ser maior que zero.")

            return valor

        except ValueError as erro:
            console.print()
            console.print(
                Panel(
                    f"[bold red]:warning: Entrada inválida![/bold red]\n\n[white]{erro}[/white]",
                    title="[bold red]Erro de Digitação[/bold red]",
                    expand=False,
                )
            )
            console.print()


console.clear()
console.print()
console.print(
    Panel.fit(
        " :construction: SISTEMA ENGENHARIA DE TERRENOS :construction: ",
        style="bold magenta",
        subtitle="Módulo de Cálculo de Área",
    )
)
console.print()

terreno = Terreno()

while True:
    try:
        largura_digitada = ler_dimensao_valida(
            "[bold yellow]:straight_ruler: Digite a largura do terreno (m): [/bold yellow]"
        )
        terreno.largura = largura_digitada
        break
    except ValueError as erro_validacao:
        console.print(f"[bold red]{erro_validacao}[/bold red]")

console.print()

while True:
    try:
        comprimento_digitado = ler_dimensao_valida(
            "[bold yellow]:straight_ruler: Digite o comprimento do terreno (m): [/bold yellow]"
        )
        terreno.comprimento = comprimento_digitado
        break
    except ValueError as erro_validacao:
        console.print(f"[bold red]{erro_validacao}[/bold red]")

console.print()

with console.status(
    "[bold cyan]Processando dimensões e estruturando relatório... :hourglass_not_done:[/bold cyan]",
    spinner="dots",
):
    time.sleep(1.5)

area_final = terreno.calcular_area()

tabela_resultados = Table(title="Métricas do Imóvel", style="magenta")
tabela_resultados.add_column(
    "Componente", justify="left", style="bold white", no_wrap=True
)
tabela_resultados.add_column("Dimensão Atual", justify="right", style="yellow")

tabela_resultados.add_row("Largura Frontal", f"{terreno.largura:.2f} m")
tabela_resultados.add_row("Comprimento Lateral", f"{terreno.comprimento:.2f} m")
tabela_resultados.add_row(
    "Área Total Disponível", f"[bold green]{area_final:.2f} m²[/bold green]"
)

console.print()
console.print(
    Panel(
        tabela_resultados,
        title="[bold green]:white_check_mark: ANÁLISE DE SOLO CONCLUÍDA[/bold green]",
        expand=False,
    )
)
console.print()
