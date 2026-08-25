"""
CYBER-LOGS v2.06

Terminal de diário pessoal criptografado com estética retro-futurista/cyberpunk,
construído inteiramente com a biblioteca Rich. O objetivo deste repositório é
demonstrar animações de terminal (boot, autenticação, HUD interativa) e não
persistência de dados: os registros vivem apenas na memória da sessão.
"""

import hashlib
import random
import sys
import time
from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text


class CyberConsole:
    """
    Orquestra toda a experiência do terminal CYBER-LOGS: boot, autenticação
    e o dashboard interativo do diário. Concentra também os utilitários de
    animação (efeito de digitação, glitch, beep) reaproveitados pelas fases
    da aplicação.
    """

    _NEON_GREEN = "#00FF00"
    _GLITCH_RED = "#FF0055"
    _CYBER_CYAN = "#00E5FF"

    _BANNER = r"""
 ██████╗██╗   ██╗██████╗ ███████╗██████╗       ██╗      ██████╗  ██████╗ ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗      ██║     ██╔═══██╗██╔════╝ ██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝█████╗██║     ██║   ██║██║  ███╗███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════╝██║     ██║   ██║██║   ██║╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║      ███████╗╚██████╔╝╚██████╔╝███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝      ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝
               v2.06 :: SISTEMA DE REGISTRO CRIPTOGRAFADO PESSOAL
"""

    def __init__(self):
        """Inicializa o console Rich, a base de usuários de demonstração e os registros em memória."""
        self._console = Console()
        self._max_tentativas = 3
        self._usuarios = self._construir_usuarios_demo()
        self._registros_diario = self._construir_registros_demo()
        self._sessao_ativa = False

    def _construir_usuarios_demo(self):
        """Retorna um dicionário de usuário -> hash SHA-256 de senha, usado apenas para fins de demonstração."""
        return {"operator": self._hash_senha("neural")}

    @staticmethod
    def _hash_senha(senha_texto_puro):
        """Converte uma senha em texto puro para seu hash SHA-256, garantindo que nenhuma credencial seja armazenada em claro."""
        return hashlib.sha256(senha_texto_puro.encode("utf-8")).hexdigest()

    def _construir_registros_demo(self):
        """Cria uma lista inicial de registros fictícios do diário para popular o dashboard."""
        return [
            {
                "timestamp": "2026-08-18 22:14",
                "titulo": "Anomalia na rede neural",
                "conteudo": "Detectada flutuação incomum nos padrões de sono registrados pelo sensor. Investigação em andamento, sem causa raiz identificada até o momento.",
                "nivel": "TOP SECRET",
                "integridade": 97,
            },
            {
                "timestamp": "2026-08-20 09:41",
                "titulo": "Backup de memórias",
                "conteudo": "Rotina de backup semanal concluída com sucesso. Nenhuma corrupção detectada nos blocos verificados.",
                "nivel": "CLASSIFIED",
                "integridade": 100,
            },
            {
                "timestamp": "2026-08-22 17:03",
                "titulo": "Contato não identificado",
                "conteudo": "Registro de comunicação criptografada recebida de origem desconhecida. Sinal descartado após triangulação inconclusiva.",
                "nivel": "RESTRICTED",
                "integridade": 88,
            },
        ]

    def _typing_effect(self, texto, style=None, delay=0.015):
        """Imprime um texto caractere a caractere, simulando digitação em um terminal antigo."""
        for caractere in texto:
            self._console.print(caractere, style=style, end="")
            time.sleep(delay)
        self._console.print()

    def _beep(self, vezes=1, intervalo=0.15):
        """Emite o caractere de campainha do terminal (BEL) uma ou mais vezes."""
        for _ in range(vezes):
            sys.stdout.write("\a")
            sys.stdout.flush()
            time.sleep(intervalo)

    @staticmethod
    def _barra_percentual(percentual, largura=10):
        """Constrói um Text com uma barra de progresso textual (blocos cheios/vazios) e o percentual ao lado."""
        preenchido = int(largura * percentual / 100)
        vazio = largura - preenchido
        barra = Text()
        barra.append("█" * preenchido, style="bold #00FF00")
        barra.append("░" * vazio, style="dim white")
        barra.append(f" {percentual:>3}%")
        return barra

    def _estilo_confidencialidade(self, nivel):
        """Mapeia um nível de confidencialidade para o estilo de cor correspondente na paleta do tema."""
        mapa = {
            "CLASSIFIED": "bold yellow",
            "TOP SECRET": f"bold {self._GLITCH_RED}",
            "RESTRICTED": f"bold {self._CYBER_CYAN}",
        }
        return mapa.get(nivel, "bold white")

    def boot_sequence(self):
        """Executa a animação de inicialização do sistema: banner, linhas digitadas e barras de progresso."""
        self._console.clear()
        self._console.print(Align.center(Text(self._BANNER, style=f"bold {self._NEON_GREEN}")))
        self._console.print()

        linhas_boot = [
            "Inicializando núcleo CYBER-LOGS...",
            "Verificando assinatura do sistema...",
            "Carregando módulos de segurança...",
        ]
        for linha in linhas_boot:
            self._typing_effect(f">> {linha}", style=self._CYBER_CYAN, delay=0.012)

        self._console.print()

        tarefas = [
            "Decodificando blocos de memória",
            "Montando partições seguras",
            "Estabelecendo conexão criptografada",
        ]
        with Progress(
            SpinnerColumn(style=self._NEON_GREEN),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=self._NEON_GREEN, finished_style=self._NEON_GREEN),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self._console,
        ) as progress:
            for descricao in tarefas:
                tarefa_id = progress.add_task(descricao, total=100)
                concluida = False
                while not concluida:
                    tarefa_atual = next(t for t in progress.tasks if t.id == tarefa_id)
                    restante = tarefa_atual.total - tarefa_atual.completed
                    if restante <= 0:
                        concluida = True
                        continue
                    incremento = min(random.randint(5, 18), restante)
                    progress.update(tarefa_id, advance=incremento)
                    time.sleep(0.08)

        self._console.print()
        self._typing_effect(">> Sistema pronto.", style=f"bold {self._NEON_GREEN}", delay=0.02)
        time.sleep(0.4)

    def _breach_animation(self, tentativas_restantes):
        """Anima uma violação de segurança: borda piscando em vermelho, texto com efeito glitch e beep sonoro."""
        caracteres_glitch = "!@#$%&*<>/\\|01"
        mensagem = "SECURITY BREACH"
        with Live(console=self._console, refresh_per_second=12) as live:
            for indice in range(8):
                estilo = f"bold {self._GLITCH_RED}" if indice % 2 == 0 else "bold white on red"
                texto_corrompido = "".join(
                    random.choice(caracteres_glitch) if random.random() < 0.35 else caractere
                    for caractere in mensagem
                )
                painel = Panel(
                    Align.center(Text(texto_corrompido, style=estilo)),
                    border_style=self._GLITCH_RED,
                    box=box.HEAVY,
                )
                live.update(painel)
                time.sleep(0.07)

        self._beep(vezes=1, intervalo=0.1)
        self._console.print(
            Panel(
                Align.center(Text(f"⚠ TENTATIVAS RESTANTES: {tentativas_restantes}", style=f"bold {self._GLITCH_RED}")),
                border_style=self._GLITCH_RED,
                box=box.DOUBLE,
            )
        )
        time.sleep(0.5)

    def _access_granted_animation(self):
        """Anima a transição de acesso concedido: borda verde neon e revelação progressiva do texto ACCESS GRANTED."""
        texto_completo = "ACCESS GRANTED"
        with Live(console=self._console, refresh_per_second=15) as live:
            for indice in range(1, len(texto_completo) + 1):
                parcial = Text(texto_completo[:indice], style=f"bold {self._NEON_GREEN}")
                painel = Panel(Align.center(parcial), border_style=self._NEON_GREEN, box=box.DOUBLE)
                live.update(painel)
                time.sleep(0.05)
            time.sleep(0.3)

        self._beep(vezes=1, intervalo=0.05)
        self._sessao_ativa = True

    def authenticate(self):
        """
        Executa o loop de autenticação. Em caso de erro, dispara a animação de
        violação de segurança e decrementa as tentativas restantes; em caso de
        acerto, dispara a animação de acesso concedido.
        """
        tentativas_restantes = self._max_tentativas

        while tentativas_restantes > 0:
            self._console.clear()
            self._console.print(
                Panel(
                    Align.center(Text("ACESSO RESTRITO", style=f"bold {self._CYBER_CYAN}")),
                    border_style=self._CYBER_CYAN,
                    box=box.DOUBLE,
                )
            )
            self._console.print("[dim italic]:: build de demonstração — usuário: operator | chave: neural ::[/dim italic]")
            self._console.print()

            try:
                usuario = Prompt.ask("[bold cyan]USUÁRIO[/bold cyan]")
                senha = Prompt.ask("[bold cyan]CHAVE DE ACESSO[/bold cyan]", password=True)
            except KeyboardInterrupt:
                raise
            except Exception:
                self._console.print("[bold red]Entrada inválida. Tente novamente.[/bold red]")
                time.sleep(1.0)
                continue

            hash_informado = self._hash_senha(senha)
            if usuario in self._usuarios and self._usuarios[usuario] == hash_informado:
                self._access_granted_animation()
                return True

            tentativas_restantes -= 1
            self._breach_animation(tentativas_restantes)

        self._console.print(
            Panel(
                Align.center(Text("SISTEMA BLOQUEADO — TENTATIVAS ESGOTADAS", style=f"bold {self._GLITCH_RED}")),
                border_style=self._GLITCH_RED,
                box=box.DOUBLE,
            )
        )
        return False

    def _build_menu_panel(self):
        """Monta o painel esquerdo do dashboard com as opções disponíveis ao usuário."""
        menu_texto = Text()
        menu_texto.append("1. ", style=f"bold {self._NEON_GREEN}")
        menu_texto.append("Ler Registros Criptografados\n\n")
        menu_texto.append("2. ", style=f"bold {self._NEON_GREEN}")
        menu_texto.append("Criar Novo Log\n\n")
        menu_texto.append("3. ", style=f"bold {self._NEON_GREEN}")
        menu_texto.append("Status de Memória\n\n")
        menu_texto.append("4. ", style=f"bold {self._GLITCH_RED}")
        menu_texto.append("Purge / Sair\n")
        return Panel(menu_texto, title="[bold]MENU[/bold]", border_style=self._CYBER_CYAN, box=box.DOUBLE)

    def _build_entries_panel(self):
        """Monta o painel direito do dashboard com a tabela de registros recentes do diário."""
        tabela = Table(box=box.SIMPLE_HEAVY, expand=True, border_style=self._CYBER_CYAN)
        tabela.add_column("TIMESTAMP", style="dim")
        tabela.add_column("TÍTULO")
        tabela.add_column("NÍVEL")
        tabela.add_column("INTEGRIDADE")

        for registro in self._registros_diario:
            estilo_nivel = self._estilo_confidencialidade(registro["nivel"])
            tabela.add_row(
                registro["timestamp"],
                registro["titulo"],
                Text(registro["nivel"], style=estilo_nivel),
                self._barra_percentual(registro["integridade"]),
            )

        return Panel(tabela, title="[bold]REGISTROS RECENTES[/bold]", border_style=self._CYBER_CYAN, box=box.DOUBLE)

    def _render_dashboard(self):
        """Renderiza o dashboard completo, dividindo a tela em menu (esquerda) e registros (direita)."""
        self._console.clear()
        layout = Layout()
        layout.split_row(
            Layout(name="menu", ratio=1),
            Layout(name="registros", ratio=2),
        )
        layout["menu"].update(self._build_menu_panel())
        layout["registros"].update(self._build_entries_panel())
        self._console.print(layout)

    def _read_logs(self):
        """Lista os registros existentes e permite ao usuário 'decifrar' um deles para leitura completa."""
        self._console.clear()
        self._console.print(
            Panel(
                Align.center(Text("REGISTROS CRIPTOGRAFADOS", style=f"bold {self._CYBER_CYAN}")),
                border_style=self._CYBER_CYAN,
                box=box.DOUBLE,
            )
        )
        for indice, registro in enumerate(self._registros_diario, start=1):
            self._console.print(f"[bold {self._NEON_GREEN}]{indice}[/bold {self._NEON_GREEN}] - {registro['titulo']} ({registro['timestamp']})")
        self._console.print()

        try:
            escolha = Prompt.ask(
                "[bold cyan]Digite o número do registro para decifrar (ou ENTER para voltar)[/bold cyan]",
                default="",
            )
        except KeyboardInterrupt:
            raise

        if not escolha.strip():
            return

        try:
            indice_escolhido = int(escolha) - 1
            registro = self._registros_diario[indice_escolhido]
        except (ValueError, IndexError):
            self._console.print("[bold red]Registro inválido.[/bold red]")
            time.sleep(1.2)
            return

        self._console.print()
        self._typing_effect(f"» Decifrando '{registro['titulo']}'...", style=self._NEON_GREEN, delay=0.02)
        self._console.print(
            Panel(
                registro["conteudo"],
                title=f"[bold]{registro['titulo']}[/bold]",
                border_style=self._estilo_confidencialidade(registro["nivel"]),
                box=box.DOUBLE,
            )
        )
        try:
            Prompt.ask("[dim]Pressione ENTER para voltar[/dim]", default="")
        except KeyboardInterrupt:
            raise

    def _create_log(self):
        """Solicita os dados de um novo registro e o insere no início da lista em memória."""
        self._console.clear()
        self._console.print(
            Panel(
                Align.center(Text("NOVO REGISTRO", style=f"bold {self._NEON_GREEN}")),
                border_style=self._NEON_GREEN,
                box=box.DOUBLE,
            )
        )

        try:
            titulo = Prompt.ask("[bold cyan]Título[/bold cyan]")
            conteudo = Prompt.ask("[bold cyan]Conteúdo[/bold cyan]")
            nivel = Prompt.ask(
                "[bold cyan]Nível de confidencialidade[/bold cyan]",
                choices=["CLASSIFIED", "TOP SECRET", "RESTRICTED"],
                default="CLASSIFIED",
            )
        except KeyboardInterrupt:
            raise
        except Exception:
            self._console.print("[bold red]Não foi possível registrar o log. Tente novamente.[/bold red]")
            time.sleep(1.2)
            return

        novo_registro = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "titulo": titulo.strip() or "SEM TÍTULO",
            "conteudo": conteudo.strip() or "(vazio)",
            "nivel": nivel,
            "integridade": random.randint(85, 100),
        }
        self._registros_diario.insert(0, novo_registro)

        self._typing_effect("» Registro salvo na memória volátil.", style=self._NEON_GREEN, delay=0.02)
        self._beep(vezes=1, intervalo=0.05)
        time.sleep(0.6)

    def _memory_status(self):
        """Exibe uma animação de uso de memória e um resumo do estado atual do sistema."""
        self._console.clear()
        self._console.print(
            Panel(
                Align.center(Text("STATUS DE MEMÓRIA", style=f"bold {self._CYBER_CYAN}")),
                border_style=self._CYBER_CYAN,
                box=box.DOUBLE,
            )
        )

        uso_memoria_alvo = random.randint(40, 92)
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style=self._NEON_GREEN, finished_style=self._GLITCH_RED),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self._console,
        ) as progress:
            tarefa_id = progress.add_task("Uso de memória volátil", total=100)
            concluida = False
            while not concluida:
                tarefa_atual = next(t for t in progress.tasks if t.id == tarefa_id)
                if tarefa_atual.completed >= uso_memoria_alvo:
                    concluida = True
                    continue
                incremento = min(random.randint(3, 9), uso_memoria_alvo - tarefa_atual.completed)
                progress.update(tarefa_id, advance=incremento)
                time.sleep(0.05)

        total_registros = len(self._registros_diario)
        integridade_media = random.randint(88, 99)
        self._console.print(
            Panel(
                f"Registros ativos: [bold {self._NEON_GREEN}]{total_registros}[/bold {self._NEON_GREEN}]\n"
                f"Integridade média do sistema: [bold {self._CYBER_CYAN}]{integridade_media}%[/bold {self._CYBER_CYAN}]",
                border_style=self._CYBER_CYAN,
                box=box.ROUNDED,
            )
        )
        try:
            Prompt.ask("[dim]Pressione ENTER para voltar[/dim]", default="")
        except KeyboardInterrupt:
            raise

    def _purge_and_exit(self):
        """Confirma com o usuário e, em caso positivo, anima a purga dos registros e encerra a sessão."""
        self._console.clear()
        try:
            confirmar = Confirm.ask(
                "[bold red]Tem certeza que deseja PURGAR a memória e encerrar a sessão?[/bold red]",
                default=False,
            )
        except KeyboardInterrupt:
            raise

        if not confirmar:
            return

        registros_restantes = list(self._registros_diario)
        with Live(console=self._console, refresh_per_second=10) as live:
            while registros_restantes:
                registros_restantes.pop()
                texto = Text(
                    f"Apagando registros... {len(registros_restantes)} restantes",
                    style=f"bold {self._GLITCH_RED}",
                )
                live.update(Panel(Align.center(texto), border_style=self._GLITCH_RED, box=box.HEAVY))
                time.sleep(0.15)

        self._registros_diario.clear()
        self._beep(vezes=2, intervalo=0.2)
        self._console.print(
            Panel(
                Align.center(Text("MEMÓRIA PURGADA — CONEXÃO ENCERRADA", style=f"bold {self._GLITCH_RED}")),
                border_style=self._GLITCH_RED,
                box=box.DOUBLE,
            )
        )
        self._sessao_ativa = False

    def run_dashboard(self):
        """Laço principal do dashboard: renderiza o layout e despacha a opção escolhida pelo usuário."""
        while self._sessao_ativa:
            self._render_dashboard()
            try:
                escolha = Prompt.ask(
                    "[bold cyan]SELECIONE UMA OPÇÃO[/bold cyan]",
                    choices=["1", "2", "3", "4"],
                    show_choices=False,
                )
            except KeyboardInterrupt:
                raise
            except Exception:
                self._console.print("[bold red]Opção inválida.[/bold red]")
                time.sleep(1.0)
                continue

            if escolha == "1":
                self._read_logs()
            elif escolha == "2":
                self._create_log()
            elif escolha == "3":
                self._memory_status()
            elif escolha == "4":
                self._purge_and_exit()

    def run(self):
        """
        Ponto de entrada principal: executa boot, autenticação e o dashboard
        interativo, tratando interrupções manuais (Ctrl+C) e erros inesperados
        de forma amigável, sem jamais expor um traceback ao usuário.
        """
        try:
            self.boot_sequence()
            if self.authenticate():
                self.run_dashboard()
                self._console.print()
                self._console.print("[dim]Sessão finalizada. Até a próxima, operador.[/dim]")
        except KeyboardInterrupt:
            self._console.print()
            self._console.print(
                Panel(
                    Align.center(Text("INTERRUPÇÃO MANUAL DETECTADA — ENCERRANDO COM SEGURANÇA", style=f"bold {self._CYBER_CYAN}")),
                    border_style=self._CYBER_CYAN,
                    box=box.DOUBLE,
                )
            )
            sys.exit(0)
        except Exception as erro:
            self._console.print()
            self._console.print(
                Panel(
                    Align.center(Text(f"FALHA INESPERADA NO SISTEMA: {erro}", style=f"bold {self._GLITCH_RED}")),
                    border_style=self._GLITCH_RED,
                    box=box.DOUBLE,
                )
            )
            sys.exit(1)


if __name__ == "__main__":
    CyberConsole().run()