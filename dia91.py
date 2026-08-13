import math
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import FloatPrompt


class PerfilMetalico:
    """Representa uma estrutura triangular de perfis metálicos para cálculo orçamentário.

    Aplica o teorema da desigualdade triangular, calcula o perímetro total de material,
    a área delimitada e o custo final da estrutura.
    """

    def __init__(self, lado_a: float, lado_b: float, lado_c: float, preco_por_metro: float):
        """Inicializa as dimensões e o valor do metro do perfil."""
        self._lado_a = lado_a
        self._lado_b = lado_b
        self._lado_c = lado_c
        self._preco_por_metro = preco_por_metro

    @property
    def lado_a(self) -> float:
        """Retorna a medida da haste A em metros."""
        return self._lado_a

    @property
    def lado_b(self) -> float:
        """Retorna a medida da haste B em metros."""
        return self._lado_b

    @property
    def lado_c(self) -> float:
        """Retorna a medida da haste C em metros."""
        return self._lado_c

    @property
    def preco_por_metro(self) -> float:
        """Retorna o custo por metro do material."""
        return self._preco_por_metro

    def eh_triangulo_valido(self) -> bool:
        """Valida a viabilidade geométrica através da Desigualdade Triangular."""
        a, b, c = self._lado_a, self._lado_b, self._lado_c
        return (a < b + c) and (b < a + c) and (c < a + b)

    def classificar_estrutura(self) -> str:
        """Determina a classificação geométrica e aplicação técnica recomendada."""
        a, b, c = self._lado_a, self._lado_b, self._lado_c
        if math.isclose(a, b) and math.isclose(b, c):
            return "Equilátero (Distribuição uniforme de carga)"
        elif math.isclose(a, b) or math.isclose(b, c) or math.isclose(a, c):
            return "Isósceles (Recomendado para suportes em esquadro)"
        return "Escaleno (Geometria adaptada para coberturas específicas)"

    def calcular_perimetro(self) -> float:
        """Calcula a metragem linear total necessária."""
        return self._lado_a + self._lado_b + self._lado_c

    def calcular_area(self) -> float:
        """Calcula a área coberta pela estrutura utilizando a Formula de Heron."""
        s = self.calcular_perimetro() / 2
        a, b, c = self._lado_a, self._lado_b, self._lado_c
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def calcular_custo_total(self) -> float:
        """Calcula o custo total do material bruto."""
        return self.calcular_perimetro() * self._preco_por_metro


class OrcadorSerralheriaApp:
    """Controlador da interface gráfica de terminal para o sistema de orçamentos."""

    def __init__(self):
        """Inicializa o console da biblioteca Rich."""
        self._console = Console()

    def _exibir_cabecalho(self) -> None:
        """Exibe o cabeçalho institucional do sistema."""
        self._console.clear()
        painel = Panel(
            "[bold cyan]SISTEMA DE ORÇAMENTO TÉCNICO - ESTRUTURAS METÁLICAS[/bold cyan]\n"
            "[white]Módulo de Validação Geométrica e Análise Financeira[/white]",
            border_style="cyan",
            expand=False,
        )
        self._console.print(painel)

    def _ler_float_positivo(self, mensagem: str) -> float:
        """Valida e retorna uma entrada numérica estritamente positiva."""
        while True:
            try:
                valor = FloatPrompt.ask(mensagem)
                if valor <= 0:
                    self._console.print("[bold red]O valor deve ser estritamente superior a zero.[/bold red]")
                    continue
                return valor
            except Exception:
                self._console.print("[bold red]Entrada inválida. Insira um número válido.[/bold red]")

    def _gerar_tabela_orcamento(self, estrutura: PerfilMetalico) -> Table:
        """Gera a tabela formatada com o resumo técnico do orçamento."""
        tabela = Table(title="Demonstrativo Financeiro e Técnico", border_style="blue")
        tabela.add_column("Especificação", style="cyan", justify="left")
        tabela.add_column("Métrica", style="bold green", justify="right")

        tabela.add_row("Classificação Estrutural", estrutura.classificar_estrutura())
        tabela.add_row("Dimensões (A | B | C)", f"{estrutura.lado_a:.2f}m | {estrutura.lado_b:.2f}m | {estrutura.lado_c:.2f}m")
        tabela.add_row("Metragem Linear (Perímetro)", f"{estrutura.calcular_perimetro():.2f} m")
        tabela.add_row("Área Interna Delimitada", f"{estrutura.calcular_area():.2f} m²")
        tabela.add_row("Custo Unitário (Metro)", f"R$ {estrutura.preco_por_metro:.2f}")
        tabela.add_row("VALOR TOTAL DO MATERIAL", f"R$ {estrutura.calcular_custo_total():.2f}")
        return tabela

    def executar(self) -> None:
        """Executa a sequência de processamento do orçamento."""
        try:
            self._exibir_cabecalho()
            self._console.print("[bold cyan]Informe as especificações do perfil em metros:[/bold cyan]\n")

            a = self._ler_float_positivo("Comprimento da Haste A")
            b = self._ler_float_positivo("Comprimento da Haste B")
            c = self._ler_float_positivo("Comprimento da Haste C")
            preco = self._ler_float_positivo("Custo por metro do perfil (R$)")

            estrutura = PerfilMetalico(a, b, c, preco)

            if not estrutura.eh_triangulo_valido():
                self._console.print(Panel(
                    "[bold red]INVIABILIDADE ESTRUTURAL DETECTADA[/bold red]\n\n"
                    "As dimensões fornecidas não atendem ao Teorema da Desigualdade Triangular.\n"
                    "A soma de dois lados deve ser estritamente maior que o terceiro lado.",
                    border_style="red",
                ))
                return

            self._console.print("\n", self._gerar_tabela_orcamento(estrutura))
            self._console.print("\n[bold green]Orçamento processado com sucesso.[/bold green]")

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]Execução interrompida pelo usuário. Encerramento seguro.[/bold yellow]")
        except Exception as e:
            self._console.print(f"\n[bold red]Falha crítica na execução do programa: {e}[/bold red]")


if __name__ == "__main__":
    OrcadorSerralheriaApp().executar()