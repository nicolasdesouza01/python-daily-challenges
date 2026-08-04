"""
Módulo de Análise Preditiva e Gestão Linear de Insumos.
Aplica o modelo matemático de Progressão Aritmética para cálculo de variação
de estoque, estimativa de esgotamento e projeção de ressuprimento.
"""

from datetime import datetime, timedelta
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, Prompt
from rich.style import Style
from rich.table import Table

console = Console()


class InsumoEstoque:
    """
    Abstração do item de estoque e sua taxa de variação diária constante.
    """

    def __init__(
        self,
        nome: str,
        quantidade_atual: float,
        consumo_diario: float,
        estoque_seguranca: float,
    ):
        """
        Define os parâmetros operacionais do item e a razão de variação diária.
        """
        self._nome = nome
        self._quantidade_atual = quantidade_atual
        self._consumo_diario = consumo_diario
        self._estoque_seguranca = estoque_seguranca

    @property
    def nome(self) -> str:
        """
        Retorna a identificação do insumo.
        """
        return self._nome

    @property
    def quantidade_atual(self) -> float:
        """
        Retorna o volume atual disponível no inventário.
        """
        return self._quantidade_atual

    @property
    def consumo_diario(self) -> float:
        """
        Retorna a taxa diária de demanda (razão do modelo linear).
        """
        return self._consumo_diario

    @property
    def estoque_seguranca(self) -> float:
        """
        Retorna o ponto crítico de ressuprimento.
        """
        return self._estoque_seguranca

    def calcular_projecao_linear(self, dias: int) -> list[dict]:
        """
        Aplica a equação da Progressão Aritmética para projetar o estoque futuro.
        Termo Geral: a_n = a_1 + (n - 1) * r
        """
        historico = []
        data_base = datetime.now()

        for dia in range(1, dias + 1):
            # Correção efetuada: parâmetro aceito pelo timedelta é 'days'
            data_termo = data_base + timedelta(days=dia - 1)
            saldo_termo = self._quantidade_atual - (
                (dia - 1) * self._consumo_diario
            )

            status = "Estável"
            estilo_status = "bold green"

            if saldo_termo <= 0:
                saldo_termo = 0.0
                status = "Esgotado"
                estilo_status = "bold red"
            elif saldo_termo <= self._estoque_seguranca:
                status = "Abaixo da Segurança"
                estilo_status = "bold yellow"

            historico.append(
                {
                    "dia": dia,
                    "data": data_termo.strftime("%d/%m/%Y"),
                    "saldo": saldo_termo,
                    "status": status,
                    "estilo": estilo_status,
                }
            )

            if saldo_termo == 0:
                break

        return historico

    def calcular_dias_ate_estoque_seguranca(self) -> int:
        """
        Estima o tempo de cobertura restante até o nível de segurança.
        """
        if self._quantidade_atual <= self._estoque_seguranca:
            return 0
        dias = (
            self._quantidade_atual - self._estoque_seguranca
        ) / self._consumo_diario
        return int(dias)


class ProcessadorPrevisaoEstoque:
    """
    Controlador de execução das simulações e renderização do painel analítico.
    """

    def renderizar_cabecalho(self) -> Panel:
        """
        Gera o painel superior com estética corporativa.
        """
        texto = "[bold slate_blue1]SISTEMA DE ANÁLISE PREDITIVA DE INVENTÁRIO[/bold slate_blue1]\n"
        texto += "[dim]Modelo Matemático: Progressão Aritmética de Demanda Contínua[/dim]"
        return Panel(
            texto,
            style=Style(color="cyan"),
            title="[bold white]Supply Chain Analytics[/bold white]",
            border_style="blue",
        )

    def processar_simulacao(
        self, item: InsumoEstoque, dias: int
    ) -> Table | None:
        """
        Executa a animação de cálculo e gera a tabela de resultados.
        """
        with console.status(
            "[bold cyan]Processando modelo de regressão linear...",
            spinner="dots12",
        ):
            time.sleep(1.0)

        projecao = item.calcular_projecao_linear(dias)

        tabela = Table(
            title=f"Projeção Preditiva - {item.nome}",
            header_style="bold cyan",
            border_style="bright_blue",
        )
        tabela.add_column("Período (Dia)", justify="center", style="bold white")
        tabela.add_column("Data Estimada", justify="center", style="cyan")
        tabela.add_column(
            "Saldo Previsto (UN)", justify="right", style="bright_white"
        )
        tabela.add_column("Status Operacional", justify="left")

        for registro in projecao:
            tabela.add_row(
                str(registro["dia"]),
                registro["data"],
                f"{registro['saldo']:.2f}",
                f"[{registro['estilo']}]{registro['status']}[/{registro['estilo']}]",
            )

        return tabela


