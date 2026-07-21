import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt


class ConversorBases:
    def __init__(self):
        self._console = Console()

    def _exibir_cabecalho(self):
        self._console.clear()
        titulo = Panel(
            "[bold cyan]:abacus: ANALISADOR E CONVERSOR DE BASES NUMÉRICAS :abacus:[/bold cyan]\n"
            "[dim]Ferramenta Prática para Análise de Sistemas e Programação[/dim]",
            expand=False,
            border_style="bold blue"
        )
        self._console.print(titulo)
        self._console.print()

    def _converter_decimal_para_todos(self, numero: int):
        binario = bin(numero)[2:]
        octal = oct(numero)[2:]
        hexadecimal = hex(numero)[2:].upper()
        qtd_bits = len(binario)
        qtd_bytes = (qtd_bits + 7) // 8

        tabela = Table(title=f":bar_chart: Conversão do Decimal [bold yellow]{numero}[/bold yellow]", border_style="cyan")
        tabela.add_column("Base Numérica", style="bold white", justify="left")
        tabela.add_column("Representação", style="bold green", justify="left")
        tabela.add_column("Prefixo de Código", style="dim white", justify="left")

        tabela.add_row("Binário (Base 2)", binario, f"0b{binario}")
        tabela.add_row("Octal (Base 8)", octal, f"0o{octal}")
        tabela.add_row("Hexadecimal (Base 16)", hexadecimal, f"0x{hexadecimal}")

        tabela_info = Table(title=":magnifying_glass_tilted_left: Análise de Alocação em Memória", border_style="magenta")
        tabela_info.add_column("Métrica Tecnológica", style="bold white")
        tabela_info.add_column("Valor Calculado", style="bold yellow")

        tabela_info.add_row("Mínimo de Bits Requeridos", f"{qtd_bits} bits")
        tabela_info.add_row("Tamanho Estimado na Memória", f"{qtd_bytes} Byte(s)")

        with self._console.status("[bold green]:hourglass_flowing_sand: Processando conversão de bases...[/bold green]", spinner="dots"):
            time.sleep(0.8)

        self._console.print(tabela)
        self._console.print()
        self._console.print(tabela_info)

    def _converter_qualquer_base_para_decimal(self, valor_str: str, base_origem: int):
        with self._console.status("[bold green]:hourglass_flowing_sand: Decodificando valor de origem...[/bold green]", spinner="dots"):
            time.sleep(0.8)

        numero_decimal = int(valor_str, base_origem)
        self._converter_decimal_para_todos(numero_decimal)

    def _converter_texto_para_bases(self, texto: str):
        tabela = Table(title=f":memo: Mapeamento ASCII do Texto: [bold yellow]'{texto}'[/bold yellow]", border_style="green")
        tabela.add_column("Caractere", style="bold white", justify="center")
        tabela.add_column("ASCII (Dec)", style="bold cyan", justify="center")
        tabela.add_column("Binário (8 bits)", style="bold green", justify="center")
        tabela.add_column("Hexadecimal", style="bold magenta", justify="center")

        with self._console.status("[bold green]:hourglass_flowing_sand: Analisando tabela de caracteres...[/bold green]", spinner="dots"):
            time.sleep(0.8)

        for char in texto:
            codigo_ascii = ord(char)
            bin_char = bin(codigo_ascii)[2:].zfill(8)
            hex_char = hex(codigo_ascii)[2:].upper()
            tabela.add_row(char, str(codigo_ascii), bin_char, f"0x{hex_char}")

        self._console.print(tabela)

    def menu_principal(self):
        while True:
            try:
                self._exibir_cabecalho()

                painel_opcoes = Panel(
                    "[bold yellow][ 1 ][/bold yellow] Converter Decimal e Analisar Alocação (Bin, Oct, Hex)\n"
                    "[bold yellow][ 2 ][/bold yellow] Decodificar de Outra Base para Decimal (Bin/Oct/Hex -> Dec)\n"
                    "[bold yellow][ 3 ][/bold yellow] Mapear Texto / String para Binário e Hexadecimal (ASCII)\n"
                    "[bold yellow][ 4 ][/bold yellow] Sair do Sistema",
                    title="[bold green]:gear: Menu Principal[/bold green]",
                    border_style="yellow"
                )
                self._console.print(painel_opcoes)
                self._console.print()

                opcao = Prompt.ask("[bold cyan]Escolha uma opção[/bold cyan]", choices=["1", "2", "3", "4"])

                if opcao == "1":
                    self._console.print()
                    entrada = Prompt.ask("[bold white]Digite um número inteiro decimal[/bold white]")
                    try:
                        num = int(entrada)
                        self._console.print()
                        self._converter_decimal_para_todos(num)
                    except ValueError:
                        self._console.print("\n[bold red]:cross_mark: Erro: Digite apenas um número inteiro decimal válido![/bold red]")

                elif opcao == "2":
                    self._console.print()
                    painel_bases = Panel(
                        "[bold yellow][ 1 ][/bold yellow] Binário (Base 2)\n"
                        "[bold yellow][ 2 ][/bold yellow] Octal (Base 8)\n"
                        "[bold yellow][ 3 ][/bold yellow] Hexadecimal (Base 16)",
                        title="[bold green]Seleção da Base de Origem[/bold green]",
                        border_style="cyan"
                    )
                    self._console.print(painel_bases)
                    sub_opcao = Prompt.ask("[bold cyan]Selecione a base de origem[/bold cyan]", choices=["1", "2", "3"])

                    mapeamento_bases = {"1": (2, "Binário"), "2": (8, "Octal"), "3": (16, "Hexadecimal")}
                    base, nome_base = mapeamento_bases[sub_opcao]

                    valor = Prompt.ask(f"[bold white]Digite o valor em {nome_base}[/bold white]")
                    try:
                        self._console.print()
                        self._converter_qualquer_base_para_decimal(valor, base)
                    except ValueError:
                        self._console.print(f"\n[bold red]:cross_mark: Erro: O valor '{valor}' não é um número válido na base {nome_base}![/bold red]")

                elif opcao == "3":
                    self._console.print()
                    texto = Prompt.ask("[bold white]Digite a palavra ou texto[/bold white]")
                    if texto.strip():
                        self._console.print()
                        self._converter_texto_para_bases(texto)
                    else:
                        self._console.print("\n[bold red]:cross_mark: Erro: O texto não pode ser vazio![/bold red]")

                elif opcao == "4":
                    self._console.print("\n[bold green]:rocket: Sistema encerrado com sucesso! Até logo.[/bold green]\n")
                    break

                self._console.print()
                Prompt.ask("[dim white]Pressione ENTER para continuar...[/dim white]")

            except KeyboardInterrupt:
                self._console.print("\n\n[bold red]:warning: Operação interrompida pelo usuário. Encerrando...[/bold red]\n")
                break
            except Exception as e:
                self._console.print(f"\n[bold red]:cross_mark: Erro inesperado: {e}[/bold red]")
                Prompt.ask("[dim white]Pressione ENTER para tentar novamente...[/dim white]")


if __name__ == "__main__":
    app = ConversorBases()
    app.menu_principal()