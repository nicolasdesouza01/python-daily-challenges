import math
import random
import time
from collections import deque
from dataclasses import dataclass
from typing import List

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


@dataclass(frozen=True)
class RegistroDiario:
    """Representa o resumo meteorológico imutável de um dia concluído."""

    dia: int
    condicao: str
    min_temp: float
    max_temp: float


class GeradorClimatico:
    """Gerador procedimental de clima e variação térmica para São Paulo."""

    def __init__(self) -> None:
        """Inicializa os perfis climáticos com limites de temperatura e amplitude."""
        self._perfis = {
            "Ensolarado ☀️": (0.35, 19.0, 22.0, 6.0, 9.0),
            "Parcialmente Nublado ⛅": (0.30, 19.0, 22.0, 6.0, 9.0),
            "Chuvoso 🌧️": (0.15, 16.0, 19.0, 3.0, 5.0),
            "Frente Fria 🥶": (0.12, 12.0, 15.0, 3.0, 5.0),
            "Onda de Calor 🔥": (0.08, 25.0, 28.0, 7.0, 10.0),
        }
        self._condicao_predominante = ""
        self._temp_base = 20.0
        self._amplitude = 6.0

    @property
    def condicao_predominante(self) -> str:
        """Retorna a condição climática geral do dia."""
        return self._condicao_predominante

    def sortear_condicao_dia(self) -> str:
        """Define o clima do dia sorteando opções e configurando parâmetros térmicos."""
        opcoes = list(self._perfis.keys())
        pesos = [v[0] for v in self._perfis.values()]
        self._condicao_predominante = random.choices(opcoes, weights=pesos)[0]

        _, t_min, t_max, a_min, a_max = self._perfis[self._condicao_predominante]
        self._temp_base = random.uniform(t_min, t_max)
        self._amplitude = random.uniform(a_min, a_max)
        return self._condicao_predominante

    def obter_condicao_hora(self, hora: int) -> str:
        """Determina a condição microclimática dinâmica para a hora atual."""
        if "Chuvoso" in self._condicao_predominante:
            return (
                "Chuva Forte 🌧️" if 12 <= hora <= 19 else "Garoa Paulista 🌧️"
            )
        if "Ensolarado" in self._condicao_predominante:
            return "Céu Limpo ☀️" if 6 <= hora <= 18 else "Noite Estrelada 🌙"
        if "Parcialmente Nublado" in self._condicao_predominante:
            return "Sol entre Nuvens ⛅" if 6 <= hora <= 18 else "Noite Nublada ☁️"
        if "Frente Fria" in self._condicao_predominante:
            return (
                "Vento Frio / Nublado 🥶☁️"
                if 6 <= hora <= 18
                else "Garoa Gelada 🥶🌧️"
            )
        if "Onda de Calor" in self._condicao_predominante:
            return (
                "Calor Intenso ☀️🔥" if 10 <= hora <= 17 else "Noite Abafada 🌙🔥"
            )
        return self._condicao_predominante

    def calcular_temperatura_hora(self, hora: int) -> float:
        """Calcula a temperatura via onda senoidal com variações microclimáticas."""
        fase = (hora - 9) * math.pi / 12
        temp = (
            self._temp_base
            + self._amplitude * math.sin(fase)
            + random.uniform(-0.4, 0.4)
        )
        if "Chuvoso" in self._condicao_predominante and 14 <= hora <= 18:
            temp -= random.uniform(1.2, 2.5)
        return round(temp, 1)


