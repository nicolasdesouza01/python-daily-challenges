"""
CLI Loading Showcase - Gerador e Visualizador de Barras de Carregamento.

Módulo que demonstra a biblioteca Rich e POO para criar um showcase
interativo de barras de progresso e carregamento no terminal.
"""

import time
import sys
from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align


class ProgressBarPreset:
    """Representa um modelo/estilo predefinido de barra de progresso."""

    def __init__(self, name: str, fill_char: str, empty_char: str, description: str):
        """Inicializa o preset com nome, caracteres e descrição."""
        self._name = name
        self._fill_char = fill_char
        self._empty_char = empty_char
        self._description = description

    @property
    def name(self) -> str:
        """Retorna o nome do preset."""
        return self._name

    @property
    def fill_char(self) -> str:
        """Retorna o caractere de preenchimento."""
        return self._fill_char

    @property
    def empty_char(self) -> str:
        """Retorna o caractere de fundo/vazio."""
        return self._empty_char

    @property
    def description(self) -> str:
        """Retorna a descrição do preset."""
        return self._description


class ProgressBarEngine:
    """Motor responsável por renderizar e animar a barra de progresso."""

    def __init__(self, console: Console):
        """Inicializa o motor associado a um console Rich."""
        self._console = console

    def render_bar(self, current: int, total: int, fill: str, empty: str, width: int = 30, style: str = "bold cyan") -> Text:
        """Gera a barra de progresso formatada com porcentagem."""
        percent = min(1.0, max(0.0, current / total)) if total > 0 else 1.0
        filled_len = int(width * percent)
        
        bar = Text("[", style="bold white")
        bar.append(fill * filled_len, style=style)
        bar.append(empty * (width - filled_len), style="dim white")
        bar.append("] ", style="bold white")
        bar.append(f"{int(percent * 100):>3}%", style="bold yellow")
        return bar

    def animate(self, fill: str, empty: str, title: str = "Carregando", steps: int = 100, step_size: int = 2, delay: float = 0.03, width: int = 30, style: str = "bold green") -> None:
        """Executa a animação fluida da barra no terminal."""
        current = 0
        with Live(console=self._console, refresh_per_second=30) as live:
            while current <= steps:
                content = Text(f" 🚀 {title}\n\n", style="bold white")
                content.append_text(self.render_bar(current, steps, fill, empty, width, style))
                live.update(Panel(Align.center(content), border_style="magenta", padding=(1, 2)))
                time.sleep(delay)
                current += step_size
            time.sleep(0.2)


class ShowcaseApp:
    """Gerencia o fluxo do aplicativo CLI e a interface do usuário."""

    def __init__(self):
        """Inicializa a aplicação com presets padrão."""
        self._console = Console()
        self._engine = ProgressBarEngine(self._console)
        self._presets: Dict[str, ProgressBarPreset] = {
            "1": ProgressBarPreset("Classic Blocks", "█", "░", "Estilo clássico com blocos"),
            "2": ProgressBarPreset("Smooth Gradient", "█", " ", "Aparência moderna sem fundo"),
            "3": ProgressBarPreset("Retro ASCII", "=", "-", "Estilo retrô de terminal"),
            "4": ProgressBarPreset("Hearts Theme", "💖", "🤍", "Emojis de corações"),
            "5": ProgressBarPreset("Stars Theme", "⭐", "▫️", "Tema estelar"),
            "6": ProgressBarPreset("Fire & Ice", "🔥", "❄️", "Tema elemental")
        }

    def _display_header(self) -> None:
        """Exibe o cabeçalho principal estilizado."""
        self._console.clear()
        content = Text("✨ CLI LOADING SHOWCASE ✨\n", style="bold cyan")
        content.append("Explore e crie barras de carregamento personalizadas", style="dim italic white")
        self._console.print(Panel(Align.center(content), border_style="cyan", padding=(1, 2)))

    def run_gallery(self) -> None:
        """Exibe a demonstração sequencial de todos os presets."""
        self._display_header()
        self._console.print("\n🎞️ [bold yellow]Iniciando Galeria de Demonstração...[/bold yellow]\n")
        time.sleep(0.8)

        colors = ["bold green", "bold cyan", "bold yellow", "bold magenta", "bold blue", "bold red"]
        for idx, (k, p) in enumerate(self._presets.items()):
            self._engine.animate(p.fill_char, p.empty_char, f"Preset {k}: {p.name} ({p.description})", steps=100, step_size=4, delay=0.02, width=25, style=colors[idx % len(colors)])
            time.sleep(0.2)

        self._console.print("\n✅ [bold green]Demonstração concluída![/bold green]")
        Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu")

    def run_custom_builder(self) -> None:
        """Permite a criação de uma barra com caracteres customizados."""
        self._display_header()
        self._console.print("\n⚙️ [bold yellow]Crie sua Barra Personalizada[/bold yellow]\n")

        try:
            fill = Prompt.ask("Caractere de [bold green]preenchimento[/bold green]", default="█")
            empty = Prompt.ask("Caractere de [bold red]fundo/vazio[/bold red]", default="░")
            width = IntPrompt.ask("Largura da barra (10 a 50)", default=30)
            width = width if 10 <= width <= 50 else 30

            speed = Prompt.ask("Velocidade ([1] Rápido | [2] Normal | [3] Lento)", choices=["1", "2", "3"], default="2")
            delay = {"1": 0.01, "2": 0.03, "3": 0.08}.get(speed, 0.03)

            self._console.print("\n🚀 [bold green]Gerando barra customizada...[/bold green]\n")
            time.sleep(0.4)
            self._engine.animate(fill, empty, "Sua Barra Customizada em Ação", steps=100, step_size=2, delay=delay, width=width)
            self._console.print("\n🎉 [bold green]Barra renderizada com sucesso![/bold green]")
        except Exception:
            self._console.print("\n❌ Erro ao processar valores.", style="bold red")

        Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu")

    def main_loop(self) -> None:
        """Loop principal do menu interativo."""
        while True:
            try:
                self._display_header()
                self._console.print()

                table = Table(title="🌟 MENU PRINCIPAL", border_style="bright_blue", header_style="bold magenta")
                table.add_column("Opção", justify="center", style="cyan")
                table.add_column("Descrição", style="white")
                table.add_row("1", "Ver Galeria de Estilos (Showcase Automático)")
                table.add_row("2", "Criar Barra Personalizada (Custom Builder)")
                table.add_row("0", "Sair do Programa")
                self._console.print(table)

                choice = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "0"], default="1")
                if choice == "1":
                    self.run_gallery()
                elif choice == "2":
                    self.run_custom_builder()
                elif choice == "0":
                    self._console.print("\n👋 [bold cyan]Até mais![/bold cyan]\n")
                    break
            except KeyboardInterrupt:
                self._console.print("\n\n⚠️ [bold yellow]Programa encerrado pelo usuário (Ctrl+C).[/bold yellow]\n")
                sys.exit(0)
            except Exception as e:
                self._console.print(f"\n❌ [bold red]Ops! Algo deu errado:[/bold red] {e}")
                Prompt.ask("\nPressione [bold white]Enter[/bold white] para tentar novamente")


if __name__ == "__main__":
    ShowcaseApp().main_loop()