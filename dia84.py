import time
from collections import deque
from datetime import datetime
from typing import Dict, List
import requests

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Mapeamento de cidades estratégicas no estado de SP (Nome: (Lat, Lon))
CIDADES_SP: Dict[str, tuple] = {
    "São Paulo (Capital)": (-23.5505, -46.6333),
    "Campinas": (-22.9056, -47.0608),
    "Santos (Baixada)": (-23.9608, -46.3339),
    "Ribeirão Preto": (-21.1704, -47.8103),
    "São José dos Campos": (-23.1794, -45.8869),
    "Bauru": (-22.3145, -49.0606),
    "Presidente Prudente": (-22.1256, -51.3889),
    "Sorocaba": (-23.5017, -47.4581),
    "Francas": (-20.5386, -47.4008),
    "São José do Rio Preto": (-20.8197, -49.3794),
}


class LeituraVento:
    """Representa um registro individual de vento em uma localidade."""

    def __init__(self, cidade: str, rajada_kmh: float, horario: str):
        """Inicializa um objeto de leitura de vento.

        Args:
            cidade (str): Nome do município de São Paulo.
            rajada_kmh (float): Velocidade da rajada em km/h.
            horario (str): Horário formatado da leitura.
        """
        self._cidade: str = cidade
        self._rajada_kmh: float = rajada_kmh
        self._horario: str = horario

    @property
    def cidade(self) -> str:
        """Retorna o nome da cidade."""
        return self._cidade

    @property
    def rajada_kmh(self) -> float:
        """Retorna a velocidade da rajada em km/h."""
        return self._rajada_kmh

    @property
    def horario(self) -> str:
        """Retorna o horário da captura."""
        return self._horario

    def obter_nivel_alerta(self) -> tuple:
        """Classifica o nível de severidade da rajada de vento.

        Returns:
            tuple: (Nível de Risco, Mensagem de Ação, Cor Rich, Emoji)
        """
        if self._rajada_kmh < 40.0:
            return (
                "NORMAL",
                "Ventos fracos a moderados. Sem risco.",
                "green",
                "🟢",
            )
        elif 40.0 <= self._rajada_kmh < 60.0:
            return (
                "ATENÇÃO",
                "Rajadas moderadas. Cuidado com objetos soltos.",
                "yellow",
                "🟡",
            )
        elif 60.0 <= self._rajada_kmh < 90.0:
            return (
                "PERIGO",
                "Ventos fortes! Risco de queda de árvores. Evite exposição.",
                "orange3",
                "🟠",
            )
        else:
            return (
                "GRANDE PERIGO",
                "Vendaval severo! Risco de danos estruturais. Procure abrigo!",
                "bold red",
                "🔴",
            )


class ClienteOpenMeteo:
    """Classe responsável por consumir a API pública do Open-Meteo."""

    def __init__(self, timeout: int = 10):
        """Inicializa o cliente da API com um tempo limite padrão.

        Args:
            timeout (int): Tempo máximo de espera da requisição HTTP em segundos.
        """
        self._url_base: str = "https://api.open-meteo.com/v1/forecast"
        self._timeout: int = timeout

    def buscar_rajadas_sp(
        self, cidades: Dict[str, tuple]
    ) -> List[LeituraVento]:
        """Obtém as leituras de rajada de vento atuais para as cidades cadastradas.

        Args:
            cidades (Dict[str, tuple]): Dicionário com nomes e coordenadas (lat, lon).

        Returns:
            List[LeituraVento]: Lista com os objetos de leitura atualizados.
        """
        leituras: List[LeituraVento] = []
        hora_atual: str = datetime.now().strftime("%H:%M:%S")

        for cidade, (lat, lon) in cidades.items():
            params: dict = {
                "latitude": lat,
                "longitude": lon,
                "current": "wind_gusts_10m",
                "wind_speed_unit": "kmh",
                "timezone": "America/Sao_Paulo",
            }
            try:
                resposta = requests.get(
                    self._url_base, params=params, timeout=self._timeout
                )
                resposta.raise_for_status()
                dados = resposta.json()

                if "current" in dados and "wind_gusts_10m" in dados["current"]:
                    valor_rajada = float(dados["current"]["wind_gusts_10m"])
                    leituras.append(
                        LeituraVento(cidade, valor_rajada, hora_atual)
                    )
            except Exception:
                continue

        return leituras


class ProcessadorVentos:
    """Gerencia a ordenação, análise e histórico circular das leituras."""

    def __init__(self, limite_historico: int = 25):
        """Inicializa o processador com uma fila de histórico circular.

        Args:
            limite_historico (int): Quantidade máxima de registros no histórico.
        """
        self._historico_alertas: deque = deque(maxlen=limite_historico)
        self._leituras_atuais: List[LeituraVento] = []

    @property
    def leituras_atuais(self) -> List[LeituraVento]:
        """Retorna as leituras atuais ordenadas da maior para a menor rajada."""
        return sorted(
            self._leituras_atuais,
            key=lambda item: item.rajada_kmh,
            reverse=True,
        )

    @property
    def historico_alertas(self) -> deque:
        """Retorna o histórico circular de alertas registrados."""
        return self._historico_alertas

    def atualizar_dados(self, novas_leituras: List[LeituraVento]) -> None:
        """Atualiza a lista de leituras e adiciona o maior destaque ao histórico.

        Args:
            novas_leituras (List[LeituraVento]): Lista com dados recém-coletados.
        """
        if not novas_leituras:
            return

        self._leituras_atuais = novas_leituras
        maior_leitura: LeituraVento = self.leituras_atuais[0]
        self._historico_alertas.appendleft(maior_leitura)


