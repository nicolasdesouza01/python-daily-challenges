import random
import time
from typing import Dict, List, Optional, Set, Tuple
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Position:
    """
    Representa e manipula coordenadas bidimensionais X e Y na grade.
    """

    _DIRECTIONS: Tuple[Tuple[int, int], ...] = (
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    )

    def __init__(self, x: int, y: int) -> None:
        """Inicializa as coordenadas cartesianas."""
        self._x: int = x
        self._y: int = y

    @property
    def x(self) -> int:
        """Retorna o valor da coordenada X."""
        return self._x

    @property
    def y(self) -> int:
        """Retorna o valor da coordenada Y."""
        return self._y

    def get_adjacent_positions(self, max_w: int, max_h: int) -> List["Position"]:
        """Calcula e retorna as posições vizinhas válidas dentro do mapa."""
        adjacent: List[Position] = []
        for dx, dy in self._DIRECTIONS:
            nx, ny = self._x + dx, self._y + dy
            if 0 <= nx < max_w and 0 <= ny < max_h:
                adjacent.append(Position(nx, ny))
        return adjacent

    def __eq__(self, other: object) -> bool:
        """Compara igualdade entre duas coordenadas."""
        return isinstance(other, Position) and self._x == other._x and self._y == other._y

    def __hash__(self) -> int:
        """Gera o código hash da coordenada para busca O(1)."""
        return hash((self._x, self._y))


class Organism:
    """
    Classe base para todas as entidades vivas do ecossistema.
    """

    def __init__(self, position: Position, energy: float, max_age: int, symbol: str) -> None:
        """Inicializa o estado fundamental do organismo."""
        self._position: Position = position
        self._energy: float = energy
        self._age: int = 0
        self._max_age: int = max_age
        self._symbol: str = symbol
        self._is_alive: bool = True

    @property
    def position(self) -> Position:
        """Retorna a posição atual."""
        return self._position

    @position.setter
    def position(self, new_pos: Position) -> None:
        """Atualiza a posição do organismo."""
        self._position = new_pos

    @property
    def energy(self) -> float:
        """Retorna o nível de energia acumulada."""
        return self._energy

    @property
    def symbol(self) -> str:
        """Retorna o caractere/emoji de representação visual."""
        return self._symbol

    @property
    def is_alive(self) -> bool:
        """Verifica se o organismo permanece vivo."""
        return self._is_alive and self._energy > 0 and self._age < self._max_age

    def consume_energy(self, amount: float) -> None:
        """Reduz a energia e atualiza o estado vital se zerar."""
        self._energy -= amount
        if self._energy <= 0:
            self._is_alive = False

    def gain_energy(self, amount: float) -> None:
        """Incrementa a energia vital do organismo."""
        self._energy += amount

    def increment_age(self) -> None:
        """Avança a idade em 1 ciclo e valida a longevidade máxima."""
        self._age += 1
        if self._age >= self._max_age:
            self._is_alive = False


class Plant(Organism):
    """
    Representa a vegetação (produtor de energia inanimado).
    """

    def __init__(self, position: Position) -> None:
        """Inicializa uma planta na posição especificada."""
        super().__init__(position, energy=15.0, max_age=100, symbol="🌱")


class Prey(Organism):
    """
    Representa a presa/herbívoro (ex: Coelho).
    """

    def __init__(self, position: Position, energy: float = 25.0) -> None:
        """Inicializa uma presa com energia configurável."""
        super().__init__(position, energy, max_age=35, symbol="🐰")

    def can_reproduce(self) -> bool:
        """Valida se possui o limiar de energia para reprodução."""
        return self._energy >= 45.0

    def reproduce(self, target_position: Position) -> "Prey":
        """Gera um descendente dividindo os recursos de energia."""
        self.consume_energy(20.0)
        return Prey(target_position, energy=18.0)


