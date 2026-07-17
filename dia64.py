import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class OrganizadorDaily:

    def __init__(self):
        self._console = Console()
        self._participantes = {}
        self._ranking = []

    def _obter_nomes(self):
        self._console.print(
            Panel(
                "[bold magenta]:speech_balloon: Daily Standup - Definir Ordem de Fala :speech_balloon:[/bold magenta]\n[dim]Insira o nome dos participantes. Deixe em branco e aperte Enter para finalizar.[/dim]"
            )
        )

        while True:
            try:
                nome = input("Digite o nome do participante: ").strip()

                if nome == "":
                    if len(self._participantes) < 2:
                        self._console.print(
                            "[bold red]:warning: Erro: Adicione pelo menos 2 participantes para a reunião.[/bold red]"
                        )
                        continue
                    break

                if nome in self._participantes:
                    self._console.print(
                        "[bold yellow]:warning: Atenção: Este participante já foi adicionado![/bold yellow]"
                    )
                    continue

                self._participantes[nome] = 0

            except KeyboardInterrupt:
                self._console.print(
                    "\n[bold red]:cross_mark: Entrada de dados cancelada pelo usuário.[/bold red]"
                )
                exit()
            except Exception as erro:
                self._console.print(
                    f"[bold red]:cross_mark: Ocorreu um erro ao ler o nome: {erro}[/bold red]"
                )

    def _sortear_prioridades(self):
        with self._console.status(
            "[bold cyan]Rolando dados de iniciativa...[/bold cyan]",
            spinner="dots",
        ) as status:
            for nome in self._participantes:
                time.sleep(0.5)
                self._participantes[nome] = random.randint(1, 100)
                self._console.print(
                    f"[bold]{nome}[/bold] tirou iniciativa [yellow]{self._participantes[nome]}[/yellow]!"
                )

    def _gerar_ranking(self):
        with self._console.status(
            "[bold magenta]Organizando a fila de apresentação...[/bold magenta]",
            spinner="bounce",
        ) as status:
            time.sleep(1.2)
            self._ranking = sorted(
                self._participantes.items(),
                key=lambda item: item[1],
                reverse=True,
            )

    def _exibir_tabela_final(self):
        tabela = Table(
            title="[bold cyan]:calendar: ORDEM OFICIAL DA REUNIÃO :calendar:[/bold cyan]",
            show_lines=True,
        )

        tabela.add_column("Ordem", justify="center", style="bold yellow")
        tabela.add_column("Participante", justify="left", style="bold white")
        tabela.add_column("Iniciativa", justify="center", style="cyan")

        for indice, (nome, iniciativa) in enumerate(self._ranking):
            tabela.add_row(f"{indice + 1}º", nome, str(iniciativa))
            time.sleep(0.3)

        self._console.print("\n")
        self._console.print(tabela)
        self._console.print(
            "\n[bold green]:star: Tudo pronto! Tenham uma excelente reunião! :star:[/bold green]"
        )

    def iniciar(self):
        try:
            self._obter_nomes()
            self._console.print("\n")
            self._sortear_prioridades()
            self._console.print("\n")
            self._gerar_ranking()
            self._exibir_tabela_final()
        except KeyboardInterrupt:
            self._console.print(
                "\n[bold red]:cross_mark: Programa finalizado antes do esperado.[/bold red]"
            )
        except Exception as erro:
            self._console.print(
                f"\n[bold red]:cross_mark: Ocorreu um erro crítico no sistema: {erro}[/bold red]"
            )


if __name__ == "__main__":
    organizador = OrganizadorDaily()
    organizador.iniciar()