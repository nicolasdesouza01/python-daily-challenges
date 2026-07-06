import time
from rich.console import Console
from rich.panel import Panel

console = Console()


class SimuladorFinanciamento:

    def __init__(self):
        self._valor_casa = 0.0
        self._salario = 0.0
        self._anos = 0


    def obter_dados(self):
        console.clear()
        console.print(Panel("[bold blue]:house: SIMULADOR DE CRÉDITO IMOBILIÁRIO :house:[/bold blue]", expand=False))
        console.print("\n")

        while True:
            try:
                entrada = console.input("[bold white]Qual o valor da casa desejada? R$ [/bold white]")
                self._valor_casa = float(entrada)
                if self._valor_casa <= 0:
                    raise ValueError
                break
            except ValueError:
                console.print("[bold red]:warning: Entrada inválida. Por favor, insira um valor numérico positivo.[/bold red]\n")

        while True:
            try:
                entrada = console.input("[bold white]Qual é o seu salário mensal atual? R$ [/bold white]")
                self._salario = float(entrada)
                if self._salario <= 0:
                    raise ValueError
                break
            except ValueError:
                console.print("[bold red]:warning: Entrada inválida. Por favor, insira um salário válido.[/bold red]\n")

        while True:
            try:
                entrada = console.input("[bold white]Em quantos anos você pretende pagar o imóvel? [/bold white]")
                self._anos = int(entrada)
                if self._anos <= 0:
                    raise ValueError
                break
            except ValueError:
                console.print("[bold red]:warning: Entrada inválida. Por favor, insira uma quantidade de anos válida.[/bold red]\n")


    def _calcular_prestacao(self):
        return self._valor_casa / (self._anos * 12)


    def _calcular_limite(self):
        return self._salario * 0.30


    def exibir_resultado(self):
        console.clear()
        
        with console.status("[bold cyan]Analisando perfil financeiro e margem de segurança...[/bold cyan]", spinner="aesthetic"):
            time.sleep(2.5)

        prestacao = self._calcular_prestacao()
        limite = self._calcular_limite()

        console.print(Panel(
            f"[bold]DADOS DA SIMULAÇÃO[/bold]\n\n"
            f"Valor do Imóvel: [bold cyan]R$ {self._valor_casa:.2f}[/bold cyan]\n"
            f"Prazo Escolhido: [bold cyan]{self._anos} anos[/bold cyan] ({self._anos * 12} parcelas)\n"
            f"Valor da Prestação: [bold yellow]R$ {prestacao:.2f}[/bold yellow]\n"
            f"Margem Permitida (30% do Salário): [bold yellow]R$ {limite:.2f}[/bold yellow]",
            title="[bold white]ANÁLISE DE CRÉDITO[/bold white]",
            expand=False
        ))
        console.print("\n")

        if prestacao <= limite:
            console.print(Panel("[bold green]:white_check_mark: Empréstimo pode ser CONCEDIDO![/bold green]", border_style="green", expand=False))
        else:
            console.print(Panel("[bold red]:x: Empréstimo NEGADO! A prestação excede o limite de segurança de 30%.[/bold red]", border_style="red", expand=False))
        
        console.print("\n")


if __name__ == "__main__":
    simulador = SimuladorFinanciamento()
    simulador.obter_dados()
    simulador.exibir_resultado()