from math import sqrt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.spinner import Spinner

console = Console()

class ValidadorEstrutural:
    def __init__(self, l1: float, l2: float, l3: float) -> None:
        """Inicializa os segmentos estruturais do triângulo com atributos protegidos."""
        self._l1 = float(l1)
        self._l2 = float(l2)
        self._l3 = float(l3)

    @property
    def l1(self) -> float:
        """Retorna o valor do primeiro segmento."""
        return self._l1

    @property
    def l2(self) -> float:
        """Retorna o valor do segundo segmento."""
        return self._l2

    @property
    def l3(self) -> float:
        """Retorna o valor do terceiro segmento."""
        return self._l3

    def verificar_existencia(self) -> bool:
        """Valida se os segmentos atendem à desigualdade triangular."""
        return (
            self._l1 < self._l2 + self._l3 and
            self._l2 < self._l1 + self._l3 and
            self._l3 < self._l1 + self._l2
        )

    def calcular_perimetro(self) -> float:
        """Calcula o perímetro total do elemento estrutural."""
        return self._l1 + self._l2 + self._l3

    def calcular_area_heron(self) -> float:
        """Calcula a área da superfície utilizando a fórmula de Heron."""
        s = self.calcular_perimetro() / 2
        return sqrt(s * (s - self._l1) * (s - self._l2) * (s - self._l3))

    def classificar_lados(self) -> str:
        """Classifica o elemento estrutural com base na simetria das arestas."""
        if self._l1 == self._l2 == self._l3:
            return "Equilátero (Simetria estrutural perfeita)"
        elif self._l1 == self._l2 or self._l1 == self._l3 or self._l2 == self._l3:
            return "Isósceles (Simetria estrutural parcial)"
        return "Escaleno (Arestas assimétricas)"

    def classificar_angulos(self) -> str:
        """Classifica o elemento com base nos ângulos internos usando a Lei dos Cossenos."""
        lados = sorted([self._l1, self._l2, self._l3])
        a, b, c = lados[0], lados[1], lados[2]
        
        c_sq = c ** 2
        soma_ab_sq = (a ** 2) + (b ** 2)
        
        if c_sq == soma_ab_sq:
            return "Retângulo (Ângulo de 90 graus na aresta maior)"
        elif c_sq < soma_ab_sq:
            return "Acutângulo (Todos os ângulos internos agudos)"
        else:
            return "Obtusângulo (Contém ângulo interno obtuso)"


class InterfaceCLI:
    def __init__(self) -> None:
        """Inicializa a interface de linha de comando com a engine Rich."""
        self._console = console

    def exibir_cabecalho(self) -> None:
        """Exibe o painel de cabeçalho corporativo do sistema."""
        painel = Panel(
            "[bold cyan]:triangular_ruler: MÓDULO DE ANÁLISE E VALIDAÇÃO ESTRUTURAL GEOMÉTRICA[/bold cyan]\n"
            "[dim]Sistema profissional para verificação de integridade e propriedades de elementos triangulares[/dim]",
            border_style="cyan",
            expand=False
        )
        self._console.print(painel)

    def coletar_segmentos(self) -> tuple[float, float, float]:
        """Coleta os dados de entrada do operador com validação rigorosa de tipo e faixa."""
        self._console.print("\n[bold yellow]:gear: Insira as dimensões dos segmentos estruturais:[/bold yellow]")
        
        segmentos = []
        nomes = ["Primeiro", "Segundo", "Terceiro"]
        
        for nome in nomes:
            while True:
                try:
                    valor = float(self._console.input(f"  [cyan]•[/cyan] {nome} segmento [dim](unidade de medida)[/dim]: "))
                    if valor <= 0:
                        self._console.print("[bold red]:x: Erro: O segmento deve possuir valor numérico estritamente positivo.[/bold red]")
                        continue
                    segmentos.append(valor)
                    break
                except ValueError:
                    self._console.print("[bold red]:x: Erro: Entrada inválida. Digite apenas valores numéricos reais.[/bold red]")
                except Exception as erro:
                    self._console.print(f"[bold red]:x: Erro inesperado no fluxo de entrada: {erro}[/bold red]")
                    
        return tuple(segmentos)

    def executar_analise(self) -> None:
        """Controla o fluxo principal de execução da aplicação de forma resiliente."""
        try:
            self._console.clear()
            self.exibir_cabecalho()
            
            l1, l2, l3 = self.coletar_segmentos()
            
            self._console.print()
            with self._console.status("[bold green]:hourglass_flowing_sand: Processando matriz geométrica e cálculos estruturais...[/bold green]", spinner="dots"):
                import time
                time.sleep(1.2)
                triangulo = ValidadorEstrutural(l1, l2, l3)
                valido = triangulo.verificar_existencia()

            self._console.print()
            if valido:
                tabela = Table(title="[bold green]:white_check_mark: RELATÓRIO DE VIABILIDADE ESTRUTURAL: APROVADO[/bold green]", border_style="green")
                tabela.add_column("Métrica Analítica", style="cyan", no_wrap=True)
                tabela.add_column("Especificação Técnica", style="magenta")

                tabela.add_row("Status de Existência", "[bold green]Viável (Forma um triângulo válido)[/bold green]")
                tabela.add_row("Perímetro Total", f"{triangulo.calcular_perimetro():.2f} unidades")
                tabela.add_row("Área da Superfície (Heron)", f"{triangulo.calcular_area_heron():.2f} unidades²")
                tabela.add_row("Classificação Tipológica (Lados)", triangulo.classificar_lados())
                tabela.add_row("Classificação Tipológica (Ângulos)", triangulo.classificar_angulos())

                painel_resultado = Panel(tabela, border_style="green", padding=(1, 2))
                self._console.print(painel_resultado)
            else:
                painel_erro = Panel(
                    "[bold red]:x: RELATÓRIO DE VIABILIDADE ESTRUTURAL: REPROVADO[/bold red]\n\n"
                    "Os segmentos informados [bold]NÃO[/bold] cumprem a condição matemática de existência.\n"
                    "[dim]A soma de dois lados quaisquer deve ser sempre estritamente maior que o terceiro lado.[/dim]",
                    border_style="red",
                    expand=False
                )
                self._console.print(painel_erro)

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]:warning: Operação interrompida pelo operador (Ctrl+C). Encerrando o sistema com segurança.[/bold yellow]")
        except Exception as erro:
            self._console.print(f"\n[bold red]:x: Falha crítica no sistema: {erro}. Contate o suporte técnico.[/bold red]")


if __name__ == "__main__":
    app = InterfaceCLI()
    app.executar_analise()