"""
Vida em Números.

Programa de terminal que recebe uma data de nascimento e apresenta,
em um painel visual, um conjunto de estatísticas curiosas calculadas
a partir dela (dias vividos, batimentos cardíacos estimados,
distância percorrida no espaço junto com a Terra, entre outras).
"""

import sys
from datetime import date, datetime
from time import sleep

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box


def formatar_numero_br(numero: int) -> str:
    """Formata um número inteiro utilizando o separador de milhar brasileiro (ponto)."""
    return f"{numero:,}".replace(",", ".")


class ValidadorDeData:
    """Responsável por validar e converter a data de nascimento informada pelo usuário."""

    FORMATO = "%d/%m/%Y"

    @classmethod
    def converter(cls, texto: str) -> date:
        """
        Converte uma string no formato dd/mm/aaaa em um objeto date.

        Lança ValueError com uma mensagem amigável caso o texto esteja
        em um formato inválido, represente uma data futura ou um ano
        implausivelmente antigo.
        """
        texto = texto.strip()

        if not texto:
            raise ValueError("Nenhuma data foi digitada. Tente novamente.")

        try:
            data_convertida = datetime.strptime(texto, cls.FORMATO).date()
        except ValueError:
            raise ValueError("Formato inválido. Use o padrão dd/mm/aaaa, como 25/12/1998.")

        if data_convertida > date.today():
            raise ValueError("A data informada está no futuro. Verifique e tente novamente.")

        if data_convertida.year < 1900:
            raise ValueError("Ano de nascimento muito antigo. Verifique e tente novamente.")

        return data_convertida


