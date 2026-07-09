import math
import time
from rich.console import Console
from rich.panel import Panel
from rich.status import Status


class TrianguloRetangulo:

    def __init__(self):
        self._cateto_oposto = 0.0
        self._cateto_adjacente = 0.0


    @property
    def cateto_oposto(self) -> float:
        return self._cateto_oposto


    @cateto_oposto.setter
    def cateto_oposto(self, valor: float):
        if valor <= 0:
            raise ValueError
        self._cateto_oposto = valor


    @property
    def cateto_adjacente(self) -> float:
        return self._cateto_adjacente


    @cateto_adjacente.setter
    def cateto_adjacente(self, valor: float):
        if valor <= 0:
            raise ValueError
        self._cateto_adjacente = valor


    def calcular_hipotenusa(self) -> float:
        return math.hypot(self._cateto_oposto, self._cateto_adjacente)


class InterfaceUsuario:

    def __init__(self):
        self._console = Console()
        self._triangulo = TrianguloRetangulo()


    def exibir_cabecalho(self):
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold blue]Calculadora de Hipotenusa Avançada[/bold blue]",
                border_style="blue"
            )
        )


    def obter_cateto(self, nome_cateto: str) -> float:
        while True:
            try:
                valor_input = self._console.input(f"[bold yellow]Digite o comprimento do {nome_cateto}: [/bold yellow]")
                valor = float(valor_input)
                
                if valor <= 0:
                    raise ValueError
                    
                return valor
            except ValueError:
                self._console.print("[bold red]:warning: Erro: Por favor, insira um valor numérico válido e maior que zero.[/bold red]")


    def simular_carregamento(self):
        with self._console.status("[bold cyan]Realizando cálculos trigonométricos...[/bold cyan]", spinner="dots"):
            time.sleep(1.5)


    def exibir_resultado(self, hipotenusa: float):
        resultado_corpo = (
            f"Cateto Oposto: [white]{self._triangulo.cateto_oposto:.2f}[/white]\n"
            f"Cateto Adjacente: [white]{self._triangulo.cateto_adjacente:.2f}[/white]\n\n"
            f"[bold green] A hipotenusa mede: {hipotenusa:.2f}[/bold green]"
        )
        
        self._console.print(
            Panel.fit(
                resultado_corpo,
                title="[bold green]Resultado Final[/bold green]",
                border_style="green"
            )
        )


    def executar(self):
        self.exibir_cabecalho()
        
        try:
            self._triangulo.cateto_oposto = self.obter_cateto("cateto oposto")
            self._triangulo.cateto_adjacente = self.obter_cateto("cateto adjacente")
            
            self.simular_carregamento()
            
            hipotenusa = self._triangulo.calcular_hipotenusa()
            self.exibir_resultado(hipotenusa)
            
        except Exception:
            self._console.print("[bold red]:warning: Ocorreu um erro inesperado no sistema.[/bold red]")


if __name__ == "__main__":
    app = InterfaceUsuario()
    app.executar()