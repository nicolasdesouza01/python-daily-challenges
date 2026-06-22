import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class SorteadorProcessador:

    def __init__(self):
        self._valores_sorteados = []
        self._resultado_soma = 0
        self._interface = Console()

    def exibir_menu_inicial(self):
        try:
            self._interface.print("")
            painel_menu = Panel(
                "[bold cyan]1[/bold cyan] - Inserir 5 números manualmente\n"
                "[bold cyan]2[/bold cyan] - Gerar 5 números aleatoriamente (0 a 10)",
                title=":control_knobs: OPÇÕES DE ENTRADA",
                border_style="cyan",
                expand=False,
            )
            self._interface.print(painel_menu)
            self._interface.print("")

            while True:
                try:
                    opcao = int(
                        self._interface.input(
                            "[bold white]Escolha uma opção (1 ou 2): [/bold white]"
                        )
                    )
                    if opcao in [1, 2]:
                        return opcao
                    self._interface.print(
                        "[bold yellow]:warning: Opção inválida! Digite apenas 1 ou 2.[/bold yellow]"
                    )
                except ValueError:
                    self._interface.print(
                        "[bold red]:x: Erro: Digite apenas números inteiros válidos.[/bold red]"
                    )

        except Exception as erro:
            self._interface.print(
                f"[bold red]Erro crítico no menu: {erro}[/bold red]"
            )
            return None

    def capturar_valores_manuais(self):
        try:
            self._valores_sorteados.clear()
            self._interface.print(
                "\n:keyboard: [bold blue]Modo Manual Ativo. Insira valores entre 0 e 10.[/bold blue]"
            )

            contador = 1
            while contador <= 5:
                try:
                    entrada = int(
                        self._interface.input(
                            f"[bold white]Digite o {contador}º número: [/bold white]"
                        )
                    )

                    if 0 <= entrada <= 10:
                        self._valores_sorteados.append(entrada)
                        contador += 1
                    else:
                        self._interface.print(
                            "[bold yellow]:warning: Valor fora do limite! Escolha um número de 0 a 10.[/bold yellow]"
                        )

                except ValueError:
                    self._interface.print(
                        "[bold red]:x: Entrada inválida! Por favor, digite um número inteiro.[/bold red]"
                    )

        except Exception as erro:
            self._interface.print(
                f"[bold red]Falha na captura manual de dados: {erro}[/bold red]"
            )

    def gerar_valores_aleatorios(self):
        try:
            self._valores_sorteados.clear()

            with self._interface.status(
                "[bold magenta]Utilizando sistema para gerar 5 valores aleatórios (0 a 10)...[/bold magenta]",
                spinner="aesthetic",
            ):
                for _ in range(0, 5):
                    numero = random.randint(0, 10)
                    self._valores_sorteados.append(numero)
                    time.sleep(0.4)

        except Exception as erro:
            self._interface.print(
                f"[bold red]Falha ao realizar o sorteio automatizado: {erro}[/bold red]"
            )

    def calcular_soma_pares(self):
        try:
            self._resultado_soma = 0

            for numero in self._valores_sorteados:
                if numero % 2 == 0:
                    self._resultado_soma += numero

        except Exception as erro:
            self._interface.print(
                f"[bold red]Falha ao processar a soma dos valores pares: {erro}[/bold red]"
            )

    def apresentar_resultados(self):
        try:
            self._interface.print("")

            tabela_valores = Table(
                title=":game_die: MATRIZ DE VALORES", title_style="bold cyan"
            )
            tabela_valores.add_column("Posição", justify="center", style="dim cyan")
            tabela_valores.add_column("Valor", justify="center", style="bold yellow")

            for indice, numero in enumerate(self._valores_sorteados, 1):
                tabela_valores.add_row(f"{indice}º número", str(numero))

            self._interface.print(tabela_valores)
            self._interface.print("")

            texto_painel = (
                f"Lista completa carregada: [bold white]{self._valores_sorteados}[/bold white]\n\n"
                f"Resultado final da soma dos pares: [bold green]{self._resultado_soma}[/bold green]"
            )

            painel_exibicao = Panel(
                texto_painel,
                title=":heavy_plus_sign: SOMA PROCESSADA",
                border_style="green",
                expand=False,
            )

            self._interface.print(painel_exibicao)
            self._interface.print("")

        except Exception as erro:
            self._interface.print(
                f"[bold red]Falha ao construir interface visual: {erro}[/bold red]"
            )

    def perguntar_se_continua(self):
        try:
            while True:
                resposta = (
                    self._interface.input(
                        "[bold white]Deseja realizar uma nova operação? (S/N): [/bold white]"
                    )
                        .strip()
                        .upper()
                )

                if resposta in ["S", "SIM"]:
                    return True
                if resposta in ["N", "NÃO", "NAO"]:
                    return False

                self._interface.print(
                    "[bold yellow]:question: Resposta inválida. Digite apenas S ou N.[/bold yellow]"
                )

        except Exception as erro:
            self._interface.print(
                f"[bold red]Erro ao processar resposta de continuidade: {erro}[/bold red]"
            )
            return False


if __name__ == "__main__":
    try:
        gerenciador = SorteadorProcessador()
        executando = True

        while executando:
            opcao_escolhida = gerenciador.exibir_menu_inicial()

            if opcao_escolhida == 1:
                gerenciador.capturar_valores_manuais()
            elif opcao_escolhida == 2:
                gerenciador.gerar_valores_aleatorios()

            gerenciador.calcular_soma_pares()
            gerenciador.apresentar_resultados()

            executando = gerenciador.perguntar_se_continua()

        Console().print(
            "\n:wave: [bold green]Programa finalizado com sucesso. Até logo![/bold green]\n"
        )

    except KeyboardInterrupt:
        Console().print(
            "\n:warning: [bold yellow]O programa foi interrompido forçadamente pelo usuário.[/bold yellow]"
        )
    except Exception as erro_sistema:
        Console().print(
            f"[bold red]Ocorreu uma exceção grave no sistema: {erro_sistema}[/bold red]"
        )
