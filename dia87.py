import os
import sys
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live


class _GerenciadorArquivoLog:
    """
    Encapsula as operações de leitura e monitoramento do arquivo físico de log.
    """

    def __init__(self, caminho_arquivo: str):
        """
        Inicializa o gerenciador com o caminho do arquivo.

        :param caminho_arquivo: Caminho relativo ou absoluto do arquivo a ser monitorado.
        """
        self._caminho = caminho_arquivo
        self._ultima_posicao = 0
        self._garantir_existencia_arquivo()

    @property
    def caminho(self) -> str:
        """Retorna o caminho do arquivo monitorado."""
        return self._caminho

    def _garantir_existencia_arquivo(self):
        """Cria o arquivo caso ele ainda não exista no sistema."""
        if not os.path.exists(self._caminho):
            with open(self._caminho, 'w', encoding='utf-8') as arq:
                data_inicio = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                arq.write(f"--- ARQUIVO DE LOG CRIADO EM {data_inicio} ---\n")

        self._ultima_posicao = os.path.getsize(self._caminho)

    def ler_novas_linhas(self) -> list:
        """
        Lê apenas os novos conteúdos adicionados ao arquivo desde a última checagem.

        :return: Lista de strings com as novas linhas adicionadas.
        """
        if not os.path.exists(self._caminho):
            return []

        tamanho_atual = os.path.getsize(self._caminho)

        if tamanho_atual < self._ultima_posicao:
            self._ultima_posicao = 0

        if tamanho_atual == self._ultima_posicao:
            return []

        novas_linhas = []
        with open(self._caminho, 'r', encoding='utf-8') as arq:
            arq.seek(self._ultima_posicao)
            linhas = arq.readlines()
            for linha in linhas:
                conteudo = linha.strip()
                if conteudo:
                    novas_linhas.append(conteudo)
            self._ultima_posicao = arq.tell()

        return novas_linhas


class MonitorLogsTerminal:
    """
    Classe principal responsável por orquestrar a interface visual Rich e a execução contínua.
    """

    def __init__(self):
        """Inicializa o console do Rich, estado do monitor e histórico de eventos."""
        self._console = Console()
        self._historico_eventos = []
        self._executando = True

    def _criar_painel_cabecalho(self, nome_arquivo: str) -> Panel:
        """
        Gera o painel de topo indicando o arquivo em monitoramento.

        :param nome_arquivo: Nome do arquivo vigiado.
        :return: Objeto Panel do Rich.
        """
        info = (
            f"[bold green]STATUS:[/bold green] MONITORANDO EM TEMPO REAL  |  "
            f"[bold yellow]ARQUIVO:[/bold yellow] [cyan]{nome_arquivo}[/cyan]\n"
            f"[dim]Pressione CTRL+C no terminal para encerrar o monitoramento.[/dim]"
        )
        return Panel(info, title=":mag: Monitor Automático de Arquivos / Logs", border_style="green")

    def _gerar_tabela_historico(self) -> Table:
        """
        Gera a tabela visual formatada com as atualizações recentes registradas.

        :return: Objeto Table do Rich.
        """
        tabela = Table(title="Histórico de Modificações Detectadas", header_style="bold magenta", border_style="blue", expand=True)
        tabela.add_column("Horário", justify="center", style="cyan", width=12)
        tabela.add_column("Conteúdo / Nova Linha Registrada", style="white")

        if not self._historico_eventos:
            tabela.add_row("--:--:--", "[dim]Aguardando alterações no arquivo...[/dim]")
        else:
            for item in self._historico_eventos[-10:]:
                tabela.add_row(item["horario"], item["conteudo"])

        return tabela

    def iniciar(self):
        """
        Inicia a interface e o loop contínuo de monitoramento do arquivo.
        """
        try:
            self._console.clear()
            self._console.print(Panel.fit(
                ":robot: [bold green]MONITOR DE LOGS E ARQUIVOS[/bold green] :robot:\n"
                "[dim]Automação de Varredura de Alterações no Disco[/dim]",
                border_style="green"
            ))

            nome_arquivo = Prompt.ask(
                "\n:file_folder: [bold green]Digite o nome do arquivo para monitorar[/bold green]",
                default="meu_log.txt"
            ).strip()

            gerenciador = _GerenciadorArquivoLog(nome_arquivo)

            self._console.clear()
            self._console.print(self._criar_painel_cabecalho(gerenciador.caminho))

            with Live(self._gerar_tabela_historico(), refresh_per_second=2, console=self._console) as live_table:
                while self._executando:
                    novas_linhas = gerenciador.ler_novas_linhas()

                    if novas_linhas:
                        horario_atual = datetime.now().strftime("%H:%M:%S")
                        for linha in novas_linhas:
                            self._historico_eventos.append({
                                "horario": horario_atual,
                                "conteudo": linha
                            })
                        live_table.update(self._gerar_tabela_historico())

                    time.sleep(1)

        except KeyboardInterrupt:
            self._console.print("\n\n:door: [bold yellow]Monitoramento encerrado com sucesso pelo usuário![/bold yellow]\n")
            sys.exit(0)
        except Exception as erro:
            self._console.print(f"\n:warning: [bold red]Erro inesperado na execução:[/bold red] {str(erro)}")
            sys.exit(1)


# Ponto de entrada padrão
if __name__ == "__main__":
    app = MonitorLogsTerminal()
    app.iniciar()