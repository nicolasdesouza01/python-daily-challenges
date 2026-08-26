import math
import sys
import time
from typing import Dict, List, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class Vector2D:
    """Representa um vetor bidimensional e suas operações de álgebra linear."""

    def __init__(self, x: float, y: float):
        """Inicializa as componentes x e y do vetor."""
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float:
        """Retorna a componente X do vetor."""
        return self._x

    @property
    def y(self) -> float:
        """Retorna a componente Y do vetor."""
        return self._y

    def magnitude(self) -> float:
        """Calcula a norma euclidiana (comprimento) do vetor."""
        return math.sqrt(self._x**2 + self._y**2)

    def normalize(self) -> "Vector2D":
        """Retorna o vetor unitário na mesma direção."""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0.0, 0.0)
        return Vector2D(self._x / mag, self._y / mag)

    def dot(self, other: "Vector2D") -> float:
        """Calcula o produto escalar entre este vetor e outro vetor 2D."""
        return self._x * other.x + self._y * other.y

    def distance_to(self, other: "Vector2D") -> float:
        """Calcula a distância euclidiana até outro ponto no espaço 2D."""
        return math.sqrt((self._x - other.x) ** 2 + (self._y - other.y) ** 2)


class RadarGate:
    """Representa um ponto individual de amostragem no feixe do radar (Portão de Varredura)."""

    def __init__(self, position: Vector2D):
        """Inicializa as variáveis de amostragem meteorológica para a coordenada dada."""
        self._position = position
        self._reflectivity_dbz = 0.0
        self._radial_velocity = 0.0
        self._differential_reflectivity = 0.0
        self._correlation_coefficient = 1.0

    @property
    def position(self) -> Vector2D:
        """Retorna a posição espacial do portão de radar."""
        return self._position

    @property
    def reflectivity_dbz(self) -> float:
        """Retorna o valor de refletividade em dBZ."""
        return self._reflectivity_dbz

    @reflectivity_dbz.setter
    def reflectivity_dbz(self, value: float):
        """Define o valor de refletividade do portão."""
        self._reflectivity_dbz = max(0.0, min(75.0, float(value)))

    @property
    def radial_velocity(self) -> float:
        """Retorna a velocidade radial Doppler em m/s."""
        return self._radial_velocity

    @radial_velocity.setter
    def radial_velocity(self, value: float):
        """Define o valor da velocidade radial Doppler."""
        self._radial_velocity = float(value)

    @property
    def correlation_coefficient(self) -> float:
        """Retorna o coeficiente de correlação de dupla polarização (RhoHV)."""
        return self._correlation_coefficient

    @correlation_coefficient.setter
    def correlation_coefficient(self, value: float):
        """Define o valor do coeficiente de correlação RhoHV (0.0 a 1.0)."""
        self._correlation_coefficient = max(0.0, min(1.0, float(value)))


