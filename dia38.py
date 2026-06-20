import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Programa de registro de pessoas.


class RegistradorPessoas:

    def __init__(self):
        self._console = Console()
        self._total_maiores_18 = 0
        self._total_homens = 0
        self._total_mulheres_menores_20 = 0

    def _exibir_cabecalho(self):
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold blue]:clipboard: SISTEMA DE CADASTRO INDUSTRIAL :clipboard:[/bold blue]",
                style="bold white on blue",
            )
        )

    def _solicitar_idade(self) -> int:
        while True:
            try:
                dado = self._console.input(
                    "\n[bold yellow]:arrow_forward: Digite sua idade: [/bold yellow]"
                ).strip()

                if not dado:
                    raise ValueError("O campo de idade não pode ficar em branco.")

                try:
                    idade = int(dado)
                except ValueError:
                    raise ValueError(
                        "A idade deve conter apenas números inteiros (letras ou caracteres especiais não são aceitos)."
                    )

                if idade < 0:
                    raise ValueError("A idade não pode ser um número negativo.")

                return idade

            except ValueError as erro:
                self._console.print(
                    f"[bold red]:warning: Erro: {erro}[/bold red]"
                )

            except KeyboardInterrupt:
                self._console.print(
                    "\n[bold red]:exclamation: Operação interrompida pelo usuário.[/bold red]"
                )
                return -1

    def _solicitar_sexo(self) -> str:
        while True:
            try:
                sexo = (
                    self._console.input(
                        "[bold yellow]:arrow_forward: Qual seu sexo [M/F]: [/bold yellow]"
                    )
                    .strip()
                    .upper()
                )

                if not sexo or sexo not in ["M", "F"]:
                    raise ValueError(
                        "Opção inválida! Por favor, digite apenas 'M' para Masculino ou 'F' para Feminino."
                    )

                return sexo

            except ValueError as erro:
                self._console.print(
                    f"[bold red]:warning: {erro}[/bold red]\n"
                )

            except KeyboardInterrupt:
                return ""

    def _solicitar_continuacao(self) -> bool:
        while True:
            try:
                opcao = (
                    self._console.input(
                        "\n[bold cyan]:question: Deseja Continuar [S/N]? [/bold cyan]"
                    )
                    .strip()
                    .upper()
                )

                if not opcao or opcao not in ["S", "N"]:
                    raise ValueError(
                        "Resposta inválida! Digite 'S' para Sim ou 'N' para Não."
                    )

                return opcao == "S"

            except ValueError as erro:
                self._console.print(
                    f"[bold red]:warning: {erro}[/bold red]"
                )

            except KeyboardInterrupt:
                return False

    def _processar_dados(self, idade: int, sexo: str):
        if idade > 18:
            self._total_maiores_18 += 1

        if sexo == "M":
            self._total_homens += 1

        if sexo == "F" and idade < 20:
            self._total_mulheres_menores_20 += 1

    def _executar_loading(self, mensagem: str):
        with self._console.status(
            f"[bold green]{mensagem}[/bold green]", spinner="dots"
        ):
            time.sleep(1.2)

    def _exibir_resultados(self):
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold green]:bar_chart: RELATÓRIO FINAL CONSOLIDADO :bar_chart:[/bold green]",
                border_style="green",
            )
        )

        tabela = Table(show_header=True, header_style="bold magenta")
        tabela.add_column("Indicador Demográfico", style="cyan", width=40)
        tabela.add_column("Total Registrado", justify="right")

        tabela.add_row(
            "Pessoas com mais de 18 anos", str(self._total_maiores_18)
        )
        tabela.add_row("Homens cadastrados", str(self._total_homens))
        tabela.add_row(
            "Mulheres com menos de 20 anos",
            str(self._total_mulheres_menores_20),
        )

        self._console.print(tabela)
        self._console.print(
            "\n[bold blue]:sparkles: Obrigado por utilizar o sistema! Sessão encerrada. :sparkles:[/bold blue]\n"
        )

    def executar(self):
        while True:
            self._exibir_cabecalho()

            idade = self._solicitar_idade()
            if idade == -1:
                break

            sexo = self._solicitar_sexo()
            if sexo == "":
                break

            self._processar_dados(idade, sexo)

            self._executar_loading(
                ":hourglass_flowing_sand: Registrando informações no sistema..."
            )

            if not self._solicitar_continuacao():
                self._executar_loading(
                    "Estruturando banco de dados..."
                )
                break

        self._exibir_resultados()


if __name__ == "__main__":
    app = RegistradorPessoas()
    app.executar()