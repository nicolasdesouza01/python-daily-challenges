"""Sistema Tático de Monitoramento Atmosférico e Mesociclônico - Estado do Paraná."""

import datetime
import math
import time
from typing import Dict, List, Optional, Tuple

import requests
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class EstacaoMonitorada:
    """Representa uma estação geográfica de monitoramento."""
    def __init__(self, nome: str, lat: float, lon: float) -> None:
        self.nome = nome
        self.lat = lat
        self.lon = lon


class RadarAtmosferico:
    """Cliente de captura de dados meteorológicos via API."""
    def __init__(self) -> None:
        self._url = "https://api.open-meteo.com/v1/forecast"

    def capturar(self, estacao: EstacaoMonitorada) -> Optional[Dict]:
        """Realiza requisição e processa métricas."""
        params = {
            "latitude": estacao.lat, "longitude": estacao.lon,
            "current": ["wind_speed_10m", "wind_direction_10m", "wind_speed_850hPa", 
                        "wind_direction_850hPa", "wind_speed_500hPa", "wind_direction_500hPa"],
            "wind_speed_unit": "ms"
        }
        try:
            res = requests.get(self._url, params=params, timeout=5).json().get("current", {})
            u10, v10 = self._vetor(res["wind_speed_10m"], res["wind_direction_10m"])
            u850, v850 = self._vetor(res["wind_speed_850hPa"], res["wind_direction_850hPa"])
            u500, v500 = self._vetor(res["wind_speed_500hPa"], res["wind_direction_500hPa"])

            s01 = math.hypot(u850 - u10, v850 - v10)
            s06 = math.hypot(u500 - u10, v500 - v10)
            veering = (res["wind_direction_850hPa"] - res["wind_direction_10m"]) % 360

            diag, rot, estilo = self._classificar(s01, s06, veering)

            return {
                "cidade": estacao.nome, "hora": datetime.datetime.now().strftime("%H:%M:%S"),
                "v_sup": res["wind_speed_10m"], "dir": res["wind_direction_10m"],
                "s01": s01, "s06": s06, "diag": diag, "rot": rot, "estilo": estilo
            }
        except:
            return None

    def _vetor(self, vel: float, direcao: float) -> Tuple[float, float]:
        rad = math.radians(direcao)
        return -vel * math.sin(rad), -vel * math.cos(rad)

    def _classificar(self, s01: float, s06: float, veering: float) -> Tuple[str, str, str]:
        if s06 >= 20.0 and s01 >= 12.0 and (10 <= veering <= 120):
            return "MESOCICLONE ATIVO", "ROTAÇÃO SEVERA", "bold red"
        elif s06 >= 15.0 or s01 >= 8.0:
            return "VORTICIDADE ELEVADA", "ROTAÇÃO EM ORGANIZAÇÃO", "bold yellow"
        return "AMBIENTE FAVORÁVEL", "INEXISTENTE", "bold green"


class InterfaceDashboard:
    """Gerenciador da interface visual com Rich."""
    def __init__(self) -> None:
        self.leituras: Dict[str, Dict] = {}
        self.historico: List[Dict] = []

    def adicionar(self, dados: Dict) -> None:
        self.leituras[dados["cidade"]] = dados
        self.historico.append(dados)

    def _formatar_valor(self, valor: float, tipo: str) -> str:
        """Aplica cor ao valor baseado em limites de periculosidade."""
        # Limites: Shear > 20 (Vermelho), > 15 (Amarelo)
        if tipo == "shear":
            if valor >= 20.0: return f"[bold red]{valor:.1f} m/s[/bold red]"
            if valor >= 15.0: return f"[bold yellow]{valor:.1f} m/s[/bold yellow]"
        return f"[bold white]{valor:.1f} m/s[/bold white]"

    def criar_tabela_cidade(self, dados: Dict) -> Table:
        estilo = dados["estilo"]
        tabela = Table(expand=True, show_header=False, box=None)
        # Rótulos em branco negrito conforme solicitado
        tabela.add_column("Metrica", style="bold white")
        tabela.add_column("Valor", justify="right")

        tabela.add_row("Horário", dados["hora"])
        tabela.add_row("Vento Sup. (10m)", f"[white]{dados['v_sup']:.1f}[/white] m/s ({dados['dir']}°)")
        tabela.add_row("Shear 0-1km", self._formatar_valor(dados["s01"], "shear"))
        tabela.add_row("Shear 0-6km", self._formatar_valor(dados["s06"], "shear"))
        tabela.add_row("Diagnóstico", f"[{estilo}]{dados['diag']}[/{estilo}]")
        tabela.add_row("Rotação", f"[{estilo}]{dados['rot']}[/{estilo}]")
        return tabela

    def gerar_layout(self, contagem: int) -> Layout:
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body", ratio=1), Layout(name="footer", size=3))
        layout["body"].split_row(Layout(name="esquerda", ratio=1), Layout(name="direita", ratio=1))

        lista_paineis = [
            Panel(self.criar_tabela_cidade(dados), title=f"[bold cyan]{nome}[/bold cyan]", border_style="blue")
            for nome, dados in self.leituras.items()
        ]

        tabela_dir = Table(expand=True, header_style="bold cyan")
        tabela_dir.add_column("Estação")
        tabela_dir.add_column("Hora")
        tabela_dir.add_column("Status")
        for reg in reversed(self.historico[-20:]):
            tabela_dir.add_row(reg["cidade"], reg["hora"], f"[{reg['estilo']}]{reg['rot']}[/{reg['estilo']}]")

        layout["header"].update(Panel("📡 REDE DE MONITORAMENTO TÁTICO - PARANÁ 📡", style="bold cyan"))
        layout["esquerda"].update(Panel(Group(*lista_paineis), title="📡 SCANNERS EM TEMPO REAL"))
        layout["direita"].update(Panel(tabela_dir, title="📋 LOG DE EVENTOS", border_style="green"))
        layout["footer"].update(Panel(f"Próxima varredura em {contagem}s | Ctrl+C para sair", style="bold yellow"))
        return layout


class ControladoraSistema:
    def __init__(self) -> None:
        self.estacoes = [
            EstacaoMonitorada("Foz do Iguaçu", -25.51, -54.58),
            EstacaoMonitorada("Cascavel", -24.95, -53.45),
            EstacaoMonitorada("Guarapuava", -25.39, -51.46),
            EstacaoMonitorada("Londrina", -23.31, -51.16),
            EstacaoMonitorada("Curitiba", -25.42, -49.27),
        ]
        self.radar = RadarAtmosferico()
        self.ui = InterfaceDashboard()

    def rodar(self) -> None:
        try:
            with Live(refresh_per_second=4, screen=True) as live:
                while True:
                    for s in range(120, 0, -1):
                        if s == 120:
                            for estacao in self.estacoes:
                                dados = self.radar.capturar(estacao)
                                if dados: self.ui.adicionar(dados)
                        live.update(self.ui.gerar_layout(s))
                        time.sleep(1)
        except KeyboardInterrupt:
            Console().print("\n[bold red]Sistema desligado pelo operador.[/bold red]")


if __name__ == "__main__":
    ControladoraSistema().rodar()