class DesenhistaClimatico:
    """Gerencia animações ASCII simétricas de alta fidelidade em 4 quadros."""

    def __init__(self) -> None:
        """Inicializa as matrizes de arte e o ponteiro de quadros."""
        self._frame = 0
        self._animacoes = {
            "sol": [
                "       \\    |    /\n     -  .-------.  -\n    ---(         )---\n     -  `-------'  -\n       /    |    \\",
                "       +    |    +\n     /  .-------.  \\\n    -  (         )  -\n     \\  `-------'  /\n       +    |    +",
                "         |       \n     -- .-------. --\n    ===(         )===\n     -- `-------' --\n         |       ",
                "       /    |    \\\n     +  .-------.  +\n    ---(         )---\n     +  `-------'  +\n       \\    |    /",
            ],
            "noite": [
                "       *     .    *\n          .--.\n         /  .-'\n        |  |     .\n         \\  `-.\n       *  `--'    *",
                "       .     *    .\n          .--.\n         /  .-'\n        |  |     *\n         \\  `-.\n       .  `--'    .",
                "       *     *    *\n          .--.\n         /  .-'\n        |  |     .\n         \\  `-.\n       *  `--'    .",
                "       .     .    *\n          .--.\n         /  .-'\n        |  |     *\n         \\  `-.\n       .  `--'    *",
            ],
            "chuva": [
                "      .---.  .---.\n    .(     )(     ).\n   (               )\n    `-------------' \n       │   │   │   │\n         │   │   │  \n       │   │   │   │",
                "      .---.  .---.\n    .(     )(     ).\n   (               )\n    `-------------' \n         │   │   │  \n       │   │   │   │\n         │   │   │  ",
                "      .---.  .---.\n    .(     )(     ).\n   (               )\n    `-------------' \n       .   .   .   .\n         │   │   │  \n       │   │   │   │",
                "      .---.  .---.\n    .(     )(     ).\n   (               )\n    `-------------' \n       │   │   │   │\n       .   .   .   .\n         │   │   │  ",
            ],
            "nublado": [
                "       .---.     .--.\n     .(     ).  (    ).\n    (         )(       )\n     `-------'  `-----'",
                "      .---.     .--.\n    .(     ).  (    ).\n   (         )(       )\n    `-------'  `-----'",
                "     .---.     .--.\n   .(     ).  (    ).\n  (         )(       )\n   `-------'  `-----'",
                "    .---.     .--.\n  .(     ).  (    ).\n (         )(       )\n  `-------'  `-----'",
            ],
        }

    def avancar_frame(self) -> None:
        """Avança o ciclo de animação em um passo rotativo de 4 quadros."""
        self._frame = (self._frame + 1) % 4

    def gerar_diagrama(self, condicao_hora: str, hora: int) -> Text:
        """Retorna o quadro de animação formatado e alinhado ao centro."""
        eh_noite = hora < 6 or hora > 18

        if "Chuva" in condicao_hora or "Garoa" in condicao_hora:
            art = self._animacoes["chuva"][self._frame]
            return Text(art, style="bold cyan", justify="center")

        if eh_noite:
            art = self._animacoes["noite"][self._frame]
            return Text(art, style="bold magenta", justify="center")

        if "Sol" in condicao_hora or "Calor" in condicao_hora:
            art = self._animacoes["sol"][self._frame]
            return Text(art, style="bold yellow", justify="center")

        art = self._animacoes["nublado"][self._frame]
        return Text(art, style="bold blue", justify="center")


class EstacaoMeteorologica:
    """Gerencia o ciclo de vida, contadores e medições da estação."""

    def __init__(self) -> None:
        """Inicializa os módulos internos e a fila de histórico circular."""
        self._gerador = GeradorClimatico()
        self._desenhista = DesenhistaClimatico()
        self._dia = 1
        self._hora = 0
        self._max_temp = float("-inf")
        self._min_temp = float("inf")
        self._temp_atual = 0.0
        self._condicao_geral_dia = self._gerador.sortear_condicao_dia()
        self._condicao_hora_atual = self._gerador.obter_condicao_hora(
            self._hora
        )
        self._historico: deque[RegistroDiario] = deque(maxlen=5)

    @property
    def dia(self) -> int:
        """Retorna o dia atual."""
        return self._dia

    @property
    def hora(self) -> int:
        """Retorna a hora atual."""
        return self._hora

    @property
    def condicao_hora_atual(self) -> str:
        """Retorna a condição climática momentânea."""
        return self._condicao_hora_atual

    @property
    def temp_atual(self) -> float:
        """Retorna a temperatura atual."""
        return self._temp_atual

    @property
    def max_temp(self) -> float:
        """Retorna a temperatura máxima parcial."""
        return self._max_temp

    @property
    def min_temp(self) -> float:
        """Retorna a temperatura mínima parcial."""
        return self._min_temp

    @property
    def historico(self) -> List[RegistroDiario]:
        """Retorna a lista dos dias armazenados no histórico."""
        return list(self._historico)

    def obter_diagrama_animado(self) -> Text:
        """Obtém a ilustração gráfica do clima atual."""
        return self._desenhista.gerar_diagrama(
            self._condicao_hora_atual, self._hora
        )

    def processar_hora(self) -> None:
        """Processa a medição da hora, atualiza extremos e avança o tempo."""
        self._desenhista.avancar_frame()
        self._condicao_hora_atual = self._gerador.obter_condicao_hora(
            self._hora
        )
        self._temp_atual = self._gerador.calcular_temperatura_hora(self._hora)

        if self._temp_atual > self._max_temp:
            self._max_temp = self._temp_atual
        if self._temp_atual < self._min_temp:
            self._min_temp = self._temp_atual

        self._hora += 1
        if self._hora >= 24:
            self._historico.append(
                RegistroDiario(
                    dia=self._dia,
                    condicao=self._condicao_geral_dia,
                    min_temp=self._min_temp,
                    max_temp=self._max_temp,
                )
            )
            self._dia += 1
            self._hora = 0
            self._max_temp = float("-inf")
            self._min_temp = float("inf")
            self._condicao_geral_dia = self._gerador.sortear_condicao_dia()


