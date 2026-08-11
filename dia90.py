"""
Módulo de Telemetria e Análise de Desempenho com Layout de Painel Duplo.

Fornece uma interface de terminal profissional (Rich Layout) com histórico
de sessões, seleção de algoritmo de média e customização visual.
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.layout import Layout


class PerformanceMetrics:
    """
    Motor matemático para cálculo de estatísticas e acumuladores de fluxo.
    """

    def __init__(self, metric_name: str = "Tempo", unit: str = "s", mode: str = "Aritmética"):
        """
        Inicializa o agregador de métricas.

        :param metric_name: Nome da métrica monitorada.
        :param unit: Unidade de medida.
        :param mode: Tipo de média ('Aritmética' ou 'Truncada').
        """
        self._metric_name = metric_name
        self._unit = unit
        self._mode = mode
        self._records: list[float] = []
        self._sum = 0.0
        self._max = None
        self._min = None

    @property
    def metric_name(self) -> str:
        """Retorna o nome da métrica atual."""
        return self._metric_name

    @property
    def unit(self) -> str:
        """Retorna a unidade de medida."""
        return self._unit

    @property
    def mode(self) -> str:
        """Retorna o algoritmo de média selecionado."""
        return self._mode

    @property
    def count(self) -> int:
        """Retorna o número total de entradas registradas."""
        return len(self._records)

    @property
    def average(self) -> float:
        """Calcula a média com base no algoritmo escolhido."""
        if not self._records:
            return 0.0

        if self._mode == "Truncada" and len(self._records) > 2:
            sorted_data = sorted(self._records)
            trimmed_data = sorted_data[1:-1]
            return sum(trimmed_data) / len(trimmed_data)

        return self._sum / len(self._records)

    @property
    def max_value(self) -> float | None:
        """Retorna o maior valor registrado."""
        return self._max

    @property
    def min_value(self) -> float | None:
        """Retorna o menor valor registrado."""
        return self._min

    def register(self, value: float) -> None:
        """
        Insere uma nova leitura no acumulador.

        :param value: Valor numérico positivo.
        """
        self._records.append(value)
        self._sum += value

        if len(self._records) == 1:
            self._max = value
            self._min = value
        else:
            if value > self._max:
                self._max = value
            if value < self._min:
                self._min = value

    def reset(self) -> None:
        """Limpa as métricas atuais mantendo as configurações de sessão."""
        self._records.clear()
        self._sum = 0.0
        self._max = None
        self._min = None


class PerformanceTrackerApp:
    """
    Controlador do Dashboard em Terminal utilizando o Rich Layout.
    """

    def __init__(self):
        """Inicializa o console, métricas e histórico de sessões anteriores."""
        self._console = Console()
        self._metrics = PerformanceMetrics()
        self._session_history: list[dict] = []
        self._theme_color = "green"

    def run(self) -> None:
        """Inicia a aplicação de monitoramento."""
        try:
            self._setup_session()
            self._main_loop()
        except KeyboardInterrupt:
            self._console.print("\n[bold red]:no_entry: Execução encerrada pelo usuário.[/bold red]")
            sys.exit(0)
        except Exception as err:
            self._console.print(f"\n[bold red]:warning: Falha crítica no sistema: {err}[/bold red]")
            sys.exit(1)

    def _setup_session(self) -> None:
        """Configurações iniciais da sessão e preferências da UI."""
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold green]:gear: CONFIGURAÇÃO DE TELEMETRIA[/bold green]\n"
                "[dim]Personalize os parâmetros do monitoramento[/dim]",
                border_style="blue"
            )
        )

        metric = Prompt.ask("[bold white]Métrica a ser Medida[/bold white]", default="Lap Time")
        unit = Prompt.ask("[bold white]Unidade de Medida[/bold white]", default="s")
        
        self._console.print("\n[bold white]Tipos de Média disponíveis:[/bold white]")
        self._console.print("1. [bold green]Aritmética[/bold green] (Padrão para todas as leituras)")
        self._console.print("2. [bold green]Truncada[/bold green] (Descarta o maior e o menor extremo no cálculo)")
        
        mode_choice = Prompt.ask("[bold white]Escolha o tipo [1/2][/bold white]", choices=["1", "2"], default="1")
        avg_mode = "Aritmética" if mode_choice == "1" else "Truncada"

        theme_choice = Prompt.ask(
            "[bold white]Tema de Cor[/bold white] [dim](green/blue/red/cyan)[/dim]", 
            choices=["green", "blue", "red", "cyan"], 
            default="green"
        )
        self._theme_color = theme_choice

        self._metrics = PerformanceMetrics(metric_name=metric, unit=unit, mode=avg_mode)

    def _build_active_panel(self) -> Panel:
        """Constrói a tabela do painel esquerdo (Sessão Ativa)."""
        table = Table(expand=True, border_style=self._theme_color)
        table.add_column("Indicador", style="white", justify="left")
        table.add_column("Métrica do Momento", justify="right")

        table.add_row("Nome do Teste", f"[bold white]{self._metrics.metric_name}[/bold white]")
        table.add_row("Modo de Média", f"[bold cyan]{self._metrics.mode}[/bold cyan]")
        table.add_row("Total de Entradas", f"[white]{self._metrics.count}[/white]")

        avg_str = f"{self._metrics.average:.2f} {self._metrics.unit}"
        table.add_row("Média Atual", f"[bold white]{avg_str}[/bold white]")

        min_str = f"{self._metrics.min_value:.2f} {self._metrics.unit}" if self._metrics.min_value is not None else "N/A"
        table.add_row("Mínimo (Recorde)", f"[bold green]:stopwatch: {min_str}[/bold green]")

        max_str = f"{self._metrics.max_value:.2f} {self._metrics.unit}" if self._metrics.max_value is not None else "N/A"
        table.add_row("Máximo (Pico)", f"[bold red]:chart_with_upwards_trend: {max_str}[/bold red]")

        return Panel(table, title=f"[{self._theme_color}]:rocket: TELEMETRIA ATIVA[/{self._theme_color}]", border_style=self._theme_color)

    def _build_history_panel(self) -> Panel:
        """Constrói a tabela do painel direito (Histórico de Testes)."""
        table = Table(expand=True, border_style="blue")
        table.add_column("Sessão", style="white")
        table.add_column("Mín", justify="right", style="green")
        table.add_column("Máx", justify="right", style="red")
        table.add_column("Média", justify="right", style="white")

        if not self._session_history:
            table.add_row("[dim]Nenhum[/dim]", "[dim]-[/dim]", "[dim]-[/dim]", "[dim]-[/dim]")
        else:
            for item in reversed(self._session_history[-5:]):
                table.add_row(
                    item["name"],
                    f"{item['min']:.2f}{item['unit']}",
                    f"{item['max']:.2f}{item['unit']}",
                    f"{item['avg']:.2f}{item['unit']}"
                )

        return Panel(table, title="[bold blue]:scroll: HISTÓRICO RECENTE[/bold blue]", border_style="blue")

    def _render_dashboard(self) -> None:
        """Renderiza o layout dividido em duas colunas no terminal."""
        layout = Layout()
        layout.split_row(
            Layout(self._build_active_panel(), name="left", ratio=1),
            Layout(self._build_history_panel(), name="right", ratio=1)
        )
        self._console.clear()
        self._console.print(layout)

    def _archive_current_session(self) -> None:
        """Guarda os dados da sessão atual no histórico antes de resetar ou mudar."""
        if self._metrics.count > 0:
            self._session_history.append({
                "name": self._metrics.metric_name,
                "min": self._metrics.min_value,
                "max": self._metrics.max_value,
                "avg": self._metrics.average,
                "unit": self._metrics.unit
            })

    def _main_loop(self) -> None:
        """Loop interativo de inserção e comando."""
        while True:
            self._render_dashboard()

            raw = Prompt.ask(
                "\n[bold white]Entrada[/bold white] [dim]('N' nova sessão, 'R' reset, 'S' sair)[/dim]"
            ).strip().upper()

            if raw == 'S':
                self._archive_current_session()
                self._console.print("\n[bold blue]Telemetria encerrada com sucesso![/bold blue]")
                break

            if raw == 'N':
                self._archive_current_session()
                self._setup_session()
                continue

            if raw == 'R':
                with self._console.status("[bold red]Resetando sessão...[/bold red]", spinner="dots"):
                    time.sleep(0.5)
                self._metrics.reset()
                continue

            try:
                val = float(raw)
                if val < 0:
                    self._console.print("[bold red]:x: Digite apenas números positivos![/bold red]")
                    time.sleep(1.2)
                    continue

                self._metrics.register(val)
            except ValueError:
                self._console.print("[bold red]:x: Entrada inválida! Insira um número.[/bold red]")
                time.sleep(1.2)


if __name__ == "__main__":
    app = PerformanceTrackerApp()
    app.run()