class Predator(Organism):
    """
    Representa o predador/carnívoro (ex: Lobo).
    """

    def __init__(self, position: Position, energy: float = 40.0) -> None:
        """Inicializa um predador com energia configurável."""
        super().__init__(position, energy, max_age=45, symbol="🐺")

    def can_reproduce(self) -> bool:
        """Valida se possui o limiar de energia para reprodução."""
        return self._energy >= 70.0

    def reproduce(self, target_position: Position) -> "Predator":
        """Gera um descendente dividindo os recursos de energia."""
        self.consume_energy(30.0)
        return Predator(target_position, energy=30.0)


class EcosystemMetrics:
    """
    Agrega contadores e histórico de desempenho da simulação.
    """

    def __init__(self) -> None:
        """Inicializa os contadores estáticos da aplicação."""
        self._generation: int = 0
        self._peak_prey: int = 0
        self._peak_predator: int = 0
        self._last_event: str = "Ecossistema inicializado."

    @property
    def generation(self) -> int:
        """Retorna o ciclo temporal atual."""
        return self._generation

    @property
    def last_event(self) -> str:
        """Retorna o registro do último acontecimento relevante."""
        return self._last_event

    def register_cycle(self, prey_count: int, predator_count: int) -> None:
        """Atualiza a contagem de tempo e os picos demográficos máximos."""
        self._generation += 1
        self._peak_prey = max(self._peak_prey, prey_count)
        self._peak_predator = max(self._peak_predator, predator_count)

    def log_event(self, message: str) -> None:
        """Atualiza a mensagem de log exibida no rodapé."""
        self._last_event = message

    def get_summary_table(self, plants: int, preys: int, predators: int) -> Table:
        """Gera a tabela formatada do painel com bibliotecas Rich."""
        table = Table(title="📊 Painel Demográfico", show_header=True, header_style="bold magenta")
        table.add_column("Espécie", style="cyan")
        table.add_column("Atual", style="yellow", justify="center")
        table.add_column("Pico", style="green", justify="center")
        table.add_row("🌱 Plantas", str(plants), "-")
        table.add_row("🐰 Presas", str(preys), str(self._peak_prey))
        table.add_row("🐺 Predadores", str(predators), str(self._peak_predator))
        return table


class EcosystemGrid:
    """
    Gerencia a alocação e renderização otimizada dos organismos no espaço.
    """

    def __init__(self, width: int = 28, height: int = 30) -> None:
        """Inicializa as dimensões da grade e as coleções de seres."""
        self._width: int = width
        self._height: int = height
        self._plants: Dict[Position, Plant] = {}
        self._preys: List[Prey] = []
        self._predators: List[Predator] = []

    @property
    def width(self) -> int:
        """Retorna a largura máxima do mapa."""
        return self._width

    @property
    def height(self) -> int:
        """Retorna a altura máxima do mapa."""
        return self._height

    @property
    def plants(self) -> Dict[Position, Plant]:
        """Retorna o mapa de plantas ativas."""
        return self._plants

    @property
    def preys(self) -> List[Prey]:
        """Retorna a lista de presas ativas."""
        return self._preys

    @property
    def predators(self) -> List[Predator]:
        """Retorna a lista de predadores ativos."""
        return self._predators

    def populate_initial_state(self, plants: int, preys: int, predators: int) -> None:
        """Semeia a população inicial de forma aleatória sem sobreposição."""
        positions = [Position(x, y) for x in range(self._width) for y in range(self._height)]
        random.shuffle(positions)
        for _ in range(min(plants, len(positions))):
            p = positions.pop()
            self._plants[p] = Plant(p)
        for _ in range(min(preys, len(positions))):
            self._preys.append(Prey(positions.pop()))
        for _ in range(min(predators, len(positions))):
            self._predators.append(Predator(positions.pop()))

    def get_empty_adjacent_position(self, position: Position) -> Optional[Position]:
        """Encontra uma célula vizinha sem presas ou predadores presentes."""
        occupied: Set[Position] = {p.position for p in self._preys} | {p.position for p in self._predators}
        free = [p for p in position.get_adjacent_positions(self._width, self._height) if p not in occupied]
        return random.choice(free) if free else None

    def remove_dead_organisms(self) -> None:
        """Filtra e descarta instâncias mortas das coleções da simulação."""
        self._preys = [p for p in self._preys if p.is_alive]
        self._predators = [p for p in self._predators if p.is_alive]

    def render_ascii_map(self) -> Text:
        """Mapeia a grade em O(1) por célula e gera a representação textual."""
        pred_map: Dict[Position, Predator] = {p.position: p for p in self._predators}
        prey_map: Dict[Position, Prey] = {p.position: p for p in self._preys}
        lines: List[str] = []

        for y in range(self._height):
            row: List[str] = []
            for x in range(self._width):
                pos = Position(x, y)
                if pos in pred_map:
                    row.append(pred_map[pos].symbol)
                elif pos in prey_map:
                    row.append(prey_map[pos].symbol)
                elif pos in self._plants:
                    row.append(self._plants[pos].symbol)
                else:
                    row.append(" 🟫 ")
            lines.append("".join(row))
        return Text("\n".join(lines))


