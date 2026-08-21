"""
Vitrine de terminal: consulta o clima atual de uma cidade brasileira usando a
API pública Open-Meteo, exibindo os dados em uma HUD estilizada com Rich e
convertendo temperatura e velocidade do vento para a unidade que o usuário
escolher.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


URL_GEOCODIFICACAO = "https://geocoding-api.open-meteo.com/v1/search"
URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

ESTADOS_BRASILEIROS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

DESCRICOES_CLIMA = {
    0: ("Céu limpo", "☀️"),
    1: ("Poucas nuvens", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Nevoeiro", "🌫️"),
    48: ("Nevoeiro com geada", "🌫️"),
    51: ("Garoa leve", "🌦️"),
    53: ("Garoa moderada", "🌦️"),
    55: ("Garoa densa", "🌧️"),
    56: ("Garoa congelante leve", "🌧️"),
    57: ("Garoa congelante densa", "🌧️"),
    61: ("Chuva leve", "🌧️"),
    63: ("Chuva moderada", "🌧️"),
    65: ("Chuva forte", "🌧️"),
    66: ("Chuva congelante leve", "🌧️"),
    67: ("Chuva congelante forte", "🌧️"),
    71: ("Neve leve", "🌨️"),
    73: ("Neve moderada", "🌨️"),
    75: ("Neve forte", "❄️"),
    77: ("Grãos de neve", "🌨️"),
    80: ("Pancadas de chuva leves", "🌦️"),
    81: ("Pancadas de chuva moderadas", "🌧️"),
    82: ("Pancadas de chuva violentas", "⛈️"),
    85: ("Pancadas de neve leves", "🌨️"),
    86: ("Pancadas de neve fortes", "❄️"),
    95: ("Trovoada", "⛈️"),
    96: ("Trovoada com granizo leve", "⛈️"),
    99: ("Trovoada com granizo forte", "⛈️"),
}


class ErroServicoClima(Exception):
    """Erro base para qualquer falha ao consultar os serviços de clima ou geocodificação."""


class ConexaoClimaError(ErroServicoClima):
    """Levantado quando não é possível conectar a um dos serviços da Open-Meteo."""


@dataclass(frozen=True)
class Localizacao:
    """Representa uma cidade brasileira já localizada via geocodificação."""

    nome: str
    estado: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ClimaAtual:
    """Fotografia do clima atual de uma localização, sempre nas unidades padrão da Open-Meteo (métrico)."""

    temperatura_c: float
    sensacao_termica_c: float
    umidade_pct: float
    precipitacao_mm: float
    cobertura_nuvens_pct: float
    pressao_hpa: float
    velocidade_vento_kmh: float
    rajada_vento_kmh: float
    direcao_vento_graus: float
    codigo_clima: int
    e_dia: bool


class DirecaoVento:
    """Traduz graus de direção do vento (0-360) para o ponto cardeal correspondente em português."""

    _PONTOS = ("N", "NE", "L", "SE", "S", "SO", "O", "NO")

    @classmethod
    def para_cardeal(cls, graus: float) -> str:
        """Converte um ângulo em graus para o ponto cardeal mais próximo."""
        indice = round(graus / 45) % 8
        return cls._PONTOS[indice]


class DescritorClima:
    """Traduz o código de clima da Open-Meteo (padrão WMO) em uma descrição e um emoji em português."""

    @classmethod
    def descrever(cls, codigo: int, e_dia: bool) -> tuple[str, str]:
        """Retorna (descrição, emoji) para o código informado, ajustando dia/noite no céu limpo."""
        descricao, emoji = DESCRICOES_CLIMA.get(codigo, ("Condição desconhecida", "❓"))
        if codigo == 0 and not e_dia:
            emoji = "🌙"
        return descricao, emoji


class ConversorUnidade(ABC):
    """Classe base abstrata para conversores de unidades físicas a partir de uma unidade padrão."""

    @property
    @abstractmethod
    def unidade_padrao(self) -> str:
        """Sigla da unidade em que os dados chegam da API."""

    @property
    @abstractmethod
    def unidades_disponiveis(self) -> dict[str, str]:
        """Mapa entre a sigla de cada unidade suportada e um rótulo legível para exibição."""

    @abstractmethod
    def simbolo(self, unidade: str) -> str:
        """Devolve o símbolo curto de uma unidade (ex.: '°C', 'km/h') para uso compacto na tabela."""

    @abstractmethod
    def converter(self, valor: float, unidade_destino: str) -> float:
        """Converte um valor, dado na unidade padrão, para a unidade de destino informada."""


class ConversorTemperatura(ConversorUnidade):
    """Converte temperaturas a partir de Celsius, que é a unidade padrão devolvida pela Open-Meteo."""

    _SIMBOLOS = {"C": "°C", "F": "°F", "K": "K"}

    @property
    def unidade_padrao(self) -> str:
        """Sigla da unidade padrão de temperatura (Celsius)."""
        return "C"

    @property
    def unidades_disponiveis(self) -> dict[str, str]:
        """Unidades de temperatura suportadas pelo conversor."""
        return {"C": "Celsius", "F": "Fahrenheit", "K": "Kelvin"}

    def simbolo(self, unidade: str) -> str:
        """Símbolo curto da unidade de temperatura informada."""
        return self._SIMBOLOS.get(unidade, unidade)

    def converter(self, valor: float, unidade_destino: str) -> float:
        """Converte uma temperatura em Celsius para Fahrenheit ou Kelvin, conforme solicitado."""
        if unidade_destino == "C":
            return valor
        if unidade_destino == "F":
            return valor * 9 / 5 + 32
        if unidade_destino == "K":
            return valor + 273.15
        raise ValueError(f"Unidade de temperatura desconhecida: {unidade_destino}")


class ConversorVelocidade(ConversorUnidade):
    """Converte velocidades a partir de km/h, que é a unidade padrão devolvida pela Open-Meteo."""

    _SIMBOLOS = {"kmh": "km/h", "mph": "mph", "ms": "m/s", "kn": "nós"}

    @property
    def unidade_padrao(self) -> str:
        """Sigla da unidade padrão de velocidade (quilômetros por hora)."""
        return "kmh"

    @property
    def unidades_disponiveis(self) -> dict[str, str]:
        """Unidades de velocidade suportadas pelo conversor."""
        return {
            "kmh": "Quilômetros por hora",
            "mph": "Milhas por hora",
            "ms": "Metros por segundo",
            "kn": "Nós",
        }

    def simbolo(self, unidade: str) -> str:
        """Símbolo curto da unidade de velocidade informada."""
        return self._SIMBOLOS.get(unidade, unidade)

    def converter(self, valor: float, unidade_destino: str) -> float:
        """Converte uma velocidade em km/h para mph, m/s ou nós, conforme solicitado."""
        if unidade_destino == "kmh":
            return valor
        if unidade_destino == "mph":
            return valor / 1.60934
        if unidade_destino == "ms":
            return valor / 3.6
        if unidade_destino == "kn":
            return valor / 1.852
        raise ValueError(f"Unidade de velocidade desconhecida: {unidade_destino}")


class GeocodificadorOpenMeteo:
    """Busca coordenadas de cidades brasileiras usando a API de geocodificação da Open-Meteo."""

    def __init__(self, console: Console) -> None:
        """Guarda a referência ao console Rich usado para eventuais mensagens."""
        self._console = console

    def buscar(self, cidade: str, estado: Optional[str]) -> list[Localizacao]:
        """Busca a cidade informada e devolve as localizações brasileiras compatíveis encontradas."""
        parametros = {"name": cidade, "count": 20, "language": "pt", "format": "json"}

        try:
            resposta = requests.get(URL_GEOCODIFICACAO, params=parametros, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.exceptions.RequestException as erro:
            raise ConexaoClimaError(
                "Não consegui acessar o serviço de busca de cidades. Verifique sua internet e tente novamente."
            ) from erro
        except ValueError as erro:
            raise ErroServicoClima(
                "O serviço de busca de cidades devolveu uma resposta inesperada. Tente novamente."
            ) from erro

        resultados = dados.get("results") or []
        candidatos_brasil = [item for item in resultados if item.get("country_code") == "BR"]

        if estado:
            nome_estado = ESTADOS_BRASILEIROS.get(estado.upper(), estado)
            filtrados = [
                item for item in candidatos_brasil
                if nome_estado.lower() in (item.get("admin1") or "").lower()
            ]
            candidatos_brasil = filtrados or candidatos_brasil

        return [
            Localizacao(
                nome=item["name"],
                estado=item.get("admin1", "—"),
                latitude=item["latitude"],
                longitude=item["longitude"],
            )
            for item in candidatos_brasil
        ]


class ServicoClima:
    """Consulta as condições atuais do tempo na Open-Meteo para uma localização já geocodificada."""

    _VARIAVEIS_ATUAIS = (
        "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,"
        "precipitation,weather_code,cloud_cover,pressure_msl,"
        "wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    )

    def __init__(self, console: Console) -> None:
        """Guarda a referência ao console Rich usado para eventuais mensagens."""
        self._console = console

    def obter_clima_atual(self, localizacao: Localizacao) -> ClimaAtual:
        """Faz a chamada HTTP à Open-Meteo e devolve os dados atuais já estruturados em um ClimaAtual."""
        parametros = {
            "latitude": localizacao.latitude,
            "longitude": localizacao.longitude,
            "current": self._VARIAVEIS_ATUAIS,
            "timezone": "auto",
        }

        try:
            resposta = requests.get(URL_PREVISAO, params=parametros, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.exceptions.RequestException as erro:
            raise ConexaoClimaError(
                "Não consegui acessar o serviço de clima. Verifique sua internet e tente novamente."
            ) from erro
        except ValueError as erro:
            raise ErroServicoClima(
                "O serviço de clima devolveu uma resposta inesperada. Tente novamente."
            ) from erro

        atual = dados.get("current", {})

        try:
            return ClimaAtual(
                temperatura_c=atual["temperature_2m"],
                sensacao_termica_c=atual["apparent_temperature"],
                umidade_pct=atual["relative_humidity_2m"],
                precipitacao_mm=atual["precipitation"],
                cobertura_nuvens_pct=atual["cloud_cover"],
                pressao_hpa=atual["pressure_msl"],
                velocidade_vento_kmh=atual["wind_speed_10m"],
                rajada_vento_kmh=atual["wind_gusts_10m"],
                direcao_vento_graus=atual["wind_direction_10m"],
                codigo_clima=atual["weather_code"],
                e_dia=bool(atual["is_day"]),
            )
        except KeyError as erro:
            raise ErroServicoClima(
                "A resposta do serviço de clima veio incompleta. Tente novamente em instantes."
            ) from erro


class PainelClima:
    """Responsável por toda a interface visual do programa, construída com a biblioteca Rich."""

    def __init__(self, console: Console) -> None:
        """Guarda a referência ao console Rich compartilhado pelo programa."""
        self._console = console

    def exibir_boas_vindas(self) -> None:
        """Mostra o painel inicial de apresentação do programa."""
        self._console.print(
            Panel(
                "[bold cyan]🌎 Clima Brasil[/bold cyan]\n"
                "Consulte o clima atual de qualquer cidade do Brasil, "
                "com conversão automática de unidades.",
                border_style="cyan",
            )
        )

    def solicitar_localizacao(self, geocodificador: GeocodificadorOpenMeteo) -> Optional[Localizacao]:
        """Pergunta cidade e estado, resolve a busca e devolve a localização escolhida (ou None)."""
        cidade = Prompt.ask("\n[bold]🏙️  Qual cidade você quer consultar?[/bold]").strip()
        if not cidade:
            self._console.print("[yellow]Nenhuma cidade informada. Encerrando.[/yellow]")
            return None

        estado = Prompt.ask(
            "[bold]📍 De qual estado (sigla ou nome, opcional)?[/bold]", default=""
        ).strip()

        with self._console.status("[cyan]Procurando a cidade...[/cyan]", spinner="dots"):
            localizacoes = geocodificador.buscar(cidade, estado or None)

        if not localizacoes:
            estado_texto = f" em {estado}" if estado else ""
            self._console.print(f"[red]Não encontrei nenhuma cidade brasileira chamada '{cidade}'{estado_texto}.[/red]")
            return None

        if len(localizacoes) == 1:
            return localizacoes[0]

        return self._escolher_entre_varias(localizacoes)

    def _escolher_entre_varias(self, localizacoes: list[Localizacao]) -> Localizacao:
        """Exibe uma tabela numerada quando mais de uma cidade compatível é encontrada."""
        tabela = Table(title="🔎 Encontrei mais de uma cidade — qual delas?")
        tabela.add_column("#", style="bold cyan", justify="right")
        tabela.add_column("Cidade")
        tabela.add_column("Estado")

        for indice, localizacao in enumerate(localizacoes, start=1):
            tabela.add_row(str(indice), localizacao.nome, localizacao.estado)

        self._console.print(tabela)

        escolha = Prompt.ask(
            "Digite o número da cidade desejada",
            choices=[str(i) for i in range(1, len(localizacoes) + 1)],
        )
        return localizacoes[int(escolha) - 1]

    def solicitar_unidades(
        self, conversor_temp: ConversorTemperatura, conversor_vento: ConversorVelocidade
    ) -> tuple[str, str]:
        """Pergunta em qual unidade de temperatura e de vento o usuário quer ver o resultado."""
        self._console.print("\n[bold]Em que unidade você quer ver a resposta?[/bold]")
        unidade_temp = self._escolher_unidade("🌡️  Temperatura", conversor_temp)
        unidade_vento = self._escolher_unidade("🌬️  Vento", conversor_vento)
        return unidade_temp, unidade_vento

    def _escolher_unidade(self, rotulo: str, conversor: ConversorUnidade) -> str:
        """Mostra as opções de unidade disponíveis para um conversor e devolve a sigla escolhida."""
        opcoes = list(conversor.unidades_disponiveis.items())

        tabela = Table(show_header=False, box=None, padding=(0, 2))
        tabela.add_column("#", style="bold cyan")
        tabela.add_column("Unidade")

        for indice, (codigo, descricao) in enumerate(opcoes, start=1):
            marcador = " [dim](padrão)[/dim]" if codigo == conversor.unidade_padrao else ""
            tabela.add_row(str(indice), f"{descricao}{marcador}")

        self._console.print(f"\n{rotulo}")
        self._console.print(tabela)

        escolha = Prompt.ask(
            "Escolha o número",
            choices=[str(i) for i in range(1, len(opcoes) + 1)],
            default="1",
        )
        return opcoes[int(escolha) - 1][0]

    def exibir_resultado(
        self,
        localizacao: Localizacao,
        clima: ClimaAtual,
        unidade_temp: str,
        unidade_vento: str,
        conversor_temp: ConversorTemperatura,
        conversor_vento: ConversorVelocidade,
    ) -> None:
        """Monta e imprime a(s) tabela(s) final(is) com o clima atual, evitando duplicar se a escolha igualar o padrão."""
        mesma_unidade = (
            unidade_temp == conversor_temp.unidade_padrao
            and unidade_vento == conversor_vento.unidade_padrao
        )

        tabela_padrao = self._montar_tabela(
            localizacao, clima, conversor_temp.unidade_padrao, conversor_vento.unidade_padrao,
            conversor_temp, conversor_vento, titulo="📊 Padrão (métrico)",
        )

        if mesma_unidade:
            self._console.print("\n")
            self._console.print(tabela_padrao)
            return

        tabela_escolhida = self._montar_tabela(
            localizacao, clima, unidade_temp, unidade_vento,
            conversor_temp, conversor_vento, titulo="🎯 Na unidade escolhida",
        )
        self._console.print("\n")
        self._console.print(Columns([tabela_padrao, tabela_escolhida], equal=True, expand=True))

    def _montar_tabela(
        self,
        localizacao: Localizacao,
        clima: ClimaAtual,
        unidade_temp: str,
        unidade_vento: str,
        conversor_temp: ConversorTemperatura,
        conversor_vento: ConversorVelocidade,
        titulo: str,
    ) -> Table:
        """Cria uma tabela Rich com todos os campos do clima já convertidos para as unidades informadas."""
        descricao, emoji = DescritorClima.descrever(clima.codigo_clima, clima.e_dia)
        direcao = DirecaoVento.para_cardeal(clima.direcao_vento_graus)

        simbolo_temp = conversor_temp.simbolo(unidade_temp)
        simbolo_vento = conversor_vento.simbolo(unidade_vento)

        temperatura = conversor_temp.converter(clima.temperatura_c, unidade_temp)
        sensacao = conversor_temp.converter(clima.sensacao_termica_c, unidade_temp)
        vento = conversor_vento.converter(clima.velocidade_vento_kmh, unidade_vento)
        rajada = conversor_vento.converter(clima.rajada_vento_kmh, unidade_vento)

        tabela = Table(title=f"{titulo} — {localizacao.nome}, {localizacao.estado}", show_header=False)
        tabela.add_column("Campo", style="bold")
        tabela.add_column("Valor")

        tabela.add_row(f"{emoji} Condição", descricao)
        tabela.add_row("🌡️ Temperatura", f"{temperatura:.1f} {simbolo_temp}")
        tabela.add_row("🤔 Sensação térmica", f"{sensacao:.1f} {simbolo_temp}")
        tabela.add_row("💧 Umidade", f"{clima.umidade_pct:.0f}%")
        tabela.add_row("🌬️ Vento", f"{vento:.1f} {simbolo_vento} ({direcao})")
        tabela.add_row("💨 Rajadas", f"{rajada:.1f} {simbolo_vento}")
        tabela.add_row("🌧️ Precipitação", f"{clima.precipitacao_mm:.1f} mm")
        tabela.add_row("☁️ Nuvens", f"{clima.cobertura_nuvens_pct:.0f}%")
        tabela.add_row("🔽 Pressão", f"{clima.pressao_hpa:.0f} hPa")

        return tabela


class AplicativoClima:
    """Orquestra o fluxo completo do programa: localizar a cidade, buscar o clima e exibir o resultado."""

    def __init__(self) -> None:
        """Monta o console compartilhado e todas as dependências do aplicativo."""
        self._console = Console()
        self._geocodificador = GeocodificadorOpenMeteo(self._console)
        self._servico_clima = ServicoClima(self._console)
        self._conversor_temp = ConversorTemperatura()
        self._conversor_vento = ConversorVelocidade()
        self._painel = PainelClima(self._console)

    def executar(self) -> None:
        """Ponto de entrada do programa: conduz toda a experiência sem nunca deixar um erro estourar na tela."""
        try:
            self._painel.exibir_boas_vindas()

            localizacao = self._painel.solicitar_localizacao(self._geocodificador)
            if localizacao is None:
                return

            with self._console.status("[cyan]Consultando o clima...[/cyan]", spinner="dots"):
                clima = self._servico_clima.obter_clima_atual(localizacao)

            unidade_temp, unidade_vento = self._painel.solicitar_unidades(
                self._conversor_temp, self._conversor_vento
            )

            self._painel.exibir_resultado(
                localizacao, clima, unidade_temp, unidade_vento,
                self._conversor_temp, self._conversor_vento,
            )

        except KeyboardInterrupt:
            self._console.print("\n[bold yellow]⚠️  Programa encerrado pelo usuário. Até a próxima! 👋[/bold yellow]")
        except ErroServicoClima as erro:
            self._console.print(f"\n[bold red]⚠️  {erro}[/bold red]")
        except Exception as erro:
            self._console.print(f"\n[bold red]⚠️  Ocorreu um erro inesperado: {erro}[/bold red]")


def main() -> None:
    """Função de entrada padrão do script."""
    aplicativo = AplicativoClima()
    aplicativo.executar()


if __name__ == "__main__":
    main()