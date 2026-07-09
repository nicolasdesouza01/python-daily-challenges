import hashlib
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class Jogador:
    def __init__(self, nome, gols):
        self._nome = nome
        self._gols = gols
        self._total = sum(gols)

    @property
    def nome(self):
        return self._nome

    @property
    def gols(self):
        return self._gols

    @property
    def total(self):
        return self._total


class SistemaTimes:
    def __init__(self):
        self._jogadores = []
        self._senha_hash = ""

    def cadastrar_senha(self, senha):
        self._senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    def validar_senha(self, senha):
        hash_verificacao = hashlib.sha256(senha.encode()).hexdigest()
        return hash_verificacao == self._senha_hash

    def adicionar_jogador(self, jogador):
        self._jogadores.append(jogador)

    def listar_jogadores(self):
        return self._jogadores


def executar_sistema():
    sistema = SistemaTimes()
    
    console.print(Panel.fit("[bold blue]:soccer_ball: SISTEMA DE GERENCIAMENTO DE JOGADORES :soccer_ball:[/bold blue]", style="blue"))
    
    console.print("\n[bold yellow]Configuração Inicial do Sistema[/bold yellow]")
    
    while True:
        senha_inicial = console.input("[bold cyan]Defina uma senha mestre para o sistema: [/bold cyan]").strip()
        if senha_inicial:
            break
        console.print("[bold red]:warning: A senha não pode ser vazia.[/bold red]\n")
        
    with console.status("[bold green]protegendo sistema... :lock:[/bold green]"):
        sistema.cadastrar_senha(senha_inicial)
        time.sleep(1)
        
    console.print("[bold green]:white_check_mark: Sistema configurado com sucesso![/bold green]\n")
    
    console.print(Panel("[bold yellow]:key: TELA DE LOGIN[/bold yellow]", expand=False))
    tentativas = 0
    
    while True:
        senha_tentativa = console.input("[bold cyan]Digite a senha para acessar: [/bold cyan]", password=True).strip()
        
        with console.status("[bold blue]Verificando credenciais... :hourglass_flowing_sand:[/bold blue]"):
            time.sleep(1)
            autenticado = sistema.validar_senha(senha_tentativa)
            
        if autenticado:
            console.print("[bold green]:white_check_mark: Acesso concedido! Bem-vindo ao sistema.[/bold green]\n")
            break
        else:
            tentativas += 1
            console.print(f"[bold red]:x: Senha incorreta! Tentativa {tentativas}. Tente novamente.[/bold red]\n")

    with console.status("[bold blue]Carregando banco de dados... :arrows_counterclockwise:[/bold blue]"):
        time.sleep(1)

    while True:
        console.print(Panel("[bold green]:clipboard: CADASTRO DE JOGADOR[/bold green]", expand=False))
        
        while True:
            nome = console.input("[bold white]Nome do jogador: [/bold white]").strip()
            if nome:
                break
            console.print("[bold red]:warning: O nome do jogador não pode ficar vazio.[/bold red]\n")
            
        while True:
            try:
                tot_partidas = int(console.input(f"[bold white]Quantas partidas {nome} jogou? [/bold white]"))
                if tot_partidas >= 0:
                    break
                console.print("[bold red]:warning: O número de partidas não pode ser negativo.[/bold red]\n")
            except ValueError:
                console.print("[bold red]:warning: ERRO! Digite um número inteiro válido.[/bold red]\n")
                
        gols = []
        for c in range(tot_partidas):
            while True:
                try:
                    g = int(console.input(f"   [bold white]Quantos gols na partida {c + 1}? [/bold white]"))
                    if g >= 0:
                        gols.append(g)
                        break
                    console.print("[bold red]:warning: O número de gols não pode ser negativo.[/bold red]\n")
                except ValueError:
                    console.print("[bold red]:warning: ERRO! Digite um número inteiro válido.[/bold red]\n")
                    
        novo_jogador = Jogador(nome, gols)
        sistema.adicionar_jogador(novo_jogador)
        
        while True:
            resp = console.input("\n[bold white]Quer continuar? [S/N]: [/bold white]").strip().upper()
            if resp in ("S", "N"):
                break
            console.print("[bold red]:warning: ERRO! Responda apenas S ou N.[/bold red]")
            
        if resp == "N":
            break

    with console.status("[bold magenta]Processando estatísticas gerais... :bar_chart:[/bold magenta]"):
        time.sleep(1.5)

    lista_jogadores = sistema.listar_jogadores()
    
    tabela = Table(title="[bold blue]:soccer_ball: RESUMO DO TIME :soccer_ball:[/bold blue]", title_style="bold blue")
    tabela.add_column("Cód", justify="center", style="cyan")
    tabela.add_column("Nome", justify="left", style="magenta")
    tabela.add_column("Gols por Partida", justify="center", style="green")
    tabela.add_column("Total de Gols", justify="center", style="bold yellow")
    
    for idx, jog in enumerate(lista_jogadores):
        tabela.add_row(str(idx), jog.nome, str(jog.gols), str(jog.total))
        
    console.print("\n")
    console.print(tabela)
    console.print("\n")

    while True:
        try:
            busca = int(console.input("[bold cyan]Mostrar dados de qual jogador? (999 para parar): [/bold cyan]"))
            
            if busca == 999:
                with console.status("[bold red]Encerrando o sistema... :wave:[/bold red]"):
                    time.sleep(1)
                break
                
            if busca < 0 or busca >= len(lista_jogadores):
                console.print(f"[bold red]:x: ERRO! Não existe jogador com código {busca}![/bold red]\n")
            else:
                jog_selecionado = lista_jogadores[busca]
                detalhes = f"[bold yellow]:bar_chart: LEVANTAMENTO DO JOGADOR {jog_selecionado.nome.upper()}:[/bold yellow]\n"
                for i, g in enumerate(jog_selecionado.gols):
                    detalhes += f"\n   -> No jogo [cyan]{i + 1}[/cyan] fez [green]{g}[/green] gols."
                
                console.print(Panel(detalhes, title="[bold green]Estatísticas Individuais[/bold green]", expand=False))
                console.print("\n")
        except ValueError:
            console.print("[bold red]:warning: ERRO! Digite um código numérico válido.[/bold red]\n")

    console.print(Panel.fit("[bold green]:sparkles: <<< VOLTE SEMPRE! >>> :sparkles:[/bold green]", style="green"))


if __name__ == "__main__":
    executar_sistema()