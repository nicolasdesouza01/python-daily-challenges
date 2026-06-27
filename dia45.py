from random import randint
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

class Jokenpo:

    def __init__(self):
        self._itens = ('pedra', 'papel', 'tesoura')
        self._console = Console()

    def _exibir_menu(self):
        self._console.clear()
        
        tabela = Table(
            title=":joystick: JOKENPÔ :joystick:", 
            title_style="bold magenta", 
            show_header=True, 
            header_style="bold cyan"
        )
        
        tabela.add_column("Código", justify="center", style="bold yellow")
        tabela.add_column("Sua Opção", justify="left")
        
        tabela.add_row("0", "PEDRA :fist:")
        tabela.add_row("1", "PAPEL :scroll:")
        tabela.add_row("2", "TESOURA :scissors:")
        
        self._console.print(Panel(tabela, expand=False, border_style="blue"))

    def _obter_jogada_jogador(self):
        while True:
            try:
                jogada = Prompt.ask("\n[bold white]Qual sua jogada?[/bold white]")
                jogada_int = int(jogada)
                
                if jogada_int in (0, 1, 2):
                    return jogada_int
                    
                self._console.print("[bold red]Opção inválida! Escolha apenas entre 0, 1 ou 2.[/bold red]")
            except ValueError:
                self._console.print("[bold red]Entrada inválida! Por favor, digite um número inteiro.[/bold red]")

    def _executar_loading(self):
        self._console.print()
        
        with self._console.status("[bold yellow]JO...[/bold yellow]", spinner="dots"):
            sleep(1)
            
        with self._console.status("[bold orange3]KEN...[/bold orange3]", spinner="dots"):
            sleep(1)
            
        with self._console.status("[bold red]PO!!![/bold red]", spinner="dots"):
            sleep(0.6)
            
        self._console.print()

    def _processar_resultado(self, jogador, computador):
        self._executar_loading()
        
        grade_confronto = Table.grid(padding=2)
        grade_confronto.add_column(justify="center")
        grade_confronto.add_column(justify="center")
        grade_confronto.add_column(justify="center")
        
        grade_confronto.add_row(
            f"[bold cyan]Você escolheu:[/bold cyan]\n[bold white]{self._itens[jogador].upper()}[/bold white]",
            "[bold red]VS[/bold red]",
            f"[bold magenta]Computador escolheu:[/bold magenta]\n[bold white]{self._itens[computador].upper()}[/bold white]"
        )
        
        self._console.print(Panel(grade_confronto, title="[bold green]Duelo[/bold green]", expand=False, border_style="white"))
        
        if computador == 0: #COMPUTADOR JOGOU PEDRA
            if jogador == 0:
                self._console.print(Panel("[bold yellow]EMPATE! :expressionless:[/bold yellow]", border_style="yellow", expand=False))
            elif jogador == 1:
                self._console.print(Panel("[bold green]JOGADOR VENCE! :party_popper:[/bold green]", border_style="green", expand=False))
            elif jogador == 2:
                self._console.print(Panel("[bold red]COMPUTADOR VENCE! :robot:[/bold red]", border_style="red", expand=False))
            else:
                print ('JOGADA INVÁLIDA!')
        elif computador == 1: #COMPUTADOR JOGOU PAPEL
            if jogador == 0:
                self._console.print(Panel("[bold red]COMPUTADOR VENCE! :robot:[/bold red]", border_style="red", expand=False))
            elif jogador == 1:
                self._console.print(Panel("[bold yellow]EMPATE! :expressionless:[/bold yellow]", border_style="yellow", expand=False))
            elif jogador == 2:
                self._console.print(Panel("[bold green]JOGADOR VENCE! :party_popper:[/bold green]", border_style="green", expand=False))
            else:
                print ('JOGADA INVÁLIDA!')
        elif computador == 2: #COMPUTADOR JOGOU TESOURA
            if jogador == 0:
                self._console.print(Panel("[bold green]JOGADOR VENCEU! :party_popper:[/bold green]", border_style="green", expand=False))
            elif jogador == 1:
                self._console.print(Panel("[bold red]COMPUTADOR VENCEU! :robot:[/bold red]", border_style="red", expand=False))
            elif jogador == 2:
                self._console.print(Panel("[bold yellow]EMPATE! :expressionless:[/bold yellow]", border_style="yellow", expand=False))
            else:
                print ('JOGADA INVÁLIDA!')

    def jogar(self):
        while True:
            try:
                self._exibir_menu()
                
                computador = randint(0, 2)
                jogador = self._obter_jogada_jogador()
                
                self._processar_resultado(jogador, computador)
                
                resposta = Prompt.ask("\nQuer continuar jogando?", choices=["s", "n"], default="s")
                if resposta.lower() == 'n':
                    self._console.print("\n[bold magenta]Obrigado por jogar! Até a próxima! :wave:[/bold magenta]\n")
                    break
                    
            except KeyboardInterrupt:
                self._console.print("\n\n[bold red]Jogo interrompido de forma forçada. Até logo! :wave:[/bold red]\n")
                break


jogo = Jokenpo()
jogo.jogar()