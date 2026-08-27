"""
Sistema Gerenciador de Rotina A/B Alternada via Paridade Temporal.

Implementa arquitetura POO para gerenciamento dinâmico, remoção e balanceamento de tarefas.
"""

import json
import sys
import time
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text


class Tarefa:
    """Representa uma unidade individual de trabalho na rotina."""

    def __init__(self, titulo: str, peso: int = 1, tipo_bloco: str = "Operacional", concluida: bool = False) -> None:
        """Inicializa a tarefa com título, peso, tipo de bloco e status."""
        self._titulo: str = titulo
        self._peso: int = max(1, min(5, peso))
        self._tipo_bloco: str = tipo_bloco
        self._concluida: bool = concluida

    @property
    def titulo(self) -> str:
        """Retorna o título da tarefa."""
        return self._titulo

    @property
    def peso(self) -> int:
        """Retorna o peso da tarefa."""
        return self._peso

    @property
    def tipo_bloco(self) -> str:
        """Retorna a classificação do bloco de trabalho."""
        return self._tipo_bloco

    @property
    def concluida(self) -> bool:
        """Retorna o status de conclusão da tarefa."""
        return self._concluida

    def alternar_status(self) -> None:
        """Inverte o estado de conclusão da tarefa (Toggle)."""
        self._concluida = not self._concluida

    def para_dicionario(self) -> Dict[str, object]:
        """Serializa os dados da tarefa em dicionário."""
        return {"titulo": self._titulo, "peso": self._peso, "tipo_bloco": self._tipo_bloco, "concluida": self._concluida}

    @classmethod
    def de_dicionario(cls, dados: Dict[str, object]) -> "Tarefa":
        """Reconstrói uma instância de Tarefa a partir de dicionário."""
        return cls(
            titulo=str(dados.get("titulo", "")),
            peso=int(dados.get("peso", 1)),
            tipo_bloco=str(dados.get("tipo_bloco", "Operacional")),
            concluida=bool(dados.get("concluida", False))
        )


class Rotina:
    """Classe base para agrupamento e gerenciamento de tarefas."""

    def __init__(self, nome: str, descricao: str) -> None:
        """Inicializa o contêiner da rotina."""
        self._nome: str = nome
        self._descricao: str = descricao
        self._tarefas: List[Tarefa] = []

    @property
    def nome(self) -> str:
        """Retorna o nome da rotina."""
        return self._nome

    @property
    def descricao(self) -> str:
        """Retorna a descrição funcional da rotina."""
        return self._descricao

    @property
    def tarefas(self) -> List[Tarefa]:
        """Retorna a lista de tarefas contidas."""
        return self._tarefas

    @property
    def progresso_percentual(self) -> float:
        """Calcula a taxa de conclusão ponderada por peso das tarefas."""
        if not self._tarefas:
            return 0.0
        peso_total = sum(t.peso for t in self._tarefas)
        peso_concluido = sum(t.peso for t in self._tarefas if t.concluida)
        return (peso_concluido / peso_total) * 100.0 if peso_total > 0 else 0.0

    def adicionar_tarefa(self, tarefa: Tarefa) -> None:
        """Insere uma nova tarefa na coleção da rotina."""
        self._tarefas.append(tarefa)

    def alternar_tarefa(self, indice: int) -> bool:
        """Alterna o estado de uma tarefa com base no seu índice numérico."""
        if 0 <= indice < len(self._tarefas):
            self._tarefas[indice].alternar_status()
            return True
        return False

    def remover_tarefa(self, indice: int) -> Optional[Tarefa]:
        """Remove uma tarefa da rotina com base no seu índice numérico."""
        return self._tarefas.pop(indice) if 0 <= indice < len(self._tarefas) else None

    def para_dicionario(self) -> Dict[str, object]:
        """Exporta o estado completo da rotina e suas tarefas."""
        return {"nome": self._nome, "descricao": self._descricao, "tarefas": [t.para_dicionario() for t in self._tarefas]}


class RotinaA(Rotina):
    """Especialização de Rotina para Ciclos Pares."""

    def __init__(self) -> None:
        """Inicializa o Ciclo Alpha sem tarefas pré-definidas."""
        super().__init__(nome="Ciclo Alpha (PAR)", descricao="Gerenciamento de bloco de tarefas para dias pares.")


class RotinaB(Rotina):
    """Especialização de Rotina para Ciclos Ímpares."""

    def __init__(self) -> None:
        """Inicializa o Ciclo Beta sem tarefas pré-definidas."""
        super().__init__(nome="Ciclo Beta (ÍMPAR)", descricao="Gerenciamento de bloco de tarefas para dias ímpares.")


