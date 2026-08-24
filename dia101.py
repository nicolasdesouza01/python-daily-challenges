"""Monitor de CAPE — réplica funcional de um diagrama de sondagem atmosférica (Skew-T Log-P)
renderizada no terminal, usando dados reais da API pública Open-Meteo, sem chave e sem banco
de dados.
"""

import math
import sys
import unicodedata

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


NIVEIS_PRESSAO_HPA = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500,
                       400, 300, 250, 200, 150, 100, 70, 50, 30]

INCLINACAO_SKEW = 100.0

URL_GEOCODIFICACAO = "https://geocoding-api.open-meteo.com/v1/search"
URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

ESTADOS_BRASIL = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

FLECHAS_DIRECAO = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]


def _normalizar_texto(texto: str) -> str:
    """Remove acentos e padroniza a caixa de um texto para permitir comparações mais tolerantes."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.strip().upper()


def _construir_mapa_estados() -> dict:
    """Monta um dicionário de busca que aceita tanto a sigla (UF) quanto o nome completo do estado."""
    mapa = {}
    for uf, nome in ESTADOS_BRASIL.items():
        mapa[_normalizar_texto(uf)] = nome
        mapa[_normalizar_texto(nome)] = nome
    return mapa


MAPA_ESTADOS_NORMALIZADO = _construir_mapa_estados()


def seta_para_direcao(graus: float) -> str:
    """Converte a direção meteorológica (de onde o vento sopra) em uma seta apontando para onde ele vai."""
    graus_ajustado = (graus + 180.0) % 360.0
    indice = int((graus_ajustado + 22.5) // 45) % 8
    return FLECHAS_DIRECAO[indice]


def cor_para_velocidade(velocidade_kmh: float) -> str:
    """Escolhe uma cor de destaque proporcional à intensidade do vento em um nível."""
    if velocidade_kmh < 20:
        return "green3"
    if velocidade_kmh < 40:
        return "yellow3"
    if velocidade_kmh < 60:
        return "dark_orange"
    return "red3"


class ErroConsultaClima(Exception):
    """Erro amigável para qualquer falha na comunicação com a API de geocodificação ou de previsão."""


class ErroEntradaEncerrada(Exception):
    """Sinaliza que a entrada padrão foi encerrada (EOF) enquanto o programa esperava uma resposta."""


class NivelAtmosferico:
    """Representa uma linha da matriz de sondagem: um nível de pressão e suas variáveis associadas."""

    def __init__(self, pressao_hpa, altura_m=None, temperatura_c=None, ponto_orvalho_c=None,
                 velocidade_vento_kmh=None, direcao_vento_graus=None):
        """Guarda as variáveis atmosféricas medidas (ou ausentes) para este nível de pressão."""
        self._pressao_hpa = pressao_hpa
        self._altura_m = altura_m
        self._temperatura_c = temperatura_c
        self._ponto_orvalho_c = ponto_orvalho_c
        self._velocidade_vento_kmh = velocidade_vento_kmh
        self._direcao_vento_graus = direcao_vento_graus

    @property
    def pressao_hpa(self):
        """Pressão atmosférica do nível, em hPa."""
        return self._pressao_hpa

    @property
    def altura_m(self):
        """Altura geopotencial aproximada do nível, em metros acima do nível do mar."""
        return self._altura_m

    @property
    def temperatura_c(self):
        """Temperatura do ar no nível, em graus Celsius."""
        return self._temperatura_c

    @property
    def ponto_orvalho_c(self):
        """Temperatura do ponto de orvalho no nível, em graus Celsius."""
        return self._ponto_orvalho_c

    @property
    def velocidade_vento_kmh(self):
        """Velocidade do vento no nível, em km/h."""
        return self._velocidade_vento_kmh

    @property
    def direcao_vento_graus(self):
        """Direção de onde o vento sopra no nível, em graus (convenção meteorológica)."""
        return self._direcao_vento_graus

    @property
    def dados_completos(self) -> bool:
        """Indica se o nível tem temperatura e ponto de orvalho suficientes para ser plotado."""
        return self._temperatura_c is not None and self._ponto_orvalho_c is not None


class PerfilAtmosferico:
    """A matriz de sondagem completa: uma cidade, um horário e a coluna de níveis atmosféricos."""

    FAIXAS_RISCO_CAPE = (
        (500, "estável", "green3"),
        (1500, "fraco", "yellow3"),
        (2500, "moderado", "dark_orange"),
        (4000, "forte", "red3"),
    )

    def __init__(self, cidade, estado, latitude, longitude, niveis, cape_jkg=None, cin_jkg=None,
                 indice_elevado=None, altura_congelamento_m=None, temperatura_superficie=None,
                 ponto_orvalho_superficie=None, horario_valido=None):
        """Monta o perfil a partir dos dados já extraídos da API, ordenando os níveis do chão para cima."""
        self._cidade = cidade
        self._estado = estado
        self._latitude = latitude
        self._longitude = longitude
        self._niveis = sorted(niveis, key=lambda nivel: -nivel.pressao_hpa)
        self._cape_jkg = cape_jkg
        self._cin_jkg = cin_jkg
        self._indice_elevado = indice_elevado
        self._altura_congelamento_m = altura_congelamento_m
        self._temperatura_superficie = temperatura_superficie
        self._ponto_orvalho_superficie = ponto_orvalho_superficie
        self._horario_valido = horario_valido

    @property
    def cidade(self):
        """Nome da cidade consultada, conforme retornado pela geocodificação."""
        return self._cidade

    @property
    def estado(self):
        """Nome do estado da cidade consultada."""
        return self._estado

    @property
    def latitude(self):
        """Latitude usada na consulta à API de previsão."""
        return self._latitude

    @property
    def longitude(self):
        """Longitude usada na consulta à API de previsão."""
        return self._longitude

    @property
    def niveis(self):
        """Cópia da lista de níveis atmosféricos, do chão para o topo."""
        return list(self._niveis)

    @property
    def cape_jkg(self):
        """Energia potencial convectiva disponível (CAPE), em J/kg, fornecida diretamente pela API."""
        return self._cape_jkg

    @property
    def cin_jkg(self):
        """Inibição convectiva (CIN), em J/kg, fornecida diretamente pela API."""
        return self._cin_jkg

    @property
    def indice_elevado(self):
        """Índice de Elevação (Lifted Index), fornecido diretamente pela API."""
        return self._indice_elevado

    @property
    def altura_congelamento_m(self):
        """Altura do nível de congelamento (0°C), em metros, fornecida diretamente pela API."""
        return self._altura_congelamento_m

    @property
    def temperatura_superficie(self):
        """Temperatura do ar na superfície, em graus Celsius."""
        return self._temperatura_superficie

    @property
    def ponto_orvalho_superficie(self):
        """Ponto de orvalho na superfície, em graus Celsius."""
        return self._ponto_orvalho_superficie

    @property
    def horario_valido(self):
        """Horário local ao qual esta sondagem se refere."""
        return self._horario_valido

    def niveis_validos(self):
        """Retorna apenas os níveis com dados suficientes para plotagem, filtrando buracos da API."""
        return [nivel for nivel in self._niveis if nivel.dados_completos]

    def classificar_risco_cape(self):
        """Classifica a energia convectiva disponível em uma categoria de risco (rótulo, cor)."""
        if self._cape_jkg is None:
            return "indisponível", "grey50"
        for limite, rotulo, cor in self.FAIXAS_RISCO_CAPE:
            if self._cape_jkg < limite:
                return rotulo, cor
        return "extremo", "bright_magenta"


class ClienteOpenMeteo:
    """Cliente HTTP para as APIs públicas Open-Meteo de geocodificação e previsão, sem necessidade de chave."""

    TIMEOUT_SEGUNDOS = 12

    def __init__(self):
        """Prepara uma sessão HTTP reutilizável para as consultas."""
        self._sessao = requests.Session()

    def _tratar_erros_de_rede(self, funcao_requisicao, mensagem_contexto):
        """Executa uma requisição convertendo qualquer falha de rede em um ErroConsultaClima amigável."""
        try:
            resposta = funcao_requisicao()
            resposta.raise_for_status()
            return resposta
        except requests.exceptions.Timeout:
            raise ErroConsultaClima(f"{mensagem_contexto} demorou demais para responder. Tente novamente.")
        except requests.exceptions.ConnectionError:
            raise ErroConsultaClima(f"Não foi possível conectar à internet para {mensagem_contexto.lower()}.")
        except requests.exceptions.HTTPError as erro:
            raise ErroConsultaClima(f"{mensagem_contexto} foi recusada pelo servidor ({erro}).")
        except requests.exceptions.RequestException as erro:
            raise ErroConsultaClima(f"Falha inesperada ao tentar {mensagem_contexto.lower()}: {erro}")

    def buscar_cidade(self, nome_cidade: str, estado: str) -> dict:
        """Busca coordenadas de uma cidade brasileira via geocodificação, qualificando pelo estado informado."""
        parametros = {
            "name": f"{nome_cidade}, {estado}",
            "count": 5,
            "language": "pt",
            "countryCode": "BR",
            "format": "json",
        }
        resposta = self._tratar_erros_de_rede(
            lambda: self._sessao.get(URL_GEOCODIFICACAO, params=parametros, timeout=self.TIMEOUT_SEGUNDOS),
            "A busca pela cidade",
        )
        try:
            dados = resposta.json()
        except ValueError:
            raise ErroConsultaClima("A resposta da busca de cidade veio em um formato inesperado.")

        resultados = dados.get("results") or []
        if not resultados:
            raise ErroConsultaClima(
                f"Não encontrei '{nome_cidade}' em {estado}. Confira a grafia e tente novamente."
            )

        melhor = resultados[0]
        return {
            "nome": melhor.get("name", nome_cidade),
            "estado": melhor.get("admin1", estado),
            "latitude": melhor["latitude"],
            "longitude": melhor["longitude"],
        }

    def obter_sondagem(self, latitude: float, longitude: float) -> dict:
        """Busca a sondagem atmosférica (níveis de pressão e índices convectivos) para uma coordenada."""
        variaveis = []
        for nivel in NIVEIS_PRESSAO_HPA:
            variaveis += [
                f"temperature_{nivel}hPa",
                f"dew_point_{nivel}hPa",
                f"wind_speed_{nivel}hPa",
                f"wind_direction_{nivel}hPa",
                f"geopotential_height_{nivel}hPa",
            ]
        variaveis += [
            "cape", "convective_inhibition", "lifted_index", "freezing_level_height",
            "temperature_2m", "dew_point_2m",
        ]
        parametros = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(variaveis),
            "forecast_hours": 1,
            "timezone": "auto",
        }
        resposta = self._tratar_erros_de_rede(
            lambda: self._sessao.get(URL_PREVISAO, params=parametros, timeout=self.TIMEOUT_SEGUNDOS),
            "A busca pelos dados atmosféricos",
        )
        try:
            return resposta.json()
        except ValueError:
            raise ErroConsultaClima("A resposta da previsão atmosférica veio em um formato inesperado.")


class MontadorPerfil:
    """Converte a resposta bruta da API Open-Meteo em um PerfilAtmosferico pronto para uso."""

    @staticmethod
    def montar(cidade, estado, latitude, longitude, dados_api: dict) -> PerfilAtmosferico:
        """Extrai a primeira hora disponível de cada variável e monta a matriz de níveis atmosféricos."""
        horario = dados_api.get("hourly", {})

        def valor(chave):
            """Lê o primeiro valor de uma série horária, retornando None se ausente ou vazia."""
            serie = horario.get(chave)
            if not serie:
                return None
            try:
                return serie[0]
            except (IndexError, TypeError):
                return None

        niveis = [
            NivelAtmosferico(
                pressao_hpa=pressao,
                altura_m=valor(f"geopotential_height_{pressao}hPa"),
                temperatura_c=valor(f"temperature_{pressao}hPa"),
                ponto_orvalho_c=valor(f"dew_point_{pressao}hPa"),
                velocidade_vento_kmh=valor(f"wind_speed_{pressao}hPa"),
                direcao_vento_graus=valor(f"wind_direction_{pressao}hPa"),
            )
            for pressao in NIVEIS_PRESSAO_HPA
        ]

        horarios = horario.get("time") or []
        return PerfilAtmosferico(
            cidade=cidade,
            estado=estado,
            latitude=latitude,
            longitude=longitude,
            niveis=niveis,
            cape_jkg=valor("cape"),
            cin_jkg=valor("convective_inhibition"),
            indice_elevado=valor("lifted_index"),
            altura_congelamento_m=valor("freezing_level_height"),
            temperatura_superficie=valor("temperature_2m"),
            ponto_orvalho_superficie=valor("dew_point_2m"),
            horario_valido=horarios[0] if horarios else None,
        )


class EixoSondagem:
    """Calcula a transformação de (pressão, temperatura) para células da tela, aplicando o cisalhamento
    clássico do diagrama Skew-T Log-P.
    """

    def __init__(self, pressao_topo_hpa, pressao_base_hpa, temp_min_c, temp_max_c, colunas, sublinhas,
                 graus_inclinacao=INCLINACAO_SKEW):
        """Define os limites físicos (pressão e temperatura) e a resolução da grade de plotagem."""
        self._pressao_topo = pressao_topo_hpa
        self._pressao_base = pressao_base_hpa
        self._temp_min = temp_min_c
        self._temp_max = temp_max_c
        self._colunas = colunas
        self._sublinhas = sublinhas
        self._inclinacao = graus_inclinacao

    @property
    def temp_min(self):
        """Limite inferior de temperatura (°C) representado no eixo horizontal."""
        return self._temp_min

    @property
    def temp_max(self):
        """Limite superior de temperatura (°C) representado no eixo horizontal."""
        return self._temp_max

    def fracao_altura(self, pressao_hpa) -> float:
        """Converte uma pressão em uma fração de altura (0 na base, 1 no topo) em escala logarítmica."""
        log_base = math.log(self._pressao_base)
        log_topo = math.log(self._pressao_topo)
        log_p = math.log(max(pressao_hpa, self._pressao_topo))
        return (log_base - log_p) / (log_base - log_topo)

    def temperatura_inclinada(self, temperatura_c, fracao_altura) -> float:
        """Aplica o cisalhamento clássico do Skew-T: quanto mais alto, mais a isoterma se desloca à direita."""
        return temperatura_c + self._inclinacao * fracao_altura

    def para_celula(self, pressao_hpa, temperatura_c):
        """Converte um ponto (pressão, temperatura) em coordenadas (sublinha, coluna) da grade de plotagem."""
        fracao = self.fracao_altura(pressao_hpa)
        t_inclinada = self.temperatura_inclinada(temperatura_c, fracao)
        sublinha = round((1.0 - fracao) * (self._sublinhas - 1))
        coluna = round((t_inclinada - self._temp_min) / (self._temp_max - self._temp_min) * (self._colunas - 1))
        return sublinha, coluna


class TelaSubpixel:
    """Uma grade de subpixels (2 por linha de terminal, via caracteres de meio bloco) para desenhar
    linhas diagonais suaves com o dobro da resolução vertical.
    """

    def __init__(self, colunas, linhas_terminal):
        """Cria uma grade vazia com a resolução necessária para acomodar o gráfico."""
        self._colunas = colunas
        self._linhas_terminal = linhas_terminal
        self._sublinhas = linhas_terminal * 2
        self._grade = [[None] * colunas for _ in range(self._sublinhas)]

    @property
    def colunas(self):
        """Número de colunas (caracteres) de largura da tela."""
        return self._colunas

    @property
    def sublinhas(self):
        """Número de subpixels verticais disponíveis (o dobro do número de linhas do terminal)."""
        return self._sublinhas

    def pintar_ponto(self, sublinha, coluna, cor):
        """Pinta um subpixel com uma cor, ignorando silenciosamente coordenadas fora da grade."""
        if 0 <= sublinha < self._sublinhas and 0 <= coluna < self._colunas:
            self._grade[sublinha][coluna] = cor

    def pintar_ponto_fraco(self, sublinha, coluna, cor):
        """Pinta um subpixel só se ele ainda estiver vazio, para não sobrepor traços de dados com a grade."""
        if 0 <= sublinha < self._sublinhas and 0 <= coluna < self._colunas and self._grade[sublinha][coluna] is None:
            self._grade[sublinha][coluna] = cor

    def desenhar_linha(self, sublinha_a, coluna_a, sublinha_b, coluna_b, cor):
        """Liga dois pontos da grade com um traço contínuo usando o algoritmo de Bresenham."""
        x0, y0, x1, y1 = coluna_a, sublinha_a, coluna_b, sublinha_b
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        passo_x = 1 if x0 < x1 else -1
        passo_y = 1 if y0 < y1 else -1
        erro = dx + dy
        while True:
            self.pintar_ponto(y0, x0, cor)
            if x0 == x1 and y0 == y1:
                break
            erro_dobrado = 2 * erro
            if erro_dobrado >= dy:
                erro += dy
                x0 += passo_x
            if erro_dobrado <= dx:
                erro += dx
                y0 += passo_y

    def para_linhas_rich(self):
        """Converte a grade de subpixels em uma lista de objetos Text do Rich, um por linha do terminal."""
        linhas = []
        for indice_linha in range(self._linhas_terminal):
            topo = self._grade[indice_linha * 2]
            base = self._grade[indice_linha * 2 + 1]
            texto = Text()
            for coluna in range(self._colunas):
                cor_topo = topo[coluna]
                cor_base = base[coluna]
                if cor_topo and cor_base:
                    texto.append("▀", style=f"{cor_topo} on {cor_base}")
                elif cor_topo:
                    texto.append("▀", style=cor_topo)
                elif cor_base:
                    texto.append("▄", style=cor_base)
                else:
                    texto.append(" ")
            linhas.append(texto)
        return linhas


class RenderizadorSkewT:
    """Monta a representação visual (Rich) de uma sondagem em um diagrama Skew-T Log-P para o terminal."""

    COR_TEMPERATURA = "bright_red"
    COR_ORVALHO = "bright_green"
    COR_ISOTERMA = "grey35"
    COR_NIVEL = "grey27"
    LARGURA_ROTULO = 9
    LARGURA_VENTO = 11
    NIVEIS_ROTULADOS = frozenset({1000, 850, 700, 500, 400, 300, 200, 100})

    def __init__(self, perfil: PerfilAtmosferico, colunas: int, linhas: int):
        """Guarda o perfil a renderizar e as dimensões de tela disponíveis para o gráfico."""
        self._perfil = perfil
        self._colunas = max(40, colunas)
        self._linhas = max(20, linhas)
        self._niveis_validos = perfil.niveis_validos()

    def _construir_eixo(self) -> EixoSondagem:
        """Determina os limites de temperatura necessários para acomodar os dados já inclinados, com folga."""
        niveis = self._perfil.niveis
        pressao_base = niveis[0].pressao_hpa if niveis else 1000
        pressao_topo = niveis[-1].pressao_hpa if niveis else 30
        eixo_temporario = EixoSondagem(pressao_topo, pressao_base, -60, 40, self._colunas, self._linhas * 2)

        temperaturas_inclinadas = []
        for nivel in self._niveis_validos:
            fracao = eixo_temporario.fracao_altura(nivel.pressao_hpa)
            temperaturas_inclinadas.append(eixo_temporario.temperatura_inclinada(nivel.temperatura_c, fracao))
            temperaturas_inclinadas.append(eixo_temporario.temperatura_inclinada(nivel.ponto_orvalho_c, fracao))
        if not temperaturas_inclinadas:
            temperaturas_inclinadas = [-40.0, 40.0]

        margem = 8
        temp_min = min(temperaturas_inclinadas) - margem
        temp_max = max(temperaturas_inclinadas) + margem
        return EixoSondagem(pressao_topo, pressao_base, temp_min, temp_max, self._colunas, self._linhas * 2)

    def _niveis_para_rotular(self):
        """Seleciona apenas os níveis de pressão marcantes, para não poluir o eixo com 19 rótulos."""
        return [nivel for nivel in self._perfil.niveis if nivel.pressao_hpa in self.NIVEIS_ROTULADOS]

    def _desenhar_grade_isotermas(self, tela: TelaSubpixel, eixo: EixoSondagem):
        """Desenha as diagonais de referência de temperatura constante, marca registrada do Skew-T."""
        for temperatura_rotulo in range(-80, 61, 10):
            for sublinha in range(tela.sublinhas):
                fracao = 1.0 - (sublinha / max(1, tela.sublinhas - 1))
                t_inclinada = eixo.temperatura_inclinada(temperatura_rotulo, fracao)
                coluna = round((t_inclinada - eixo.temp_min) / (eixo.temp_max - eixo.temp_min) * (tela.colunas - 1))
                tela.pintar_ponto_fraco(sublinha, coluna, self.COR_ISOTERMA)

    def _desenhar_niveis_pressao(self, tela: TelaSubpixel, eixo: EixoSondagem, niveis_rotulados):
        """Desenha uma linha horizontal fraca em cada nível de pressão marcante, como referência de altura."""
        for nivel in niveis_rotulados:
            fracao = eixo.fracao_altura(nivel.pressao_hpa)
            sublinha = round((1.0 - fracao) * (tela.sublinhas - 1))
            for coluna in range(tela.colunas):
                tela.pintar_ponto_fraco(sublinha, coluna, self.COR_NIVEL)

    def _desenhar_perfil(self, tela: TelaSubpixel, eixo: EixoSondagem):
        """Liga os pontos de temperatura e ponto de orvalho de níveis consecutivos, pulando lacunas sem dado."""
        for anterior, atual in zip(self._niveis_validos, self._niveis_validos[1:]):
            sub_a, col_a = eixo.para_celula(anterior.pressao_hpa, anterior.temperatura_c)
            sub_b, col_b = eixo.para_celula(atual.pressao_hpa, atual.temperatura_c)
            tela.desenhar_linha(sub_a, col_a, sub_b, col_b, self.COR_TEMPERATURA)

            sub_a, col_a = eixo.para_celula(anterior.pressao_hpa, anterior.ponto_orvalho_c)
            sub_b, col_b = eixo.para_celula(atual.pressao_hpa, atual.ponto_orvalho_c)
            tela.desenhar_linha(sub_a, col_a, sub_b, col_b, self.COR_ORVALHO)

    def _montar_coluna_vento(self, niveis_rotulados, eixo: EixoSondagem):
        """Cria a coluna lateral com a seta de direção e a velocidade do vento em cada nível rotulado."""
        linhas = [Text(" " * self.LARGURA_VENTO) for _ in range(self._linhas)]
        for nivel in niveis_rotulados:
            if nivel.velocidade_vento_kmh is None or nivel.direcao_vento_graus is None:
                continue
            fracao = eixo.fracao_altura(nivel.pressao_hpa)
            linha_terminal = round((1.0 - fracao) * (self._linhas - 1))
            if 0 <= linha_terminal < self._linhas:
                seta = seta_para_direcao(nivel.direcao_vento_graus)
                cor = cor_para_velocidade(nivel.velocidade_vento_kmh)
                texto = Text()
                texto.append(f" {seta} ", style=f"bold {cor}")
                texto.append(f"{nivel.velocidade_vento_kmh:>3.0f}km/h", style=cor)
                linhas[linha_terminal] = texto
        return linhas

    def _montar_coluna_rotulos(self, niveis_rotulados, eixo: EixoSondagem):
        """Cria a coluna lateral com a pressão (e altura, quando disponível) de cada nível rotulado."""
        rotulos = [Text(" " * self.LARGURA_ROTULO) for _ in range(self._linhas)]
        for nivel in niveis_rotulados:
            fracao = eixo.fracao_altura(nivel.pressao_hpa)
            linha_terminal = round((1.0 - fracao) * (self._linhas - 1))
            if 0 <= linha_terminal < self._linhas:
                texto = f"{nivel.pressao_hpa:>4}hPa"
                rotulos[linha_terminal] = Text(texto.rjust(self.LARGURA_ROTULO), style="grey62")
        return rotulos

    def _montar_rodape_temperaturas(self, eixo: EixoSondagem):
        """Cria a régua de temperaturas do rodapé, alinhada à base (sem inclinação) de cada isoterma."""
        caracteres = [" "] * self._colunas
        for temperatura_rotulo in range(-40, 41, 20):
            coluna = round(
                (temperatura_rotulo - eixo.temp_min) / (eixo.temp_max - eixo.temp_min) * (self._colunas - 1)
            )
            rotulo = f"{temperatura_rotulo}°C"
            inicio = max(0, coluna - len(rotulo) // 2)
            for deslocamento, caractere in enumerate(rotulo):
                posicao = inicio + deslocamento
                if 0 <= posicao < self._colunas:
                    caracteres[posicao] = caractere
        return Text(" " * self.LARGURA_ROTULO + "".join(caracteres), style="grey62")

    def montar_painel(self) -> Panel:
        """Monta o painel Rich completo: rótulos de pressão, gráfico Skew-T e coluna de vento por nível."""
        eixo = self._construir_eixo()
        tela = TelaSubpixel(self._colunas, self._linhas)
        niveis_rotulados = self._niveis_para_rotular()

        self._desenhar_grade_isotermas(tela, eixo)
        self._desenhar_niveis_pressao(tela, eixo, niveis_rotulados)
        self._desenhar_perfil(tela, eixo)

        linhas_grafico = tela.para_linhas_rich()
        linhas_vento = self._montar_coluna_vento(niveis_rotulados, eixo)
        linhas_rotulo = self._montar_coluna_rotulos(niveis_rotulados, eixo)

        tabela = Table.grid(padding=(0, 1))
        tabela.add_column(width=self.LARGURA_ROTULO)
        tabela.add_column()
        tabela.add_column(width=self.LARGURA_VENTO)
        for rotulo, grafico, vento in zip(linhas_rotulo, linhas_grafico, linhas_vento):
            tabela.add_row(rotulo, grafico, vento)

        conteudo = Table.grid()
        conteudo.add_row(tabela)
        conteudo.add_row(self._montar_rodape_temperaturas(eixo))
        conteudo.add_row(Text("Vermelho: temperatura   Verde: ponto de orvalho", style="grey50"))

        subtitulo = f"{self._perfil.cidade}/{self._perfil.estado} — {self._perfil.horario_valido or 'horário indisponível'}"
        return Panel(conteudo, title="🌩️  Sondagem Skew-T Log-P", subtitle=subtitulo,
                     border_style="cyan", box=box.ROUNDED)


class PainelParametros:
    """Monta o painel de índices de instabilidade atmosférica, no espírito do quadro de um sounding real."""

    def __init__(self, perfil: PerfilAtmosferico):
        """Guarda o perfil do qual os índices serão extraídos e apresentados."""
        self._perfil = perfil

    def _estimar_altura_lcl(self):
        """Estima a altura da base da nuvem (LCL) pela fórmula clássica de Espy, pois a API não a fornece."""
        temperatura = self._perfil.temperatura_superficie
        orvalho = self._perfil.ponto_orvalho_superficie
        if temperatura is None or orvalho is None:
            return None
        return max(0.0, 125.0 * (temperatura - orvalho))

    def montar(self) -> Panel:
        """Monta a tabela final de índices convectivos, sinalizando quando um valor é uma estimativa."""
        tabela = Table(box=box.SIMPLE, show_header=False, expand=True)
        tabela.add_column(style="bold")
        tabela.add_column(justify="right")

        rotulo_risco, cor_risco = self._perfil.classificar_risco_cape()
        cape_texto = f"{self._perfil.cape_jkg:.0f} J/kg" if self._perfil.cape_jkg is not None else "indisponível"
        tabela.add_row("⚡ CAPE", Text(f"{cape_texto} ({rotulo_risco})", style=cor_risco))

        cin_texto = f"{self._perfil.cin_jkg:.0f} J/kg" if self._perfil.cin_jkg is not None else "indisponível"
        tabela.add_row("CIN (inibição convectiva)", cin_texto)

        li_texto = f"{self._perfil.indice_elevado:.1f}" if self._perfil.indice_elevado is not None else "indisponível"
        tabela.add_row("Índice de Elevação (LI)", li_texto)

        congelamento = self._perfil.altura_congelamento_m
        congelamento_texto = f"{congelamento:.0f} m" if congelamento is not None else "indisponível"
        tabela.add_row("Nível de congelamento (0°C)", congelamento_texto)

        lcl = self._estimar_altura_lcl()
        lcl_texto = f"~{lcl:.0f} m (estimativa)" if lcl is not None else "indisponível"
        tabela.add_row("Base da nuvem (LCL)", lcl_texto)

        if self._perfil.temperatura_superficie is not None:
            tabela.add_row("Temperatura na superfície", f"{self._perfil.temperatura_superficie:.1f}°C")
        if self._perfil.ponto_orvalho_superficie is not None:
            tabela.add_row("Ponto de orvalho na superfície", f"{self._perfil.ponto_orvalho_superficie:.1f}°C")

        return Panel(tabela, title="📊 Índices Convectivos", border_style="magenta", box=box.ROUNDED)


def pedir_estado(console: Console) -> str:
    """Pede repetidamente o estado até receber uma UF ou nome válido, tratando entradas incorretas."""
    while True:
        try:
            bruto = console.input("[bold cyan]Estado (UF ou nome)[/bold cyan]: ")
        except EOFError:
            raise ErroEntradaEncerrada()
        estado = MAPA_ESTADOS_NORMALIZADO.get(_normalizar_texto(bruto))
        if estado:
            return estado
        console.print("[red]Não reconheci esse estado. Use a sigla (ex: SP) ou o nome completo (ex: São Paulo).[/red]")


def pedir_cidade(console: Console) -> str:
    """Pede repetidamente o nome da cidade até receber um valor não vazio."""
    while True:
        try:
            bruto = console.input("[bold cyan]Cidade[/bold cyan]: ").strip()
        except EOFError:
            raise ErroEntradaEncerrada()
        if bruto:
            return bruto
        console.print("[red]O nome da cidade não pode ficar em branco.[/red]")


class AplicativoMonitorCAPE:
    """Orquestra o fluxo do programa: entrada do usuário, consulta à API e renderização do painel."""

    def __init__(self):
        """Prepara o console Rich e o cliente HTTP compartilhados por toda a execução."""
        self._console = Console()
        self._cliente = ClienteOpenMeteo()

    def executar(self):
        """Laço principal do aplicativo, com tratamento de interrupção e erros para nunca quebrar em traceback."""
        self._exibir_cabecalho()
        try:
            while True:
                self._executar_uma_consulta()
                if not self._perguntar_sim_nao("Consultar outra cidade?"):
                    break
        except (KeyboardInterrupt, ErroEntradaEncerrada):
            self._console.print()
            self._console.print("[yellow]Encerrando o monitor de CAPE. Até a próxima![/yellow]")
            sys.exit(0)
        except Exception as erro:
            self._console.print()
            self._console.print(f"[bold red]Ocorreu um problema inesperado e o programa precisou parar: {erro}[/bold red]")
            sys.exit(1)

    def _executar_uma_consulta(self):
        """Coleta estado e cidade, busca os dados na API e exibe o painel de sondagem correspondente."""
        estado = pedir_estado(self._console)
        cidade = pedir_cidade(self._console)
        try:
            with self._console.status("[cyan]Localizando cidade...[/cyan]", spinner="dots"):
                local = self._cliente.buscar_cidade(cidade, estado)
            with self._console.status("[cyan]Buscando dados atmosféricos...[/cyan]", spinner="dots"):
                dados_brutos = self._cliente.obter_sondagem(local["latitude"], local["longitude"])
        except ErroConsultaClima as erro:
            self._console.print(f"[red]{erro}[/red]")
            return

        perfil = MontadorPerfil.montar(local["nome"], local["estado"], local["latitude"], local["longitude"],
                                        dados_brutos)
        self._exibir_perfil(perfil)

    def _exibir_perfil(self, perfil: PerfilAtmosferico):
        """Calcula o espaço disponível no terminal e imprime o gráfico e o painel de índices."""
        largura_disponivel = max(60, self._console.size.width - (RenderizadorSkewT.LARGURA_ROTULO +
                                                                   RenderizadorSkewT.LARGURA_VENTO + 6))
        altura_disponivel = max(20, self._console.size.height - 12)
        renderizador = RenderizadorSkewT(perfil, colunas=largura_disponivel, linhas=altura_disponivel)
        self._console.print(renderizador.montar_painel())
        self._console.print(PainelParametros(perfil).montar())

    def _perguntar_sim_nao(self, pergunta: str) -> bool:
        """Pede uma resposta sim/não, tratando entradas inválidas e o fim inesperado da entrada padrão."""
        while True:
            try:
                resposta = self._console.input(f"[bold]{pergunta} (s/n)[/bold]: ").strip().lower()
            except EOFError:
                return False
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            self._console.print("[red]Responda apenas com 's' ou 'n'.[/red]")

    def _exibir_cabecalho(self):
        """Imprime o cabeçalho de boas-vindas do aplicativo."""
        titulo = Text("⚡ MONITOR DE CAPE — Sondagem Atmosférica em Tempo Real ⚡", justify="center",
                       style="bold white on dark_red")
        self._console.print(Panel(titulo, box=box.DOUBLE))


if __name__ == "__main__":
    AplicativoMonitorCAPE().executar()