class CalculadoraDeVida:
    """
    Calcula estatísticas derivadas a partir de uma data de nascimento.

    Todos os valores são estimativas aproximadas, obtidas a partir de
    médias conhecidas (frequência cardíaca e respiratória em repouso,
    velocidade orbital da Terra) e não substituem dados médicos reais.
    """

    _BATIMENTOS_POR_MINUTO = 80
    _RESPIRACOES_POR_MINUTO = 16
    _VELOCIDADE_ORBITAL_TERRA_KMH = 107_000

    _DIAS_SEMANA_PT = {
        "Monday": "segunda-feira",
        "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira",
        "Thursday": "quinta-feira",
        "Friday": "sexta-feira",
        "Saturday": "sábado",
        "Sunday": "domingo",
    }

    _INICIO_SIGNOS = (
        ((1, 1), "Capricórnio"),
        ((1, 20), "Aquário"),
        ((2, 19), "Peixes"),
        ((3, 21), "Áries"),
        ((4, 20), "Touro"),
        ((5, 21), "Gêmeos"),
        ((6, 21), "Câncer"),
        ((7, 23), "Leão"),
        ((8, 23), "Virgem"),
        ((9, 23), "Libra"),
        ((10, 23), "Escorpião"),
        ((11, 22), "Sagitário"),
        ((12, 22), "Capricórnio"),
    )

    def __init__(self, data_nascimento: date):
        """Recebe a data de nascimento e prepara os valores base usados nos cálculos."""
        self._nascimento = data_nascimento
        self._hoje = date.today()
        self._dias_vividos = (self._hoje - self._nascimento).days

    @property
    def dias_vividos(self) -> int:
        """Retorna o total de dias vividos até hoje."""
        return self._dias_vividos

    @property
    def idade_anos_meses_dias(self) -> tuple:
        """Retorna a idade exata da pessoa como uma tupla (anos, meses, dias)."""
        anos = self._hoje.year - self._nascimento.year
        meses = self._hoje.month - self._nascimento.month
        dias = self._hoje.day - self._nascimento.day

        if dias < 0:
            meses -= 1
            mes_anterior = self._hoje.month - 1 or 12
            ano_referencia = self._hoje.year if self._hoje.month > 1 else self._hoje.year - 1
            dias += self._dias_no_mes(ano_referencia, mes_anterior)

        if meses < 0:
            anos -= 1
            meses += 12

        return anos, meses, dias

    @staticmethod
    def _dias_no_mes(ano: int, mes: int) -> int:
        """Retorna a quantidade de dias de um mês/ano específico, considerando anos bissextos."""
        proximo_mes = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
        primeiro_dia_do_mes = date(ano, mes, 1)
        return (proximo_mes - primeiro_dia_do_mes).days

    @property
    def horas_vividas(self) -> int:
        """Retorna o total aproximado de horas vividas."""
        return self._dias_vividos * 24

    @property
    def minutos_vividos(self) -> int:
        """Retorna o total aproximado de minutos vividos."""
        return self.horas_vividas * 60

    @property
    def batimentos_cardiacos_estimados(self) -> int:
        """Estima o total de batimentos cardíacos com base em uma frequência média de repouso."""
        return self.minutos_vividos * self._BATIMENTOS_POR_MINUTO

    @property
    def respiracoes_estimadas(self) -> int:
        """Estima o total de respirações realizadas com base em uma média de repouso."""
        return self.minutos_vividos * self._RESPIRACOES_POR_MINUTO

    @property
    def fins_de_semana_vividos(self) -> int:
        """Estima quantos fins de semana já foram vividos."""
        return self._dias_vividos // 7

    @property
    def voltas_ao_redor_do_sol(self) -> int:
        """Retorna quantas voltas completas a Terra deu ao redor do Sol desde o nascimento."""
        anos, _, _ = self.idade_anos_meses_dias
        return anos

    @property
    def distancia_percorrida_no_espaco_km(self) -> int:
        """Estima, em quilômetros, a distância percorrida junto com a Terra em sua órbita."""
        return int(self.horas_vividas * self._VELOCIDADE_ORBITAL_TERRA_KMH)

    @property
    def dia_da_semana_nascimento(self) -> str:
        """Retorna, em português, o dia da semana em que a pessoa nasceu."""
        nome_em_ingles = self._nascimento.strftime("%A")
        return self._DIAS_SEMANA_PT.get(nome_em_ingles, nome_em_ingles)

    @property
    def anos_bissextos_vividos(self) -> int:
        """Conta quantos anos bissextos ocorreram entre o nascimento e o ano atual."""
        return sum(
            1
            for ano in range(self._nascimento.year, self._hoje.year + 1)
            if self._eh_bissexto(ano)
        )

    @staticmethod
    def _eh_bissexto(ano: int) -> bool:
        """Verifica se um determinado ano é bissexto."""
        return ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)

    @property
    def signo(self) -> str:
        """Retorna o signo do zodíaco correspondente à data de nascimento."""
        mes_dia = (self._nascimento.month, self._nascimento.day)
        signo_atual = self._INICIO_SIGNOS[0][1]
        for inicio, nome_signo in self._INICIO_SIGNOS:
            if mes_dia >= inicio:
                signo_atual = nome_signo
            else:
                break
        return signo_atual

    @property
    def dias_ate_proximo_aniversario(self) -> int:
        """Calcula quantos dias faltam para o próximo aniversário."""
        proximo_aniversario = date(self._hoje.year, self._nascimento.month, self._nascimento.day)
        if proximo_aniversario < self._hoje:
            proximo_aniversario = date(
                self._hoje.year + 1, self._nascimento.month, self._nascimento.day
            )
        return (proximo_aniversario - self._hoje).days


