from __future__ import annotations

import sys
from datetime import datetime
from typing import Dict, List, Optional
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text


class Partida:
    """Representa os dados de desempenho de um atleta em uma partida específica.

    Attributes:
        _data (str): Data de realização do jogo no formato DD/MM/AAAA.
        _oponente (str): Nome da equipe adversária.
        _gols (int): Quantidade de gols marcados pelo atleta.
        _assistencias (int): Quantidade de passes para gol concedidos.
        _minutos_jogados (int): Tempo em minutos que o atleta esteve em campo.
        _cartao_amarelo (bool): Indica se o atleta recebeu cartão amarelo.
        _cartao_vermelho (bool): Indica se o atleta recebeu cartão vermelho.
    """

    def __init__(
        self,
        data: str,
        oponente: str,
        gols: int,
        assistencias: int,
        minutos_jogados: int,
        cartao_amarelo: bool = False,
        cartao_vermelho: bool = False,
    ) -> None:
        """Inicializa um novo registro de partida com suas métricas individuais.

        Args:
            data (str): Data do jogo.
            oponente (str): Nome do time adversário.
            gols (int): Gols marcados.
            assistencias (int): Assistências realizadas.
            minutos_jogados (int): Minutos em campo.
            cartao_amarelo (bool, optional): Cartão amarelo. Defaults to False.
            cartao_vermelho (bool, optional): Cartão vermelho. Defaults to False.
        """
        self._data: str = data
        self._oponente: str = oponente
        self._gols: int = max(0, gols)
        self._assistencias: int = max(0, assistencias)
        self._minutos_jogados: int = max(0, minutos_jogados)
        self._cartao_amarelo: bool = cartao_amarelo
        self._cartao_vermelho: bool = cartao_vermelho

    @property
    def data(self) -> str:
        """Retorna a data da partida."""
        return self._data

    @property
    def oponente(self) -> str:
        """Retorna o nome do time oponente."""
        return self._oponente

    @property
    def gols(self) -> int:
        """Retorna a quantidade de gols na partida."""
        return self._gols

    @property
    def assistencias(self) -> int:
        """Retorna a quantidade de assistências na partida."""
        return self._assistencias

    @property
    def minutos_jogados(self) -> int:
        """Retorna o tempo jogado em minutos."""
        return self._minutos_jogados

    @property
    def cartao_amarelo(self) -> bool:
        """Retorna se o jogador recebeu cartão amarelo."""
        return self._cartao_amarelo

    @property
    def cartao_vermelho(self) -> bool:
        """Retorna se o jogador recebeu cartão vermelho."""
        return self._cartao_vermelho


class Jogador:
    """Representa o perfil do atleta, seu histórico de partidas e cálculo de estatísticas.

    Attributes:
        _codigo (int): Identificador único do jogador.
        _nome (str): Nome completo ou apelido do atleta.
        _posicao (str): Posição tática em campo.
        _historico (List[Partida]): Lista com o registro de todas as partidas jogadas.
    """

    def __init__(self, codigo: int, nome: str, posicao: str) -> None:
        """Inicializa um novo atleta na plataforma.

        Args:
            codigo (int): Código identificador.
            nome (str): Nome do jogador.
            posicao (str): Posição principal.
        """
        self._codigo: int = codigo
        self._nome: str = nome
        self._posicao: str = posicao
        self._historico: List[Partida] = []

    @property
    def codigo(self) -> int:
        """Retorna o código do atleta."""
        return self._codigo

    @property
    def nome(self) -> str:
        """Retorna o nome do atleta."""
        return self._nome

    @property
    def posicao(self) -> str:
        """Retorna a posição tática do atleta."""
        return self._posicao

    @property
    def historico(self) -> List[Partida]:
        """Retorna uma cópia da lista de partidas do jogador."""
        return self._historico.copy()

    @property
    def total_jogos(self) -> int:
        """Calcula o total de partidas disputadas."""
        return len(self._historico)

    @property
    def total_gols(self) -> int:
        """Calcula o somatório total de gols marcados."""
        return sum(partida.gols for partida in self._historico)

    @property
    def total_assistencias(self) -> int:
        """Calcula o somatório total de assistências."""
        return sum(partida.assistencias for partida in self._historico)

    @property
    def participacoes_diretas(self) -> int:
        """Calcula a soma de gols e assistências."""
        return self.total_gols + self.total_assistencias

    @property
    def media_gols(self) -> float:
        """Calcula a média de gols por partida."""
        if self.total_jogos == 0:
            return 0.0
        return self.total_gols / self.total_jogos

    @property
    def pontuacao_overall(self) -> int:
        """Calcula um índice de desempenho dinâmico (Overall 0-99) baseado em produtividade.

        Returns:
            int: Pontuação de desempenho calculada para a temporada.
        """
        if self.total_jogos == 0:
            return 50

        base: float = 60.0
        bonus_gols: float = self.total_gols * 3.5
        bonus_assistencias: float = self.total_assistencias * 2.0
        fator_consistencia: float = min(self.total_jogos * 1.2, 15.0)

        calculado: float = base + (bonus_gols + bonus_assistencias) / self.total_jogos * 5 + fator_consistencia
        return min(99, max(40, int(calculado)))

    def adicionar_partida(self, partida: Partida) -> None:
        """Registra uma nova partida no histórico do atleta.

        Args:
            partida (Partida): Instância da partida realizada.
        """
        self._historico.append(partida)


