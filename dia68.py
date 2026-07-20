# Instale o rich requests para funcionar.
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

console = Console()


class LeituraAnemometrica:
    def __init__(self, velocidade_sustentada, rajada_maxima):
        self._velocidade_sustentada = velocidade_sustentada
        self._rajada_maxima = rajada_maxima

    @property
    def velocidade_sustentada(self):
        return self._velocidade_sustentada

    @property
    def rajada_maxima(self):
        return self._rajada_maxima

    def obter_escala_beaufort(self):
        v = self._velocidade_sustentada
        if v < 12:
            return "Vento Calmo"
        elif v < 28:
            return "Brisa Moderada"
        elif v < 50:
            return "Vento Forte"
        elif v < 75:
            return "Vendaval Severo"
        else:
            return "Tempestade Extrema"

    def calcular_fator_rajada(self):
        if self._velocidade_sustentada == 0:
            return 0.0
        return self._rajada_maxima / self._velocidade_sustentada


class ClienteMeteorologico:
    def __init__(self, latitude=-23.5505, longitude=-46.6333):
        self._url_base = "https://api.open-meteo.com/v1/forecast"
        self._parametros = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "wind_speed_10m,wind_gusts_10m",
            "wind_speed_unit": "kmh"
        }

    def buscar_telemetria_real(self):
        try:
            resposta = requests.get(self._url_base, params=self._parametros, timeout=5)
            resposta.raise_for_status()
            dados = resposta.json().get("current", {})
            v_sustentada = float(dados.get("wind_speed_10m", 0.0))
            v_rajada = float(dados.get("wind_gusts_10m", v_sustentada))
            return LeituraAnemometrica(v_sustentada, v_rajada)
        except requests.RequestException:
            return None


class RenderizadorGrafico:
    def __init__(self, tamanho_maximo=20):
        self._tamanho_maximo = tamanho_maximo
        self._historico_valores = []
        self._blocos_ascii = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def adicionar_valor(self, valor):
        self._historico_valores.append(valor)
        if len(self._historico_valores) > self._tamanho_maximo:
            self._historico_valores.pop(0)

    def gerar_sparkline(self):
        if not self._historico_valores:
            return ""

        max_val = max(50.0, max(self._historico_valores))
        min_val = 0.0

        representacao = []
        for val in self._historico_valores:
            proporcao = (val - min_val) / (max_val - min_val)
            indice = int(proporcao * (len(self._blocos_ascii) - 1))
            indice = max(0, min(len(self._blocos_ascii) - 1, indice))
            representacao.append(self._blocos_ascii[indice])

        return " ".join(representacao)


class EstacaoTelemetriaViva:
    def __init__(self, localizacao="São Paulo - SP (Open-Meteo API Real)"):
        self._localizacao = localizacao
        self._cliente_api = ClienteMeteorologico()
        self._grafico_sustentado = RenderizadorGrafico()
        self._grafico_rajada = RenderizadorGrafico()
        self._total_requisisoes = 0
        self._pico_historico = 0.0

    def executar_transmissao(self):
        console.clear()
        try:
            with Live(self._gerar_layout_painel(), refresh_per_second=1) as live:
                while True:
                    leitura = self._cliente_api.buscar_telemetria_real()

                    if leitura is not None:
                        self._total_requisisoes += 1
                        if leitura.rajada_maxima > self._pico_historico:
                            self._pico_historico = leitura.rajada_maxima

                        self._grafico_sustentado.adicionar_valor(leitura.velocidade_sustentada)
                        self._grafico_rajada.adicionar_valor(leitura.rajada_maxima)

                    live.update(self._gerar_layout_painel(leitura))
                    time.sleep(2.0)

        except KeyboardInterrupt:
            console.print("\n")
            console.print(Panel("Transmissão encerrada pelo operador. Conexão fechada com sucesso.", style="bold green"))
        except Exception:
            console.print("\n")
            console.print(Panel(":x: Erro crítico inesperado na execução do painel.", style="bold red"))

    def _gerar_layout_painel(self, leitura=None):
        layout = Layout()
        layout.split_column(
            Layout(name="cabecalho", size=4),
            Layout(name="corpo", size=12),
            Layout(name="rodape", size=3)
        )

        titulo = f"[bold cyan]:satellite: ESTAÇÃO TELEMÉTRICA LIVE (DADOS REAIS DA API)[/bold cyan]\n[dim]Monitoramento Metereológico em Tempo Real | {self._localizacao}[/dim]"
        layout["cabecalho"].update(Panel(Align.center(titulo), style="blue"))

        if leitura is None:
            layout["corpo"].update(Panel("[bold yellow]:warning: Conectando aos servidores do Open-Meteo ou aguardando resposta da rede...[/bold yellow]", style="yellow"))
        else:
            if leitura.rajada_maxima >= 60.0:
                cor_status = "red"
                alerta_txt = ":warning: EMERGÊNCIA: CONDICOES EXTREMAS DE RAJADA"
            elif leitura.rajada_maxima >= 35.0:
                cor_status = "yellow"
                alerta_txt = ":exclamation: ALERTA: RAJADAS DENTRO DO LIMIAR DE ATENÇÃO"
            else:
                cor_status = "green"
                alerta_txt = ":white_check_mark: OPERAÇÃO NORMAL - CONDIÇÕES ATMOSFÉRICAS ESTÁVEIS"

            tabela_dados = Table(show_header=True, expand=True, header_style="bold magenta")
            tabela_dados.add_column("Sensor / Métrica Real", style="bold white")
            tabela_dados.add_column("Dado em Tempo Real", justify="right", style="bold cyan")
            tabela_dados.add_column("Tendência Histórica Visual (Sparkline)", style="bold yellow")

            spark_sust = self._grafico_sustentado.gerar_sparkline()
            spark_raj = self._grafico_rajada.gerar_sparkline()

            tabela_dados.add_row(
                "Vento Sustentado (10m)",
                f"{leitura.velocidade_sustentada:.1f} km/h",
                f"[cyan]{spark_sust}[/cyan]"
            )
            tabela_dados.add_row(
                "Rajada Máxima Medida",
                f"{leitura.rajada_maxima:.1f} km/h",
                f"[magenta]{spark_raj}[/magenta]"
            )
            tabela_dados.add_row(
                "Fator de Rajada",
                f"{leitura.calcular_fator_rajada():.2f}x",
                f"Escala: [bold]{leitura.obter_escala_beaufort()}[/bold]"
            )

            painel_principal = Panel(
                tabela_dados,
                title=f"[{cor_status}]Status da Estação: {alerta_txt}[/{cor_status}]",
                subtitle=f"[dim]Consultas HTTP realizadas: {self._total_requisisoes} | Maior Rajada Real: {self._pico_historico:.1f} km/h[/dim]",
                style=cor_status
            )

            layout["corpo"].update(painel_principal)

        instrucoes = "[bold white]Pressione [red]Ctrl + C[/red] no terminal para desconectar a estação com segurança.[/bold white]"
        layout["rodape"].update(Panel(Align.center(instrucoes), style="dim"))

        return layout


if __name__ == "__main__":
    estacao = EstacaoTelemetriaViva()
    estacao.executar_transmissao()