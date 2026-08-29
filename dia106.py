from collections import deque
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple
import urllib.parse
import urllib.request

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


@dataclass(frozen=True)
class DadosMeteorologicos:
    """
    Representa a estrutura de dados imutável dos parâmetros meteorológicos processados.
    """
    cidade: str
    estado: str
    temperatura: float
    sensacao: float
    umidade: int
    pressao: float
    ponto_orvalho: float
    vento_velocidade: float
    condicao: str
    classificacao_estabilidade: str
    data_hora: str


class ClienteOpenMeteo:
    """
    Encapsula as integrações HTTP com as APIs de Geocodificação e Previsão do Open-Meteo.
    """

    _BASE_URL_GEOCODING: str = "https://geocoding-api.open-meteo.com/v1/search"
    _BASE_URL_WEATHER: str = "https://api.open-meteo.com/v1/forecast"

    _WEATHER_CODES: Dict[int, str] = {
        0: "Céu Limpo",
        1: "Predominantemente Ensolarado",
        2: "Parcialmente Nublado",
        3: "Encoberto",
        45: "Nevoeiro Raso",
        48: "Nevoeiro com Deposição de Geada",
        51: "Garoa Leve",
        53: "Garoa Moderada",
        55: "Garoa Densa",
        61: "Chuva Leve",
        63: "Chuva Moderada",
        65: "Chuva Forte",
        80: "Pancadas de Chuva Leves",
        81: "Pancadas de Chuva Moderadas",
        82: "Pancadas de Chuva Violentas",
        95: "Atividade Convectiva / Trovoada Leve",
        96: "Atividade Convectiva com Granizo Leve",
        99: "Atividade Convectiva Severa com Granizo",
    }

    def buscar_coordenadas(self, cidade: str, estado: str) -> Optional[Tuple[float, float, str, str]]:
        """
        Consulta a API de geocodificação para obter coordenadas geográficas exatas da localidade.
        """
        termo_busca: str = f"{cidade}, {estado}, Brasil"
        params: str = urllib.parse.urlencode({
            "name": termo_busca,
            "count": 1,
            "language": "pt",
            "format": "json"
        })
        url: str = f"{self._BASE_URL_GEOCODING}?{params}"

        try:
            requisicao = urllib.request.Request(url, headers={"User-Agent": "WeatherFacadeEngine/1.0"})
            with urllib.request.urlopen(requisicao, timeout=8) as resposta:
                dados = json.loads(resposta.read().decode())
                if "results" in dados and len(dados["results"]) > 0:
                    resultado = dados["results"][0]
                    nome_cidade: str = resultado.get("name", cidade)
                    nome_estado: str = resultado.get("admin1", estado)
                    return resultado["latitude"], resultado["longitude"], nome_cidade, nome_estado
        except Exception:
            return None
        return None

    def obter_condicoes_atuais(self, lat: float, lon: float, cidade: str, estado: str) -> Optional[DadosMeteorologicos]:
        """
        Requisita variáveis atmosféricas atuais e gera a entidade de dados formatada.
        """
        params: str = urllib.parse.urlencode({
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,wind_speed_10m,weather_code",
            "hourly": "dew_point_2m",
            "timezone": "auto"
        })
        url: str = f"{self._BASE_URL_WEATHER}?{params}"

        try:
            requisicao = urllib.request.Request(url, headers={"User-Agent": "WeatherFacadeEngine/1.0"})
            with urllib.request.urlopen(requisicao, timeout=8) as resposta:
                payload = json.loads(resposta.read().decode())
                dados_atuais = payload.get("current", {})
                dados_horarios = payload.get("hourly", {})

                temp = float(dados_atuais.get("temperature_2m", 0.0))
                sens = float(dados_atuais.get("apparent_temperature", temp))
                umid = int(dados_atuais.get("relative_humidity_2m", 0))
                press = float(dados_atuais.get("surface_pressure", 1013.25))
                vento = float(dados_atuais.get("wind_speed_10m", 0.0))
                codigo_tempo = int(dados_atuais.get("weather_code", 0))

                pontos_orvalho = dados_horarios.get("dew_point_2m", [temp])
                ponto_orvalho = float(pontos_orvalho[0]) if pontos_orvalho else temp

                descricao = self._WEATHER_CODES.get(codigo_tempo, "Condição Indeterminada")
                estabilidade = self._classificar_estabilidade(press, umid, temp, codigo_tempo)

                return DadosMeteorologicos(
                    cidade=cidade,
                    estado=estado,
                    temperatura=temp,
                    sensacao=sens,
                    umidade=umid,
                    pressao=press,
                    ponto_orvalho=ponto_orvalho,
                    vento_velocidade=vento,
                    condicao=descricao,
                    classificacao_estabilidade=estabilidade,
                    data_hora=datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
                )
        except Exception:
            return None

    def _classificar_estabilidade(self, pressao: float, umidade: int, temp: float, codigo: int) -> str:
        """
        Analisa a combinação de variáveis para emitir uma avaliação sinótica técnica e sóbria.
        """
        if codigo in [95, 96, 99]:
            return "Instabilidade Convectiva Severa"
        if pressao < 1008.0 and umidade > 75:
            return "Instabilidade Moderada / Baixa Pressão"
        if umidade > 80 and temp > 26.0:
            return "Potencial Convectivo Elevado"
        if pressao >= 1016.0:
            return "Massa de Ar Estável / Atuação Anticiclônica"
        return "Atmosfera Neutra / Sem Alertas Operacionais"


