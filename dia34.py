import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class SistemaNotas:
    def __init__(self):
        self._console = Console()

    def _solicitar_nota(self, mensagem):
        while True:
            try:
                nota = float(input(mensagem))
                if 0 <= nota <= 10:
                    return nota
                else:
                    self._console.print("[bold red]Nota inválida! Digite uma nota entre 0 e 10.[/bold red]")
            except ValueError:
                self._console.print("[bold red]Entrada inválida! Por favor, digite apenas números.[/bold red]")

    def _exibir_resultado(self, nota1, nota2, media):
        status = ""
        cor_status = ""
        final_msg = ""

        if media < 5.0:
            status = "REPROVADO"
            cor_status = "red"
            final_msg = f"Sua média foi de {media:.1f}. Você não atingiu a média. :cry:"
        elif media < 7.0:
            status = "RECUPERAÇÃO"
            cor_status = "yellow"
            final_msg = f"Sua média foi de {media:.1f}. Você está de recuperação. :thinking_face:"
        else:
            status = "APROVADO"
            cor_status = "green"
            final_msg = f"Sua média foi de {media:.1f}. Você passou! Parabéns! :party_popper:"

        tabela = Table(title="Boletim do Aluno", title_style="italic")
        tabela.add_column("Avaliação", justify="left", style="cyan")
        tabela.add_column("Nota", justify="right", style="white")

        tabela.add_row("Primeira Nota", f"{nota1:.1f}")
        tabela.add_row("Segunda Nota", f"{nota2:.1f}")
        tabela.add_row("Média Final", f"{media:.1f}", style="bold")
        tabela.add_row("Situação", f"[bold {cor_status}]{status}[/bold {cor_status}]")

        painel = Panel(
            tabela,
            title="[bold white]Resultado Final[/bold white]",
            expand=False
        )

        print()
        self._console.print(painel)
        self._console.print(f"\n[italic]{final_msg}[/italic]")
        print()

    def iniciar(self):
        self._console.print("[magenta]=== Sistema de Avaliação Escolar ===[/magenta]\n")
        while True:
            nota1 = self._solicitar_nota("Digite a primeira nota: ")
            nota2 = self._solicitar_nota("Digite a segunda nota: ")
            
            print()
            with self._console.status("[bold cyan]Calculando a média... :hourglass_flowing_sand:[/bold cyan]", spinner="arc"):
                time.sleep(1.2)
            
            media = (nota1 + nota2) / 2
            self._exibir_resultado(nota1, nota2, media)

            while True:
                try:
                    escolha = input("\nDeseja calcular a média de outro aluno? (s/n): ").lower()
                    if escolha in ['s', 'n']:
                        break
                    else:
                        self._console.print("[red]Entrada inválida! Digite 's' para sim ou 'n' para não.[/red]")
                except Exception:
                    self._console.print("[red]Erro inesperado. Tente novamente.[/red]")
            
            if escolha == 'n':
                break
            print()
            
        self._console.print("\n[magenta]Até logo! :wave:[/magenta]")

if __name__ == "__main__":
    try:
        sistema = SistemaNotas()
        sistema.iniciar()
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário. Até logo! :wave:")