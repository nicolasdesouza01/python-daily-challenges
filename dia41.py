import time
from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

class AlistamentoMilitar:
    def __init__(self):
        self._ano_atual = date.today().year
        self._ano_nascimento = None
        self._console = Console()

    def obter_ano_nascimento(self):
        while True:
            try:
                entrada = Prompt.ask("[bold cyan]Que ano você nasceu? (Apenas números)[/bold cyan]")
                ano = int(entrada)
                
                if ano < 1900 or ano > self._ano_atual:
                    self._console.print(
                        Panel(
                            "[bold red]:warning: Erro: Por favor, insira um ano válido entre 1900 e o ano atual.[/bold red]", 
                            title="Ano Inválido",
                            border_style="red"
                        )
                    )
                    continue
                    
                self._ano_nascimento = ano
                break
                
            except ValueError:
                self._console.print(
                    Panel(
                        "[bold red]:heavy_exclamation_mark: Erro: Entrada inválida! Digite apenas números inteiros.[/bold red]", 
                        title="Erro de Digitação",
                        border_style="red"
                    )
                )

    def processar_e_exibir(self):
        with self._console.status("[bold green]Consultando banco de dados militar...[/bold green]", spinner="dots"):
            time.sleep(1.5)

        idade = self._ano_atual - self._ano_nascimento
        
        if idade == 18:
            mensagem = "[bold green]:arrow_right: Você completa 18 anos este ano. Deve se alistar imediatamente![/bold green]"
            estilo = "green"
        elif idade < 18:
            anos_restantes = 18 - idade
            mensagem = f"[bold yellow]:clock1: Ainda faltam {anos_restantes} ano(s) para você se alistar![/bold yellow]"
            estilo = "yellow"
        else:
            anos_atraso = status_atraso = idade - 18
            mensagem = f"[bold red]:exclamation: Você já passou do período ou está {anos_atraso} ano(s) atrasado.[/bold red]"
            estilo = "red"

        self._console.print(
            Panel(
                f"[bold]Ano Atual:[/bold] {self._ano_atual}\n"
                f"[bold]Seu Ano de Nascimento:[/bold] {self._ano_nascimento}\n"
                f"[bold]Idade Calculada:[/bold] {idade} anos\n\n"
                f"{mensagem}",
                title="Resultado da Análise",
                border_style=estilo,
                expand=False
            )
        )

    def executar(self):
        self._console.print(
            Panel.fit(
                "[bold blue]Sistema de Consulta de Alistamento Militar[/bold blue]", 
                subtitle="Verificação de Status"
            )
        )
        
        while True:
            self.obter_ano_nascimento()
            self.processar_e_exibir()
            
            continuar = Prompt.ask(
                "\n[bold magenta]Deseja realizar outra consulta?[/bold magenta]",
                choices=["S", "N"],
                default="S"
            ).upper()
            
            if continuar == "N":
                self._console.print("[bold green]\nObrigado por usar o sistema! Encerrando... :wave:\n[/bold green]")
                break

if __name__ == "__main__":
    sistema = AlistamentoMilitar()
    sistema.executar()