class PainelVisual:
    """Responsável por toda a apresentação visual do programa no terminal, usando a Rich."""

    def __init__(self):
        """Inicializa o console utilizado para renderizar os elementos visuais."""
        self._console = Console()

    def exibir_boas_vindas(self) -> None:
        """Exibe o painel inicial de boas-vindas do programa."""
        texto = "Descubra estatísticas curiosas sobre a sua vida em números."
        painel = Panel(
            Align.center(texto), title="Vida em Números", border_style="cyan", box=box.ROUNDED
        )
        self._console.print(painel)

    def solicitar_data_nascimento(self) -> str:
        """Solicita ao usuário a data de nascimento e retorna o texto informado."""
        return self._console.input(
            "\n[bold cyan]Digite sua data de nascimento (dd/mm/aaaa): [/bold cyan]"
        )

    def exibir_erro(self, mensagem: str) -> None:
        """Exibe uma mensagem de erro amigável dentro de um painel destacado."""
        painel = Panel(mensagem, title="Ops", border_style="red", box=box.ROUNDED)
        self._console.print(painel)

    def exibir_calculando(self) -> None:
        """Exibe uma animação de carregamento enquanto as estatísticas são calculadas."""
        with self._console.status(
            "[bold cyan]Calculando sua vida em números...[/bold cyan]", spinner="dots"
        ):
            sleep(1.5)

    def exibir_resultado(self, calculadora: CalculadoraDeVida, nascimento: date) -> None:
        """Monta e exibe a tabela final com todas as estatísticas calculadas."""
        anos, meses, dias = calculadora.idade_anos_meses_dias

        tabela = Table(show_header=False, box=box.SIMPLE_HEAD, padding=(0, 1))
        tabela.add_column("Estatística", style="bold white")
        tabela.add_column("Valor", style="cyan")

        tabela.add_row("Idade exata", f"{anos} anos, {meses} meses e {dias} dias")
        tabela.add_row(
            "Nasceu em",
            f"{nascimento.strftime('%d/%m/%Y')} ({calculadora.dia_da_semana_nascimento})",
        )
        tabela.add_row("Signo", calculadora.signo)
        tabela.add_row("Dias vividos", formatar_numero_br(calculadora.dias_vividos))
        tabela.add_row("Horas vividas", formatar_numero_br(calculadora.horas_vividas))
        tabela.add_row("Minutos vividos", formatar_numero_br(calculadora.minutos_vividos))
        tabela.add_row(
            "Batimentos cardíacos estimados",
            formatar_numero_br(calculadora.batimentos_cardiacos_estimados),
        )
        tabela.add_row(
            "Respirações estimadas", formatar_numero_br(calculadora.respiracoes_estimadas)
        )
        tabela.add_row(
            "Fins de semana vividos", formatar_numero_br(calculadora.fins_de_semana_vividos)
        )
        tabela.add_row("Voltas ao redor do Sol", str(calculadora.voltas_ao_redor_do_sol))
        tabela.add_row(
            "Distância percorrida no espaço",
            f"{formatar_numero_br(calculadora.distancia_percorrida_no_espaco_km)} km",
        )
        tabela.add_row("Anos bissextos vividos", str(calculadora.anos_bissextos_vividos))
        tabela.add_row(
            "Dias até o próximo aniversário", str(calculadora.dias_ate_proximo_aniversario)
        )

        painel = Panel(tabela, title="Sua vida em números", border_style="green", box=box.ROUNDED)
        self._console.print(painel)

    def exibir_despedida(self) -> None:
        """Exibe uma mensagem de encerramento amigável."""
        self._console.print("\n[bold yellow]Programa encerrado. Até a próxima![/bold yellow]")


class AplicativoVidaEmNumeros:
    """Classe principal que orquestra a execução do programa, do início ao fim."""

    _TENTATIVAS_MAXIMAS = 5

    def __init__(self):
        """Inicializa o painel visual utilizado durante toda a execução."""
        self._painel = PainelVisual()

    def executar(self) -> None:
        """Executa o fluxo completo: boas-vindas, entrada de dados, cálculo e resultado."""
        self._painel.exibir_boas_vindas()

        data_nascimento = self._obter_data_nascimento_valida()
        if data_nascimento is None:
            return

        self._painel.exibir_calculando()

        calculadora = CalculadoraDeVida(data_nascimento)
        self._painel.exibir_resultado(calculadora, data_nascimento)

    def _obter_data_nascimento_valida(self):
        """Solicita repetidamente a data de nascimento até obter uma entrada válida."""
        tentativas_restantes = self._TENTATIVAS_MAXIMAS

        while tentativas_restantes > 0:
            texto_digitado = self._painel.solicitar_data_nascimento()
            try:
                return ValidadorDeData.converter(texto_digitado)
            except ValueError as erro:
                tentativas_restantes -= 1
                self._painel.exibir_erro(str(erro))

        self._painel.exibir_erro("Número máximo de tentativas atingido. Tente novamente mais tarde.")
        return None


def main() -> None:
    """Ponto de entrada do programa, tratando o encerramento pelo usuário de forma elegante."""
    aplicativo = AplicativoVidaEmNumeros()
    try:
        aplicativo.executar()
    except KeyboardInterrupt:
        Console().print("\n[bold yellow]Programa encerrado pelo usuário. Até a próxima![/bold yellow]")
        sys.exit(0)
    except Exception as erro_inesperado:
        Console().print(f"\n[bold red]Ocorreu um erro inesperado: {erro_inesperado}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()