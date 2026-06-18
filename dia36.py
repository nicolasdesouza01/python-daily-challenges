import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class AnalisadorNotas:

    def __init__(self):
        self._notas = []
        self._dados = {}
        self._console = Console()

    def armazenar_nota(self, nota):
        self._notas.append(nota)

    def _analisar(self, sit=True):
        if not self._notas:
            raise ValueError("O sistema não pode realizar cálculos sem notas registradas.")

        self._dados['total'] = len(self._notas)
        self._dados['maior'] = max(self._notas)
        self._dados['menor'] = min(self._notas)
        
        media = sum(self._notas) / len(self._notas)
        self._dados['média'] = round(media, 2)

        if sit:
            if media >= 7:
                self._dados['situação'] = 'BOA!'
            elif media >= 5:
                self._dados['situação'] = 'RAZOÁVEL'
            else:
                self._dados['situação'] = 'RUIM'

    def exibir_interface(self):
        try:
            self._console.print("")
            with self._console.status("[bold yellow]Gerando relatório final... :hourglass_flowing_sand:", spinner="dots"):
                time.sleep(1.8)
                self._analisar(sit=True)

            tabela = Table(title="Relatório de Desempenho Acadêmico", title_style="bold cyan", show_lines=True)
            tabela.add_column("Métrica", justify="left", style="bold white")
            tabela.add_column("Resultado", justify="center", style="bold green")

            for chave, valor in self._dados.items():
                tabela.add_row(chave.upper(), str(valor))

            painel = Panel(tabela, border_style="green", title=":white_check_mark: Análise Concluída", expand=False)
            self._console.print(painel)

        except Exception as erro_sistema:
            painel_erro = Panel(f"[bold red]Erro crítico no processamento:[/bold red] {erro_sistema}", title=":x: Falha", border_style="red")
            self._console.print(painel_erro)


def iniciar_sistema():
    console = Console()
    analisador = AnalisadorNotas()

    console.print(Panel("[bold magenta]Sistema Interativo de Notas de Alunos[/bold magenta]", border_style="magenta", expand=False))

    while True:
        try:
            print("")
            entrada = input("Digite uma nota (0 a 10): ").strip()

            nota = float(entrada)
            if not (0 <= nota <= 10):
                console.print("[bold red]:x: Erro: A nota deve estar obrigatoriamente entre 0 e 10.[/bold red]")
                continue

            analisador.armazenar_nota(nota)
            console.print("[bold green]:white_check_mark: Nota adicionada com sucesso![/bold green]")

            print("")
            resposta = input("Deseja adicionar mais uma nota? [S/N]: ").strip().upper()
            
            if resposta == 'N':
                break
            elif resposta != 'S':
                console.print("[bold yellow]:warning: Comando inválido. Retornando ao menu de inserção.[/bold yellow]")

        except ValueError:
            console.print("[bold red]:x: Erro: Entrada inválida! Digite apenas números.[/bold red]")
        except Exception as erro_inesperado:
            console.print(f"[bold red]:x: Ocorreu um comportamento inesperado: {erro_inesperado}[/bold red]")

    analisador.exibir_interface()


iniciar_sistema()