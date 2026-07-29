import random
import sys
import time
import urllib.request
from urllib.error import HTTPError, URLError

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text


class PudimMetrics:
    """Encapsula os dados e métricas obtidas na requisição HTTP."""

    def __init__(self, status_code: int, response_time: float, size_bytes: int):
        """Inicializa as métricas privadas da requisição."""
        self._status_code = status_code
        self._response_time = response_time
        self._size_bytes = size_bytes

    @property
    def status_code(self) -> int:
        """Retorna o código de status HTTP."""
        return self._status_code

    @property
    def response_time_ms(self) -> float:
        """Calcula e retorna o tempo de resposta em milissegundos."""
        return self._response_time * 1000

    @property
    def size_kb(self) -> float:
        """Calcula e retorna o tamanho do payload em Kilobytes."""
        return self._size_bytes / 1024


class PudimChecker:
    """Gerencia as conexões HTTP com o servidor do Pudim."""

    def __init__(self, url: str = "http://www.pudim.com.br"):
        """Define a URL do site e o User-Agent da requisição."""
        self._url = url
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    def check_status(self) -> tuple[bool, PudimMetrics | None, str]:
        """Efetua a requisição ao servidor e calcula o tempo e tamanho recebido."""
        start_time = time.time()
        try:
            request = urllib.request.Request(self._url, headers=self._headers)
            with urllib.request.urlopen(request, timeout=8) as response:
                content = response.read()
                end_time = time.time()
                elapsed = end_time - start_time
                metrics = PudimMetrics(response.status, elapsed, len(content))
                return True, metrics, "Sucesso"
        except HTTPError as err:
            return False, None, f"Erro HTTP {err.code}: {err.reason}"
        except URLError as err:
            return False, None, f"Servidor inacessível: {err.reason}"
        except Exception as err:
            return False, None, f"Falha inesperada: {str(err)}"


class PartyEngine:
    """Gerencia animações visuais, confetes em tempo real e arte ASCII."""

    def __init__(self, console: Console):
        """Inicializa o motor de festa com o console do Rich."""
        self._console = console
        self._confetti_symbols = ["✨", "🎉", "🍰", "⭐", "🌟", "🎈", "🎊", "🍮", "🍬", "🍭"]
        self._colors = ["bright_yellow", "bright_red", "bright_green", "bright_magenta", "bright_cyan", "gold1"]

    @staticmethod
    def get_ascii_pudim() -> str:
        """Retorna a representação em ASCII Art gigante do pudim."""
        return """
                 (   .   🍮   .   )
                )                 (
               (   .   ✨  ✨  .   )
             .________________________.
            /                          \\
           /     (~~~~ CALDA ~~~~)      \\
          /   /                     \\    \\
         /   /   . ~ ~ ~ ~ ~ ~ ~ .   \\    \\
        /   /   /                 \\   \\    \\
       /___/___/___________________\\___\\____\\
      |    |                       |    |    |
      |    |   P U D I M   P R O   |    |    |
      |____|_______________________|____|____|
     (________________________________________)
      \\______________________________________/
         \\__________________________________/
        """

    def _generate_confetti_frame(self, height: int = 10, width: int = 55) -> Text:
        """Gera um frame individual de confetes caindo aleatoriamente."""
        frame = Text()
        for row in range(height):
            for col in range(width):
                if random.random() < 0.12:
                    symbol = random.choice(self._confetti_symbols)
                    color = random.choice(self._colors)
                    frame.append(symbol, style=color)
                else:
                    frame.append(" ")
            frame.append("\n")
        return frame

    def run_party_animation(self, duration_seconds: int = 6):
        """Executa a animação interativa de confetes caindo no terminal."""
        start_time = time.time()
        title_text = Text(" 🎉 FESTA NO TERMINAL! O PUDIM ESTÁ ONLINE! 🎉 ", style="bold yellow blink")
        
        with Live(console=self._console, refresh_per_second=12, transient=True) as live:
            while time.time() - start_time < duration_seconds:
                confetti = self._generate_confetti_frame()
                panel = Panel(
                    Align.center(confetti),
                    title=title_text,
                    subtitle="[bold green]Status: 100% Doce e Funcional[/bold green]",
                    border_style="gold1"
                )
                live.update(panel)
                time.sleep(0.08)


