from hashlib import sha256
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class Membro:
    """
    Representa um membro individual no sistema.

    Atributos encapsulados garantem a higienização do nome e a geração
    de identificadores únicos para cada cadastro.
    """

    _contador_id = 1000

    def __init__(self, nome: str, plano: str, senha_plana: str):
        """
        Inicializa uma nova instância de Membro.

        :param nome: Nome do membro a ser cadastrado.
        :param plano: Nome do plano assinado (ex: Basic, Premium, VIP).
        :param senha_plana: Senha enviada pelo usuário para geração do hash.
        """
        Membro._contador_id += 1
        self._id = f"MEM-{Membro._contador_id}"
        self._nome = self._formatar_nome(nome)
        self._plano = plano.strip().title()
        self._senha_hash = self._gerar_hash(senha_plana)

    @property
    def id(self) -> str:
        """Retorna o identificador único do membro."""
        return self._id

    @property
    def nome(self) -> str:
        """Retorna o nome formatado do membro."""
        return self._nome

    @nome.setter
    def nome(self, novo_nome: str):
        """Atualiza o nome do membro com higienização prévia."""
        self._nome = self._formatar_nome(novo_nome)

    @property
    def plano(self) -> str:
        """Retorna o plano do membro."""
        return self._plano

    @plano.setter
    def plano(self, novo_plano: str):
        """Atualiza o plano do membro."""
        self._plano = novo_plano.strip().title()

    @property
    def senha_hash(self) -> str:
        """Retorna a representação em hash da senha do membro."""
        return self._senha_hash

    def atualizar_senha(self, nova_senha_plana: str):
        """Atualiza a senha do membro redefinindo o hash SHA-256."""
        self._senha_hash = self._gerar_hash(nova_senha_plana)

    def _formatar_nome(self, nome: str) -> str:
        """
        Remove espaços sobressalentes e padroniza a caixa das letras.

        :param nome: String bruta enviada no input.
        :return: Nome higienizado em formato Title Case.
        """
        return " ".join(nome.strip().split()).title()

    def _gerar_hash(self, texto: str) -> str:
        """
        Gera um hash SHA-256 a partir de uma string em texto puro.

        :param texto: Texto a ser mascarado.
        :return: Hexdigest resultante da criptografia de sentido único.
        """
        return sha256(texto.encode("utf-8")).hexdigest()


