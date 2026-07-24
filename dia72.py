import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align


@dataclass
class UnidadeMedida:
    """
    Representa uma unidade de medida de distância, contendo suas
    metadados e o fator de conversão em relação à unidade base (Metro).
    """
    nome: str
    simbolo: str
    fator_metro: float
    sistema: str


class ConversorDistancia:
    """
    Motor de cálculo responsável por registrar as unidades de medida e
    executar a lógica matemática de conversão entre diferentes sistemas.
    """

    def __init__(self) -> None:
        """Inicializa o repositório interno de unidades disponíveis."""
        self._unidades: Dict[str, UnidadeMedida] = {}
        self._carregar_unidades_padrao()

    def _carregar_unidades_padrao(self) -> None:
        """Popula o dicionário interno com as unidades Métricas e Imperiais."""
        unidades = [
            UnidadeMedida("Quilômetro", "km", 1000.0, "Métrico"),
            UnidadeMedida("Hectômetro", "hm", 100.0, "Métrico"),
            UnidadeMedida("Decâmetro", "dam", 10.0, "Métrico"),
            UnidadeMedida("Metro", "m", 1.0, "Métrico"),
            UnidadeMedida("Decímetro", "dm", 0.1, "Métrico"),
            UnidadeMedida("Centímetro", "cm", 0.01, "Métrico"),
            UnidadeMedida("Milímetro", "mm", 0.001, "Métrico"),
            UnidadeMedida("Milha", "mi", 1609.344, "Imperial"),
            UnidadeMedida("Jarda", "yd", 0.9144, "Imperial"),
            UnidadeMedida("Pé", "ft", 0.3048, "Imperial"),
            UnidadeMedida("Polegada", "in", 0.0254, "Imperial"),
        ]
        for unidade in unidades:
            self._unidades[unidade.simbolo.lower()] = unidade

    @property
    def unidades_disponiveis(self) -> Dict[str, UnidadeMedida]:
        """Retorna uma cópia protegida do dicionário de unidades registradas."""
        return self._unidades.copy()

    def converter(self, valor: float, simbolo_origem: str, simbolo_destino: str) -> float:
        """
        Executa a conversão de um valor numérico entre duas unidades registradas.

        Raises:
            KeyError: Caso uma das unidades informadas não esteja cadastrada.
        """
        origem = simbolo_origem.lower()
        destino = simbolo_destino.lower()

        if origem not in self._unidades or destino not in self._unidades:
            raise KeyError("Uma ou ambas as unidades informadas são inválidas.")

        valor_em_metros = valor * self._unidades[origem].fator_metro
        valor_convertido = valor_em_metros / self._unidades[destino].fator_metro
        return valor_convertido

    def gerar_relatorio_geral(self, valor: float, simbolo_origem: str) -> List[Tuple[UnidadeMedida, float]]:
        """
        Gera uma lista com a conversão do valor de origem para todas as
        unidades cadastradas no sistema.
        """
        origem = simbolo_origem.lower()
        if origem not in self._unidades:
            raise KeyError("Unidade de origem não cadastrada.")

        relatorio = []
        for unidade in self._unidades.values():
            resultado = self.converter(valor, origem, unidade.simbolo)
            relatorio.append((unidade, resultado))

        return relatorio


