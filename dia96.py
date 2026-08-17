import os
import random
import select
import sys
import termios
import tty
from datetime import datetime
from time import sleep, time

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Particle:
    """Representa uma partícula individual de fogo de artifício em expansão."""

    def __init__(self, x: int, y: int, char: str, color: str) -> None:
        """Inicializa posição, velocidade e tempo de vida da partícula."""
        self.x, self.y, self.char, self.color = float(x), float(y), char, color
        self.vx, self.vy = random.uniform(-1.8, 1.8), random.uniform(-1.0, 1.0)
        self.life: int = random.randint(8, 15)

    def atualizar(self) -> None:
        """Aplica vetor de movimento e decrementa vida."""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1


class GerenciadorFogos:
    """Gerencia a criação e renderização da animação ASCII de fogos de artifício."""

    def __init__(self, largura: int = 50, altura: int = 10) -> None:
        """Inicializa dimensões e paletas visuais."""
        self.w, self.h, self.particulas = largura, altura, []
        self.simbolos = ["*", ".", "+", "o", "O", "x", "#", "@"]
        self.cores = [
            "bold red",
            "bold yellow",
            "bold green",
            "bold cyan",
            "bold magenta",
            "bold white",
            "bold gold1",
        ]

    def renderizar_frame(self) -> Text:
        """Gera a grade textual com as partículas ativas."""
        if random.random() < 0.4 or len(self.particulas) < 10:
            cx, cy, cor = (
                random.randint(10, self.w - 10),
                random.randint(3, self.h - 3),
                random.choice(self.cores),
            )
            self.particulas.extend(
                Particle(
                    cx, cy, random.choice(self.simbolos), cor
                )
                for _ in range(25)
            )

        grid = [
            [(" ", "white") for _ in range(self.w)] for _ in range(self.h)
        ]
        novas = []
        for p in self.particulas:
            p.atualizar()
            ix, iy = int(p.x), int(p.y)
            if 0 <= ix < self.w and 0 <= iy < self.h and p.life > 0:
                grid[iy][ix] = (p.char, p.color)
                novas.append(p)
        self.particulas = novas

        res = Text()
        for linha in grid:
            for char, color in linha:
                res.append(char, style=color)
            res.append("\n")
        return res


class ContadorAnoNovo:
    """Gerencia o cálculo de tempo restante e simulações para o Ano Novo."""

    def __init__(self) -> None:
        """Inicializa estado de simulação."""
        self._modo_simulacao: bool = False

    @property
    def modo_simulacao(self) -> bool:
        """Retorna estado da simulação."""
        return self._modo_simulacao

    def alternar_simulacao(self) -> None:
        """Inverte o estado do modo de simulação."""
        self._modo_simulacao = not self._modo_simulacao

    def obter_tempo_restante(self) -> tuple[int, int, int, int, bool]:
        """Calcula a diferença exata até a virada do ano."""
        if self._modo_simulacao:
            return 0, 0, 0, 0, True
        agora = datetime.now()
        diff = datetime(agora.year + 1, 1, 1) - agora
        if diff.total_seconds() <= 0:
            return 0, 0, 0, 0, True
        m, s = divmod(diff.seconds, 60)
        h, m = divmod(m, 60)
        return diff.days, h, m, s, False


class InterfaceContador:
    """Gerencia a renderização visual do contador e áudio do terminal."""

    def __init__(self, contador: ContadorAnoNovo) -> None:
        """Inicializa interface e controle de tempo de áudio."""
        self._c, self._console = contador, Console()
        self._fogos, self._ultimo_beep = GerenciadorFogos(), 0.0

    def _tocar_beep(self) -> None:
        """Emite sinal sonoro (\a) no terminal respeitando intervalo mínimo."""
        if time() - self._ultimo_beep >= 1.0:
            sys.stdout.write("\a")
            sys.stdout.flush()
            self._ultimo_beep = time()

    def gerar_painel(self) -> Panel:
        """Constrói a estrutura Rich da HUD visual com Emojis Nativos."""
        agora = datetime.now()
        dias, h, m, s, chegou = self._c.obter_tempo_restante()

        if chegou:
            self._tocar_beep()
            conteudo = Table.grid(expand=True)
            conteudo.add_row(Align.center(self._fogos.renderizar_frame()))
            conteudo.add_row(
                Align.center(
                    Text(
                        "\n✨ 🎆 FELIZ ANO NOVO! 🎆 ✨\n",
                        style="bold yellow",
                        justify="center",
                    )
                )
            )
            titulo, cor = "🎉 CELEBRAÇÃO EM ANDAMENTO 🎉", "bold gold1"
        else:
            if dias == 0 and h == 0 and m == 0 and s <= 10:
                self._tocar_beep()

            tab = Table(show_header=True, header_style="bold cyan", expand=True)
            for col in ["Dias", "Horas", "Minutos", "Segundos"]:
                tab.add_column(col, justify="center")
            tab.add_row(
                f"[bold green]{dias}[/]",
                f"[bold green]{h:02d}[/]",
                f"[bold green]{m:02d}[/]",
                f"[bold green]{s:02d}[/]",
            )

            status = (
                "[bold magenta][SIMULAÇÃO ATIVA][/bold magenta]\n"
                if self._c.modo_simulacao
                else ""
            )
            info = Text.from_markup(
                f"{status}Horário Atual: {agora.strftime('%H:%M:%S - %d/%m/%Y')}",
                justify="center",
            )
            conteudo = Align.center(
                Panel(tab, border_style="dim white", title=info)
            )
            titulo, cor = (
                "⏳ CONTAGEM REGRESSIVA ANO NOVO ⏳",
                "bright_blue",
            )

        instrucoes = Text.from_markup(
            "\n[dim]Pressione [bold yellow]S[/] para alternar simulação | [bold red]Q[/] para sair[/dim]",
            justify="center",
        )
        layout = Table.grid(expand=True)
        layout.add_row(conteudo)
        layout.add_row(instrucoes)

        return Panel(
            layout,
            title=f"[bold]{titulo}[/bold]",
            border_style=cor,
            padding=(1, 2),
        )

    def executar(self) -> None:
        """Executa o loop visual em tempo real com captura precisa de teclado."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)  # Ativa leitura instantânea de teclas sem buffer
            with Live(
                self.gerar_painel(),
                console=self._console,
                refresh_per_second=12,
                screen=True,
            ) as live:
                while True:
                    self._verificar_teclado()
                    live.update(self.gerar_painel())
                    sleep(0.08)
        except KeyboardInterrupt:
            self._encerrar()
        except Exception as e:
            self._console.print(f"[bold red]❌ Erro:[/] {e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _verificar_teclado(self) -> None:
        """Captura comandos de teclado de forma assíncrona instantânea."""
        try:
            if select.select([sys.stdin], [], [], 0)[0]:
                tecla = sys.stdin.read(1).lower()
                if tecla == "s":
                    self._c.alternar_simulacao()
                elif tecla == "q":
                    self._encerrar()
        except Exception:
            pass

    def _encerrar(self) -> None:
        """Encerra a aplicação elegantemente."""
        self._console.print(
            "\n[bold cyan]🚀 Aplicação encerrada com sucesso![/]\n"
        )
        sys.exit(0)


if __name__ == "__main__":
    try:
        InterfaceContador(ContadorAnoNovo()).executar()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as erro:
        print(f"Erro fatal: {erro}")
        sys.exit(1)