class CalculadorParidade:
    """Utilitário matemático responsável por determinar a paridade temporal."""

    @staticmethod
    def obter_dia_do_ano(data_alvo: Optional[date] = None) -> int:
        """Calcula o dia numérico dentro do ano (1 a 366)."""
        return (data_alvo or date.today()).timetuple().tm_yday

    @staticmethod
    def obter_offset_ano(data_alvo: Optional[date] = None) -> int:
        """Gera offset compensatório para virada de anos."""
        return (data_alvo or date.today()).year - 2024

    @staticmethod
    def eh_dia_par(data_alvo: Optional[date] = None) -> bool:
        """Determina se a data informada resulta em um ciclo PAR via mod 2."""
        dia = CalculadorParidade.obter_dia_do_ano(data_alvo)
        offset = CalculadorParidade.obter_offset_ano(data_alvo)
        return ((dia + offset) % 2) == 0

    @staticmethod
    def obter_identificador_ciclo(data_alvo: Optional[date] = None) -> Tuple[str, str]:
        """Retorna o rótulo descritivo e a paridade do dia."""
        return ("PAR", "A") if CalculadorParidade.eh_dia_par(data_alvo) else ("ÍMPAR", "B")


class GerenciadorRotina:
    """Gerenciador central de persistência de dados, estatísticas e regra de negócio."""

    def __init__(self, caminho_arquivo: str = "dados_rotina_ab.json") -> None:
        """Inicializa o gerenciador e carrega as informações salvas."""
        self._caminho_arquivo: Path = Path(caminho_arquivo)
        self._historico: Dict[str, object] = {}
        self._rotina_hoje: Rotina = self._instanciar_rotina_do_dia()
        self.carregar_dados()

    def _instanciar_rotina_do_dia(self) -> Rotina:
        """Cria a rotina adequada para a data de hoje baseada em paridade."""
        _, tipo = CalculadorParidade.obter_identificador_ciclo()
        return RotinaA() if tipo == "A" else RotinaB()

    @property
    def rotina_hoje(self) -> Rotina:
        """Retorna a rotina ativa para a data atual."""
        return self._rotina_hoje

    def carregar_dados(self) -> None:
        """Carrega os dados persistidos em formato JSON no disco."""
        if not self._caminho_arquivo.exists():
            return
        try:
            with open(self._caminho_arquivo, "r", encoding="utf-8") as f:
                self._historico = json.load(f)
            chave_hoje = date.today().isoformat()
            if chave_hoje in self._historico:
                dados_hoje = self._historico[chave_hoje]
                self._rotina_hoje.tarefas.clear()
                for t_data in dados_hoje.get("tarefas", []):
                    self._rotina_hoje.adicionar_tarefa(Tarefa.de_dicionario(t_data))
        except (json.JSONDecodeError, OSError):
            self._historico = {}

    def salvar_dados(self) -> None:
        """Persiste o estado atual da rotina no arquivo JSON local."""
        try:
            self._historico[date.today().isoformat()] = self._rotina_hoje.para_dicionario()
            with open(self._caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(self._historico, f, ensure_ascii=False, indent=4)
        except OSError as err:
            raise RuntimeError(f"Erro ao salvar arquivo de dados: {err}") from err

    def calcular_estatisticas(self) -> Dict[str, object]:
        """Computa métricas globais de balanceamento A/B e constância."""
        conclusoes_a, conclusoes_b = 0, 0
        for reg in self._historico.values():
            nome = str(reg.get("nome", ""))
            concluidas = sum(1 for t in reg.get("tarefas", []) if t.get("concluida"))
            if "Alpha" in nome or "(PAR)" in nome:
                conclusoes_a += concluidas
            else:
                conclusoes_b += concluidas
        dif = abs(conclusoes_a - conclusoes_b)
        return {
            "total_dias_registrados": len(self._historico),
            "tarefas_concluidas_a": conclusoes_a,
            "tarefas_concluidas_b": conclusoes_b,
            "diferenca_balanceamento": dif,
            "equilibrado": dif <= 3
        }


class InterfaceCLI:
    """Camada de apresentação e interface de usuário no terminal via Rich."""

    def __init__(self) -> None:
        """Inicializa a interface e o console Rich."""
        self._console: Console = Console()
        self._gerenciador: GerenciadorRotina = GerenciadorRotina()

    def exibir_spinner(self, mensagem: str, duracao: float = 0.8) -> None:
        """Exibe uma animação de carregamento visual temporária."""
        with Progress(SpinnerColumn(), TextColumn("[bold cyan]{task.description}"), console=self._console, transient=True) as progress:
            progress.add_task(description=mensagem, total=None)
            time.sleep(duracao)

    def construir_tabela_tarefas(self) -> Table:
        """Gera uma tabela Rich com as tarefas ativas do dia."""
        rotina = self._gerenciador.rotina_hoje
        tabela = Table(title=f"📋 [bold yellow]{rotina.nome}[/bold yellow]", expand=True)
        tabela.add_column("Nº", justify="center", style="bold cyan", width=4)
        tabela.add_column("Status", justify="center", width=8)
        tabela.add_column("Descrição da Tarefa", style="white")
        tabela.add_column("Bloco", justify="center", style="magenta")
        tabela.add_column("Peso", justify="center", style="green")

        if not rotina.tarefas:
            tabela.add_row("-", "📭", "[italic dim]Nenhuma tarefa cadastrada para o ciclo de hoje.[/italic dim]", "-", "-")
            return tabela

        for idx, t in enumerate(rotina.tarefas, start=1):
            status = "✅ [green]FEITO[/green]" if t.concluida else "❌ [red]PENDENTE[/red]"
            tabela.add_row(str(idx), status, f"[strike]{t.titulo}[/strike]" if t.concluida else t.titulo, f"⚡ {t.tipo_bloco}", "★" * t.peso)
        return tabela

    def exibir_dashboard(self) -> None:
        """Desenha a tela principal com estatísticas e lista de afazeres."""
        self._console.clear()
        paridade, tipo_rotina = CalculadorParidade.obter_identificador_ciclo()
        dia_ano, data_formatada = CalculadorParidade.obter_dia_do_ano(), date.today().strftime("%d/%m/%Y")

        header = (
            f"🚀 [bold white]GERENCIADOR DE ROTINA A/B[/bold white] | [bold cyan]{data_formatada}[/bold cyan] (Dia {dia_ano} do Ano)\n"
            f"⚡ Paridade Temporal: [bold yellow]{paridade}[/bold yellow] (Modulo 2) | Rotina Ativa: [bold green]Ciclo {tipo_rotina}[/bold green]"
        )
        self._console.print(Panel(Text.from_markup(header, justify="center"), border_style="bright_blue", padding=(1, 2)))

        rotina = self._gerenciador.rotina_hoje
        self._console.print(f"📌 [italic]{rotina.descricao}[/italic]\n")
        self._console.print(self.construir_tabela_tarefas())

        prog = rotina.progresso_percentual
        cor = "green" if prog == 100 else "yellow" if prog > 0 else "red"
        barra = f"[{'=' * int(prog // 5)}{' ' * (20 - int(prog // 5))}]" if rotina.tarefas else "[ Sem Tarefas ]"
        self._console.print(f"\n📊 Progresso do Dia: [{cor}]{prog:.1f}%[/] {barra}\n")

    def adicionar_tarefa_menu(self) -> None:
        """Interface interativa para adicionar uma nova tarefa à rotina ativa."""
        self._console.print("\n[bold green]➕ Cadastrar Nova Tarefa[/bold green]")
        titulo = Prompt.ask("Descrição / Título da tarefa")
        if not titulo.strip():
            self._console.print("[bold red]⚠️ Título inválido. Operação cancelada.[/bold red]")
            time.sleep(1)
            return

        peso = IntPrompt.ask("Peso da tarefa (1 a 5)", default=1)
        tipo_bloco = Prompt.ask("Tipo de Bloco (ex: Foco Alto, Operacional, Estudo)", default="Operacional")

        self._gerenciador.rotina_hoje.adicionar_tarefa(Tarefa(titulo=titulo.strip(), peso=peso, tipo_bloco=tipo_bloco.strip()))
        self._gerenciador.salvar_dados()
        self.exibir_spinner("💾 Tarefa adicionada e salva com sucesso...", 0.6)

    def alternar_tarefa_menu(self) -> None:
        """Solicita o número da tarefa ao usuário e altera seu estado."""
        qtd = len(self._gerenciador.rotina_hoje.tarefas)
        if qtd == 0:
            self._console.print("[bold yellow]⚠️ Não há tarefas para alternar. Adicione uma tarefa primeiro![/bold yellow]")
            time.sleep(1.2)
            return

        entrada = Prompt.ask(f"Digite o número da tarefa para alternar (1-{qtd}) ou '0' para cancelar")
        try:
            opcao = int(entrada)
            if opcao == 0:
                return
            if 1 <= opcao <= qtd:
                self.exibir_spinner("🔄 Atualizando estado da tarefa...", 0.6)
                self._gerenciador.rotina_hoje.alternar_tarefa(opcao - 1)
                self._gerenciador.salvar_dados()
            else:
                self._console.print("[bold red]⚠️ Número fora do intervalo válido![/bold red]")
                time.sleep(1)
        except ValueError:
            self._console.print("[bold red]⚠️ Por favor, insira um número inteiro válido![/bold red]")
            time.sleep(1)

    def deletar_tarefa_menu(self) -> None:
        """Interface interativa para remover uma tarefa cadastrada na rotina ativa."""
        qtd = len(self._gerenciador.rotina_hoje.tarefas)
        if qtd == 0:
            self._console.print("[bold yellow]⚠️ Não há tarefas para deletar. Adicione uma tarefa primeiro![/bold yellow]")
            time.sleep(1.2)
            return

        entrada = Prompt.ask(f"Digite o número da tarefa a ser deletada (1-{qtd}) ou '0' para cancelar")
        try:
            opcao = int(entrada)
            if opcao == 0:
                return
            if 1 <= opcao <= qtd:
                tarefa_alvo = self._gerenciador.rotina_hoje.tarefas[opcao - 1]
                confirmacao = Prompt.ask(f"\nTem certeza que deseja deletar '[bold red]{tarefa_alvo.titulo}[/bold red]'?", choices=["s", "n"], default="n")
                if confirmacao.lower() == "s":
                    self._gerenciador.rotina_hoje.remover_tarefa(opcao - 1)
                    self._gerenciador.salvar_dados()
                    self.exibir_spinner("🗑️ Removendo tarefa e atualizando arquivo de dados...", 0.6)
                else:
                    self._console.print("[bold yellow]⚠️ Operação de remoção cancelada.[/bold yellow]")
                    time.sleep(1)
            else:
                self._console.print("[bold red]⚠️ Número fora do intervalo válido![/bold red]")
                time.sleep(1)
        except ValueError:
            self._console.print("[bold red]⚠️ Por favor, insira um número inteiro válido![/bold red]")
            time.sleep(1)

    def exibir_estatisticas_balanceamento(self) -> None:
        """Exibe o relatório resumido de balanceamento A/B no console."""
        self.exibir_spinner("📊 Calculando métricas de balanceamento A/B...", 0.6)
        stats = self._gerenciador.calcular_estatisticas()

        tabela = Table(title="⚖️ [bold cyan]Relatório de Balanceamento A/B[/bold cyan]")
        tabela.add_column("Métrica", style="bold")
        tabela.add_column("Valor", justify="center")
        tabela.add_row("Dias Registrados no Histórico", str(stats["total_dias_registrados"]))
        tabela.add_row("Tarefas Concluídas no Ciclo A (PAR)", str(stats["tarefas_concluidas_a"]))
        tabela.add_row("Tarefas Concluídas no Ciclo B (ÍMPAR)", str(stats["tarefas_concluidas_b"]))
        tabela.add_row("Diferença de Desempenho", f"{stats['diferenca_balanceamento']} tarefas")
        tabela.add_row("Status do Balanceamento", "[green]Perfeitamente Equilibrado 🎯[/green]" if stats["equilibrado"] else "[yellow]Atenção ao Desbalanceamento ⚠️[/yellow]")

        self._console.print(Panel(tabela, border_style="magenta"))
        Prompt.ask("\nPressione [bold cyan]Enter[/bold cyan] para voltar ao menu")

    def executar(self) -> None:
        """Loop principal de execução da interface interativa."""
        self.exibir_spinner("🐍 Inicializando Gerenciador de Rotina A/B...", 1.0)

        while True:
            try:
                self.exibir_dashboard()
                self._console.print("[bold cyan]Opções de Comando:[/bold cyan]")
                self._console.print(" [1] Alternar Status de uma Tarefa")
                self._console.print(" [2] Adicionar Nova Tarefa")
                self._console.print(" [3] Deletar Tarefa Cadastrada")
                self._console.print(" [4] Visualizar Estatísticas de Balanceamento A/B")
                self._console.print(" [0] Sair do Programa")

                opcao = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3", "4", "0"], default="1")

                if opcao == "1":
                    self.alternar_tarefa_menu()
                elif opcao == "2":
                    self.adicionar_tarefa_menu()
                elif opcao == "3":
                    self.deletar_tarefa_menu()
                elif opcao == "4":
                    self.exibir_estatisticas_balanceamento()
                elif opcao == "0":
                    self.exibir_spinner("💾 Salvando dados e encerrando...", 0.6)
                    self._console.print("\n👋 [bold green]Até logo! Mantenha a consistência nos ciclos![/bold green]\n")
                    break
            except KeyboardInterrupt:
                self._console.print("\n\n⚠️ [bold yellow]Interrupção manual detectada. Encerrando o sistema com segurança...[/bold yellow]\n")
                try:
                    self._gerenciador.salvar_dados()
                except Exception:
                    pass
                sys.exit(0)
            except Exception as err:
                self._console.print(f"\n[bold red]⚠️ Ocorreu um erro inesperado: {err}[/bold red]")
                Prompt.ask("\nPressione [bold cyan]Enter[/bold cyan] para continuar")


if __name__ == "__main__":
    app = InterfaceCLI()
    app.executar()