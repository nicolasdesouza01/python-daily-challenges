import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class Produto:
    def __init__(self, nome: str, preco: float):
        self._nome = nome
        self._preco = preco


class LojaWeather:
    def __init__(self):
        self._produtos = []
        self._console = Console()

    def exibir_cabecalho(self):
        self._console.print(Panel.fit("[bold blue]:cloud: LOJAS WEATHER :cloud:[/bold blue]", width=80))

    def adicionar_produto(self):
        while True:
            try:
                nome = input("Digite o nome do produto: ").strip()
                if not nome:
                    self._console.print("[bold red]:warning: O nome do produto não pode estar vazio.[/bold red]")
                    continue
                break
            except Exception:
                self._console.print("[bold red]:warning: Erro ao ler o nome. Tente novamente.[/bold red]")

        while True:
            try:
                preco = float(input("Qual o preço do produto? R$ "))
                if preco < 0:
                    self._console.print("[bold red]:warning: O preço não pode ser negativo.[/bold red]")
                    continue
                break
            except ValueError:
                self._console.print("[bold red]:warning: Entrada inválida! Digite um número válido para o preço.[/bold red]")
            except Exception:
                self._console.print("[bold red]:warning: Ocorreu um erro inesperado.[/bold red]")

        novo_produto = Produto(nome, preco)
        self._produtos.append(novo_produto)

        with self._console.status("[bold cyan]Registrando produto no sistema... :hourglass_not_done:", spinner="dots"):
            time.sleep(1.2)
        self._console.print("[bold green]:white_check_mark: Produto adicionado com sucesso![/bold green]\n")

    def verificar_continuidade(self):
        while True:
            try:
                opcao = input("Deseja Continuar? [S/N]: ").strip().upper()
                if opcao in ("S", "N"):
                    return opcao
                self._console.print("[bold red]:warning: Resposta inválida! Digite apenas S ou N.[/bold red]")
            except Exception:
                self._console.print("[bold red]:warning: Erro ao processar a opção. Tente novamente.[/bold red]")

    def _calcular_estatisticas(self):
        if not self._produtos:
            return 0, 0, "", 0

        total_gasto = sum(p._preco for p in self._produtos)
        mais_de_mil = sum(1 for p in self._produtos if p._preco > 1000)
        
        produto_mais_barato = self._produtos[0]
        for p in self._produtos:
            if p._preco < produto_mais_barato._preco:
                produto_mais_barato = p
                
        return total_gasto, mais_de_mil, produto_mais_barato._nome, produto_mais_barato._preco

    def exibir_resultados(self):
        with self._console.status("[bold yellow]Gerando relatório meteorológico de vendas... :chart_with_upwards_trend:", spinner="dots"):
            time.sleep(1.5)

        total_gasto, mais_de_mil, nome_barato, preco_barato = self._calcular_estatisticas()

        tabela = Table(title=":clipboard: Resumo da Compra", show_header=True, header_style="bold magenta")
        tabela.add_column("Produto", justify="left")
        tabela.add_column("Preço", justify="right")

        for p in self._produtos:
            tabela.add_row(p._nome, f"R$ {p._preco:.2f}")

        self._console.print(tabela)

        resultados = (
            f"[bold green]:money_bag: Total gasto:[/bold green] R$ {total_gasto:.2f}\n"
            f"[bold yellow]:sparkles: Produtos acima de R$ 1000,00:[/bold yellow] {mais_de_mil}\n"
            f"[bold cyan]:chart_with_downwards_trend: Produto mais barato:[/bold cyan] {nome_barato} (R$ {preco_barato:.2f})"
        )
        
        self._console.print(Panel(resultados, title="[bold blue]:sun_behind_cloud: Estatísticas Finais :sun_behind_cloud:", expand=False))
        self._console.print("\n[bold green]:wave: Fim do programa, obrigado por participar![/bold green]")

    def executar(self):
        self.exibir_cabecalho()
        while True:
            self.adicionar_produto()
            if self.verificar_continuidade() == "N":
                break
        self.exibir_resultados()


if __name__ == "__main__":
    loja = LojaWeather()
    loja.executar()