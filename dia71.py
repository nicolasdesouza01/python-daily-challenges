import sys
from decimal import Decimal, InvalidOperation
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class ConversorNumeroExtenso:
    """Classe utilitária para conversão de números inteiros em texto por extenso em português."""

    def __init__(self) -> None:
        self._unidades: tuple[str, ...] = (
            "",
            "um",
            "dois",
            "três",
            "quatro",
            "cinco",
            "seis",
            "sete",
            "oito",
            "nove",
            "dez",
            "onze",
            "doze",
            "treze",
            "quatorze",
            "quinze",
            "dezesseis",
            "dezessete",
            "dezoito",
            "dezenove",
        )
        self._dezenas: tuple[str, ...] = (
            "",
            "",
            "vinte",
            "trinta",
            "quarenta",
            "cinquenta",
            "sessenta",
            "setenta",
            "oitenta",
            "noventa",
        )
        self._centenas: tuple[str, ...] = (
            "",
            "cento",
            "duzentos",
            "trezentos",
            "quatrocentos",
            "quinhentos",
            "seiscentos",
            "setecentos",
            "oitocentos",
            "novecentos",
        )

    def converter_inteiro(self, numero: int) -> str:
        """Converte um número inteiro de 0 até 999.999.999.999 para o equivalente por extenso.

        Args:
            numero (int): Número inteiro a ser convertido.

        Returns:
            str: Representação por extenso do número.

        Raises:
            ValueError: Se o número for negativo ou exceder o limite suportado.
        """
        if numero < 0 or numero > 999_999_999_999:
            raise ValueError(
                "O número fornecido deve estar entre 0 e 999.999.999.999."
            )

        if numero == 0:
            return "zero"

        return self._processar_grupos(numero)

    def _converter_grupo_tres_digitos(self, n: int) -> str:
        """Converte um grupo de até 3 dígitos (0 a 999) por extenso.

        Args:
            n (int): Grupo numérico de 0 a 999.

        Returns:
            str: Texto por extenso do grupo.
        """
        if n == 100:
            return "cem"

        partes: list[str] = []
        c = n // 100
        resto_c = n % 100

        if c > 0:
            partes.append(self._centenas[c])

        if resto_c < 20:
            if resto_c > 0:
                partes.append(self._unidades[resto_c])
        else:
            d = resto_c // 10
            u = resto_c % 10
            partes.append(self._dezenas[d])
            if u > 0:
                partes.append(self._unidades[u])

        return " e ".join(partes)

    def _processar_grupos(self, numero: int) -> str:
        """Divide o número em tríades de dígitos e aplica a escala correspondente.

        Args:
            numero (int): Número inteiro a ser processado.

        Returns:
            str: Texto por extenso formatado.
        """
        escalas = [
            ("", ""),
            ("mil", "mil"),
            ("milhão", "milhões"),
            ("bilhão", "bilhões"),
        ]

        grupos: list[int] = []
        temp = numero
        while temp > 0:
            grupos.append(temp % 1000)
            temp //= 1000

        partes_extenso: list[str] = []

        for i in range(len(grupos) - 1, -1, -1):
            val = grupos[i]
            if val == 0:
                continue

            extenso_grupo = self._converter_grupo_tres_digitos(val)
            singular, plural = escalas[i]

            if i == 0:
                partes_extenso.append(extenso_grupo)
            elif i == 1:
                partes_extenso.append(f"{extenso_grupo} {singular}")
            else:
                nome_escala = singular if val == 1 else plural
                partes_extenso.append(f"{extenso_grupo} {nome_escala}")

        if len(partes_extenso) == 1:
            return partes_extenso[0]

        return " e ".join(partes_extenso)


