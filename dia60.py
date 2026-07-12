import time
from random import randint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class JogoAdivinhacao:

    def __init__(self):
        self._console = Console()
        self._computador = 0
        self._tentativas_restantes = 0
        self._palpites = 0
        self._pontuacao = 100
        self._limite_max = 10


    def _exibir_boas_vindas(self):
        self._console.clear()
        
        mensagem = (
            "Seja bem-vindo ao Jogo de Adivinhação! :brain:\n"
            "Eu sou seu computador e acabei de gerar um número secreto.\n"
            "Será que você consegue vencer a máquina?"
        )
        
        self._console.print(
            Panel(
                mensagem, 
                title="[bold cyan]Mente Eletrônica[/bold cyan]", 
                border_style="cyan",
                expand=False
            )
        )


    def _configurar_dificuldade(self):
        while True:
            self._console.print("\n[bold yellow]Escolha o nível de dificuldade:[/bold yellow]")
            self._console.print("[1] - Fácil (0 a 10) :seedling:")
            self._console.print("[2] - Médio (0 a 50) :fire:")
            self._console.print("[3] - Difícil (0 a 100) :zap:")
            
            try:
                opcao = int(self._console.input("\n[bold]Sua opção: [/bold]"))
                
                if opcao == 1:
                    self._limite_max = 10
                    self._tentativas_restantes = 5
                    break
                elif opcao == 2:
                    self._limite_max = 50
                    self._tentativas_restantes = 7
                    break
                elif opcao == 3:
                    self._limite_max = 100
                    self._tentativas_restantes = 10
                    break
                else:
                    self._console.print("[bold red]:warning: Opção inválida! Escolha 1, 2 ou 3.[/bold red]")
                    
            except ValueError:
                self._console.print("[bold red]:warning: Entrada inválida! Digite apenas o número da opção.[/bold red]")

        with self._console.status("[bold magenta]Sintonizando neurônios artificiais... Calculando número secreto...[/bold magenta]", spinner="aesthetic"):
            self._computador = randint(0, self._limite_max)
            time.sleep(2)


    def _exibir_status(self):
        tabela = Table(title="[bold]Painel de Controle[/bold]", show_header=True, header_style="bold magenta")
        
        tabela.add_column("Vidas :heart:", justify="center")
        tabela.add_column("Pontuação :star:", justify="center")
        tabela.add_column("Palpites Feitos :speech_balloon:", justify="center")
        
        tabela.add_row(
            f"[bold red]{self._tentativas_restantes}[/bold red]", 
            f"[bold yellow]{self._pontuacao}[/bold yellow]", 
            f"[bold cyan]{self._palpites}[/bold cyan]"
        )
        
        self._console.print(tabela)


    def _obter_palpite(self):
        while True:
            try:
                entrada = self._console.input(f"\n[bold green]Qual seu palpite (0 a {self._limite_max})? [/bold green]")
                palpite = int(entrada)
                
                if 0 <= palpite <= self._limite_max:
                    return palpite
                    
                self._console.print(f"[bold red]:warning: Erro: O número deve estar estritamente entre 0 e {self._limite_max}![/bold red]")
                
            except ValueError:
                self._console.print("[bold red]:warning: Erro: Entrada inválida! Por favor, digite um número inteiro válido.[/bold red]")


    def iniciar_jogo(self):
        self._exibir_boas_vindas()
        self._configurar_dificuldade()
        
        while True:
            self._exibir_status()
            palpite = self._obter_palpite()
            self._palpites += 1

            if palpite == self._computador:
                msg_vitoria = (
                    f":trophy: PARABÉNS! Você quebrou o sistema!\n"
                    f"O número correto era {self._computador}.\n"
                    f"Você precisou de {self._palpites} palpites e terminou com {self._pontuacao} pontos!"
                )
                self._console.print(Panel(msg_vitoria, title="[bold green]VITÓRIA![/bold green]", border_style="green"))
                break

            self._tentativas_restantes -= 1
            
            penalidade = max(5, abs(self._computador - palpite) // 2)
            self._pontuacao = max(0, self._pontuacao - penalidade)

            if self._tentativas_restantes == 0:
                msg_derrota = (
                    f":skull: GAME OVER! Suas vidas acabaram de esgotar.\n"
                    f"O núcleo do computador permaneceu intacto. O número era {self._computador}."
                )
                self._console.print(Panel(msg_derrota, title="[bold red]FIM DE JOGO[/bold red]", border_style="red"))
                break

            if self._computador > palpite:
                self._console.print("[bold cyan]:arrow_up_small: Um pouco MAIS!! Tente novamente.[/bold cyan]")
            else:
                self._console.print("[bold yellow]:arrow_down_small: Um pouco MENOS!! Tente novamente.[/bold yellow]")


if __name__ == "__main__":
    jogo = JogoAdivinhacao()
    jogo.iniciar_jogo()