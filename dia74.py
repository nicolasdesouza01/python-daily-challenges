import math
import random
import sys
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class CelulaRadar:
    """Representa um elemento de resolucao espacial (pixel) na grade de refletividade do radar."""

    def __init__(self, x: int, y: int) -> None:
        """Inicializa o ponto de amostragem georreferenciado."""
        self._x = x
        self._y = y
        self._dbz = 0.0

    @property
    def x(self) -> int:
        """Retorna a coordenada X da matriz."""
        return self._x

    @property
    def y(self) -> int:
        """Retorna a coordenada Y da matriz."""
        return self._y

    @property
    def dbz(self) -> float:
        """Retorna a refletividade equivalente calculada em dBZ."""
        return self._dbz

    @dbz.setter
    def dbz(self, valor: float) -> None:
        """Atualiza a refletividade limitando o piso em zero."""
        self._dbz = max(0.0, valor)


class TempestadeConvectiva:
    """Simula a dinamica de mesoescala, refletividade tridimensional e assinaturas Doppler de supercelulas."""

    def __init__(
        self,
        designacao: str,
        modo_convectivo: str,
        x_inicial: float,
        y_inicial: float,
        vx: float,
        vy: float,
        dbz_pico_base: float,
        cape_ambiente: int,
        shear_0_6km: int,
        tem_hook: bool = False,
        nivel_mda: str = "Inexistente"
    ) -> None:
        """Inicializa os atributos fisicos e vetoriais da estrutura convectiva."""
        self._designacao = designacao
        self._modo_convectivo = modo_convectivo
        self._x = x_inicial
        self._y = y_inicial
        self._vx = vx
        self._vy = vy
        self._dbz_pico_base = dbz_pico_base
        self._cape = cape_ambiente
        self._shear = shear_0_6km
        self._tem_hook = tem_hook
        self._nivel_mda = nivel_mda

        self._dbz_atual = 18.0
        self._fase_termodinamica = "Iniciacao Convectiva"
        self._frames_ativos = 0
        self._echo_top_fl = 280

    @property
    def designacao(self) -> str:
        """Retorna o codigo ICAO/NEXRAD da celula."""
        return self._designacao

    @property
    def modo_convectivo(self) -> str:
        """Retorna a classificacao morfologica da tempestade."""
        return self._modo_convectivo

    @property
    def x(self) -> float:
        """Retorna a posicao X do mesociclone/centro."""
        return self._x

    @property
    def y(self) -> float:
        """Retorna a posicao Y do mesociclone/centro."""
        return self._y

    @property
    def dbz_atual(self) -> float:
        """Retorna o pico maximo de refletividade em dBZ."""
        return self._dbz_atual

    @property
    def fase_termodinamica(self) -> str:
        """Retorna o estagio do ciclo de vida convectivo."""
        return self._fase_termodinamica

    @property
    def tem_hook(self) -> bool:
        """Retorna True se ha presenca de Hook Echo no flanco traseiro."""
        return self._tem_hook

    @property
    def nivel_mda(self) -> str:
        """Retorna o nivel do Algoritmo de Detecao de Mesociclone (MDA)."""
        return self._nivel_mda

    @property
    def cape(self) -> int:
        """Retorna a Energia Potencial Convectiva Disponivel (CAPE) em J/kg."""
        return self._cape

    @property
    def shear(self) -> int:
        """Retorna o cisalhamento do vento na camada de 0 a 6 km em nos (kts)."""
        return self._shear

    @property
    def echo_top_fl(self) -> int:
        """Retorna o teto do eco de refletividade em Flight Level (FL)."""
        return self._echo_top_fl

    @property
    def vetor_deslocamento(self) -> str:
        """Calcula o rumo em graus e velocidade em nos a partir dos vetores Vx e Vy."""
        angulo_rad = math.atan2(self._vx, -self._vy)
        graus = (math.degrees(angulo_rad) + 360) % 360
        velocidade_kts = math.sqrt(self._vx ** 2 + self._vy ** 2) * 60.0
        return f"{graus:03.0f}° @ {velocidade_kts:.0f} kts"

    def evoluir_termodinamica(self) -> None:
        """Atualiza a cinemática e os estágios de refletividade ao longo do tempo."""
        self._x += self._vx
        self._y += self._vy
        self._frames_ativos += 1

        if self._frames_ativos < 12:
            self._fase_termodinamica = "Iniciacao / Cumulus"
            self._dbz_atual = min(self._dbz_pico_base, self._dbz_atual + 4.2)
            self._echo_top_fl = int(280 + (self._dbz_atual * 3.5))
        elif self._frames_ativos < 40:
            self._fase_termodinamica = "Maturidade Supercelular"
            pulsacao = math.sin(self._frames_ativos * 0.4) * 2.2
            self._dbz_atual = min(78.0, self._dbz_pico_base + pulsacao)
            self._echo_top_fl = int(480 + pulsacao * 10)
        else:
            self._fase_termodinamica = "Oclusao / Outflow Boundary"
            self._dbz_atual = max(12.0, self._dbz_atual - 3.2)
            self._echo_top_fl = max(180, self._echo_top_fl - 15)

    def calcular_refletividade_ponto(self, px: float, py: float) -> float:
        """Calcula a refletividade espacial modelando FFD, RFD, BWER e Hook Echo nitido."""
        dx = px - self._x
        dy = py - self._y

        # 1. Corpo Principal da Tempestade (FFD - Forward Flank Downdraft) inclinado a Nordeste
        dx_ffd = dx - 4.5
        dy_ffd = dy + 2.5
        dist_ffd = math.sqrt((dx_ffd * 0.75) ** 2 + (dy_ffd * 1.1) ** 2)
        dbz_ffd = self._dbz_atual * math.exp(- (dist_ffd ** 2) / (2 * (5.5 ** 2)))

        if not self._tem_hook:
            return dbz_ffd if dbz_ffd >= 12.0 else 0.0

        # 2. Trajetória Paramétrica do Hook Echo (Cauda em Foice no Flanco Sudoeste)
        # O gancho se projeta para o Sudoeste (dy de -2 a +7)
        dbz_hook = 0.0
        if -2.0 <= dy <= 7.0:
            # Função matemática da curva do Hook (Sudoeste -> Sul -> Curva para Leste na ponta)
            if dy < 1.0:
                x_hook_alvo = -1.5 - 1.2 * (dy + 2.0)
            elif dy <= 4.5:
                x_hook_alvo = -5.1 + 0.25 * ((dy - 1.0) ** 2)
            else:
                x_hook_alvo = -4.2 + 1.6 * (dy - 4.5)  # Curvatura final da ponta para Leste

            dist_da_curva = abs(dx - x_hook_alvo)
            # Largura bem fina do gancho (exp de 1.1) para garantir nitidez impecável
            dbz_hook = (self._dbz_atual * 0.95) * math.exp(- (dist_da_curva ** 2) / 1.1)

        # 3. Assinatura de Detritos do Tornado (TDS / Debris Ball) na extremidade do Hook
        dx_tds = dx - (-1.8)
        dy_tds = dy - 6.0
        dist_tds = math.sqrt(dx_tds ** 2 + dy_tds ** 2)
        dbz_tds = (self._dbz_atual + 4.0) * math.exp(- (dist_tds ** 2) / 1.3)

        # Unifica os componentes
        dbz_bruto = max(dbz_ffd, dbz_hook, dbz_tds)

        # 4. Inflow Notch / BWER (Escavação de Ar Limpo/Vácuo entre o Núcleo e o Gancho)
        dx_notch = dx - (-1.2)
        dy_notch = dy - 2.2
        dist_notch = math.sqrt((dx_notch / 1.2) ** 2 + (dy_notch / 1.8) ** 2)

        if dist_notch < 1.6:
            # Aplica atenuador drástico de refletividade no notch para criar a separação preta
            fator_escala = (dist_notch / 1.6) ** 3
            dbz_bruto *= fator_escala

        return dbz_bruto if dbz_bruto >= 12.0 else 0.0


