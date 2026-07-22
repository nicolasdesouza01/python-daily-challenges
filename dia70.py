from random import sample
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class GeradorMegaSena:
    """Classe responsável por gerenciar a lógica de geração de jogos da Mega-Sena."""

    def __init__(self, quantidade_jogos: int = 1, dezenas_por_jogo: int = 6):
        """Inicializa o gerador com a quantidade de jogos e dezenas desejadas."""
        self._quantidade_jogos = quantidade_jogos
        self._dezenas_por_jogo = dezenas_por_jogo
        self._jogos = []

    @property
    def quantidade_jogos(self) -> int:
        """Retorna a quantidade de jogos configurada."""
        return self._quantidade_jogos

    @property
    def jogos(self) -> list:
        """Retorna a lista de jogos gerados."""
        return self._jogos

    def _gerar_dezenas(self) -> list:
        """Gera uma lista de dezenas únicas e ordenadas para um único jogo."""
        dezenas = sample(range(1, 61), self._dezenas_por_jogo)
        dezenas.sort()
        return dezenas

    def gerar_todos_jogos(self) -> list:
        """Gera todos os jogos solicitados e armazena na estrutura interna."""
        self._jogos = [self._gerar_dezenas() for _ in range(self._quantidade_jogos)]
        return self._jogos


class MegaSenaApp:
    """Classe responsável pela interface de usuário e fluxo do programa."""

    def __init__(self):
        """Inicializa a aplicação com o console da biblioteca Rich."""
        self._console = Console()

    def _exibir_cabecalho(self) -> None:
        """Exibe o painel inicial estilizado no terminal."""
        self._console.print(
            Panel.fit(
                "[bold yellow]:game_die: GERADOR DA MEGA-SENA :game_die:[/bold yellow]",
                border_style="bold green",
            )
        )

    def _obter_quantidade_jogos(self) -> int:
        """Solicita e valida a quantidade de jogos informada pelo usuário."""
        while True:
            try:
                entrada = self._console.input(
                    "[bold cyan]Quantos jogos você quer sortear? [/bold cyan]"
                )
                quantidade = int(entrada)
                if quantidade <= 0:
                    self._console.print(
                        "[bold red]:x: Por favor, digite um número inteiro maior que zero.[/bold red]"
                    )
                    continue
                return quantidade
            except ValueError:
                self._console.print(
                    "[bold red]:x: Entrada inválida! Digite apenas números inteiros.[/bold red]"
                )

    def _exibir_tabela_jogos(self, jogos: list) -> None:
        """Formata e exibe os jogos gerados dentro de uma tabela estilizada."""
        tabela = Table(
            title="[bold gold1]:ticket: JOGOS GERADOS :ticket:[/bold gold1]",
            show_header=True,
            header_style="bold magenta",
        )
        tabela.add_column("Jogo", justify="center", style="cyan", no_wrap=True)
        tabela.add_column("Dezenas Sorteadas", justify="center", style="green")

        for indice, jogo in enumerate(jogos, start=1):
            dezenas_formatadas = " - ".join(f"{num:02d}" for num in jogo)
            tabela.add_row(f"Jogo {indice}", f"[ {dezenas_formatadas} ]")

        self._console.print(tabela)

    def executar(self) -> None:
        """Executa a aplicação com tratamento total de erros e interrupções."""
        try:
            self._console.clear()
            self._exibir_cabecalho()
            quantidade = self._obter_quantidade_jogos()

            gerador = GeradorMegaSena(quantidade_jogos=quantidade)

            with self._console.status(
                "[bold green]Sorteando dezenas com a sorte ao seu lado... :sparkles:[/bold green]",
                spinner="dots",
            ):
                sleep(1.2)
                jogos = gerador.gerar_todos_jogos()

            self._console.print()
            self._exibir_tabela_jogos(jogos)

            self._console.print()
            self._console.print(
                Panel.fit(
                    "[bold green]:four_leaf_clover: BOA SORTE NOS SEUS JOGOS! :four_leaf_clover:[/bold green]",
                    border_style="bold yellow",
                )
            )

        except KeyboardInterrupt:
            self._console.print(
                "\n\n[bold yellow]:warning: Operação cancelada pelo usuário. Até a próxima![/bold yellow]"
            )
        except Exception as erro:
            self._console.print(
                f"\n[bold red]:x: Ocorreu um erro inesperado: {erro}[/bold red]"
            )


if __name__ == "__main__":
    app = MegaSenaApp()
    app.executar()