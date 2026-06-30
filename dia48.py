import time
from random import shuffle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class SorteadorProfissional:

    def __init__(self):
        self._console = Console()
        self._participantes = []
        self._ganhadores = {}


    def _validar_e_processar(self, entrada_usuarios):
        if not entrada_usuarios or entrada_usuarios.isspace():
            raise ValueError("A lista de alunos não pode estar vazia.")

        nomes_limpos = [nome.strip() for nome in entrada_usuarios.split(",") if nome.strip()]

        if len(nomes_limpos) < 3:
            raise ValueError("Para gerar um pódio completo, insira ao menos 3 alunos.")

        self._participantes = nomes_limpos


    def _definir_colocacoes(self):
        shuffle(self._participantes)

        self._ganhadores["1º Lugar"] = self._participantes[0]
        self._ganhadores["2º Lugar"] = self._participantes[1]
        self._ganhadores["3º Lugar"] = self._participantes[2]
        self._ganhadores["4º Lugar (Restantes)"] = self._participantes[3:]


    def _renderizar_painel_sucesso(self):
        tabela = Table(title=":sparkles: RESULTADO OFICIAL DO SORTEIO :sparkles:", show_header=True, header_style="bold violet")
        
        tabela.add_column("Posição", style="bold cyan", justify="center")
        tabela.add_column("Nome do Aluno", style="bold white")

        tabela.add_row(":trophy: 1º Colocado", self._ganhadores["1º Lugar"], style="gold1")
        tabela.add_row(":star: 2º Colocado", self._ganhadores["2º Lugar"], style="grey70")
        tabela.add_row(":gem: 3º Colocado", self._ganhadores["3º Lugar"], style="orange_red1")

        outros_alunos = self._ganhadores["4º Lugar (Restantes)"]
        lista_outros = ", ".join(outros_alunos) if outros_alunos else "Nenhum aluno restante"
        
        tabela.add_row(":scroll: 4º Lugar (Restantes)", lista_outros, style="deep_sky_blue1")

        self._console.print("\n")
        self._console.print(Panel(tabela, border_style="bold green", expand=False))
        self._console.print("\n")


    def iniciar_sistema(self):
        self._console.print(Panel(":rocket: SISTEMA DE SORTEIO :rocket:\nInsira os nomes separados por vírgula para iniciar.", border_style="cyan"))
        
        while True:
            try:
                self._console.print("\n")
                dados_input = input("Diga o nome dos alunos separados por vírgula: ")
                
                self._validar_e_processar(dados_input)
                
                self._console.print("\n")
                with self._console.status("[bold magenta]Embaralhando a urna eletrônica... :game_die:[/bold magenta]", spinner="aesthetic"):
                    time.sleep(3)
                
                self._definir_colocacoes()
                self._renderizar_painel_sucesso()
                break
                
            except ValueError as erro_validacao:
                self._console.print("\n")
                self._console.print(Panel(f"[bold red]Erro nos dados de entrada: {erro_validacao} :x:\nTente novamente.[/bold red]", title="[bold red]Aviso[/bold red]", border_style="red"))
            
            except KeyboardInterrupt:
                self._console.print("\n\n")
                self._console.print(Panel("[bold yellow]Operação cancelada de forma segura... :wave:[/bold yellow]", border_style="yellow"))
                self._console.print("\n")
                break
                
            except Exception as erro_inesperado:
                self._console.print("\n")
                self._console.print(Panel(f"[bold red]Ocorreu um imprevisto: {erro_inesperado} :boom:\nTente novamente.[/bold red]", title="[bold red]Erro Fatal[/bold red]", border_style="red"))


if __name__ == "__main__":
    sorteio = SorteadorProfissional()
    sorteio.iniciar_sistema()