class GerenciadorHistorico:
    """
    Gerencia o buffer circular (FIFO) de memória para armazenar as últimas consultas.
    """

    def __init__(self, capacidade_maxima: int = 15) -> None:
        """
        Inicializa o deque com limite rígido de elementos.
        """
        self._buffer: deque = deque(maxlen=capacidade_maxima)

    def registrar(self, dados: DadosMeteorologicos) -> None:
        """
        Insere um novo registro no início da fila, descartando automaticamente o mais antigo se cheia.
        """
        self._buffer.appendleft(dados)

    @property
    def historico(self) -> List[DadosMeteorologicos]:
        """
        Retorna a coleção de consultas mantidas na sessão atual.
        """
        return list(self._buffer)


class InterfaceTerminal:
    """
    Controlador de apresentação responsável pela renderização visual CLI via Rich.
    """

    def __init__(self) -> None:
        """
        Instancia dependências operacionais e de interface.
        """
        self._console: Console = Console()
        self._cliente_api: ClienteOpenMeteo = ClienteOpenMeteo()
        self._gerenciador_historico: GerenciadorHistorico = GerenciadorHistorico(capacidade_maxima=15)

    def _construir_tabela_atual(self, dados: DadosMeteorologicos) -> Table:
        """
        Monta o painel tabular detalhado contendo a análise da consulta ativa.
        """
        tabela = Table(
            title=f"🌡️ Diagnóstico Sinótico Atual — {dados.cidade} ({dados.estado})",
            title_style="bold cyan",
            border_style="blue",
            header_style="bold white"
        )
        tabela.add_column("Parâmetro Atmosférico", style="bold yellow")
        tabela.add_column("Medição", style="bold white")
        tabela.add_column("Avaliação Técnica", style="bold green")

        tabela.add_row(
            "Temperatura / Sensação",
            f"{dados.temperatura:.1f} °C / {dados.sensacao:.1f} °C",
            "Afastamento Térmico Expressivo" if abs(dados.temperatura - dados.sensacao) >= 3 else "Faixa de Normalidade"
        )
        tabela.add_row(
            "Ponto de Orvalho",
            f"{dados.ponto_orvalho:.1f} °C",
            "Saturação de Umidade Elevada" if dados.ponto_orvalho >= 20 else "Saturação Moderada"
        )
        tabela.add_row(
            "Umidade Relativa do Ar",
            f"{dados.umidade} %",
            "Atenção: Nível Crítico de Secura" if dados.umidade < 30 else ("Ar Próximo à Saturação" if dados.umidade > 85 else "Nível Adequado")
        )
        tabela.add_row(
            "Pressão Atmosférica",
            f"{dados.pressao:.1f} hPa",
            "Tendência Depressiva" if dados.pressao < 1010 else "Atuação de Alta Pressão"
        )
        tabela.add_row(
            "Velocidade do Vento",
            f"{dados.vento_velocidade:.1f} km/h",
            "Ventos Moderados" if dados.vento_velocidade > 20 else "Brisa Fraca / Calmaria"
        )
        tabela.add_row("Condição Registrada", dados.condicao, "Tempo Presente")
        tabela.add_row("Classificação Sinótica", dados.classificacao_estabilidade, "Diagnóstico da Atmosfera")

        return tabela

    def _construir_tabela_historico(self) -> Table:
        """
        Monta a tabela secundária contendo até 15 registros da memória FIFO.
        """
        tabela = Table(
            title="📜 Histórico Circular de Consultas (Buffer de Sessão — Máx 15)",
            title_style="bold magenta",
            border_style="bright_black",
            header_style="bold yellow"
        )
        tabela.add_column("Horário", style="dim white")
        tabela.add_column("Localidade")
        tabela.add_column("Temperatura")
        tabela.add_column("Umidade")
        tabela.add_column("Pressão")
        tabela.add_column("Diagnóstico")

        registros = self._gerenciador_historico.historico
        if not registros:
            tabela.add_row("-", "Nenhum histórico registrado nesta sessão", "-", "-", "-", "-")
        else:
            for item in registros:
                hora = item.data_hora.split(" - ")[0]
                tabela.add_row(
                    hora,
                    f"{item.cidade}/{item.estado}",
                    f"{item.temperatura:.1f} °C",
                    f"{item.umidade} %",
                    f"{item.pressao:.0f} hPa",
                    item.condicao
                )

        return tabela

    def executar(self) -> None:
        """
        Inicia o loop interativo da aplicação tratando entradas e exceções de usuário.
        """
        self._console.clear()
        self._console.print(
            Panel.fit(
                "[bold white]🌐 ENGINE METEOROLÓGICA & ANÁLISE SINÓTICA[/bold white]\n"
                "[dim]Módulo Facade Auto-Suficiente Integrado ao Open-Meteo[/dim]",
                border_style="blue"
            )
        )

        while True:
            try:
                self._console.print("\n[bold green]>>> Nova Consulta Atmosférica[/bold green] (Pressione Ctrl+C para encerrar)")
                estado = self._console.input("[bold yellow]Digite o Estado/UF (ex: RJ): [/bold yellow]").strip()
                if not estado:
                    continue

                cidade = self._console.input("[bold yellow]Digite a Cidade (ex: Niterói): [/bold yellow]").strip()
                if not cidade:
                    continue

                with self._console.status("[bold cyan]Buscando coordenadas e integrando com a API Open-Meteo...[/bold cyan]", spinner="dots"):
                    coordenadas = self._cliente_api.buscar_coordenadas(cidade, estado)
                    if not coordenadas:
                        self._console.print("[bold red]❌ Erro:[/bold red] Localidade não encontrada. Verifique os dados digitados.")
                        continue

                    lat, lon, nome_cidade, nome_estado = coordenadas
                    dados = self._cliente_api.obter_condicoes_atuais(lat, lon, nome_cidade, nome_estado)

                    if not dados:
                        self._console.print("[bold red]❌ Erro:[/bold red] Falha na comunicação com o serviço meteorológico.")
                        continue

                    self._gerenciador_historico.registrar(dados)

                self._console.clear()
                self._console.print(
                    Panel.fit(
                        "[bold white]🌐 ENGINE METEOROLÓGICA & ANÁLISE SINÓTICA[/bold white]",
                        border_style="blue"
                    )
                )
                self._console.print(self._construir_tabela_atual(dados))
                self._console.print("\n")
                self._console.print(self._construir_tabela_historico())

            except (KeyboardInterrupt, EOFError):
                self._console.print("\n\n[bold blue]👋 Sessão encerrada com sucesso. Até logo![/bold blue]\n")
                break
            except Exception as erro:
                self._console.print(f"[bold red]❌ Erro inesperado:[/bold red] {str(erro)}")


if __name__ == "__main__":
    aplicacao = InterfaceTerminal()
    aplicacao.executar()