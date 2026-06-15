import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt


class Aluno:

    def __init__(self, nome: str, nota1: float, nota2: float):
        self._nome = nome
        self._nota1 = nota1
        self._nota2 = nota2

    @property
    def nome(self):
        return self._nome

    @property
    def nota1(self):
        return self._nota1

    @property
    def nota2(self):
        return self._nota2

    @property
    def media(self):
        return (self._nota1 + self._nota2) / 2


class GerenciadorEscolar:

    def __init__(self):
        self._alunos = []
        self._console = Console()

    def exibir_carregamento(self, mensagem_status: str):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progresso:
            progresso.add_task(description=mensagem_status, total=None)
            time.sleep(1.2)

    def coletar_nota(self, ordem_nota: str) -> float:
        while True:
            try:
                entrada = Prompt.ask(f"[bold white]{ordem_nota} Nota[/]")
                nota = float(entrada)
                
                if not (0 <= nota <= 10):
                    raise ValueError("A nota precisa estar contida no intervalo entre 0 e 10.")
                    
                return nota
                
            except ValueError as erro:
                if "could not convert string to float" in str(erro):
                    self._console.print("[bold red]Erro de Entrada: Digite apenas números válidos, utilizando ponto para decimais.[/]")
                else:
                    self._console.print(f"[bold red]Erro de Validação: {erro}[/]")

    def cadastrar_alunos(self):
        self._console.print(Panel("[bold magenta]Fase de Cadastro de Alunos[/]", border_style="magenta", expand=False))
        
        while True:
            try:
                nome = Prompt.ask("\n[bold white]Nome do Aluno[/]")
                
                if not nome.strip():
                    raise ValueError("O nome do aluno não pode ser composto apenas por espaços vazios.")
                
                nota1 = self.coletar_nota("Primeira")
                nota2 = self.coletar_nota("Segunda")
                
                novo_aluno = Aluno(nome, nota1, nota2)
                self._alunos.append(novo_aluno)
                
                self.exibir_carregamento("[yellow]Registrando informações no banco de dados... :floppy_disk:[/]")
                self._console.print("[bold green]:white_check_mark: Aluno cadastrado com absoluto sucesso![/]")
                
                continuar = str(input("\nDeseja inserir mais um aluno? [S/N]")).lower()
                if continuar == "n":
                    break
                    
            except ValueError as erro_nome:
                self._console.print(f"[bold red]Erro no Nome: {erro_nome}[/]")
            except Exception as erro_sistema:
                self._console.print(f"[bold red]Falha inesperada no cadastro: {erro_sistema}[/]")

    def exibir_boletim_geral(self):
        self.exibir_carregamento("[cyan]Estruturando e calculando médias do boletim... :bar_chart:[/]")
        
        if not self._alunos:
            self._console.print(Panel("[bold red]:warning: Nenhum registro localizado no sistema escolar.[/]", border_style="red"))
            return

        tabela = Table(title="[bold cyan]BOLETIM GERAL DA TURMA", show_header=True, header_style="bold blue")
        tabela.add_column("Índice", justify="center", style="bold yellow")
        tabela.add_column("Nome do Aluno", justify="left", style="green")
        tabela.add_column("Média Final", justify="center", style="bold white")

        for posicao, aluno in enumerate(self._alunos):
            tabela.add_row(str(posicao), aluno.nome, f"{aluno.media:.2f}")

        self._console.print(tabela)

    def gerenciar_consultas(self):
        if not self._alunos:
            return

        while True:
            try:
                escolha = Prompt.ask("\n[bold white]Digite o índice do aluno para ver as notas individuais (ou 999 para encerrar)[/]")
                
                try:
                    indice = int(escolha)
                except ValueError:
                    raise ValueError("A entrada fornecida deve ser um número inteiro correspondente ao índice.")

                if indice == 999:
                    self.exibir_carregamento("[magenta]Desconectando do sistema escolar... :wave:[/]")
                    break

                if not (0 <= indice < len(self._alunos)):
                    raise IndexError(f"O índice {indice} não corresponde a nenhum aluno listado na tabela.")

                aluno_selecionado = self._alunos[indice]
                
                self.exibir_carregamento(f"[blue]Puxando histórico de {aluno_selecionado.nome}... :mag:[/]")
                
                bloco_notas = (
                    f"[bold]Nome do Universitário:[/] {aluno_selecionado.nome}\n\n"
                    f"[bold]Avaliação Avaliativa 1:[/] [yellow]{aluno_selecionado.nota1:.1f}[/]\n"
                    f"[bold]Avaliação Avaliativa 2:[/] [yellow]{aluno_selecionado.nota2:.1f}[/]\n"
                    f"[bold]Resultado da Média:[/] [green]{aluno_selecionado.media:.1f}[/]"
                )
                
                self._console.print(Panel(bloco_notas, title=f":mortar_board: Histórico Acadêmico", border_style="green", expand=False))

            except ValueError as erro_entrada:
                self._console.print(f"[bold red]Erro de Formato: {erro_entrada}[/]")
            except IndexError as erro_limite:
                self._console.print(f"[bold red]Erro de Escopo: {erro_limite}[/]")
            except Exception as erro_critico:
                self._console.print(f"[bold red]Instabilidade detectada: {erro_critico}[/]")

    def iniciar_sistema(self):
        self._console.print(Panel("[bold green]:rocket: AMBIENTE DE GESTÃO ACADÊMICA :rocket:[/]", border_style="green", expand=False))
        self.cadastrar_alunos()
        self.exibir_boletim_geral()
        self.gerenciar_consultas()
        self._console.print(Panel("[bold yellow]:sparkles: Processos finalizados com segurança. Bons estudos! :sparkles:[/]", border_style="yellow", expand=False))


if __name__ == "__main__":
    sistema = GerenciadorEscolar()
    sistema.iniciar_sistema()