class InterfaceEstacao:
    """Renderiza a HUD no terminal utilizando componentes da biblioteca Rich."""

    def __init__(self) -> None:
        """Inicializa o console da Rich."""
        self._console = Console()

    def renderizar_layout(self, estacao: EstacaoMeteorologica) -> Layout:
        """Monta o painel visual dividindo a tela em seções estilizadas."""
        layout = Layout()
        layout.split_column(
            Layout(name="cabecalho", size=4),
            Layout(name="corpo", ratio=1),
            Layout(name="rodape", size=3),
        )

        texto_cabecalho = Text(justify="center")
        texto_cabecalho.append(
            "ESTAÇÃO METEOROLÓGICA AUTOMÁTICA — SÃO PAULO / SP\n",
            style="bold cyan",
        )
        texto_cabecalho.append(
            "(simulação - ambiente meramente ilustrativo)", style="dim grey50"
        )
        layout["cabecalho"].update(Panel(texto_cabecalho, border_style="cyan"))

        tabela_atual = Table(
            title="📊 Medições em Tempo Real (Dia Atual)", expand=True
        )
        tabela_atual.add_column("Métrica", style="bold white")
        tabela_atual.add_column("Valor Registrado", justify="right")
        tabela_atual.add_row(
            "📅 Dia da Simulação",
            f"[bold yellow]Dia {estacao.dia:02d}[/bold yellow]",
        )
        tabela_atual.add_row(
            "🕒 Horário Local", f"[bold green]{estacao.hora:02d}:00[/bold green]"
        )
        tabela_atual.add_row(
            "🌤️ Condição Momentânea", estacao.condicao_hora_atual
        )
        tabela_atual.add_row(
            "🌡️ Temperatura Atual",
            f"[bold bright_white]{estacao.temp_atual:5.1f} °C[/bold bright_white]",
        )
        tabela_atual.add_row(
            "🔺 MÁXIMA Parcial",
            f"[bold red]{estacao.max_temp:5.1f} °C[/bold red]",
        )
        tabela_atual.add_row(
            "🔻 MÍNIMA Parcial",
            f"[bold blue]{estacao.min_temp:5.1f} °C[/bold blue]",
        )

        layout_esquerda = Layout()
        layout_esquerda.split_column(
            Layout(Panel(tabela_atual, border_style="green"), ratio=3),
            Layout(
                Panel(
                    estacao.obter_diagrama_animado(),
                    title="🎨 Diagrama de Clima Vivo",
                    border_style="yellow",
                ),
                ratio=2,
            ),
        )

        tabela_historico = Table(
            title="📋 Histórico Recente (Até 5 Dias)", expand=True
        )
        tabela_historico.add_column("Identificação", style="bold white")
        tabela_historico.add_column("Condição Geral", justify="center")
        tabela_historico.add_column("Mínima", justify="right")
        tabela_historico.add_column("Máxima", justify="right")

        if estacao.historico:
            for item in estacao.historico:
                tabela_historico.add_row(
                    f"Dia {item.dia:02d}",
                    item.condicao,
                    f"[blue]{item.min_temp:.1f} °C[/blue]",
                    f"[red]{item.max_temp:.1f} °C[/red]",
                )
        else:
            tabela_historico.add_row(
                "[italic grey50]----[/italic grey50]",
                "[italic grey50]Aguardando conclusão do 1º dia...[/italic grey50]",
                "[italic grey50]--.- °C[/italic grey50]",
                "[italic grey50]--.- °C[/italic grey50]",
            )

        layout["corpo"].split_row(
            layout_esquerda,
            Layout(Panel(tabela_historico, border_style="magenta")),
        )

        layout["rodape"].update(
            Panel(
                Text(
                    "Pressione Ctrl + C a qualquer momento para encerrar o programa com segurança.",
                    justify="center",
                    style="dim white",
                ),
                border_style="grey50",
            )
        )

        return layout


def executar_simulacao() -> None:
    """Executa o loop principal da simulação garantindo o tratamento de exceções."""
    console = Console()
    estacao = EstacaoMeteorologica()
    interface = InterfaceEstacao()

    try:
        with Live(
            interface.renderizar_layout(estacao),
            console=console,
            refresh_per_second=2,
            screen=True,
        ) as live:
            while True:
                estacao.processar_hora()
                live.update(interface.renderizar_layout(estacao))
                time.sleep(2)

    except KeyboardInterrupt:
        console.print(
            "\n[bold yellow]Simulação encerrada com sucesso pelo operador. Até logo![/bold yellow]"
        )
    except Exception as erro:
        console.print(
            f"\n[bold red]Ocorreu um erro inesperado na execução: {erro}[/bold red]"
        )


if __name__ == "__main__":
    executar_simulacao()