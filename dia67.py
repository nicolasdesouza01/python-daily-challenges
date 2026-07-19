import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class Aluno:
    def __init__(self, nome, nota1, nota2, trabalho, aulas_totais, presencas):
        self._nome = nome
        self._nota1 = nota1
        self._nota2 = nota2
        self._trabalho = trabalho
        self._aulas_totais = aulas_totais
        self._presencas = presencas

    def _calcular_media(self):
        return (self._nota1 + self._nota2 + self._trabalho) / 3

    def _calcular_frequencia(self):
        if self._aulas_totais == 0:
            return 0.0
        return (self._presencas / self._aulas_totais) * 100

    def _obter_situacao(self):
        media = self._calcular_media()
        frequencia = self._calcular_frequencia()

        if frequencia < 75:
            return "Reprovado por Falta", "red"
        elif media >= 7.0:
            return "Aprovado", "green"
        elif 5.0 <= media < 7.0:
            return "Recuperação", "yellow"
        else:
            return "Reprovado por Nota", "red"

    def obter_dados(self):
        media = self._calcular_media()
        frequencia = self._calcular_frequencia()
        situacao, cor = self._obter_situacao()
        return {
            "nome": self._nome,
            "media": media,
            "frequencia": frequencia,
            "situacao": situacao,
            "cor": cor
        }


class Turma:
    def __init__(self):
        self._alunos = []

    def adicionar_aluno(self, aluno):
        self._alunos.append(aluno)

    def possui_alunos(self):
        return len(self._alunos) > 0

    def obter_estatisticas(self):
        if not self._alunos:
            return None

        total_alunos = len(self._alunos)
        soma_medias = sum(a.obter_dados()["media"] for a in self._alunos)
        media_geral = soma_medias / total_alunos

        aprovados = sum(1 for a in self._alunos if a.obter_dados()["situacao"] == "Aprovado")
        recuperacao = sum(1 for a in self._alunos if a.obter_dados()["situacao"] == "Recuperação")
        reprovados = total_alunos - aprovados - recuperacao

        return {
            "total": total_alunos,
            "media_geral": media_geral,
            "aprovados": aprovados,
            "recuperacao": recuperacao,
            "reprovados": reprovados
        }

    def gerar_tabela_alunos(self):
        tabela = Table(title=":graduation_cap: Diário de Classe - Registro de Alunos", header_style="bold magenta")
        tabela.add_column("Nome", style="cyan", justify="left")
        tabela.add_column("Média", justify="center")
        tabela.add_column("Frequência", justify="center")
        tabela.add_column("Situação", justify="center")

        for aluno in self._alunos:
            dados = aluno.obter_dados()
            tabela.add_row(
                dados["nome"],
                f"{dados['media']:.1f}",
                f"{dados['frequencia']:.1f}%",
                f"[{dados['cor']}]{dados['situacao']}[/{dados['cor']}]"
            )
        return tabela


def ler_float(console, mensagem, min_val=0.0, max_val=10.0):
    while True:
        try:
            valor = float(console.input(mensagem))
            if min_val <= valor <= max_val:
                return valor
            console.print(f"[bold red]:x: Erro: O valor deve estar entre {min_val} e {max_val}.[/bold red]")
        except ValueError:
            console.print("[bold red]:x: Erro: Entrada inválida! Digite apenas números inteiros ou decimais.[/bold red]")


def ler_int(console, mensagem, min_val=1):
    while True:
        try:
            valor = int(console.input(mensagem))
            if valor >= min_val:
                return valor
            console.print(f"[bold red]:x: Erro: O valor deve ser maior ou igual a {min_val}.[/bold red]")
        except ValueError:
            console.print("[bold red]:x: Erro: Entrada inválida! Digite apenas números inteiros.[/bold red]")


def ler_presencas(console, mensagem, max_aulas):
    while True:
        try:
            valor = int(console.input(mensagem))
            if 0 <= valor <= max_aulas:
                return valor
            console.print(f"[bold red]:x: Erro: Presenças não podem ser negativas ou maiores que o total de aulas ({max_aulas}).[/bold red]")
        except ValueError:
            console.print("[bold red]:x: Erro: Entrada inválida! Digite apenas números inteiros.[/bold red]")


def executar_sistema():
    console = Console()
    turma = Turma()

    console.clear()
    console.print(Panel.fit(
        "[bold cyan]:school: SISTEMA DE GESTÃO ACADÊMICA :school:[/bold cyan]\n"
        "[dim]Módulo de Gestão de Turma e Diário Escolar[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold yellow]:memo: CADASTRAR NOVO ALUNO[/bold yellow]")

        nome = console.input("[cyan]Nome do Aluno:[/cyan] ").strip()
        while not nome:
            console.print("[bold red]:x: Erro: O nome não pode ser vazio.[/bold red]")
            nome = console.input("[cyan]Nome do Aluno:[/cyan] ").strip()

        nota1 = ler_float(console, "[cyan]Nota da P1 (0 a 10):[/cyan] ")
        nota2 = ler_float(console, "[cyan]Nota da P2 (0 a 10):[/cyan] ")
        trabalho = ler_float(console, "[cyan]Nota do Trabalho (0 a 10):[/cyan] ")

        aulas_totais = ler_int(console, "[cyan]Total de Aulas dadas na matéria:[/cyan] ")
        presencas = ler_presencas(console, f"[cyan]Aulas frequentadas pelo aluno (max {aulas_totais}):[/cyan] ", aulas_totais)

        aluno = Aluno(nome, nota1, nota2, trabalho, aulas_totais, presencas)

        with console.status("[bold green]Processando e registrando dados...", spinner="dots"):
            time.sleep(1)
            turma.adicionar_aluno(aluno)

        console.print("[bold green]:white_check_mark: Aluno cadastrado com sucesso![/bold green]\n")

        opcao = console.input("[bold cyan]Deseja cadastrar outro aluno? (S/N):[/bold cyan] ").strip().upper()
        while opcao not in ["S", "N"]:
            console.print("[bold red]:x: Opção inválida! Digite apenas 'S' para sim ou 'N' para não.[/bold red]")
            opcao = console.input("[bold cyan]Deseja cadastrar outro aluno? (S/N):[/bold cyan] ").strip().upper()

        if opcao == "N":
            break

    if turma.possui_alunos():
        with console.status("[bold yellow]Gerando diário de classe e estatísticas...", spinner="bouncingBall"):
            time.sleep(1.5)

        console.clear()
        console.print(turma.gerar_tabela_alunos())

        estatisticas = turma.obter_estatisticas()

        resumo_texto = (
            f"[bold]Total de Alunos:[/bold] {estatisticas['total']}\n"
            f"[bold]Média Geral da Turma:[/bold] {estatisticas['media_geral']:.2f}\n\n"
            f"[green]:white_check_mark: Aprovados:[/green] {estatisticas['aprovados']}\n"
            f"[yellow]:warning: Recuperação:[/yellow] {estatisticas['recuperacao']}\n"
            f"[red]:x: Reprovados:[/red] {estatisticas['reprovados']}"
        )

        console.print("\n")
        console.print(Panel(
            resumo_texto,
            title=":bar_chart: Painel de Desempenho da Turma",
            border_style="yellow",
            expand=False
        ))

    console.print("\n[bold cyan]:wave: Programa finalizado. Até a próxima![/bold cyan]\n")


if __name__ == "__main__":
    executar_sistema()

# O código também pode ser melhorado com a adição de um banco de dados, ou por outro método de permanência da informação, mas para este exemplo e simplicidade não usei.