class RankineVortexModel:
    """Modelo físico-matemático de um mesociclone baseado em Vórtice Combinado de Rankine."""

    def __init__(self, center: Vector2D, core_radius: float, max_velocity: float):
        """Inicializa os parâmetros dinâmicos da supercélula e rotação mesociclônica."""
        self._center = center
        self._core_radius = max(0.5, float(core_radius))
        self._max_velocity = float(max_velocity)
        self._environmental_wind = Vector2D(16.0, 6.0)

    @property
    def center(self) -> Vector2D:
        """Retorna a posição central do mesociclone."""
        return self._center

    @center.setter
    def center(self, new_center: Vector2D):
        """Atualiza a posição central da estrutura tempestuosa."""
        self._center = new_center

    def calculate_wind_vector(self, point: Vector2D) -> Vector2D:
        """Calcula o vetor de vento total no ponto combinando campo ambiente e cinemática do vórtice."""
        dx = point.x - self._center.x
        dy = point.y - self._center.y
        r = math.sqrt(dx**2 + dy**2)

        if r == 0:
            return self._environmental_wind

        angle = math.atan2(dy, dx)

        if r <= self._core_radius:
            v_tangential = self._max_velocity * (r / self._core_radius)
        else:
            v_tangential = self._max_velocity * (self._core_radius / r)

        v_inflow = -0.32 * v_tangential

        v_rot_x = -v_tangential * math.sin(angle)
        v_rot_y = v_tangential * math.cos(angle)

        v_inf_x = v_inflow * math.cos(angle)
        v_inf_y = v_inflow * math.sin(angle)

        total_x = self._environmental_wind.x + v_rot_x + v_inf_x
        total_y = self._environmental_wind.y + v_rot_y + v_inf_y

        return Vector2D(total_x, total_y)

    def calculate_reflectivity(self, point: Vector2D) -> float:
        """Sintetiza o eco de refletividade (dBZ) expandido incluindo a estrutura do eco em gancho."""
        dx = point.x - self._center.x
        dy = point.y - self._center.y
        r = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)

        core_factor = math.exp(-(r**2) / 75.0) * 62.0

        spiral_angle = angle - 1.5 * (r / 10.0)
        hook_intensity = math.exp(-((r - 7.0) ** 2) / 12.0) * math.exp(
            -((math.sin(spiral_angle / 2)) ** 2) * 2.8
        )
        hook_factor = hook_intensity * 56.0

        rfd_precipitation = math.exp(-((dx - 5.0) ** 2 + (dy + 3.0) ** 2) / 45.0) * 68.0

        total_dbz = max(core_factor, max(hook_factor, rfd_precipitation))
        return min(75.0, total_dbz)


class DopplerRadarEngine:
    """Motor de processamento de sinal do radar Doppler e análise de dupla polarização."""

    def __init__(self, grid_size: int, range_km: float):
        """Inicializa a grade de varredura espacial do radar e detectores meteorológicos."""
        self._grid_size = grid_size
        self._range_km = range_km
        self._radar_position = Vector2D(0.0, 0.0)
        self._grid: List[List[RadarGate]] = []
        self._initialize_grid()

    def _initialize_grid(self):
        """Constrói a matriz de portões de amostragem do radar centrada na origem."""
        self._grid = []
        step = (2 * self._range_km) / self._grid_size
        start = -self._range_km + step / 2.0

        for row in range(self._grid_size):
            grid_row = []
            y = start + row * step
            for col in range(self._grid_size):
                x = start + col * step
                grid_row.append(RadarGate(Vector2D(x, y)))
            self._grid.append(grid_row)

    def scan_atmosphere(self, storm_model: RankineVortexModel):
        """Realiza a varredura Doppler computando refletividade, velocidade radial e assinaturas Dual-Pol."""
        for row in range(self._grid_size):
            for col in range(self._grid_size):
                gate = self._grid[row][col]
                pos = gate.position

                reflectivity = storm_model.calculate_reflectivity(pos)
                gate.reflectivity_dbz = reflectivity

                wind_vector = storm_model.calculate_wind_vector(pos)

                radar_to_gate = pos.normalize()
                gate.radial_velocity = wind_vector.dot(radar_to_gate)

                dist_to_vortex = pos.distance_to(storm_model.center)
                if dist_to_vortex < 2.8 and reflectivity > 48.0:
                    gate.correlation_coefficient = 0.68
                else:
                    gate.correlation_coefficient = 0.99

    def analyze_severe_weather(self) -> Dict[str, float]:
        """Detecta cisalhamento azimutal extremo (TVS) e assinatura de detritos tornádicos (TDS)."""
        max_shear = 0.0
        max_dbz = 0.0
        min_rho_hv = 1.0

        for row in range(self._grid_size - 1):
            for col in range(self._grid_size - 1):
                g1 = self._grid[row][col]
                g2 = self._grid[row + 1][col]
                g3 = self._grid[row][col + 1]

                max_dbz = max(max_dbz, g1.reflectivity_dbz)
                min_rho_hv = min(min_rho_hv, g1.correlation_coefficient)

                v_diff1 = abs(g1.radial_velocity - g2.radial_velocity)
                v_diff2 = abs(g1.radial_velocity - g3.radial_velocity)
                max_shear = max(max_shear, max(v_diff1, v_diff2))

        return {
            "max_dbz": max_dbz,
            "max_shear": max_shear,
            "min_rho_hv": min_rho_hv,
            "tvs_detected": 1.0 if max_shear > 36.0 else 0.0,
            "tds_detected": 1.0 if (min_rho_hv < 0.80 and max_dbz > 48.0) else 0.0,
        }

    @property
    def grid(self) -> List[List[RadarGate]]:
        """Retorna a matriz de dados do radar."""
        return self._grid

    @property
    def grid_size(self) -> int:
        """Retorna a dimensão da grade do radar."""
        return self._grid_size