class GestorLiga:
    """Gerencia o cadastro de atletas, ingestão de partidas e geração de estatísticas globais.

    Attributes:
        _nome_liga (str): Nome da liga ou escolinha.
        _jogadores (Dict[int, Jogador]): Mapeamento de código para instância de Jogador.
        _proximo_codigo (int): Contador para auto-incremento de código do jogador.
    """

    def __init__(self, nome_liga: str) -> None:
        """Inicializa a infraestrutura de gerenciamento da liga.

        Args:
            nome_liga (str): Nome identificador da organização.
        """
        self._nome_liga: str = nome_liga
        self._jogadores: Dict[int, Jogador] = {}
        self._proximo_codigo: int = 101

    @property
    def nome_liga(self) -> str:
        """Retorna o nome da liga."""
        return self._nome_liga

    @property
    def jogadores(self) -> List[Jogador]:
        """Retorna a lista de todos os jogadores cadastrados."""
        return list(self._jogadores.values())

    def cadastrar_jogador(self, nome: str, posicao: str) -> Jogador:
        """Cria e armazena um novo jogador no sistema.

        Args:
            nome (str): Nome do atleta.
            posicao (str): Posição principal.

        Returns:
            Jogador: Instância do jogador criado.
        """
        atleta = Jogador(self._proximo_codigo, nome, posicao)
        self._jogadores[self._proximo_codigo] = atleta
        self._proximo_codigo += 1
        return atleta

    def buscar_jogador(self, codigo: int) -> Optional[Jogador]:
        """Obtém a referência de um atleta pelo seu código identificador.

        Args:
            codigo (int): Código do jogador.

        Returns:
            Optional[Jogador]: Atleta encontrado ou None.
        """
        return self._jogadores.get(codigo)

    def obter_artilheiro(self) -> Optional[Jogador]:
        """Encontra o atleta com maior número de gols na temporada.

        Returns:
            Optional[Jogador]: O maior artilheiro ou None se não houver jogadores.
        """
        if not self._jogadores:
            return None
        return max(self._jogadores.values(), key=lambda j: j.total_gols)