class AplicacaoConversor:
    """
    Gerenciador da interface de usuário em terminal utilizando a biblioteca Rich.
    Controla o fluxo de execução, entrada de dados e tratamento de exceções.
    """

    def __init__(self) -> None:
        """Inicializa o console e o motor de conversão."""
        self._console = Console()
        self._conversor = ConversorDistancia()

    @staticmethod
    def _formatar_numero(valor: float, precisao_maxima: int = 4) -> str:
        """
        Formata valores numéricos para o padrão brasileiro (ponto no milhar e vírgula no decimal)
        e remove zeros desnecessários à direita.
        """
        texto = f"{valor:,.{precisao_maxima}f}"
        
        if "." in texto:
            parte_inteira, parte_decimal = texto.split(".")
            parte_decimal = parte_decimal.rstrip("0")
        else:
            parte_inteira, parte_decimal = texto, ""

        inteiro_br = parte_inteira.replace(",", ".")

        if parte_decimal:
            return f"{inteiro_br},{parte_decimal}"
        return inteiro_br

    def _exibir_cabecalho(self) -> None:
        """Limpa o terminal e renderiza o painel principal do sistema."""
        self._console.clear()
        conteudo_cabecalho = (
            "[bold cyan]:straight_ruler: CONVERSOR UNIVERSAL DE DISTÂNCIAS :straight_ruler:[/bold cyan]\n"
            "[dim]Sistemas Métrico & Imperial | Engine em POO[/dim]"
        )
        painel = Panel(
            Align.center(conteudo_cabecalho),
            border_style="cyan",
            padding=(1, 2)
        )
        self._console.print(painel)

    def _exibir_menu(self) -> None:
        """Exibe as opções principais de navegação."""
        tabela = Table(show_header=False, box=None, padding=(0, 1))
        tabela.add_row("[bold yellow][1][/bold yellow]", "Conversão Direta (Origem :arrow_right: Destino)")
        tabela.add_row("[bold yellow][2][/bold yellow]", "Matriz de Conversão Completa")
        tabela.add_row("[bold yellow][3][/bold yellow]", "Listar Unidades Suportadas")
        tabela.add_row("[bold red][0][/bold red]", "Sair da Aplicação")
        
        painel_menu = Panel(tabela, title="[bold]Menu de Operações[/bold]", border_style="yellow")
        self._console.print(painel_menu)

    def _listar_unidades(self) -> None:
        """Exibe uma tabela formatada com todas as unidades cadastradas."""
        tabela = Table(title="Unidades de Medida Cadastradas", header_style="bold magenta")
        tabela.add_column("Nome", style="white")
        tabela.add_column("Símbolo", style="cyan", justify="center")
        tabela.add_column("Sistema", style="green", justify="center")
        tabela.add_column("Equivalência em Metros", style="dim", justify="right")

        for u in self._conversor.unidades_disponiveis.values():
            fator_br = self._formatar_numero(u.fator_metro, precisao_maxima=4)
            tabela.add_row(u.nome, u.simbolo, u.sistema, f"{fator_br} m")

        self._console.print(tabela)

    def _obter_unidade_valida(self, mensagem_prompt: str) -> str:
        """
        Solicita repetidamente ao usuário o símbolo de uma unidade até que
        uma opção válida e cadastrada no motor de conversão seja digitada.
        """
        while True:
            unidade = Prompt.ask(mensagem_prompt).strip().lower()
            if unidade in self._conversor.unidades_disponiveis:
                return unidade
            self._console.print(
                "[bold red]:warning: Unidade inválida![/bold red] "
                "Digite uma unidade registrada (ex: m, km, cm, in, ft, mi)."
            )

    def _obter_valor_valido(self, mensagem_prompt: str) -> float:
        """
        Solicita repetidamente ao usuário um valor numérico até que
        uma entrada válida seja informada.
        """
        while True:
            entrada = Prompt.ask(mensagem_prompt).strip().replace(",", ".")
            try:
                valor = float(entrada)
                return valor
            except ValueError:
                self._console.print(
                    "[bold red]:warning: Valor numérico inválido![/bold red] "
                    "Por favor, insira um número válido."
                )

    def _executar_conversao_direta(self) -> None:
        """Processa a conversão pontual entre duas unidades escolhidas pelo usuário."""
        origem = self._obter_unidade_valida("\n:small_blue_diamond: Digite a unidade de [bold cyan]origem[/bold cyan] (ex: m, km, in)")
        destino = self._obter_unidade_valida(":small_blue_diamond: Digite a unidade de [bold cyan]destino[/bold cyan] (ex: ft, mi, cm)")
        valor = self._obter_valor_valido(":small_blue_diamond: Digite o valor a ser convertido")

        with self._console.status("[bold green]Processando cálculo...", spinner="dots"):
            time.sleep(0.4)
            resultado = self._conversor.converter(valor, origem, destino)

        u_origem = self._conversor.unidades_disponiveis[origem]
        u_destino = self._conversor.unidades_disponiveis[destino]

        valor_origem_fmt = self._formatar_numero(valor)
        resultado_fmt = self._formatar_numero(resultado)

        mensagem = (
            f"[bold white]{valor_origem_fmt} {u_origem.simbolo}[/bold white] ({u_origem.nome}) "
            f"corresponde a\n[bold green]{resultado_fmt} {u_destino.simbolo}[/bold green] ({u_destino.nome})"
        )
        
        painel_resultado = Panel(Align.center(mensagem), title=":sparkles: Resultado", border_style="green")
        self._console.print(painel_resultado)

    def _executar_matriz_completa(self) -> None:
        """Exibe a conversão de uma medida de origem em relação a todas as outras."""
        origem = self._obter_unidade_valida("\n:small_blue_diamond: Digite a unidade de [bold cyan]origem[/bold cyan] (ex: m, km, mi)")
        valor = self._obter_valor_valido(":small_blue_diamond: Digite o valor a ser analisado")

        with self._console.status("[bold green]Gerando matriz completa...", spinner="dots"):
            time.sleep(0.4)
            relatorio = self._conversor.gerar_relatorio_geral(valor, origem)

        u_origem = self._conversor.unidades_disponiveis[origem]
        valor_origem_fmt = self._formatar_numero(valor)
        
        tabela = Table(title=f"Matriz de Conversão para {valor_origem_fmt} {u_origem.simbolo}", header_style="bold blue")
        tabela.add_column("Sistema", style="magenta")
        tabela.add_column("Unidade", style="white")
        tabela.add_column("Símbolo", style="cyan", justify="center")
        tabela.add_column("Valor Convertido", style="bold green", justify="right")

        for unidade, val_convertido in relatorio:
            val_fmt = self._formatar_numero(val_convertido, precisao_maxima=6)
            tabela.add_row(
                unidade.sistema,
                unidade.nome,
                unidade.simbolo,
                val_fmt
            )

        self._console.print(tabela)

    def iniciar(self) -> None:
        """Loop principal da aplicação com tratamento gracioso de encerramento."""
        while True:
            try:
                self._exibir_cabecalho()
                self._exibir_menu()
                
                opcao = Prompt.ask("\n[bold]Escolha uma opção[/bold]", choices=["0", "1", "2", "3"])

                if opcao == "1":
                    self._executar_conversao_direta()
                elif opcao == "2":
                    self._executar_matriz_completa()
                elif opcao == "3":
                    self._listar_unidades()
                elif opcao == "0":
                    self._console.print("\n[bold cyan]:door: Aplicação encerrada com sucesso. Até logo![/bold cyan]")
                    sys.exit(0)

                Prompt.ask("\n[dim]Pressione ENTER para continuar...[/dim]")

            except KeyboardInterrupt:
                self._console.print("\n\n[bold yellow]:warning: Execução interrompida pelo usuário (Ctrl+C). Saindo...[/bold yellow]")
                sys.exit(0)


if __name__ == "__main__":
    app = AplicacaoConversor()
    app.iniciar()