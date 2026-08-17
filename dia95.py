import os, time
from random import randint, choice
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.prompt import Prompt, IntPrompt
from rich.align import Align
from rich.text import Text

console = Console()

@dataclass
class GeradorPassivo:
    nome: str
    preco_base: int
    rendimento_base: int
    quantidade: int = 0

    @property
    def preco_atual(self) -> int: return int(self.preco_base * (1.2 ** self.quantidade))
    @property
    def rendimento_total(self) -> int: return self.quantidade * self.rendimento_base

@dataclass
class Conquista:
    id_c: str
    titulo: str
    descricao: str
    recompensa: int
    desbloqueada: bool = False

@dataclass
class Chefao:
    nome: str
    titulo: str
    max_limite: int
    modificador: str

class Jogador:
    def __init__(self):
        self.hp_max = self.hp = 3
        self.moedas, self.gemas_elite, self.vitorias, self.sequencia_atual, self.maior_sequencia, self.rodada, self.total_rebirths = 100, 0, 0, 0, 0, 1, 0
        self.multiplicador_permanente = 1.0
        self.inventario = {"Espião": 0, "Escudo": 0, "Aposta Dupla": 0}
        self.historico_compras = set()
        self.upgrades_rebirth = {"HP Permanente": 0, "Escudo de Entrada": 0, "Juros Bancários": 0, "Passe VIP Boss": 0}
        self.reliqueas = {"Trevo de 4 Folhas": False, "Calculadora Quebrada": False}
        self._reset_geradores()

    def _reset_geradores(self):
        self.geradores = [
            GeradorPassivo("Bot Apostador", 40, 4), GeradorPassivo("Cassino Clandestino", 150, 18),
            GeradorPassivo("Minerador de Dados", 600, 80), GeradorPassivo("Servidor Quantico", 2000, 300)
        ]

    def modificar_moedas(self, qtd: int):
        self.moedas = self.moedas + int(qtd * self.multiplicador_permanente) if qtd > 0 else max(0, self.moedas + qtd)

    def modificar_hp(self, qtd: int): self.hp = min(self.hp_max, max(0, self.hp + qtd))

    def processar_renda_passiva(self) -> int:
        renda = sum(g.rendimento_total for g in self.geradores) + (int(self.moedas * (0.02 * self.upgrades_rebirth["Juros Bancários"])) if self.upgrades_rebirth["Juros Bancários"] else 0)
        if renda > 0: self.modificar_moedas(renda)
        return renda

    def usar_item(self, item: str) -> bool:
        if self.inventario.get(item, 0) > 0:
            self.inventario[item] -= 1
            return True
        return False

    def executar_rebirth(self) -> bool:
        if self.total_rebirths >= 5 or (self.rodada < 12 and self.moedas < 1500): return False
        self.total_rebirths += 1
        self.gemas_elite += max(2, (self.rodada // 3) + (self.moedas // 800))
        self.multiplicador_permanente += 0.4
        self.hp_max = 3 + self.upgrades_rebirth["HP Permanente"]
        self.hp, self.moedas, self.vitorias, self.sequencia_atual, self.rodada = self.hp_max, 100, 0, 0, 1
        self.inventario = {"Espião": 0, "Escudo": self.upgrades_rebirth["Escudo de Entrada"], "Aposta Dupla": 0}
        self._reset_geradores()
        return True

class GerenciadorConquistas:
    def __init__(self):
        self.conquistas = [
            Conquista("C1", "Primeiro Passo", "Vença sua primeira rodada", 30),
            Conquista("C2", "Mestre da Automação", "Compre seu primeiro Bot ou Gerador", 60),
            Conquista("C3", "Sequência Imparável", "Atinja uma sequência de 5 vitórias", 150),
            Conquista("C4", "Matador de Chefes", "Derrote o seu primeiro Boss", 200),
            Conquista("C5", "Magnata do Par", "Acumule 1.500 moedas na carteira", 500),
            Conquista("C6", "Primeiro Renascimento", "Realize seu 1º Rebirth", 300),
            Conquista("C7", "Colecionador", "Compre tudo da loja pelo menos 1 vez", 600),
            Conquista("C8", "Mestre das Relíquias", "Adquira sua primeira Relíquia de Elite", 800),
            Conquista("C9", "Rebirth Final", "Alcance o Rebirth nível 5 máximo", 2500)
        ]

    def verificar(self, j: Jogador, boss_derrotado: bool = False) -> list:
        novas = []
        for c in self.conquistas:
            if not c.desbloqueada:
                cond = (
                    (c.id_c == "C1" and j.vitorias >= 1) or (c.id_c == "C2" and any(g.quantidade > 0 for g in j.geradores)) or
                    (c.id_c == "C3" and j.sequencia_atual >= 5) or (c.id_c == "C4" and boss_derrotado) or
                    (c.id_c == "C5" and j.moedas >= 1500) or (c.id_c == "C6" and j.total_rebirths >= 1) or
                    (c.id_c == "C7" and {"1","2","3","4","5","6","7","8"}.issubset(j.historico_compras)) or
                    (c.id_c == "C8" and any(j.reliqueas.values())) or (c.id_c == "C9" and j.total_rebirths >= 5)
                )
                if cond:
                    c.desbloqueada = True
                    j.modificar_moedas(c.recompensa)
                    novas.append(c)
        return novas

class JogoEngine:
    def __init__(self):
        self.j = Jogador()
        self.gc = GerenciadorConquistas()
        self.bosses = [Chefao("Titan Par", "Devorador de Números", 15, "Números até 15"), Chefao("Ciber Ímpar", "Lorde do Caos", 20, "Números até 20"), Chefao("Mestre Supremo", "Inflexível", 25, "Desafio supremo até 25")]

    def _limpar(self): os.system('cls' if os.name == 'nt' else 'clear')

    def _renderizar_hud(self) -> Layout:
        layout = Layout()
        layout.split(Layout(name="header", size=3), Layout(name="body", ratio=1), Layout(name="footer", size=3))
        layout["body"].split_row(Layout(name="main", ratio=2), Layout(name="side", ratio=1))

        head = Text.assemble(
            (" PAR OU ÍMPAR TYCOON ", "bold gold1"), ("| ", "white"), (f"Rodada {self.j.rodada} ", "bold cyan"), ("| ", "white"),
            (f"HP: {self.j.hp}/{self.j.hp_max} ", "bold red"), ("| ", "white"), (f"MOEDAS: $ {self.j.moedas} ", "bold yellow"), ("| ", "white"),
            (f"Gemas: {self.j.gemas_elite} ", "bold magenta"), ("| ", "white"), (f"Rebirth: {self.j.total_rebirths}/5", "bold green")
        )
        layout["header"].update(Panel(Align.center(head), style="bold blue"))

        st = Table(expand=True, show_header=False, padding=(0, 1))
        st.add_column("K", style="bold cyan"); st.add_column("V", style="bold white", justify="right")
        st.add_row("Vida Atual", f"{self.j.hp}/{self.j.hp_max}"); st.add_row("Saldo", f"$ {self.j.moedas}")
        st.add_row("Gemas", f"{self.j.gemas_elite}"); st.add_row("Sequência", f"{self.j.sequencia_atual}x")
        st.add_row("Passivo", f"+${sum(g.rendimento_total for g in self.j.geradores)}/rd"); st.add_row("Rebirth Multi", f"{self.j.multiplicador_permanente:.2f}x")
        st.add_section()
        for k, v in self.j.inventario.items(): st.add_row(f"Item: {k}", str(v))

        layout["side"].update(Panel(st, title="[bold green]Status[/bold green]", style="green"))
        layout["footer"].update(Panel(Align.center("[1] Jogar | [2] Loja Padrao | [3] Loja Rebirth | [4] Conquistas | [5] Rebirth | [0] Sair"), style="bold magenta"))
        return layout

    def exibe_conquistas(self, conquistas: list):
        for c in conquistas:
            console.print(Panel(f"[bold yellow]{c.titulo}[/bold yellow]\n{c.descricao}\n+${c.recompensa} moedas!", title="CONQUISTA", style="yellow"))
            time.sleep(1)

    def menu_loja(self):
        itens = [("1", "Poção de HP", "Restaura +1 HP", 30), ("2", "Espião", "Revela a IA", 45), ("3", "Escudo", "Protege de 1 dano", 65), ("4", "Aposta Dupla", "Vitória 3x", 90)]
        while True:
            self._limpar()
            layout = self._renderizar_hud()
            tb = Table(title="LOJA PADRÃO", expand=True, padding=(0, 1))
            tb.add_column("ID", style="bold cyan", width=4); tb.add_column("Item", style="bold white"); tb.add_column("Efeito / Renda", style="bold green"); tb.add_column("Preço", style="bold yellow", justify="right")
            for cod, nome, ef, pr in itens: tb.add_row(cod, nome, ef, f"$ {pr}")
            tb.add_section()
            for idx, g in enumerate(self.j.geradores, start=5): tb.add_row(str(idx), f"{g.nome} ({g.quantidade})", f"+${g.rendimento_total}/rd", f"$ {g.preco_atual}")
            layout["main"].update(Panel(tb, style="yellow"))
            console.print(layout)

            op = Prompt.ask("\n[bold yellow]Escolha um item (0 para voltar)[/bold yellow]", default="0")
            if op == "0": break
            self.j.historico_compras.add(op)
            if op == "1" and self.j.moedas >= 30 and self.j.hp < self.j.hp_max:
                self.j.modificar_moedas(-30); self.j.modificar_hp(1)
            elif op in ["2", "3", "4"]:
                m = {"2": (45, "Espião"), "3": (65, "Escudo"), "4": (90, "Aposta Dupla")}
                c, n = m[op]
                if self.j.moedas >= c: self.j.modificar_moedas(-c); self.j.inventario[n] += 1
            elif op in ["5", "6", "7", "8"]:
                g = self.j.geradores[int(op) - 5]
                if self.j.moedas >= g.preco_atual: self.j.modificar_moedas(-g.preco_atual); g.quantidade += 1
            self.exibe_conquistas(self.gc.verificar(self.j))

    def menu_loja_rebirth(self):
        while True:
            self._limpar()
            layout = self._renderizar_hud()
            tb = Table(title="LOJA DE GEMAS DE ELITE", expand=True, padding=(0, 1))
            tb.add_column("ID", style="bold cyan", width=4); tb.add_column("Upgrade / Relíquia", style="bold white"); tb.add_column("Efeito Permanente", style="bold green"); tb.add_column("Preço", style="bold magenta", justify="right")
            tb.add_row("1", f"HP Perm ({self.j.upgrades_rebirth['HP Permanente']})", "+1 HP máximo", "3 Gemas")
            tb.add_row("2", f"Escudo Entrada ({self.j.upgrades_rebirth['Escudo de Entrada']})", "+1 Escudo inicial", "4 Gemas")
            tb.add_row("3", f"Juros ({self.j.upgrades_rebirth['Juros Bancários']})", "+2% do saldo/rd", "5 Gemas")
            tb.add_row("4", f"Passe VIP ({self.j.upgrades_rebirth['Passe VIP Boss']})", "Dobra prêmio de Bosses", "6 Gemas")
            tb.add_section()
            tb.add_row("5", f"Relíquia: Trevo [{'OK' if self.j.reliqueas['Trevo de 4 Folhas'] else 'Disp'}]", "20% chance ignora erro", "8 Gemas")
            tb.add_row("6", f"Relíquia: Calculadora [{'OK' if self.j.reliqueas['Calculadora Quebrada'] else 'Disp'}]", "Revela se soma >10", "10 Gemas")
            layout["main"].update(Panel(tb, style="magenta"))
            console.print(layout)

            op = Prompt.ask("\n[bold magenta]Comprar com Gemas (0 para voltar)[/bold magenta]", default="0")
            if op == "0": break
            upg = [("1", 3, "HP Permanente"), ("2", 4, "Escudo de Entrada"), ("3", 5, "Juros Bancários"), ("4", 6, "Passe VIP Boss")]
            for id_u, custo, chave in upg:
                if op == id_u and self.j.gemas_elite >= custo:
                    self.j.gemas_elite -= custo; self.j.upgrades_rebirth[chave] += 1
                    if chave == "HP Permanente": self.j.hp_max += 1; self.j.hp += 1
                    elif chave == "Escudo de Entrada": self.j.inventario["Escudo"] += 1
            if op == "5" and self.j.gemas_elite >= 8 and not self.j.reliqueas["Trevo de 4 Folhas"]:
                self.j.gemas_elite -= 8; self.j.reliqueas["Trevo de 4 Folhas"] = True
            elif op == "6" and self.j.gemas_elite >= 10 and not self.j.reliqueas["Calculadora Quebrada"]:
                self.j.gemas_elite -= 10; self.j.reliqueas["Calculadora Quebrada"] = True
            self.exibe_conquistas(self.gc.verificar(self.j))

    def menu_conquistas(self):
        self._limpar()
        layout = self._renderizar_hud()
        tb = Table(title="CONQUISTAS DO JOGO", expand=True, padding=(0, 1))
        tb.add_column("Status", width=8); tb.add_column("Título", style="bold white"); tb.add_column("Descrição"); tb.add_column("Bônus", style="bold yellow", justify="right")
        for c in self.gc.conquistas: tb.add_row("[OK]" if c.desbloqueada else "[LOCKED]", c.titulo, c.descricao, f"+${c.recompensa}")
        layout["main"].update(Panel(tb, style="cyan"))
        console.print(layout)
        Prompt.ask("\n[bold cyan]ENTER para voltar...[/bold cyan]")

    def menu_rebirth(self):
        self._limpar()
        layout = self._renderizar_hud()
        pode = self.j.rodada >= 12 or self.j.moedas >= 1500
        msg = "[bold gold1]Rebirth MÁXIMO (5/5)![/bold gold1]" if self.j.total_rebirths >= 5 else f"Rebirth: {self.j.total_rebirths}/5\nReq: Rodada 12 OU $1.500 Moedas.\nStatus: {'[bold green]DISPONÍVEL![/bold green]' if pode else '[bold red]INDISPONÍVEL[/bold red]'}"
        layout["main"].update(Panel(Align.center(msg), style="bold magenta"))
        console.print(layout)
        if self.j.total_rebirths < 5 and pode and Prompt.ask("Realizar Rebirth? [S/N]", choices=["S", "N"], default="N").upper() == "S":
            if self.j.executar_rebirth():
                console.print("[bold gold1]Rebirth concluído![/bold gold1]")
                self.exibe_conquistas(self.gc.verificar(self.j))
                time.sleep(1.5)
        else: Prompt.ask("\n[bold cyan]ENTER para voltar...[/bold cyan]")

    def jogar_rodada(self):
        self._limpar()
        is_boss = (self.j.rodada % 5 == 0)
        boss = choice(self.bosses) if is_boss else None
        num_ia = randint(0, boss.max_limite if is_boss else 10)
        aposta_ativa = False

        layout = self._renderizar_hud()
        info = f"BOSS: {boss.nome}\n{boss.modificador}\n" if is_boss else f"RODADA {self.j.rodada}\n"
        if self.j.reliqueas["Calculadora Quebrada"]:
            info += f"\n[bold magenta]Calculadora: Soma > 10? {'SIM' if (num_ia + 5) > 10 else 'NÃO/IGUAL'}[/bold magenta]\n"
        layout["main"].update(Panel(Align.center(info), style="bold blue"))
        console.print(layout)

        if self.j.inventario["Espião"] > 0 and Prompt.ask("Usar Espião? [S/N]", choices=["S", "N"], default="N").upper() == "S":
            if self.j.usar_item("Espião"): console.print(f"[bold green]Espião: Número é {'PAR' if num_ia % 2 == 0 else 'ÍMPAR'}![/bold green]")
        if self.j.inventario["Aposta Dupla"] > 0 and Prompt.ask("Usar Aposta Dupla? [S/N]", choices=["S", "N"], default="N").upper() == "S":
            if self.j.usar_item("Aposta Dupla"): aposta_ativa = True

        pi = Prompt.ask("[bold cyan]Par ou Ímpar?[/bold cyan]", choices=["P", "I", "p", "i"]).upper()
        num_jog = IntPrompt.ask("[bold cyan]Digite um número (0 a 10)[/bold cyan]")
        with console.status("[bold green]Calculando...", spinner="dots"): time.sleep(1)

        soma = num_jog + num_ia
        par = (soma % 2 == 0)
        venceu = (pi == 'P' and par) or (pi == 'I' and not par)

        self._limpar()
        layout = self._renderizar_hud()
        res = Text(f"Você: {num_jog} | IA: {num_ia} | Total: {soma} ({'PAR' if par else 'ÍMPAR'})\n\n", style="bold white")

        if venceu:
            res.append("VOCÊ VENCEU!\n", style="bold green")
            self.j.vitorias += 1; self.j.sequencia_atual += 1
            self.j.maior_sequencia = max(self.j.maior_sequencia, self.j.sequencia_atual)
            ganho = (20 + self.j.sequencia_atual * 5) * (3 if aposta_ativa else 1) + ((100 * (2 if self.j.upgrades_rebirth["Passe VIP Boss"] else 1)) if is_boss else 0)
            self.j.modificar_moedas(ganho)
            res.append(f"Ganhou: +${ganho} moedas!\n", style="bold yellow")
        else:
            trevo = self.j.reliqueas["Trevo de 4 Folhas"] and randint(1, 100) <= 20
            if trevo: res.append("ERROU, mas o Trevo te salvou!\n", style="bold green")
            else:
                res.append("VOCÊ PERDEU!\n", style="bold red")
                if self.j.inventario["Escudo"] > 0 and Prompt.ask("Usar Escudo? [S/N]", choices=["S", "N"], default="S").upper() == "S":
                    self.j.usar_item("Escudo"); res.append("Dano bloqueado!\n", style="bold green")
                else:
                    self.j.modificar_hp(-1); self.j.sequencia_atual = 0
                    res.append("Perdeu 1 HP!\n", style="bold red")

        renda = self.j.processar_renda_passiva()
        if renda > 0: res.append(f"Automação/Juros: +${renda} moedas!\n", style="bold cyan")
        self.j.rodada += 1
        layout["main"].update(Panel(Align.center(res), style="bold green" if venceu else "bold red"))
        console.print(layout)
        self.exibe_conquistas(self.gc.verificar(self.j, boss_derrotado=(venceu and is_boss)))
        Prompt.ask("\n[bold cyan]ENTER para continuar...[/bold cyan]")

    def iniciar(self):
        while True:
            try:
                if self.j.hp <= 0:
                    self._limpar()
                    console.print(Panel(Align.center(f"GAME OVER!\nSobreviveu até a Rodada {self.j.rodada}"), style="bold red"))
                    if Prompt.ask("Jogar novamente? [S/N]", choices=["S", "N"], default="S").upper() == "S":
                        self.j = Jogador(); continue
                    break

                self._limpar()
                layout = self._renderizar_hud()
                bv = Text(" BEM-VINDO AO PAR OU ÍMPAR TYCOON \n\n", style="bold gold1")
                bv.append("[1] Jogar | [2] Loja Padrao | [3] Loja Rebirth | [4] Conquistas | [5] Rebirth", style="bold white")
                layout["main"].update(Panel(Align.center(bv), style="bold blue"))
                console.print(layout)

                op = Prompt.ask("[bold yellow]Opção[/bold yellow]", choices=["1", "2", "3", "4", "5", "0"], default="1")
                if op == "1": self.jogar_rodada()
                elif op == "2": self.menu_loja()
                elif op == "3": self.menu_loja_rebirth()
                elif op == "4": self.menu_conquistas()
                elif op == "5": self.menu_rebirth()
                elif op == "0": break
            except KeyboardInterrupt: break
            except Exception as e:
                console.print(f"\n[bold red]Erro: {e}[/bold red]"); time.sleep(1.5)

if __name__ == "__main__": JogoEngine().iniciar()