class DashboardVentos:
    """Gerencia a interface gráfica no terminal usando a biblioteca Rich."""

    def __init__(self, processador: ProcessadorVentos):
        """Inicializa o renderizador do Dashboard.

        Args:
            processador (ProcessadorVentos): Instância da classe de dados.
        """
        self._processador: ProcessadorVentos = processador
        self._console: Console = Console()

    def gerar_layout(self, status_conexao: str) -> Layout:
        """Monta e retorna a estrutura visual com duas colunas lado a lado.

        Args:
            status_conexao (str): Texto explicativo sobre o status da coleta.

        Returns:
            Layout: Estrutura do Rich pronta para exibição.
        """
        layout = Layout()
        layout.split_column(
            Layout(name="cabecalho", size=3),
            Layout(name="corpo"),
            Layout(name="rodape", size=3),
        )
        layout["corpo"].split_row(
            Layout(name="esquerda", ratio=1),
            Layout(name="direita", ratio=1),
        )

        titulo = Text(
            "🌪️ MONITOR DE RAJADAS DE VENTO - ESTADO DE SÃO PAULO 🌪️",
            justify="center",
            style="bold cyan",
        )
        layout["cabecalho"].update(Panel(titulo, style="blue"))

        layout["esquerda"].update(
            Panel(
                self._gerar_tabela_ao_vivo(),
                title="📊 Ao Vivo - Maiores Rajadas (SP)",
                border_style="cyan",
            )
        )
        layout["direita"].update(
            Panel(
                self._gerar_tabela_historico(),
                title="📜 Histórico Circular (Últimos 25 Registros)",
                border_style="magenta",
            )
        )

        layout["rodape"].update(
            Panel(
                Text(status_conexao, justify="center", style="italic gray70"),
                border_style="dim white",
            )
        )
        return layout

    def _gerar_tabela_ao_vivo(self) -> Table:
        """Cria a tabela do painel esquerdo com ordenação em tempo real.

        Returns:
            Table: Tabela preenchida com o ranking de vento.
        """
        tabela = Table(expand=True, show_lines=False)
        tabela.add_column("Cidade", style="bold white")
        tabela.add_column("Vento (km/h)", justify="right")
        tabela.add_column("Alerta", justify="center")

        leituras = self._processador.leituras_atuais
        if not leituras:
            tabela.add_row(
                "Aguardando dados...", "--", "Conectando à API..."
            )
            return tabela

        for item in leituras:
            nivel, _, cor, emoji = item.obter_nivel_alerta()
            tabela.add_row(
                item.cidade,
                f"{item.rajada_kmh:.1f} km/h",
                f"[{cor}]{emoji} {nivel}[/{cor}]",
            )
        return tabela

    def _gerar_tabela_historico(self) -> Table:
        """Cria a tabela do painel direito com a lista circular de registros.

        Returns:
            Table: Tabela formatada com o histórico de eventos.
        """
        tabela = Table(expand=True, show_lines=False)
        tabela.add_column("Hora", style="dim", width=8)
        tabela.add_column("Registro de Alerta / Cidade", style="white")

        historico = self._processador.historico_alertas
        if not historico:
            tabela.add_row("--:--:--", "Nenhum histórico registrado ainda.")
            return tabela

        for item in historico:
            nivel, mensagem, cor, emoji = item.obter_nivel_alerta()
            detalhe = (
                f"[{cor}]{emoji} [bold]{item.cidade}[/bold]: {item.rajada_kmh:.1f} km/h "
                f"({nivel}) - {mensagem}[/{cor}]"
            )
            tabela.add_row(item.horario, detalhe)

        return tabela


def executar_sistema():
    """Função principal responsável pela orquestração e loop do sistema."""
    cliente_api = ClienteOpenMeteo()
    processador = ProcessadorVentos(limite_historico=25)
    dashboard = DashboardVentos(processador)
    console = Console()

    intervalo_api_segundos: int = 60
    ultima_requisicao: float = 0.0
    contadores_loop: int = 0

    console.clear()

    try:
        with Live(
            dashboard.gerar_layout("Iniciando conexões com os sensores de SP..."),
            console=console,
            refresh_per_second=2,
            screen=True,
        ) as live:
            while True:
                agora = time.time()
                tempo_decorrido = agora - ultima_requisicao

                if tempo_decorrido >= intervalo_api_segundos or ultima_requisicao == 0.0:
                    status_msg = (
                        "🔄 Solicitando dados de vento atualizados às estações de SP..."
                    )
                    live.update(dashboard.gerar_layout(status_msg))

                    novas_leituras = cliente_api.buscar_rajadas_sp(CIDADES_SP)
                    if novas_leituras:
                        processador.atualizar_dados(novas_leituras)
                        ultima_requisicao = time.time()
                    else:
                        status_msg = "⚠️ Falha ao obter dados da API. Tentando novamente em breve..."

                tempo_restante = max(
                    0, int(intervalo_api_segundos - (time.time() - ultima_requisicao))
                )
                status_rodape = (
                    f"🟢 Sistema operando normalmente | Próxima varredura nas estações de SP em: {tempo_restante}s "
                    f"| Pressione Ctrl+C para encerrar."
                )

                live.update(dashboard.gerar_layout(status_rodape))
                time.sleep(2.0)

    except KeyboardInterrupt:
        console.clear()
        console.print(
            "\n[bold yellow]👋 Monitoramento encerrado com sucesso pelo usuário. Até a próxima![/bold yellow]\n"
        )
    except Exception as e:
        console.clear()
        console.print(
            f"\n[bold red]❌ Ocorreu um erro inesperado na aplicação:[/bold red] {str(e)}\n"
        )


if __name__ == "__main__":
    executar_sistema()