class RadarUIFormatter:
    """Formatador de renderização ANSI e gerador de componentes visuais da biblioteca Rich."""

    def __init__(self):
        """Inicializa mapeamentos de cores e paletas meteorológicas."""
        pass

    def get_dbz_char_and_style(self, dbz: float) -> Tuple[str, str]:
        """Mapeia os valores de refletividade (dBZ) para caracteres e estilos ANSI."""
        if dbz < 15.0:
            return ".", "dim blue"
        elif dbz < 28.0:
            return "░", "bold cyan"
        elif dbz < 40.0:
            return "▒", "bold green"
        elif dbz < 52.0:
            return "▓", "bold yellow"
        elif dbz < 62.0:
            return "█", "bold red"
        else:
            return "█", "bold white on red"

    def get_velocity_char_and_style(self, vel: float) -> Tuple[str, str]:
        """Mapeia os valores de velocidade radial Doppler em m/s para representação visual."""
        if vel < -24.0:
            return "█", "bold bright_green"
        elif vel < -14.0:
            return "▓", "bold green"
        elif vel < -4.0:
            return "▒", "dim green"
        elif vel <= 4.0:
            return ".", "dim white"
        elif vel <= 14.0:
            return "▒", "dim red"
        elif vel <= 24.0:
            return "▓", "bold red"
        else:
            return "█", "bold bright_magenta"

    def render_reflectivity_panel(self, radar: DopplerRadarEngine) -> Panel:
        """Gera o painel visual formatado da refletividade de radar (dBZ) em proporção ajustada."""
        lines = []
        for row in radar.grid:
            line_str = ""
            for gate in row:
                char, style = self.get_dbz_char_and_style(gate.reflectivity_dbz)
                line_str += f"[{style}]{char * 2}[/]"
            lines.append(line_str)
        content = "\n".join(lines)
        return Panel(content, title="[bold cyan]REFLETIVIDADE (dBZ)[/]", border_style="cyan")

    def render_velocity_panel(self, radar: DopplerRadarEngine) -> Panel:
        """Gera o painel visual formatado da velocidade radial Doppler (m/s) em proporção ajustada."""
        lines = []
        for row in radar.grid:
            line_str = ""
            for gate in row:
                char, style = self.get_velocity_char_and_style(gate.radial_velocity)
                line_str += f"[{style}]{char * 2}[/]"
            lines.append(line_str)
        content = "\n".join(lines)
        return Panel(
            content,
            title="[bold magenta]VELOCIDADE RADIAL DOPPLER (m/s)[/]",
            border_style="magenta",
        )

    def render_telemetry_table(self, diagnostics: Dict[str, float], step: int) -> Table:
        """Constrói a tabela de métricas táticas e diagnóstico de tempestade severa."""
        table = Table(expand=True, show_header=True, header_style="bold blue")
        table.add_column("Métrica Meteorológica", style="white")
        table.add_column("Valor Medido", justify="center")
        table.add_column("Status de Alerta", justify="center")

        dbz_val = diagnostics["max_dbz"]
        table.add_row(
            "Refletividade Máxima Peak (dBZ)",
            f"{dbz_val:.1f} dBZ",
            "[bold red]EXTREMO[/]" if dbz_val > 55 else "[green]NORMAL[/]",
        )

        shear_val = diagnostics["max_shear"]
        table.add_row(
            "Cisalhamento Azimutal (ΔV)",
            f"{shear_val:.1f} m/s",
            "[bold red]SEVERO[/]" if shear_val > 35 else "[yellow]MODERADO[/]",
        )

        rho_val = diagnostics["min_rho_hv"]
        table.add_row(
            "Coeficiente de Correlação (RhoHV)",
            f"{rho_val:.2f}",
            "[bold bright_magenta]QUEDA DE DEBRIS (TDS)[/]"
            if rho_val < 0.85
            else "[green]METEOROLÓGICO[/]",
        )

        tvs = diagnostics["tvs_detected"] == 1.0
        table.add_row(
            "Assinatura de Vórtice de Tornado (TVS)",
            "POSITIVO" if tvs else "NEGATIVO",
            "[bold white on red] ALERTA DE TORNADO [/]" if tvs else "[dim green]MONITORANDO[/]",
        )

        return table


