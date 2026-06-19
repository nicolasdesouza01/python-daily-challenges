import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class ConversorMoedas:
    def __init__(self):
        self._console = Console()
        self._taxas = {
            "USD": 5.33,
            "EUR": 5.75,
            "GBP": 6.82,
            "ARS": 0.0059
        }

    def _exibir_abertura(self):
        self._console.clear()
        texto_painel = "[bold gold1]:money_bag: SISTEMA DE CONVERSÃO MULTIMOEDAS :money_bag:[/bold gold1]"
        self._console.print(Panel.fit(texto_painel, border_style="bold blue", padding=(1, 5)))

    def _coletar_valor(self):
        while True:
            try:
                entrada = self._console.input("\n[bold cyan]:money_with_wings: Quanto dinheiro você quer converter? R$ [/]")
                
                if not entrada.strip():
                    raise ValueError("O valor não pode ser vazio.")
                
                valor_limpo = entrada.replace(",", ".")
                valor = float(valor_limpo)
                
                if valor < 0:
                    raise ValueError("O valor digitado não pode ser negativo.")
                
                return valor
                
            except ValueError as erro:
                self._console.print(f"\n[bold red]:warning: Entrada Inválida:[/] {erro} Tente novamente usando números.", style="italic")

    def _processar_conversao(self, valor_real):
        print()
        with self._console.status("[bold green]Buscando taxas de câmbio no banco de dados...[/]", spinner="dots"):
            time.sleep(1.2)

        tabela = Table(
            title=f"Resultados da Conversão para R$ {valor_real:.2f}", 
            title_style="bold magenta", 
            header_style="bold violet",
            expand=False
        )
        
        tabela.add_column("Moeda Estrangeira", justify="center")
        tabela.add_column("Taxa de Câmbio", justify="right")
        tabela.add_column("Valor Convertido", justify="right")

        simbolos = {"USD": "U$", "EUR": "€", "GBP": "£", "ARS": "$"}

        for moeda, taxa in self._taxas.items():
            valor_convertido = valor_real / taxa
            simbolo = simbolos.get(moeda, "$")
            tabela.add_row(
                f"[bold white]{moeda}[/]", 
                f"R$ {taxa:.2f}", 
                f"[bold green]{simbolo} {valor_convertido:.2f}[/]"
            )

        self._console.print(tabela)

    def iniciar(self):
        while True:
            self._exibir_abertura()
            
            valor_real = self._coletar_valor()
            
            self._processar_conversao(valor_real)
            
            self._console.print("\n" + "—" * 60, style="dim white")
            self._console.print("[bold yellow]:arrows_counterclockwise: Deseja realizar uma nova consulta?[/]")
            
            decisao = self._console.input(
                "[cyan]Pressione [bold white]\[ ESPAÇO ][/] e depois [bold white]\[ ENTER ][/] para sair, ou apenas [bold white]\[ ENTER ][/] para continuar: [/]"
            )
            
            if decisao == " ":
                print()
                with self._console.status("[bold red]Encerrando o ambiente com segurança...[/]", spinner="bouncingBall"):
                    time.sleep(1)
                self._console.print("\n[bold green]:wave: Operação finalizada com sucesso![/]\n")
                break

if __name__ == "__main__":
    sistema = ConversorMoedas()
    sistema.iniciar()