class GeradorProceduralNEXRAD:
    """Gerador procedural de mesossistemas convectivos operando em horario de pico de severidade."""

    def __init__(self) -> None:
        """Inicializa o sequenciador de eventos meteorologicos."""
        self._evento_id = 0
        self._hora_simulada = datetime.now().replace(hour=15, minute=30, second=0)

    def gerar_proxima_celula(self) -> Tuple[TempestadeConvectiva, datetime]:
        """Gera uma nova celula convectiva procedural avançando a cronologia de radar."""
        self._evento_id += 1
        self._hora_simulada += timedelta(minutes=random.randint(25, 55))
        
        modos = [
            ("Supercélula HP com Hook Nitido", "Extrema / Mesociclônica", 70.0, 3800, 58, True, "MDA Nível 4 (Mesociclone)"),
            ("Supercélula Tornádica Violenta", "Extrema / TDS Ativo", 76.0, 4500, 68, True, "MDA Nível 5 (TORNÁDICO EXTREMO)")
        ]

        m_nome, m_cat, dbz_pico, cape, shear, hook, mda = random.choice(modos)
        
        x_init = -2.0
        y_init = random.uniform(8.0, 22.0)
        vx = random.uniform(0.35, 0.48)
        vy = random.uniform(-0.10, 0.10)

        designacao = f"NX-{self._evento_id:03d}"

        tempestade = TempestadeConvectiva(
            designacao=designacao,
            modo_convectivo=m_nome,
            x_inicial=x_init,
            y_inicial=y_init,
            vx=vx,
            vy=vy,
            dbz_pico_base=dbz_pico,
            cape_ambiente=cape,
            shear_0_6km=shear,
            tem_hook=hook,
            nivel_mda=mda
        )

        return tempestade, self._hora_simulada


