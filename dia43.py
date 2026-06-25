import time
from datetime import date
from rich.console import Console
from rich.panel import Panel


class AnalisadorBissexto:

    def __init__(self):
        self.console = Console()
        self._ano = 0

    def _verificar_bissexto(self):
        if self._ano % 4 == 0 and self._ano % 100 != 0 or self._ano % 400 == 0:
            return True
        return False

    def executar(self):
        while True:
            self.console.clear()

            self.console.print(
                Panel.fit(
                    "[bold blue]:calendar: ANALISADOR DE ANOS BISSEXTOS :calendar:[/]",
                    border_style="blue",
                )
            )

            try:
                entrada = self.console.input(
                    "\n[bold yellow]Que ano você quer analisar? (Coloque 0 para o ano atual): [/]"
                )
                ano_int = int(entrada)

                if ano_int < 0:
                    raise ValueError

            except ValueError:
                self.console.print(
                    Panel(
                        "[bold red]:warning: Erro: Por favor, digite um ano válido (número inteiro positivo).[/]",
                        border_style="red",
                    )
                )
                time.sleep(2)
                continue

            if ano_int == 0:
                self._ano = date.today().year
            else:
                self._ano = ano_int

            print()
            with self.console.status(
                "[bold cyan]Analisando o ano... :hourglass_not_done:",
                spinner="dots",
            ):
                time.sleep(1.5)

            print()
            if self._verificar_bissexto():
                mensagem = f"[bold green]:white_check_mark: O ano {self._ano} é BISSEXTO![/]"
                estilo_borda = "green"
            else:
                mensagem = (
                    f"[bold red]:cross_mark: O ano {self._ano} NÃO é BISSEXTO![/]"
                )
                estilo_borda = "red"

            self.console.print(
                Panel.fit(mensagem, border_style=estilo_borda, padding=(1, 4))
            )

            print()
            resposta = (
                self.console.input(
                    "[bold white]Quer analisar outro ano? [S/N]: [/]"
                )
                .strip()
                .upper()
            )

            if resposta != "S":
                self.console.print(
                    "\n[bold magenta]:wave: Programa encerrado. Até a próxima![/]\n"
                )
                break


if __name__ == "__main__":
    analisador = AnalisadorBissexto()
    analisador.executar()