class DopplerEngineApp:
    """Aplicativo principal que coordena a simulação em tempo real e captura eventos."""

    def __init__(self):
        """Inicializa as dependências do aplicativo, modelo atmosférico e geradores de UI."""
        self._console = Console()
        self._grid_size = 44
        self._range_km = 22.0
        self._radar = DopplerRadarEngine(self._grid_size, self._range_km)
        self._storm_center = Vector2D(-12.0, -10.0)
        self._storm_model = RankineVortexModel(self._storm_center, core_radius=4.8, max_velocity=38.0)
        self._ui_formatter = RadarUIFormatter()
        self._is_running = True

    def _build_layout(self, diagnostics: Dict[str, float], step: int) -> Layout:
        """Monta a estrutura de layout dividido (Split Screen) com painéis e telemetria."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=7),
        )

        header_panel = Panel(
            f"[bold white]ESTAÇÃO RADAR DOPPLER DUPLA POLARIZAÇÃO[/] | RADAR VORTEX-1 | CICLO: {step}",
            style="bold white on blue",
        )
        layout["header"].update(header_panel)

        layout["body"].split_row(
            Layout(self._ui_formatter.render_reflectivity_panel(self._radar)),
            Layout(self._ui_formatter.render_velocity_panel(self._radar)),
        )

        telemetry_table = self._ui_formatter.render_telemetry_table(diagnostics, step)
        layout["footer"].update(
            Panel(telemetry_table, title="[bold yellow]DIAGNÓSTICO DA SUPER CÉLULA[/]", border_style="yellow")
        )

        return layout

    def run(self):
        """Inicia o loop principal de simulação dinâmica e renderização no terminal."""
        try:
            self._console.clear()
            step = 0
            with Live(console=self._console, refresh_per_second=4) as live:
                while self._is_running:
                    step += 1
                    new_x = -12.0 + (step * 0.55)
                    new_y = -10.0 + (step * 0.45)
                    self._storm_model.center = Vector2D(new_x, new_y)

                    self._radar.scan_atmosphere(self._storm_model)
                    diagnostics = self._radar.analyze_severe_weather()

                    layout = self._build_layout(diagnostics, step)
                    live.update(layout)

                    time.sleep(0.3)
                    if new_x > 14.0:
                        step = 0

        except KeyboardInterrupt:
            self._console.print("\n[bold yellow][!] Simulação encerrada pelo usuário.[/]")
            sys.exit(0)
        except Exception as e:
            self._console.print(f"\n[bold red][ERRO] Ocorreu uma falha inesperada no programa: {e}[/]")
            sys.exit(1)


if __name__ == "__main__":
    try:
        app = DopplerEngineApp()
        app.run()
    except KeyboardInterrupt:
        print("\n[!] Programa interrompido.")
        sys.exit(0)
    except Exception as err:
        print(f"\n[ERRO] Falha ao inicializar a aplicação: {err}")
        sys.exit(1)