class SistemaOnboarding:
    """
    Gerencia o ciclo de vida, navegação e operações do sistema no terminal.
    """

    def __init__(self):
        """Inicializa o sistema com o console da Rich e o repositório de membros."""
        self._console = Console()
        self._membros = []

    def executar(self):
        """Inicia o loop do menu principal da aplicação."""
        try:
            while True:
                self._limpar_e_exibir_cabecalho("PAINEL PRINCIPAL DE GESTÃO")
                self._exibir_menu_opcoes()
                opcao = Prompt.ask("\n[bold white]Selecione uma opção[/bold white]", choices=["1", "2", "3", "4", "5"])

                if opcao == "1":
                    self._menu_cadastrar_membros()
                elif opcao == "2":
                    self._menu_listar_membros()
                elif opcao == "3":
                    self._menu_editar_membro()
                elif opcao == "4":
                    self._menu_remover_membro()
                elif opcao == "5":
                    self._limpar_e_exibir_cabecalho("ENCERRANDO SISTEMA")
                    self._console.print("[bold yellow]Sessão finalizada com sucesso. Até logo![/bold yellow]\n")
                    break
        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]Operação cancelada. Encerrando o sistema de forma segura...[/bold yellow]\n")
        except Exception as erro:
            self._console.print(f"\n[bold red]Ocorreu um erro inesperado na aplicação:[bold red] {erro}\n")

    def _limpar_e_exibir_cabecalho(self, subtitulo: str):
        """Limpa a tela e re-desenha o cabeçalho superior utilizando toda a largura."""
        self._console.clear()
        conteudo = f"[bold cyan]SISTEMA DE GESTÃO DE MEMBROS[/bold cyan]\n[dim]{subtitulo}[/dim]"
        painel = Panel(conteudo, border_style="blue", expand=True)
        self._console.print(painel)
        self._console.print()

    def _exibir_menu_opcoes(self):
        """Exibe o menu de navegação do painel principal."""
        self._console.print("[bold white]Menu de Navegação:[/bold white]\n")
        self._console.print(" 1. Cadastrar Novo(s) Membro(s)")
        self._console.print(" 2. Listar Todos os Membros Cadastrados")
        self._console.print(" 3. Editar Dados de um Membro")
        self._console.print(" 4. Remover Membro da Base")
        self._console.print(" 5. Sair do Sistema")

    def _menu_cadastrar_membros(self):
        """Permite o cadastro contínuo de múltiplos membros até interrupção do usuário."""
        while True:
            self._limpar_e_exibir_cabecalho("CADASTRO DE NOVO MEMBRO")
            
            nome = self._solicitar_nome_valido()
            plano = self._solicitar_plano_valido()
            senha = self._solicitar_senha_valida()

            membro = Membro(nome=nome, plano=plano, senha_plana=senha)
            self._membros.append(membro)

            with self._console.status(f"[bold cyan]Processando criptografia e registrando {membro.nome}...[/bold cyan]", spinner="dots"):
                sleep(1.2)

            self._console.print(f"\n[bold green]✔ Membro {membro.nome} registrado com ID {membro.id}![/bold green]\n")

            continuar = Prompt.ask("[bold white]Deseja cadastrar outro membro?[/bold white] (s/n)", choices=["s", "n"], default="s")
            if continuar.lower() != "s":
                break

    def _menu_listar_membros(self):
        """Exibe a visualização completa e estilizada dos membros cadastrados."""
        self._limpar_e_exibir_cabecalho("VISUALIZAÇÃO DA BASE DE DADOS")

        if not self._membros:
            self._console.print(Panel("[bold yellow]Nenhum membro cadastrado até o momento.[/bold yellow]", border_style="yellow", expand=True))
        else:
            tabela = Table(title="Lista Oficial de Membros", header_style="bold cyan", border_style="dim", expand=True)
            tabela.add_column("ID", style="cyan", justify="center")
            tabela.add_column("Nome Completo", style="white")
            tabela.add_column("Plano Assinado", style="magenta", justify="center")
            tabela.add_column("Hash de Segurança (SHA-256)", style="dim")

            for m in self._membros:
                tabela.add_row(m.id, m.nome, m.plano, f"{m.senha_hash[:20]}...")

            self._console.print(tabela)

        Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu principal")

    def _menu_editar_membro(self):
        """Permite alterar informações de um membro específico buscando pelo seu ID."""
        self._limpar_e_exibir_cabecalho("EDIÇÃO DE CADASTRO")

        if not self._membros:
            self._console.print(Panel("[bold yellow]Base vazia. Não há membros para editar.[/bold yellow]", border_style="yellow", expand=True))
            Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu principal")
            return

        id_busca = Prompt.ask("[bold white]Digite o ID do membro que deseja editar[/bold white] (ex: MEM-1001)")
        membro = next((m for m in self._membros if m.id.upper() == id_busca.strip().upper()), None)

        if not membro:
            self._console.print(f"\n[bold red] Erro:[/bold red] Nenhum membro localizado com o ID '{id_busca}'.", style="red")
            Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu principal")
            return

        self._console.print(f"\n[bold white]Membro Selecionado:[/bold white] [cyan]{membro.id}[/cyan] - {membro.nome} ({membro.plano})")
        self._console.print("\nO que deseja alterar?")
        self._console.print(" 1. Nome")
        self._console.print(" 2. Plano")
        self._console.print(" 3. Senha")
        self._console.print(" 4. Cancelar Edição")

        opcao = Prompt.ask("\nEscolha a opção", choices=["1", "2", "3", "4"])

        if opcao == "1":
            novo_nome = self._solicitar_nome_valido()
            membro.nome = novo_nome
            self._console.print(f"\n[bold green]✔ Nome atualizado para '{membro.nome}' com sucesso![/bold green]")
        elif opcao == "2":
            novo_plano = self._solicitar_plano_valido()
            membro.plano = novo_plano
            self._console.print(f"\n[bold green]✔ Plano alterado para '{membro.plano}' com sucesso![/bold green]")
        elif opcao == "3":
            nova_senha = self._solicitar_senha_valida()
            membro.atualizar_senha(nova_senha)
            self._console.print("\n[bold green]✔ Hash da senha redefinido com sucesso![/bold green]")
        elif opcao == "4":
            self._console.print("\n[bold yellow]Edição cancelada.[/bold yellow]")

        Prompt.ask("\nPressione [bold white]Enter[/bold white] para retornar")

    def _menu_remover_membro(self):
        """Remove um membro selecionado pelo ID da lista em memória."""
        self._limpar_e_exibir_cabecalho("REMOÇÃO DE CADASTRO")

        if not self._membros:
            self._console.print(Panel("[bold yellow]Base vazia. Não há membros para remover.[/bold yellow]", border_style="yellow", expand=True))
            Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar ao menu principal")
            return

        id_busca = Prompt.ask("[bold white]Digite o ID do membro que deseja remover[/bold white]")
        membro = next((m for m in self._membros if m.id.upper() == id_busca.strip().upper()), None)

        if not membro:
            self._console.print(f"\n[bold red] Erro:[/bold red] Membro com ID '{id_busca}' não encontrado.", style="red")
            Prompt.ask("\nPressione [bold white]Enter[/bold white] para voltar")
            return

        confirmacao = Prompt.ask(
            f"\n[bold red]Tem certeza que deseja remover {membro.nome} ({membro.id})?[/bold red] (s/n)",
            choices=["s", "n"],
            default="n"
        )

        if confirmacao.lower() == "s":
            self._membros.remove(membro)
            self._console.print(f"\n[bold green]✔ Membro {id_busca} removido da base de dados![/bold green]")
        else:
            self._console.print("\n[bold yellow]Operação de remoção cancelada.[/bold yellow]")

        Prompt.ask("\nPressione [bold white]Enter[/bold white] para retornar")

    def _solicitar_nome_valido(self) -> str:
        """Garante a entrada de um nome com caracteres válidos."""
        while True:
            nome = Prompt.ask("[bold white]Digite o nome completo[/bold white]")
            nome_limpo = nome.strip()
            if len(nome_limpo) >= 3 and all(parte.isalpha() for parte in nome_limpo.split()):
                return nome_limpo
            self._console.print("[bold red] Erro:[/bold red] O nome deve ter ao menos 3 letras e nenhum símbolo/número.")

    def _solicitar_plano_valido(self) -> str:
        """Apresenta opções e retorna um nome de plano válido."""
        self._console.print("\n[bold white]Planos disponíveis:[/bold white]")
        self._console.print(" 1. Basic")
        self._console.print(" 2. Premium")
        self._console.print(" 3. VIP")
        planos_map = {"1": "Basic", "2": "Premium", "3": "VIP"}
        opcao = Prompt.ask("Selecione o plano (1-3)", choices=["1", "2", "3"])
        return planos_map[opcao]

    def _solicitar_senha_valida(self) -> str:
        """Garante uma entrada de senha que cumpra o tamanho mínimo estipulado."""
        while True:
            senha = Prompt.ask("[bold white]Defina a senha[/bold white]", password=True)
            if len(senha) >= 6:
                return senha
            self._console.print("[bold red] Erro:[/bold red] A senha deve conter no mínimo 6 caracteres.")


if __name__ == "__main__":
    app = SistemaOnboarding()
    app.executar()