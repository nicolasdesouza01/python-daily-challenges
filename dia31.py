from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class SistemaMonetario:
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, novo_valor):
        self._valor = novo_valor

    def _formatar(self, preco):
        return f"R${preco:.2f}".replace(".", ",")

    def aumentar(self, taxa):
        resultado = self._valor + (self._valor * taxa / 100)
        return self._formatar(resultado)

    def diminuir(self, taxa):
        resultado = self._valor - (self._valor * taxa / 100)
        return self._formatar(resultado)

    def dobro(self):
        resultado = self._valor * 2
        return self._formatar(resultado)

    def metade(self):
        resultado = self._valor / 2
        return self._formatar(resultado)

    def resumo(self, aumento=10, reducao=5):
        with console.status("[bold cyan]Processando os dados financeiros... :hourglass_flowing_sand:[/bold cyan]", spinner="bouncingBar"):
            sleep(2.5)

        tabela = Table(title="[bold green]Resumo do Valor Analisado[/bold green]", show_header=False)
        tabela.add_column("Operação", justify="left", style="white")
        tabela.add_column("Resultado", justify="right", style="bold yellow")

        tabela.add_row("Preço analisado:", self._formatar(self._valor))
        tabela.add_row("Dobro do preço:", self.dobro())
        tabela.add_row("Metade do preço:", self.metade())
        tabela.add_row(f"{aumento}% de aumento:", self.aumentar(aumento))
        tabela.add_row(f"{reducao}% de redução:", self.diminuir(reducao))

        painel = Panel(tabela, expand=False, border_style="cyan")
        console.print(painel)

def leia_dinheiro(mensagem):
    while True:
        entrada = console.input(f"[bold cyan]{mensagem}[/bold cyan]").strip().replace(",", ".")
        
        try:
            if not entrada:
                raise ValueError("vazio")
                
            valor_float = float(entrada)
            return valor_float
            
        except ValueError:
            console.print(f"[bold red]:warning: Erro: '{entrada}' não é um preço válido! Tente novamente.[/bold red]\n")

def main():
    console.clear()
    titulo = Panel.fit(
        "[bold blue]:money_with_wings: Validador Financeiro :money_with_wings:[/bold blue]", 
        border_style="blue"
    )
    console.print(titulo)
    print("\n")
    
    valor_valido = leia_dinheiro("Digite o preço: R$ ")
    print("\n")
    
    sistema = SistemaMonetario(valor_valido)
    sistema.resumo(aumento=35, reducao=22)

if __name__ == "__main__":
    main()