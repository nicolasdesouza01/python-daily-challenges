import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

class AnalistaDeIdentidade:

    def __init__(self):
        self._console = Console()
        self._banco_de_dados = []

    def _exibir_banner(self):
        self._console.print(Panel.fit(
            "[bold magenta]:computer: NÚCLEO DE PROCESSAMENTO NOMINAL :computer:[/bold magenta]\n"
            "[white]Engine de Extração, Armazenamento e Estruturação[/white]",
            border_style="bright_magenta",
            padding=(1, 4)
        ))

    def _carregar_sistema(self, mensagem="Acessando banco de dados..."):
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description=mensagem, total=None)
                time.sleep(1.2)
        except Exception:
            time.sleep(1.2)

    def _coletar_nome(self):
        while True:
            try:
                entrada = self._console.input("\n[bold cyan]:arrow_right: Digite o nome completo para o registro:[/bold cyan] ").strip()

                if not entrada:
                    self._console.print("[bold red]:warning: Erro: A entrada não pode estar vazia.[/bold red]")
                    continue
                
                partes = entrada.split()
                if all(parte.isalpha() for parte in partes):
                    return entrada
                else:
                    self._console.print("[bold red]:warning: Erro: O sistema aceita apenas caracteres alfabéticos.[/bold red]")
            except Exception as erro:
                self._console.print(f"[bold red]:warning: Ocorreu um erro inesperado na coleta de dados: {erro}[/bold red]")

    def _gerar_relatorio(self, nome_completo):
        try:
            fragmentos = nome_completo.split()
            self._carregar_sistema("Mapeando fragmentos do nome...")
            
            tabela = Table(
                title=":bar_chart: RELATÓRIO DE ESTRUTURA", 
                title_style="bold yellow", 
                show_lines=True,
                header_style="bold cyan"
            )
            
            tabela.add_column("Propriedade", justify="right")
            tabela.add_column("Conteúdo Identificado", style="bold white")

            primeiro_nome = fragmentos[0].capitalize()
            sobrenome_final = fragmentos[-1].capitalize() if len(fragmentos) > 1 else "Não informado"

            tabela.add_row("Primeiro Nome", primeiro_nome)
            tabela.add_row("Sobrenome Final", sobrenome_final)
            tabela.add_row("Total de Termos", str(len(fragmentos)))

            self._console.print("\n")
            self._console.print(tabela)
            
            self._console.print(Panel(
                f"[bold green]:white_check_mark: Objeto processado e salvo: {nome_completo.upper()}[/bold green]",
                border_style="green"
            ))
        except Exception as erro:
            self._console.print(f"[bold red]:warning: Erro inesperado ao gerar o relatório: {erro}[/bold red]")

    def _exibir_pessoas_cadastradas(self):
        try:
            if not self._banco_de_dados:
                self._console.print("\n[bold yellow]:warning: Nenhum registro encontrado no banco de dados temporário.[/bold yellow]")
                return

            self._carregar_sistema("Consultando registros na memória...")

            tabela_geral = Table(
                title=":card_index_dividers: REGISTROS DO SISTEMA",
                title_style="bold magenta",
                show_lines=True,
                header_style="bold white"
            )

            tabela_geral.add_column("ID", justify="center", style="cyan")
            tabela_geral.add_column("Nome Completo Cadastrado", style="bold green")

            for indice, nome in enumerate(self._banco_de_dados, start=1):
                tabela_geral.add_row(str(indice), nome.upper())

            self._console.print("\n")
            self._console.print(tabela_geral)
        except Exception as erro:
            self._console.print(f"[bold red]:warning: Erro ao acessar a base de dados: {erro}[/bold red]")

    def executar(self):
        try:
            self._exibir_banner()
            
            while True:
                nome_valido = self._coletar_nome()
                self._banco_de_dados.append(nome_valido)
                self._gerar_relatorio(nome_valido)

                while True:
                    try:
                        deseja_ver = self._console.input("\n[bold yellow]:eyes: Deseja ver a lista de pessoas já cadastradas? (S/N):[/bold yellow] ").strip().upper()
                        if deseja_ver in ["S", "N", "SIM", "NÃO", "NAO"]:
                            if deseja_ver in ["S", "SIM"]:
                                self._exibir_pessoas_cadastradas()
                            break
                        else:
                            self._console.print("[bold red]:warning: Entrada inválida. Digite apenas S ou N.[/bold red]")
                    except Exception as erro:
                        self._console.print(f"[bold red]:warning: Erro na leitura da opção: {erro}[/bold red]")

                while True:
                    try:
                        continuar = self._console.input("\n[bold cyan]:door: Deseja cadastrar uma nova pessoa ou parar o programa? (C/P):[/bold cyan] ").strip().upper()
                        if continuar in ["C", "P", "CONTINUAR", "PARAR"]:
                            break
                        else:
                            self._console.print("[bold red]:warning: Entrada inválida. Digite C para continuar ou P para parar.[/bold red]")
                    except Exception as erro:
                        self._console.print(f"[bold red]:warning: Erro na leitura da opção: {erro}[/bold red]")

                if continuar in ["P", "PARAR"]:
                    self._console.print("\n[bold magenta]:wave: Desconectando do Núcleo de Processamento. Até logo![/bold magenta]\n")
                    break

        except KeyboardInterrupt:
            self._console.print("\n[bold yellow]:warning: Execução interrompida pelo usuário. Saindo do sistema...[/bold yellow]")
        except Exception as erro:
            self._console.print(f"[bold red]:warning: Ocorreu um erro crítico na execução do sistema: {erro}[/bold red]")


if __name__ == "__main__":
    try:
        app = AnalistaDeIdentidade()
        app.executar()
    except Exception:
        pass