class SportsTechConsole:
    """Interface gráfica em terminal (CLI) usando a biblioteca Rich para interação com o usuário.

    Attributes:
        _console (Console): Instância principal do console Rich.
        _gestor (GestorLiga): Motor de regras de negócio da liga.
    """

    def __init__(self) -> None:
        """Inicializa o terminal estilizado e o gestor da liga."""
        self._console: Console = Console()
        self._gestor: GestorLiga = GestorLiga("Liga Amadora SportsTech")

    def executar(self) -> None:
        """Inicia o loop principal de eventos da interface CLI com tratamento de exceções."""
        try:
            while True:
                self._exibir_cabecalho()
                self._exibir_menu()
                opcao = Prompt.ask(
                    "Selecione uma opção",
                    choices=["1", "2", "3", "4", "5", "0"],
                    default="0",
                )

                if opcao == "1":
                    self._menu_cadastrar_jogador()
                elif opcao == "2":
                    self._menu_registrar_partida()
                elif opcao == "3":
                    self._menu_listar_jogadores()
                elif opcao == "4":
                    self._menu_passaporte_atleta()
                elif opcao == "5":
                    self._menu_leaderboard()
                elif opcao == "0":
                    self._console.print(
                        Panel("[bold green]🚀 Encerrando plataforma... Até logo![/bold green]", border_style="green")
                    )
                    break
        except KeyboardInterrupt:
            self._console.print("\n[bold yellow]⚠️ Operação interrompida pelo usuário. Encerrando de forma segura...[/bold yellow]")
            sys.exit(0)
        except Exception as erro:
            self._console.print(f"\n[bold red]❌ Erro inesperado no sistema: {erro}[/bold red]")

    def _exibir_cabecalho(self) -> None:
        """Renderiza o painel superior da aplicação."""
        self._console.clear()
        titulo = Text("⚽ PLATAFORMA SPORTSTECH - GESTÃO DE PERFORMANCE", style="bold white on blue", justify="center")
        self._console.print(Panel(titulo, border_style="blue"))

    def _exibir_menu(self) -> None:
        """Exibe as opções principais de navegação."""
        tabela = Table(show_header=False, box=None, expand=True)
        tabela.add_row("[bold cyan][1][/bold cyan] 👤 Cadastrar Novo Atleta")
        tabela.add_row("[bold cyan][2][/bold cyan] 📊 Registrar Dados de Partida")
        tabela.add_row("[bold cyan][3][/bold cyan] 📋 Listar Elenco e Status")
        tabela.add_row("[bold cyan][4][/bold cyan] 🪪 Passaporte do Atleta (FIFA Card)")
        tabela.add_row("[bold cyan][5][/bold cyan] 🏆 Leaderboard e Artilharia")
        tabela.add_row("[bold red][0][/bold red] 🚪 Sair do Sistema")
        self._console.print(Panel(tabela, title="[bold yellow]Menu Principal[/bold yellow]", border_style="yellow"))

    def _menu_cadastrar_jogador(self) -> None:
        """Interage com o usuário para obter dados e efetuar o cadastro de um atleta."""
        self._console.print("\n[bold green]➕ Cadastrar Novo Atleta[/bold green]")
        nome = Prompt.ask("Nome do atleta").strip()
        if not nome:
            self._console.print("[red]ERRO: O nome não pode estar em branco.[/red]")
            Prompt.ask("\nPressione ENTER para continuar")
            return

        posicao = Prompt.ask(
            "Posição principal",
            choices=["Ataque", "Meio-Campo", "Defesa", "Goleiro"],
            default="Ataque",
        )

        atleta = self._gestor.cadastrar_jogador(nome, posicao)
        self._console.print(
            f"\n[bold green]✅ Atleta {atleta.nome} cadastrado com sucesso! Código ID: [bold yellow]{atleta.codigo}[/bold yellow][/bold green]"
        )
        Prompt.ask("\nPressione ENTER para continuar")

    def _menu_registrar_partida(self) -> None:
        """Gerencia a entrada de dados de uma partida para um jogador específico."""
        self._console.print("\n[bold green]📊 Registrar Partida[/bold green]")
        if not self._gestor.jogadores:
            self._console.print("[yellow]⚠️ Nenhum atleta cadastrado no sistema.[/yellow]")
            Prompt.ask("\nPressione ENTER para continuar")
            return

        try:
            codigo = IntPrompt.ask("Código ID do atleta")
            atleta = self._gestor.buscar_jogador(codigo)

            if not atleta:
                self._console.print(f"[bold red]❌ Atleta com código {codigo} não encontrado![/bold red]")
                Prompt.ask("\nPressione ENTER para continuar")
                return

            self._console.print(f"\n[bold cyan]Atleta Selecionado: {atleta.nome} ({atleta.posicao})[/bold cyan]")
            oponente = Prompt.ask("Nome do time adversário").strip()
            gols = IntPrompt.ask("Gols marcados pelo atleta", default=0)
            assistencias = IntPrompt.ask("Assistências realizadas", default=0)
            minutos = IntPrompt.ask("Minutos em campo", default=90)
            amarelo = Confirm.ask("Recebeu cartão amarelo?", default=False)
            vermelho = Confirm.ask("Recebeu cartão vermelho?", default=False)

            data_atual = datetime.now().strftime("%d/%m/%Y")
            partida = Partida(
                data=data_atual,
                oponente=oponente,
                gols=gols,
                assistencias=assistencias,
                minutos_jogados=minutos,
                cartao_amarelo=amarelo,
                cartao_vermelho=vermelho,
            )

            atleta.adicionar_partida(partida)
            self._console.print(f"\n[bold green]✅ Partida contra {oponente} inserida no histórico de {atleta.nome}![/bold green]")
        except ValueError:
            self._console.print("[bold red]❌ Erro: Por favor insira valores numéricos válidos.[/bold red]")

        Prompt.ask("\nPressione ENTER para continuar")

    def _menu_listar_jogadores(self) -> None:
        """Exibe uma tabela consolidada com todos os atletas e suas principais métricas acumuladas."""
        self._console.print("\n[bold green]📋 Elenco da Temporada[/bold green]")
        atleta_list = self._gestor.jogadores

        if not atleta_list:
            self._console.print("[yellow]⚠️ Nenhum atleta cadastrado.[/yellow]")
            Prompt.ask("\nPressione ENTER para continuar")
            return

        tabela = Table(title="Desempenho Geral do Elenco", border_style="cyan")
        tabela.add_column("ID", justify="center", style="yellow")
        tabela.add_column("Nome", style="bold white")
        tabela.add_column("Posição", justify="center")
        tabela.add_column("Jogos", justify="right")
        tabela.add_column("Gols", justify="right", style="green")
        tabela.add_column("Assist.", justify="right", style="blue")
        tabela.add_column("Média Gols", justify="right")
        tabela.add_column("OVR", justify="center", style="bold magenta")

        for atleta in atleta_list:
            tabela.add_row(
                str(atleta.codigo),
                atleta.nome,
                atleta.posicao,
                str(atleta.total_jogos),
                str(atleta.total_gols),
                str(atleta.total_assistencias),
                f"{atleta.media_gols:.2f}",
                str(atleta.pontuacao_overall),
            )

        self._console.print(tabela)
        Prompt.ask("\nPressione ENTER para continuar")

    def _menu_passaporte_atleta(self) -> None:
        """Gera um painel estilizado (estilo Card de videogame) com os dados individuais do atleta."""
        self._console.print("\n[bold green]🪪 Passaporte do Atleta[/bold green]")
        if not self._gestor.jogadores:
            self._console.print("[yellow]⚠️ Nenhum atleta registrado.[/yellow]")
            Prompt.ask("\nPressione ENTER para continuar")
            return

        try:
            codigo = IntPrompt.ask("Digite o Código ID do atleta para ver o Passaporte")
            atleta = self._gestor.buscar_jogador(codigo)

            if not atleta:
                self._console.print(f"[bold red]❌ Atleta {codigo} não encontrado![/bold red]")
                Prompt.ask("\nPressione ENTER para continuar")
                return

            conteudo = Text()
            conteudo.append(f"ATLETA: {atleta.nome.upper()}\n", style="bold yellow")
            conteudo.append(f"POSIÇÃO: {atleta.posicao} | OVERALL: {atleta.pontuacao_overall}\n\n", style="bold magenta")
            conteudo.append(f"⚽ Total de Gols: {atleta.total_gols}\n", style="white")
            conteudo.append(f"🎯 Total de Assistências: {atleta.total_assistencias}\n", style="white")
            conteudo.append(f"⚡ Participações em Gols: {atleta.participacoes_diretas}\n", style="white")
            conteudo.append(f"📊 Jogos Disputados: {atleta.total_jogos}\n", style="white")
            conteudo.append(f"📈 Média de Gols/Jogo: {atleta.media_gols:.2f}\n", style="white")

            painel_card = Panel(
                Align.center(conteudo),
                title=f"🪪 CARD DE ATLETA - #{atleta.codigo}",
                border_style="magenta",
                expand=False,
            )
            self._console.print(painel_card)

            if atleta.historico:
                tabela_partidas = Table(title=f"Histórico Recente - {atleta.nome}", border_style="yellow")
                tabela_partidas.add_column("Data", justify="center")
                tabela_partidas.add_column("Adversário")
                tabela_partidas.add_column("Gols", justify="center")
                tabela_partidas.add_column("Assist.", justify="center")
                tabela_partidas.add_column("Minutos", justify="center")

                for p in atleta.historico:
                    tabela_partidas.add_row(
                        p.data,
                        p.oponente,
                        str(p.gols),
                        str(p.assistencias),
                        f"{p.minutos_jogados}'",
                    )
                self._console.print(tabela_partidas)

        except ValueError:
            self._console.print("[bold red]❌ Erro: Insira um valor numérico válido.[/bold red]")

        Prompt.ask("\nPressione ENTER para continuar")

    def _menu_leaderboard(self) -> None:
        """Exibe os destaques e o líder de artilharia da competição."""
        self._console.print("\n[bold green]🏆 Leaderboard da Temporada[/bold green]")
        artilheiro = self._gestor.obter_artilheiro()

        if not artilheiro or artilheiro.total_gols == 0:
            self._console.print("[yellow]⚠️ Nenhuma gol registrado até o momento na liga.[/yellow]")
            Prompt.ask("\nPressione ENTER para continuar")
            return

        texto_artilheiro = Text()
        texto_artilheiro.append("👑 MAIOR ARTILHEIRO DA LIGA 👑\n\n", style="bold gold1")
        texto_artilheiro.append(f"{artilheiro.nome} ({artilheiro.posicao})\n", style="bold white")
        texto_artilheiro.append(f"Gols Marcados: {artilheiro.total_gols} ⚽ | Overall: {artilheiro.pontuacao_overall}", style="bold green")

        self._console.print(Panel(Align.center(texto_artilheiro), border_style="gold1"))
        Prompt.ask("\nPressione ENTER para continuar")


if __name__ == "__main__":
    app = SportsTechConsole()
    app.executar()