class PudimApp:
    """Coordenador do fluxo principal da aplicação e interface interativa."""

    def __init__(self):
        """Inicializa os módulos e a instância principal do console."""
        self._console = Console()
        self._checker = PudimChecker()
        self._party = PartyEngine(self._console)

    def _simulate_cooking(self):
        """Exibe o processo temático de cozinhamento da requisição."""
        self._console.clear()
        self._console.print("\n[bold orange3]🍮 Preparando o forno e iniciando o cozinhamento da requisição...[/bold orange3]\n")
        
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            console=self._console,
            transient=True
        ) as progress:
            task = progress.add_task("[bold yellow]Derretendo o açúcar para a calda...", total=100)
            time.sleep(0.5)
            progress.update(task, completed=35, description="[bold gold1]Aquecendo o leite condensado...")
            time.sleep(0.5)
            progress.update(task, completed=70, description="[bold orange1]Conectando ao servidor do Pudim...")
            time.sleep(0.6)
            progress.update(task, completed=100, description="[bold green]Pudim assado com sucesso!")
            time.sleep(0.3)

    def _display_dashboard(self, metrics: PudimMetrics):
        """Exibe o banner ASCII gigante e a tabela detalhada de métricas."""
        pudim_art = PartyEngine.get_ascii_pudim()
        
        table = Table(title="[bold yellow]📊 Métricas Oficiais do Pudim[/bold yellow]", border_style="gold1", expand=True)
        table.add_column("Métrica", style="bold cyan", justify="left")
        table.add_column("Valor Observado", style="bold white", justify="right")
        table.add_column("Avaliação Gastronômica", style="italic green", justify="left")

        table.add_row("Status HTTP", f"{metrics.status_code} OK", "Perfeição Total")
        table.add_row("Tempo de Resposta", f"{metrics.response_time_ms:.2f} ms", "Mais rápido que um raio")
        table.add_row("Tamanho da Massa", f"{metrics.size_kb:.2f} KB", "Leve e saboroso")

        panel_content = Align.center(f"[bold gold1]{pudim_art}[/bold gold1]\n")
        
        self._console.clear()
        self._console.print(Panel(panel_content, title="[bold orange3]🍮 PUDIM DASHBOARD SYSTEM PRO 🍮[/bold orange3]", border_style="orange3"))
        self._console.print(table)
        self._console.print("\n")

    def _prompt_user(self, text: str) -> str:
        """Captura entradas do usuário tratando cancelamentos abruptos."""
        try:
            return self._console.input(f"{text} ")
        except (KeyboardInterrupt, EOFError):
            return "0"

    def _show_menu(self) -> bool:
        """Renderiza o menu interativo e processa as escolhas do usuário."""
        self._console.print("\n" + "─" * 55)
        self._console.print("[bold cyan]🎮 MENU INTERATIVO DO PUDIM[/bold cyan]")
        self._console.print("[1] 🔄 Rechecar disponibilidade do site")
        self._console.print("[2] 🎉 Continuar a festa de confetes (Mais 8s)")
        self._console.print("[0] 🚪 Sair do programa")

        opcao = self._prompt_user("\n[bold yellow]Escolha uma opção:[bold yellow]")

        if opcao == "1":
            return True
        elif opcao == "2":
            self._party.run_party_animation(duration_seconds=8)
            return self._show_menu()
        elif opcao == "0":
            self._console.print("\n[bold green]🍮 Obrigado por usar o Pudim Monitor Pro! Até a próxima receita![/bold green]\n")
            return False
        else:
            self._console.print("[bold red]Opção inválida! Tente novamente.[/bold red]")
            time.sleep(1)
            return self._show_menu()

    def run(self):
        """Executa o ciclo principal da aplicação com tolerância a falhas."""
        try:
            while True:
                self._simulate_cooking()
                is_online, metrics, message = self._checker.check_status()

                if is_online and metrics:
                    self._display_dashboard(metrics)
                    self._console.print("[bold green]✅ O site Pudim está 100% ONLINE e pronto para degustação![/bold green]\n")
                    
                    self._prompt_user("[bold yellow]Pressione ENTER para estourar a FESTA DE CONFETES![/bold yellow]")
                    self._party.run_party_animation(duration_seconds=6)
                else:
                    self._console.clear()
                    self._console.print(Panel(
                        f"[bold red]❌ Ops! O Pudim desandou![/bold red]\n\n[white]{message}[/white]",
                        title="[bold red]Erro de Conexão[/bold red]",
                        border_style="red"
                    ))

                if not self._show_menu():
                    break

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]👋 Encerrando o Monitor de Pudim via atalho de teclado. Até mais![/bold yellow]\n")
        except Exception as err:
            self._console.print(f"\n[bold red]❌ Ocorreu uma exceção não esperada: {err}[/bold red]\n")


if __name__ == "__main__":
    app = PudimApp()
    app.run()