class MatrizRadar:
    """Gerencia a grade espacial de alta resolucao de 36x36 elementos."""

    def __init__(self, dimensao: int = 36) -> None:
        """Inicializa a matriz de amostragem de refletividade."""
        self._dimensao = dimensao
        self._grid = [
            [CelulaRadar(x, y) for x in range(dimensao)]
            for y in range(dimensao)
        ]

    @property
    def dimensao(self) -> int:
        """Retorna o tamanho do lado da grade."""
        return self._dimensao

    def obter_celula(self, x: int, y: int) -> CelulaRadar:
        """Retorna o objeto CelulaRadar em coordenadas especificas."""
        return self._grid[y][x]

    def processar_varredura(self, tempestade: TempestadeConvectiva) -> None:
        """Varre e calcula os valores dBZ para todos os pixels da grade 36x36."""
        for y in range(self._dimensao):
            for x in range(self._dimensao):
                self._grid[y][x].dbz = tempestade.calcular_refletividade_ponto(float(x), float(y))


class RenderizadorNEXRAD:
    """Renderiza a interface grafica de terminal com telemetria profissional de nivel III."""

    def __init__(self, matriz: MatrizRadar) -> None:
        """Inicializa o renderizador e o historico de varreduras."""
        self._matriz = matriz
        self._historico: deque = deque(maxlen=8)

    def limpar_historico(self) -> None:
        """Reseta a fila de historico dinâmico para uma nova tempestade."""
        self._historico.clear()

    def registrar_historico(self, scan_id: int, dbz: float, mda: str, echo_top: int) -> None:
        """Adiciona uma nova varredura de varredura ao log continuo."""
        self._historico.append({
            "scan": scan_id,
            "dbz": dbz,
            "mda": mda,
            "top": echo_top
        })

    def _obter_pixel_dbz(self, dbz: float) -> str:
        """Mapeia os valores de dBZ para a paleta oficial de radar de alta resolucao."""
        if dbz < 15.0:
            return "[dim blue]░░[/dim blue]"
        elif dbz < 30.0:
            return "[bold green]██[/bold green]"
        elif dbz < 40.0:
            return "[bold yellow]██[/bold yellow]"
        elif dbz < 52.0:
            return "[bold bright_red]██[/bold bright_red]"
        elif dbz < 68.0:
            return "[bold magenta]██[/bold magenta]"
        else:
            return "[bold white on magenta]██[/bold white on magenta]"

    def construir_grade_radar(self) -> Table:
        """Monta a tabela 36x36 representando o produto de Refletividade de Nivel III."""
        tabela = Table(show_header=False, show_lines=False, border_style="cyan", padding=(0, 0))
        for _ in range(self._matriz.dimensao):
            tabela.add_column(justify="center")

        for y in range(self._matriz.dimensao):
            linha = [self._obter_pixel_dbz(self._matriz.obter_celula(x, y).dbz) for x in range(self._matriz.dimensao)]
            tabela.add_row(*linha)

        return tabela

    def construir_painel_telemetria(self, tempestade: TempestadeConvectiva, hora_sim: datetime) -> Panel:
        """Monta a HUD com telemetria termodinâmica, Doppler e alertas meteorologicos."""
        dbz = tempestade.dbz_atual
        hora_utc = (hora_sim + timedelta(hours=3)).strftime("%H:%M:%S ZULU")
        hora_brt = hora_sim.strftime("%H:%M:%S BRT")

        if "TORNÁDICO" in tempestade.nivel_mda:
            status = "[bold white on red] 🚨 TORNADO WARNING / TDS DETECTADO [/bold white on red]"
        elif dbz > 55.0:
            status = "[bold white on magenta] ⚡ SEVERE THUNDERSTORM WARNING [/bold white on magenta]"
        elif dbz > 40.0:
            status = "[bold yellow] ⚠️ SEVERE WEATHER WATCH [/bold yellow]"
        else:
            status = "[bold green] ✅ ADVISORY / NO IMMEDIATE THREAT [/bold green]"

        vil_estimado = (dbz ** 1.8) / 350.0

        conteudo = (
            f"[bold cyan]📡 ESTAÇÃO RADAR DOPPLER OPERACIONAL (WSR-88D)[/bold cyan]\n"
            f"[dim]Horário Observado: {hora_brt} ({hora_utc})[/dim]\n\n"
            f"[bold white]Célula Convectiva:[/bold white] {tempestade.designacao}\n"
            f"[bold white]Morfologia:[/bold white] {tempestade.modo_convectivo}\n"
            f"[bold white]Vetor de Deslocamento:[/bold white] {tempestade.vetor_deslocamento}\n"
            f"[bold white]Refletividade Max (Z0):[/bold white] [bold magenta]{dbz:.1f} dBZ[/bold magenta]\n"
            f"[bold white]Teto do Eco (Echo Top):[/bold white] FL{tempestade.echo_top_fl} ({tempestade.echo_top_fl * 100:,} ft)\n"
            f"[bold white]Líquido Integrado (VIL):[/bold white] {vil_estimado:.1f} kg/m²\n"
            f"[bold white]Algoritmo MDA (Mesociclone):[/bold white] {tempestade.nivel_mda}\n\n"
            f"[bold cyan]🌡️ PARÂMETROS AMBIENTAIS DE MESOESCALA[/bold cyan]\n"
            f"[bold white]SBCAPE:[/bold white] {tempestade.cape} J/kg  |  [bold white]Cisalhamento (0-6km):[/bold white] {tempestade.shear} kts\n\n"
            f"[bold white]Status Operacional:[/bold white]\n{status}\n\n"
            f"[dim]Escala dBZ (NEXRAD Level-III):\n"
            f"[dim blue]░░[/dim blue] <15  [green]██[/green] 15-30  [yellow]██[/yellow] 30-42  [bright_red]██[/bright_red] 42-52  [magenta]██[/magenta] 52-68  [white on magenta]██[/white on magenta] >68 (TDS)[/dim]"
        )
        return Panel(conteudo, border_style="bold blue", title="📊 Telemetria Doppler & Sounding", expand=True)

    def construir_painel_historico(self) -> Panel:
        """Monta a tabela de log dinâmico de varreduras em tempo real."""
        tabela = Table(title="📈 Log de Varreduras (Sweeps Sequenciais)", expand=True, border_style="dim cyan")
        tabela.add_column("Sweep", justify="center", style="cyan")
        tabela.add_column("Refletividade", justify="center")
        tabela.add_column("Echo Top", justify="center", style="dim white")
        tabela.add_column("Assinatura MDA", justify="left")

        for reg in self._historico:
            val_dbz = reg["dbz"]
            cor = "green" if val_dbz < 35 else "yellow" if val_dbz < 52 else "red"
            tabela.add_row(
                f"#{reg['scan']:02d}",
                f"[{cor}]{val_dbz:.1f} dBZ[/{cor}]",
                f"FL{reg['top']}",
                reg["mda"]
            )

        return Panel(tabela, border_style="cyan", title="📋 Histórico de Varredura da Célula")

    def gerar_layout_completo(self, tempestade: TempestadeConvectiva, hora_sim: datetime) -> Layout:
        """Combina os componentes no layout principal do Rich sem quebra de quadro."""
        layout = Layout()
        
        painel_radar = Panel(
            self.construir_grade_radar(),
            title="📡 PRODUTO REFLETIVIDADE TOTAL (Z) - GRADE 36x36",
            border_style="cyan"
        )

        coluna_direita = Layout()
        coluna_direita.split_column(
            Layout(self.construir_painel_telemetria(tempestade, hora_sim), ratio=3),
            Layout(self.construir_painel_historico(), ratio=2)
        )

        layout.split_row(
            Layout(painel_radar, ratio=3),
            Layout(coluna_direita, ratio=2)
        )
        return layout