class FormatadorChequeMoeda:
    """Encapsula a lógica de formatação monetária e emissão por extenso em Reais (R$)."""

    def __init__(self) -> None:
        self._conversor = ConversorNumeroExtenso()

    def valor_por_extenso(self, valor: Decimal | float | int) -> str:
        """Converte um valor monetário para o texto formal por extenso em Reais.

        Args:
            valor (Decimal | float | int): O valor numérico a ser formatado.

        Returns:
            str: A descrição por extenso do valor monetário.

        Raises:
            ValueError: Se o valor for negativo.
        """
        dec_valor = Decimal(str(valor)).quantize(Decimal("0.01"))
        if dec_valor < Decimal("0"):
            raise ValueError("O valor monetário não pode ser negativo.")

        inteiro = int(dec_valor)
        centavos = int((dec_valor - inteiro) * 100)

        partes: list[str] = []

        if inteiro > 0:
            extenso_inteiro = self._conversor.converter_inteiro(inteiro)
            moeda = "real" if inteiro == 1 else "reais"

            if any(
                extenso_inteiro.endswith(termo)
                for termo in ("milhão", "milhões", "bilhão", "bilhões")
            ):
                partes.append(f"{extenso_inteiro} de {moeda}")
            else:
                partes.append(f"{extenso_inteiro} {moeda}")

        if centavos > 0:
            extenso_centavos = self._conversor.converter_inteiro(centavos)
            nome_centavo = "centavo" if centavos == 1 else "centavos"
            partes.append(f"{extenso_centavos} {nome_centavo}")

        if not partes:
            return "zero reais"

        return " e ".join(partes)

    def gerar_dados_cheque(
        self,
        valor: Decimal | float | int,
        favorecido: str,
        cidade: str,
        data: str,
    ) -> dict[str, str]:
        """Gera um dicionário estruturado com os dados formatados de um cheque.

        Args:
            valor (Decimal | float | int): Valor monetário do cheque.
            favorecido (str): Nome do beneficiário.
            cidade (str): Cidade da emissão.
            data (str): Data de emissão formatada.

        Returns:
            dict[str, str]: Dados organizados para preenchimento ou exibição.
        """
        dec_valor = Decimal(str(valor)).quantize(Decimal("0.01"))
        valor_formatado = (
            f"R$ {dec_valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        extenso = self.valor_por_extenso(dec_valor)

        return {
            "valor_num": valor_formatado,
            "valor_extenso": extenso,
            "favorecido": favorecido.strip(),
            "cidade_data": f"{cidade.strip()}, {data.strip()}",
        }


class InterfaceTerminal:
    """Gerencia a interface de terminal interativa com Rich para demonstração do módulo."""

    def __init__(self) -> None:
        self._console = Console()
        self._formatador = FormatadorChequeMoeda()

    def exibir_boas_vindas(self) -> None:
        """Exibe o cabeçalho de apresentação do utilitário."""
        self._console.print(
            Panel(
                "[bold green]:bank: Emissor de Cheques & Extenso Monetário (R$)[/bold green]\n"
                "[dim]Módulo para conversão formal de valores monetários e simulação visual de cheques.[/dim]",
                border_style="green",
                expand=False,
            )
        )

    def executar(self) -> None:
        """Inicia o loop principal da interface de linha de comando."""
        self.exibir_boas_vindas()

        while True:
            try:
                self._console.print(
                    "\n[bold cyan]:round_pushpin: Opções Disponíveis:[/bold cyan]"
                )
                self._console.print(
                    " [bold white]1.[/bold white] Converter valor para Extenso Monetário"
                )
                self._console.print(
                    " [bold white]2.[/bold white] Simular Emissão de Cheque Preenchido"
                )
                self._console.print(" [bold white]3.[/bold white] Sair")

                opcao = Prompt.ask(
                    "\n[bold yellow]:pencil: Escolha uma opção (1-3)[/bold yellow]",
                    choices=["1", "2", "3"],
                )

                if opcao == "3":
                    self._console.print(
                        "\n[bold cyan]:wave: Encerrando a aplicação... Até logo![/bold cyan]"
                    )
                    break

                if opcao == "1":
                    self._demo_conversao_simples()
                elif opcao == "2":
                    self._demo_emissao_cheque()

            except KeyboardInterrupt:
                self._console.print(
                    "\n\n[bold red]:exclamation: Execução interrompida pelo usuário (Ctrl+C). Encerrando suavemente.[/bold red]"
                )
                sys.exit(0)
            except Exception as erro:
                self._console.print(
                    f"[bold red]:warning: Ocorreu um erro inesperado: {erro}[/bold red]"
                )

    def _solicitar_valor_monetario(self) -> Decimal | None:
        """Solicita e valida uma entrada monetária do usuário.

        Returns:
            Decimal | None: O valor convertido ou None se for inválido.
        """
        raw_input = Prompt.ask("Digite o valor em R$ (ex: 1250,50 ou 500)")
        tratado = (
            raw_input.replace(".", "")
            .replace(",", ".")
            .replace("R$", "")
            .strip()
        )
        try:
            val = Decimal(tratado)
            if val < 0:
                self._console.print(
                    "[bold red]:warning: O valor precisa ser maior ou igual a zero.[/bold red]"
                )
                return None
            return val
        except InvalidOperation:
            self._console.print(
                "[bold red]:warning: Formato numérico inválido! Tente usar apenas dígitos e vírgula (ex: 1250,50).[/bold red]"
            )
            return None

    def _demo_conversao_simples(self) -> None:
        """Executa a demonstração de conversão direta para extenso."""
        valor = self._solicitar_valor_monetario()
        if valor is None:
            return

        extenso = self._formatador.valor_por_extenso(valor)

        tabela = Table(
            title=":moneybag: Resultado da Conversão Monetária",
            show_header=True,
            header_style="bold magenta",
        )
        tabela.add_column("Atributo", style="cyan", width=20)
        tabela.add_column("Representação", style="white")

        dec_fmt = (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        tabela.add_row("Valor Numérico", dec_fmt)
        tabela.add_row(
            "Valor por Extenso", f"[bold green]{extenso}[/bold green]"
        )

        self._console.print(tabela)

    def _demo_emissao_cheque(self) -> None:
        """Executa a demonstração visual de montagem de um cheque bancário."""
        valor = self._solicitar_valor_monetario()
        if valor is None:
            return

        favorecido = Prompt.ask("Nome do Favorecido/Beneficiário")
        if not favorecido.strip():
            self._console.print(
                "[bold red]:warning: O nome do favorecido não pode estar em branco.[/bold red]"
            )
            return

        cidade = Prompt.ask("Cidade de emissão", default="São Paulo")
        data = Prompt.ask("Data de emissão", default="23/07/2026")

        dados = self._formatador.gerar_dados_cheque(
            valor, favorecido, cidade, data
        )

        corpo_cheque = (
            f"[bold yellow]Pague por este cheque a quantia de:[/bold yellow]\n"
            f"[bold white font_style=italic]({dados['valor_extenso']})[/bold white font_style=italic]\n\n"
            f"[bold yellow]A ordem de:[/bold yellow] [bold white]{dados['favorecido']}[/bold white]\n"
            f"[bold yellow]Local e Data:[/bold yellow] [bold white]{dados['cidade_data']}[/bold white]\n\n"
            f"[right][bold green]Valor: {dados['valor_num']}[/bold green][/right]"
        )

        self._console.print("\n")
        self._console.print(
            Panel(
                corpo_cheque,
                title=":credit_card: CHEQUE BANCÁRIO SIMULADO",
                subtitle="[dim]Módulo FormatadorChequeMoeda[/dim]",
                border_style="bright_blue",
                padding=(1, 2),
            )
        )


if __name__ == "__main__":
    app = InterfaceTerminal()
    app.executar()