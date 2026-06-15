from random import choice
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

console = Console()

class Aluno:
    def __init__(self, nome: str, sexo: str):
        if not nome.strip():
            raise ValueError("O nome do aluno não pode estar vazio.")
        if sexo.strip().upper() not in ["M", "F"]:
            raise ValueError("Sexo inválido! Digite apenas 'M' para Masculino ou 'F' para Feminino.")
        
        self._nome = nome.strip()
        self._sexo = sexo.strip().upper()

    @property
    def nome(self):
        return self._nome

    @property
    def artigo_definido(self):
        return "O aluno" if self._sexo == "M" else "A aluna"


class SorteadorAlunos:
    def __init__(self):
        self._alunos = []

    def adicionar_aluno(self, aluno: Aluno):
        self._alunos.append(aluno)

    def sortear_escolhido(self):
        if not self._alunos:
            raise ValueError("Nenhum aluno foi cadastrado para realizar o sorteio.")
        return choice(self._alunos)

    @property
    def total_alunos(self):
        return len(self._alunos)


def executar_sistema():
    sorteador = SorteadorAlunos()
    
    console.print(
        Panel(
            Align.center("[bold cyan]:mortar_board: GESTOR DE SALA DE AULA :mortar_board:[/bold cyan]"),
            subtitle="[italic]Cadastro Dinâmico com Filtro de Gênero[/italic]",
            expand=False
        )
    )
    
    console.print("[bold white]Digite [red]'sair'[/red] no nome do aluno para encerrar o cadastro e realizar o sorteio.[/bold white]\n")
    
    while True:
        try:
            nome = Prompt.ask("[bold yellow]Nome do aluno(a)[/bold yellow]")
            
            if nome.strip().lower() == "sair":
                if sorteador.total_alunos < 2:
                    console.print("[bold red]:warning: Adicione pelo menos 2 alunos para fazer um sorteio justo![/bold red]\n")
                    continue
                break
                
            sexo = Prompt.ask("[bold yellow]Gênero [M/F][/bold yellow]")
            
            novo_aluno = Aluno(nome, sexo)
            sorteador.adicionar_aluno(novo_aluno)
            
            console.print(f"[green]:white_check_mark: {novo_aluno.artigo_definido} [bold]{novo_aluno.nome}[/bold] foi adicionado(a) com sucesso![/green]\n")
            
        except ValueError as erro:
            console.print(f"[bold red]:warning: Erro de Validação: {erro}[/bold red]\n")
        except Exception:
            console.print("[bold red]:warning: Ocorreu um problema inesperado ao processar a entrada.[/bold red]\n")

    console.print("\n")
    
    with console.status("[bold magenta]Embaralhando a urna eletrônica... :game_die:[/bold magenta]", spinner="aesthetic"):
        sleep(2.5)
        
    try:
        escolhido = sorteador.sortear_escolhido()
        
        resultado_texto = f"[bold green]:sparkles: {escolhido.artigo_definido} sorteado(a) para a atividade é: [yellow]{escolhido.nome}[/yellow]! :sparkles:[/bold green]"
        
        console.print(
            Align.center(
                Panel(
                    resultado_texto,
                    border_style="green",
                    expand=False
                )
            )
        )
    except ValueError as erro:
        console.print(f"[bold red]:warning: Erro no sorteio: {erro}[/bold red]")
    except Exception:
        console.print("[bold red]:warning: Ocorreu um erro crítico ao sortear o aluno.[/bold red]")


if __name__ == "__main__":
    executar_sistema()