class SimuladorRadarDoppler:
    """Gerenciador de alto nivel da simulacao continua de radar meteorologico."""

    def __init__(self) -> None:
        """Inicializa os motores do simulador."""
        self._console = Console()
        self._matriz = MatrizRadar(dimensao=36)
        self._renderizador = RenderizadorNEXRAD(self._matriz)
        self._gerador = GeradorProceduralNEXRAD()

    def executar(self) -> None:
        """Inicia o loop contínuo de varredura Doppler mantendo o painel estavel."""
        try:
            self._console.clear()
            self._console.print(
                Panel(
                    "[bold cyan]📡 SISTEMA OPERACIONAL DE RADAR DOPPLER NEXRAD LEVEL-III 🌪️[/bold cyan]\n"
                    "[dim]Carregando matriz de 36x36 sensores e algoritmo de detecção de mesociclones...[/dim]",
                    border_style="cyan",
                    expand=False
                )
            )
            time.sleep(1.5)

            tempestade_atual, hora_simulada = self._gerador.gerar_proxima_celula()
            layout_inicial = self._renderizador.gerar_layout_completo(tempestade_atual, hora_simulada)

            with Live(layout_inicial, console=self._console, refresh_per_second=2, auto_refresh=True) as live:
                while True:
                    self._renderizador.limpar_historico()
                    scan_count = 0

                    while True:
                        self._matriz.processar_varredura(tempestade_atual)
                        
                        scan_count += 1
                        self._renderizador.registrar_historico(
                            scan_id=scan_count,
                            dbz=tempestade_atual.dbz_atual,
                            mda=tempestade_atual.nivel_mda,
                            echo_top=tempestade_atual.echo_top_fl
                        )

                        live.update(self._renderizador.gerar_layout_completo(tempestade_atual, hora_simulada))
                        
                        time.sleep(0.8)
                        
                        tempestade_atual.evoluir_termodinamica()

                        if (
                            (tempestade_atual.x > 42.0 or tempestade_atual.x < -10.0) or
                            (tempestade_atual.y > 42.0 or tempestade_atual.y < -10.0)
                        ) and scan_count > 15:
                            break

                    tempestade_atual, hora_simulada = self._gerador.gerar_proxima_celula()

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]🚪 Encerrando sistema de radar Doppler e salvando telemetria...[/bold yellow]\n")
            sys.exit(0)
        except Exception as erro:
            self._console.print(f"\n[bold red]🚨 Falha critica no processamento de radar: {erro}[/bold red]\n")


if __name__ == "__main__":
    app = SimuladorRadarDoppler()
    app.executar()