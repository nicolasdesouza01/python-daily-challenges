import os
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.live import Live

class CassinoSlotMachine:
    """
    Gerencia a lógica de um jogo de Caça-Níveis (Slot Machine) em tempo real.
    Inclui cálculo de pontuação baseada em risco, animação sequencial das roletas
    e controle rigoroso de encerramento por vitória ou limite de jogadas.
    A interface utiliza cores vibrantes como rosa e magenta.
    """
    VALORES = {"👑": 100, "💎": 70, "💵": 50, "🎲": 30, "🃏": 10, "💣": -50}
    EMOJIS = list(VALORES.keys())

    def __init__(self, meta: int = 1000, saldo_inicial: int = 200):
        """
        Inicializa as configurações base do jogo.

        :param meta: Pontuação alvo para a vitória.
        :param saldo_inicial: Pontuação inicial do jogador.
        """
        self._meta = meta
        self._saldo_inicial = saldo_inicial
        self._pontos = saldo_inicial
        self._jogadas = 0
        self._limite_jogadas = 0
        self._fator_multiplicador = 1.0
        self._roletas = ["🎰", "🎰", "🎰"]
        self._console = Console()

    def _limpar_tela(self) -> None:
        """Limpa o terminal de forma compatível com Windows e Linux."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def configurar_partida(self) -> None:
        """
        Apresenta o menu inicial para definição da dificuldade e multiplicador.
        Trata entradas inválidas de forma resiliente.
        """
        self._limpar_tela()
        self._console.print(Panel("[bold bright_green]🎰 BEM-VINDO AO CASSINO SLOT MACHINE 🎰[/bold bright_green]", border_style="bright_magenta"))
        self._console.print("\n[bold magenta]Escolha o limite de rodadas (define dificuldade e bônus):[/bold magenta]")
        self._console.print(" [bold green]1[/bold green] - Rápido (10 Rodadas) ➔ [bold yellow]x1.5 Pts[/bold yellow]")
        self._console.print(" [bold green]2[/bold green] - Padrão (20 Rodadas) ➔ [bold yellow]x1.0 Pts[/bold yellow]")
        self._console.print(" [bold green]3[/bold green] - Longo  (35 Rodadas) ➔ [bold yellow]x0.8 Pts[/bold yellow]")
        self._console.print(" [bold green]4[/bold green] - Livre  (Sem Limite) ➔ [bold yellow]x0.5 Pts[/bold yellow]\n")

        opcoes = {
            "1": (10, 1.5),
            "2": (20, 1.0),
            "3": (35, 0.8),
            "4": (0, 0.5)
        }

        while True:
            self._console.print("[bold magenta]Digite a opção (1-4): [/bold magenta]", end="")
            opcao = input().strip()
            if opcao in opcoes:
                self._limite_jogadas, self._fator_multiplicador = opcoes[opcao]
                break
            self._console.print("[bold yellow]⚠️ Opção inválida! Tente novamente.[/bold yellow]")

    def _gerar_dashboard(self, status_msg: str = "") -> Table:
        """
        Constrói a interface visual dividida em Coluna de Valores, Painel Central e Sistema.

        :param status_msg: Mensagem descritiva opcional no painel central.
        :return: Tabela Rich formatada para exibição Live.
        """
        tab_valores = Table(title="[bold green]VALORES[/bold green]", show_edge=False, pad_edge=False)
        tab_valores.add_column("Símbolo", justify="center")
        tab_valores.add_column("Pts", justify="right", style="magenta")
        for symb, val in self.VALORES.items():
            cor = "green" if val > 0 else "bold red"
            tab_valores.add_row(symb, f"[{cor}]{val:+d}[/{cor}]")

        info_rodadas = f"{self._jogadas}/{self._limite_jogadas}" if self._limite_jogadas > 0 else f"{self._jogadas}"
        vis_roletas = f"[bold bright_green]  {self._roletas[0]}  |  {self._roletas[1]}  |  {self._roletas[2]}  [/bold bright_green]"
        diferenca = self._meta - self._pontos
        
        conteudo_centro = (
            f"[bold magenta]PONTUAÇÃO:[/bold magenta] [bold bright_green]{self._pontos}[/bold bright_green] / [bold green]{self._meta}[/bold green] pts\n"
            f"[bold magenta]RODADAS:[/bold magenta] [bold white]{info_rodadas}[/bold white] | [bold magenta]FALTAM:[/bold magenta] [bold yellow]{max(0, diferenca)}[/bold yellow] pts\n\n"
            f"[purple]────────────────────────────────────────────[/purple]\n"
            f"{vis_roletas}\n"
            f"[purple]────────────────────────────────────────────[/purple]\n"
            f"{status_msg if status_msg else '[dim magenta]Pressione ENTER para girar a roleta![/dim magenta]'}"
        )
        
        layout = Table(show_header=False, show_edge=False, pad_edge=False, expand=True)
        layout.add_column(ratio=1)
        layout.add_column(ratio=2)
        layout.add_column(ratio=1)
        layout.add_row(
            Panel(Align.center(tab_valores), border_style="green"),
            Panel(Align.center(conteudo_centro), title="[bold bright_green]🎲 MESA DE JOGO 🎲[/bold bright_green]", border_style="bright_magenta"),
            Panel(Align.center(f"\n[bold magenta]SISTEMA[/bold magenta]\n\nMult: [bold yellow]{self._fator_multiplicador}x[/bold yellow]\n3x = TRIPLO\n2x = DOBRO\n💣💣💣 = ZERA\n"), title="[bold magenta]REGRAS[/bold magenta]", border_style="green")
        )
        return layout

    def calcular_resultado(self, r1: str, r2: str, r3: str) -> tuple[int, str]:
        """
        Calcula os pontos ganhos/perdidos e gera a mensagem de feedback.
        Aplica multiplicadores de combo e de risco.

        :return: Tupla com (pontos_ganhos, mensagem_explicativa).
        """
        soma_base = self.VALORES[r1] + self.VALORES[r2] + self.VALORES[r3]
        
        if r1 == r2 == r3 == "💣":
            self._pontos = 0
            return 0, "[bold red]💣 ZEROU! Três bombas destruíram tudo![/bold red]"
        
        combo = 1
        msg_combo = ""
        if r1 == r2 == r3:
            combo = 3
            msg_combo = "[bold bright_green]⚡ TRINCA! (3x)[/bold bright_green] "
        elif r1 == r2 or r2 == r3 or r1 == r3:
            combo = 2
            msg_combo = "[bold pink]🔥 PAR! (2x)[/bold pink] "

        ganho = int((soma_base * combo) * self._fator_multiplicador)
        msg = f"{msg_combo}Ganhos: [bold white]{ganho:+d}[/bold white] pts (x{self._fator_multiplicador} risco)."
        return ganho, msg

    def girar_com_suspense(self, live: Live) -> None:
        """
        Executa a animação de giro onde as roletas para individualmente,
        criando suspense e atualizando a interface Live.

        :param live: Instância Rich Live ativa.
        """
        self._jogadas += 1
        resultados = [random.choice(self.EMOJIS) for _ in range(3)]
        fases = [
            (10, 0.06, "[dim magenta]GIRANDO...[/dim magenta]", [0,1,2]),
            (8, 0.1, f"[bold magenta]FIXADA 1: {resultados[0]}[/bold magenta]", [1,2]),
            (10, 0.12, f"[bold magenta]FIXADA 2: {resultados[1]}! ÚLTIMA...[/bold magenta]", [2])
        ]

        for loops, delay, msg, roletas_ativas in fases:
            for i in range(loops):
                for r in roletas_ativas:
                    self._roletas[r] = random.choice(self.EMOJIS)
                
                atraso = delay + (i * 0.03 if len(roletas_ativas) == 1 else 0)
                live.update(self._gerar_dashboard(msg))
                time.sleep(atraso)
            
            if len(roletas_ativas) > 0:
                self._roletas[roletas_ativas[0]-1 if len(roletas_ativas) > 1 else 2] = resultados[roletas_ativas[0]-1 if len(roletas_ativas) > 1 else 2]

        self._roletas = resultados
        ganho, msg_res = self.calcular_resultado(*resultados)
        self._pontos = max(0, self._pontos + ganho)
        live.update(self._gerar_dashboard(msg_res))

    def jogar(self) -> None:
        """Loop principal do jogo, gerenciando turnos, menus pós-jogo e encerramento seguro."""
        while True:
            self.configurar_partida()
            self._pontos, self._jogadas, self._roletas = self._saldo_inicial, 0, ["🎰", "🎰", "🎰"]

            try:
                with Live(self._gerar_dashboard(), console=self._console, refresh_per_second=15) as live:
                    while True:
                        live.stop()
                        if self._pontos >= self._meta or (self._limite_jogadas > 0 and self._jogadas >= self._limite_jogadas):
                            break

                        self._console.print("\n[bold magenta]Pressione [ENTER] para girar [/bold magenta][dim white]('s' para menu):[/dim white] ", end="")
                        if input().strip().lower() in ['s', 'sair', 'menu']: break
                        
                        live.start()
                        self.girar_com_suspense(live)

                self._limpar_tela()
                venceu = self._pontos >= self._meta
                cor_status = 'green' if venceu else 'red'
                titulo_final = '🏆 VITÓRIA! META ATINGIDA!' if venceu else '💥 FIM DE JOGO! RODADAS ESGOTADAS!'
                p_final = Panel(Align.center(f"\n[bold {cor_status}]{titulo_final} 🏆[/bold {cor_status}]\n\nPontos: [bold magenta]{self._pontos}[/bold magenta] / [bold white]{self._meta}[/bold white]\nRodadas: [bold white]{self._jogadas}[/bold white]\n"), border_style="green" if venceu else "red")
                self._console.print(p_final)
                
                self._console.print("[bold magenta]O que deseja fazer?[/bold magenta]\n [bold green]1[/bold green] - Nova Partida\n [bold pink]2[/bold pink] - Continuar (+10 rodadas)\n [bold red]3[/bold red] - Sair\n")
                escolha = input("Opção: ").strip()
                if escolha == "2" and not venceu: self._limite_jogadas += 10; continue
                if escolha == "3": break

            except KeyboardInterrupt:
                self._console.print("\n\n[bold pink]Aplicação finalizada pelo usuário.[/bold pink]"); break

if __name__ == "__main__":
    jogo = CassinoSlotMachine()
    jogo.jogar()