def executar_sistema() -> None:
    """
    Garante o loop seguro de simulação do módulo.
    """
    processador = ProcessadorPrevisaoEstoque()

    while True:
        try:
            console.clear()
            console.print(processador.renderizar_cabecalho())

            console.print("\n[bold cyan]Opções de Operação:[/bold cyan]")
            console.print("1. Iniciar Nova Simulação de Consumo")
            console.print("2. Encerrar Módulo\n")

            opcao = Prompt.ask(
                "Selecione uma opção", choices=["1", "2"], default="1"
            )

            if opcao == "2":
                with console.status(
                    "[bold cyan]Finalizando sessões e desalocando memória...",
                    spinner="arc",
                ):
                    time.sleep(0.8)
                console.print(
                    "\n[bold blue]Módulo finalizado com sucesso.[/bold blue]"
                )
                break

            console.print(
                "\n[bold white]--- Entrada de Parâmetros Operacionais ---[/bold white]"
            )
            nome = Prompt.ask("Identificação do Insumo/Material")
            qtd_atual = FloatPrompt.ask(
                "Volume Atual em Inventário (Quantidade)"
            )
            consumo = FloatPrompt.ask(
                "Taxa Média de Demanda Diária (Razão de Desgaste)"
            )
            seguranca = FloatPrompt.ask("Estoque Mínimo de Segurança")

            entrada_dias = Prompt.ask(
                "Horizonte de Projeção em Dias", default="10"
            )
            try:
                dias_projecao = int(entrada_dias)
            except ValueError:
                dias_projecao = 10

            if consumo <= 0:
                console.print(
                    "\n[bold red]Inconsistência de Dados:[/bold red] A taxa de demanda deve ser estritamente superior a zero."
                )
                Prompt.ask("\nPressione [Enter] para continuar...")
                continue

            item = InsumoEstoque(
                nome=nome,
                quantidade_atual=qtd_atual,
                consumo_diario=consumo,
                estoque_seguranca=seguranca,
            )

            tabela_resultado = processador.processar_simulacao(
                item, dias_projecao
            )

            console.clear()
            console.print(processador.renderizar_cabecalho())
            console.print("\n", tabela_resultado)

            dias_critico = item.calcular_dias_ate_estoque_seguranca()
            console.print(
                Panel(
                    f"Ponto de Atenção: O item [bold cyan]{item.nome}[/bold cyan] atingirá o limite do estoque de segurança em aproximadamente [bold yellow]{dias_critico} dia(s)[/bold yellow].",
                    title="[bold yellow]Análise de Cobertura[/bold yellow]",
                    border_style="yellow",
                )
            )

            Prompt.ask("\nPressione [Enter] para retornar ao menu principal...")

        except (KeyboardInterrupt, EOFError):
            console.print("\n")
            with console.status(
                "[bold red]Interrupção forçada. Encerrando processos...",
                spinner="moon",
            ):
                time.sleep(0.6)
            console.print(
                "[bold red]Operação cancelada pelo usuário.[/bold red]"
            )
            break
        except Exception as erro:
            console.print(
                f"\n[bold red]Falha na execução do processo:[/bold red] {erro}"
            )
            Prompt.ask("\nPressione [Enter] para tentar novamente...")


if __name__ == "__main__":
    executar_sistema()