class EcosystemEngine:
    """
    Executa a lógica de ciclos, interações de caça, alimentação e velhice.
    """

    def __init__(self, grid: EcosystemGrid, metrics: EcosystemMetrics) -> None:
        """Inicializa o motor acoplado à grade e às métricas."""
        self._grid: EcosystemGrid = grid
        self._metrics: EcosystemMetrics = metrics

    def step(self) -> None:
        """Executa um ciclo completo de atualização biológica no mapa."""
        self._regenerate_plants()
        self._update_prey_phase()
        self._update_predator_phase()
        self._grid.remove_dead_organisms()
        self._metrics.register_cycle(len(self._grid.preys), len(self._grid.predators))

    def _regenerate_plants(self) -> None:
        """Semeia novas plantas aleatoriamente no mapa proporcionalmente ao tamanho."""
        for _ in range(2):
            if random.random() < 0.5:
                pos = Position(random.randint(0, self._grid.width - 1), random.randint(0, self._grid.height - 1))
                if pos not in self._grid.plants:
                    self._grid.plants[pos] = Plant(pos)

    def _update_prey_phase(self) -> None:
        """Atualiza a busca por plantas, deslocamento e nascimento de presas."""
        new_preys: List[Prey] = []
        for prey in list(self._grid.preys):
            if not prey.is_alive:
                continue
            prey.increment_age()
            prey.consume_energy(1.2)
            adj = prey.position.get_adjacent_positions(self._grid.width, self._grid.height)
            plant_pos = next((p for p in adj if p in self._grid.plants), None)

            if plant_pos:
                prey.position = plant_pos
                prey.gain_energy(self._grid.plants[plant_pos].energy)
                del self._grid.plants[plant_pos]
            else:
                free_pos = self._grid.get_empty_adjacent_position(prey.position)
                if free_pos:
                    prey.position = free_pos

            if prey.is_alive and prey.can_reproduce():
                spawn = self._grid.get_empty_adjacent_position(prey.position)
                if spawn:
                    new_preys.append(prey.reproduce(spawn))
                    self._metrics.log_event(f"🐰 Novo coelho nasceu em ({spawn.x}, {spawn.y})!")

        self._grid.preys.extend(new_preys)

    def _update_predator_phase(self) -> None:
        """Atualiza a caça por presas, deslocamento e nascimento de predadores."""
        new_predators: List[Predator] = []
        for pred in list(self._grid.predators):
            if not pred.is_alive:
                continue
            pred.increment_age()
            pred.consume_energy(2.0)
            adj = pred.position.get_adjacent_positions(self._grid.width, self._grid.height)
            target_prey = next((p for p in self._grid.preys if p.position in adj and p.is_alive), None)

            if target_prey:
                pred.position = target_prey.position
                pred.gain_energy(25.0)
                target_prey.consume_energy(999.0)
                self._metrics.log_event(f"🐺 Lobo caçou em ({pred.position.x}, {pred.position.y})!")
            else:
                free_pos = self._grid.get_empty_adjacent_position(pred.position)
                if free_pos:
                    pred.position = free_pos

            if pred.is_alive and pred.can_reproduce():
                spawn = self._grid.get_empty_adjacent_position(pred.position)
                if spawn:
                    new_predators.append(pred.reproduce(spawn))

        self._grid.predators.extend(new_predators)


