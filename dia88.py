import sys
import time
import json
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from math import factorial
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

@dataclass
class Station:
    """Dados de uma estação meteorológica."""
    name: str
    region: str
    lat: float
    lon: float
    metrics: list = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])

class MeteoSystem:
    """Gerencia a coleta e análise de dados meteorológicos."""

    def __init__(self):
        self.history = deque(maxlen=30)
        self.stations = [
            Station("São Paulo", "RMSP", -23.55, -46.63),
            Station("Campinas", "Macro", -22.91, -47.06),
            Station("Bauru", "Centro", -22.31, -49.06),
            Station("Santos", "Litoral", -23.96, -46.33),
            Station("Ribeirão", "Norte", -21.17, -47.81)
        ]

    def fetch(self, s: Station):
        """Coleta dados da Open-Meteo (CAPE, Temp, Orvalho, Vento)."""
        url = f"https://api.open-meteo.com/v1/forecast?latitude={s.lat}&longitude={s.lon}&hourly=cape,temperature_2m,dew_point_2m,wind_speed_10m"
        try:
            with urllib.request.urlopen(url, timeout=5) as res:
                data = json.loads(res.read().decode())['hourly']
                # Índice 0: CAPE | 1: Temp | 2: Ponto Orvalho | 3: Vento
                s.metrics = [data['cape'][0], data['temperature_2m'][0], data['dew_point_2m'][0], data['wind_speed_10m'][0]]
        except Exception:
            s.metrics = [0.0, 0.0, 0.0, 0.0]

    def get_risk(self, m: list):
        """Calcula risco via análise combinatória."""
        # Limiares: CAPE >= 1000, Temp >= 30°C, Orvalho >= 18°C, Vento >= 40km/h
        critical = sum(1 for i, v in enumerate(m) if v >= [1000, 30, 18, 40][i])
        arr = factorial(critical) // factorial(max(0, critical - 2)) if critical >= 2 else 0
        return min(100, (critical * 20) + (arr * 5)), arr

    def record_peak(self):
        """Encontra a estação com o maior valor de CAPE e registra no histórico."""
        top_station = max(self.stations, key=lambda s: s.metrics[0])
        self.history.append((top_station.name, top_station.metrics[0]))

class Dashboard:
    """Responsável pela visualização no terminal."""

    def __init__(self):
        self.console = Console()

    def build_layout(self):
        layout = Layout()
        layout.split_column(Layout(name="head", size=3), Layout(name="body"))
        layout["body"].split_row(Layout(name="main", ratio=65), Layout(name="hist", ratio=35))
        return layout

    def update(self, layout, system):
        """Renderiza os painéis com dados atuais e o histórico detalhado por cidade."""
        layout["head"].update(Panel(f":satellite: [bold blue]MONITORAMENTO METEOROLÓGICO SP[/] | {datetime.now():%H:%M:%S}", style="slate_blue1"))
        
        # Tabela Principal
        table = Table(title="Dados Atuais", expand=True, header_style="bold blue")
        
        table.add_column("Local", style="cyan")
        table.add_column("CAPE", justify="right")
        table.add_column("Temp", justify="right")
        table.add_column("Orvalho", justify="right")
        table.add_column("Vento", justify="right")
        table.add_column("Risco", justify="center")
        table.add_column("Status", justify="center")

        for s in system.stations:
            score, arr = system.get_risk(s.metrics)
            status = "[red]ALERTA[/]" if score > 60 else "[yellow]ATENÇÃO[/]" if score > 30 else "[blue]OK[/]"
            
            table.add_row(
                s.name, 
                f"{s.metrics[0]:.0f} J/kg", 
                f"{s.metrics[1]:.1f}°C", 
                f"{s.metrics[2]:.1f}°C", 
                f"{s.metrics[3]:.0f} km/h", 
                str(arr), 
                status
            )

        layout["main"].update(Panel(table))

        # Tabela Histórico detalhado
        hist = Table(title="Histórico (30 min)", expand=True, header_style="bold slate_blue1")
        hist.add_column("Min", justify="center", style="dim")
        hist.add_column("Cidade Pico", style="bold white")
        hist.add_column("CAPE Máx", justify="right", style="cyan")

        for i, (city, cape_val) in enumerate(system.history): 
            hist.add_row(f"M{i+1}", city, f"{cape_val:.0f} J/kg")

        layout["hist"].update(Panel(hist))

def run():
    sys_model = MeteoSystem()
    view = Dashboard()
    layout = view.build_layout()

    try:
        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                view.update(layout, sys_model)
                
                for s in sys_model.stations: 
                    sys_model.fetch(s)
                
                sys_model.record_peak()
                
                view.update(layout, sys_model)
                time.sleep(60)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    run()