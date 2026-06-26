import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class Jokenpo:

    def __init__(self):
        self._options = {1: "Pedra", 2: "Papel", 3: "Tesoura"}
        self._emojis = {1: ":fist:", 2: ":raised_hand:", 3: ":victory_hand:"}
        self._console = Console()

    def _mostrar_abertura(self):
        self._console.print(
            Panel(
                "[bold cyan]JOGO DE JOKENPÔ[/bold cyan]",
                expand=False,
                style="cyan",
            )
        )

    def _obter_jogada_jogador(self):
        while True:
            try:
                self._console.print(
                    "\n[bold yellow]Escolha sua jogada:[/bold yellow]"
                )
                for k, v in self._options.items():
                    self._console.print(
                        f"[bold white]{k}[/bold white] - {v} {self._emojis[k]}"
                    )

                escolha = input("\nSua opção: ").strip()

                if not escolha:
                    raise ValueError("A escolha não pode ser vazia.")

                opcao = int(escolha)

                if opcao in self._options:
                    return opcao
                else:
                    self._console.print(
                        "[bold red]Opção inválida! Escolha entre 1, 2 ou 3.[/bold red]"
                    )

            except ValueError:
                self._console.print(
                    "[bold red]Entrada inválida! Digite apenas os números 1, 2 ou 3.[/bold red]"
                )

    def _efeito_loading(self):
        palavras = [
            "[bold red]JO...[/bold red]",
            "[bold yellow]KEN...[/bold yellow]",
            "[bold green]PÔ!!![/bold green]",
        ]
        for palavra in palavras:
            with self._console.status(palavra, spinner="bouncingBall"):
                time.sleep(0.8)

    def _determinar_vencedor(self, jogador, computador):
        if jogador == computador:
            return "EMPATE"

        if (
            (jogador == 1 and computador == 3)
            or (jogador == 2 and computador == 1)
            or (jogador == 3 and computador == 2)
        ):
            return "JOGADOR"

        return "COMPUTADOR"

    def _exibir_resultado(self, jogador, computador, resultado):
        tabela = Table(
            title="RESULTADO DA RODADA", title_style="bold magenta"
        )
        tabela.add_column("Jogador", justify="center", style="cyan")
        tabela.add_column("Computador", justify="center", style="red")
        tabela.add_column("Resultado", justify="center")

        jogada_jogador = f"{self._options[jogador]} {self._emojis[jogador]}"
        jogada_computador = (
            f"{self._options[computador]} {self._emojis[computador]}"
        )

        if resultado == "JOGADOR":
            res_texto = "[bold green]Você Venceu! :party_popper:[/bold green]"
        elif resultado == "COMPUTADOR":
            res_texto = "[bold red]Você Perdeu! :pensive:[/bold red]"
        else:
            res_texto = "[bold yellow]Empate! :handshake:[/bold yellow]"

        tabela.add_row(jogada_jogador, jogada_computador, res_texto)
        self._console.print(tabela)

    def _deseja_continuar(self):
        while True:
            try:
                resposta = (
                    input("\nDeseja jogar novamente? [S/N]: ").strip().upper()
                )

                if not resposta:
                    raise ValueError("A resposta não pode ser vazia.")

                if resposta in ("S", "N"):
                    return resposta == "S"
                else:
                    self._console.print(
                        "[bold red]Opção inválida! Digite apenas S para Sim ou N para Não.[/bold red]"
                    )

            except ValueError:
                self._console.print(
                    "[bold red]Entrada inválida! Digite apenas S ou N.[/bold red]"
                )

    def jogar(self):
        while True:
            self._mostrar_abertura()
            jogada_p = self._obter_jogada_jogador()
            jogada_c = random.randint(1, 3)

            self._efeito_loading()

            res = self._determinar_vencedor(jogada_p, jogada_c)
            self._exibir_resultado(jogada_p, jogada_c, res)

            if not self._deseja_continuar():
                self._console.print(
                    "\n[bold cyan]Obrigado por jogar! Até a próxima! :wave:[/bold cyan]\n"
                )
                break


if __name__ == "__main__":
    jogo = Jokenpo()
    jogo.jogar()