class EcosystemRenderer:
    """
    Compositor e construtor dos painéis visuais usando a biblioteca Rich.
    """

    def __init__(self, grid: EcosystemGrid, metrics: EcosystemMetrics) -> None:
        """Inicializa o renderizador visual e o layout base."""
        self._grid: EcosystemGrid = grid
        self._metrics: EcosystemMetrics = metrics
        self._layout: Layout = Layout()
        self._setup_layout()

    def _setup_layout(self) -> None:
        """Configura a geometria e seções da interface."""
        self._layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )
        self._layout["body"].split_row(
            Layout(name="map", ratio=2),
            Layout(name="sidebar", ratio=1),
        )

    def render(self) -> Layout:
        """Atualiza o conteúdo gráfico de todas as regiões do painel."""
        title = Text("🌍 SIMULADOR DE ECOSSISTEMA E VIDA ARTIFICIAL — AUTÔMATO CELULAR 🚀", style="bold white on blue", justify="center")
        self._layout["header"].update(Panel(title))
        self._layout["map"].update(Panel(self._grid.render_ascii_map(), title=f"🗺️ Campo de Simulação (Ciclo {self._metrics.generation})", border_style="green"))
        self._layout["sidebar"].update(Panel(self._metrics.get_summary_table(len(self._grid.plants), len(self._grid.preys), len(self._grid.predators)), title="⚙️ Estatísticas", border_style="yellow"))
        self._layout["footer"].update(Panel(Text(f"📢 Status: {self._metrics.last_event} | Pressione Ctrl+C para parar.", style="italic cyan"), title="ℹ️ Informações"))
        return self._layout


class EcosystemApplication:
    """
    Orquestrador principal e ponto de entrada da aplicação com menu de reinício.
    """

    def __init__(self) -> None:
        """Inicializa a aplicação base."""
        self._console: Console = Console()

    def run(self) -> None:
        """Inicia o loop interativo permitindo reiniciar a simulação após a extinção."""
        while True:
            grid = EcosystemGrid(width=28, height=30)
            metrics = EcosystemMetrics()
            engine = EcosystemEngine(grid, metrics)
            renderer = EcosystemRenderer(grid, metrics)

            grid.populate_initial_state(plants=100, preys=45, predators=15)

            try:
                # refresh_per_second reduzido para diminuir a velocidade visual
                with Live(renderer.render(), console=self._console, refresh_per_second=2, screen=True) as live:
                    while True:
                        engine.step()
                        live.update(renderer.render())
                        # Intervalo aumentado para 0.7s para a simulação rodar mais devagar e legível
                        time.sleep(0.7)

                        if not grid.preys and not grid.predators:
                            metrics.log_event("💀 Extinção detectada! A vida no ecossistema encerrou.")
                            live.update(renderer.render())
                            time.sleep(1.5)
                            break
            except KeyboardInterrupt:
                self._console.print("\n[bold yellow]⚠️ Simulação interrompida pelo usuário.[/bold yellow]")

            self._console.print("\n[bold cyan]🏁 O ciclo de simulação foi encerrado.[/bold cyan]")
            user_input = self._console.input("[bold yellow]Deseja reiniciar a simulação? (s/n): [/bold yellow]").strip().lower()

            if user_input not in ("s", "sim"):
                self._console.print("[bold green]👋 Aplicação finalizada com sucesso. Até a próxima![/bold green]")
                break


if __name__ == "__main__":
    app = EcosystemApplication()
    app.run()