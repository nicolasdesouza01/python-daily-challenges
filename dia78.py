import hashlib
import sys
import time
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, Confirm
from rich.status import Status


class Usuario:
    """Representa um operador ou motorista autenticado no sistema de logística."""

    def __init__(self, login: str, senha_plana: str):
        """Inicializa o usuário aplicando hash SHA-256 na senha recebida."""
        self._login = login.strip()
        self._hash_senha = self._gerar_hash(senha_plana.strip())

    @property
    def login(self) -> str:
        """Retorna o identificador/login do operador."""
        return self._login

    def _gerar_hash(self, senha: str) -> str:
        """Gera um hash SHA-256 para a senha fornecida garantindo segurança."""
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    def verificar_senha(self, senha_plana: str) -> bool:
        """Compara a senha digitada em texto puro com o hash SHA-256 armazenado."""
        return self._hash_senha == self._gerar_hash(senha_plana.strip())


class Pacote:
    """Representa uma encomenda ou pacote indivisível a ser transportado."""

    def __init__(self, identificador: str, descricao: str, peso: float):
        """Inicializa um pacote com código, descrição e peso validado em Kg."""
        self._identificador = identificador.strip()
        self._descricao = descricao.strip()
        self._peso = max(0.01, peso)

    @property
    def identificador(self) -> str:
        """Retorna o código de rastreio/identificador único do pacote."""
        return self._identificador

    @property
    def descricao(self) -> str:
        """Retorna a descrição do conteúdo do pacote."""
        return self._descricao

    @property
    def peso(self) -> float:
        """Retorna o peso individual do pacote em Kg."""
        return self._peso


class VeiculoCarga:
    """Representa um veículo de frete gerenciando seu limite de capacidade e manifesto de cargas."""

    def __init__(self, placa: str, modelo: str, capacidade_maxima: float):
        """Inicializa o veículo com seus limites operacionais."""
        self._placa = placa.upper().strip()
        self._modelo = modelo.strip()
        self._capacidade_maxima = max(1.0, capacidade_maxima)
        self._cargas: List[Pacote] = []

    @property
    def placa(self) -> str:
        """Retorna a placa do veículo."""
        return self._placa

    @property
    def modelo(self) -> str:
        """Retorna o modelo do veículo."""
        return self._modelo

    @property
    def capacidade_maxima(self) -> float:
        """Retorna o peso máximo permitido para o veículo em Kg."""
        return self._capacidade_maxima

    @property
    def cargas(self) -> List[Pacote]:
        """Retorna uma cópia da lista de cargas alocadas no veículo."""
        return self._cargas.copy()

    @property
    def peso_total(self) -> float:
        """Calcula o peso total das cargas atualmente embarcadas."""
        return sum(pacote.peso for pacote in self._cargas)

    @property
    def espaco_disponivel(self) -> float:
        """Calcula a capacidade de carga remanescente do veículo."""
        return max(0.0, self._capacidade_maxima - self.peso_total)

    @property
    def percentual_ocupacao(self) -> float:
        """Retorna a porcentagem de ocupação da capacidade do veículo."""
        return (self.peso_total / self._capacidade_maxima) * 100

    def cabe_carga(self, peso: float) -> bool:
        """Verifica se um peso específico pode ser adicionado sem exceder a capacidade."""
        return (self.peso_total + peso) <= self._capacidade_maxima

    def adicionar_pacote(self, pacote: Pacote) -> bool:
        """Adiciona um pacote ao veículo caso o limite de peso permita."""
        if self.cabe_carga(pacote.peso):
            self._cargas.append(pacote)
            return True
        return False

    def obter_pacotes_mais_pesados(self) -> List[Pacote]:
        """Identifica os pacotes com o maior peso cadastrado no lote atual."""
        if not self._cargas:
            return []
        maior_peso = max(p.peso for p in self._cargas)
        return [p for p in self._cargas if p.peso == maior_peso]

    def obter_pacotes_mais_leves(self) -> List[Pacote]:
        """Identifica os pacotes com o menor peso cadastrado no lote atual."""
        if not self._cargas:
            return []
        menor_peso = min(p.peso for p in self._cargas)
        return [p for p in self._cargas if p.peso == menor_peso]


class SistemaLogisticaHUD:
    """Gerencia a interface gráfica via terminal e executa o fluxo principal do sistema."""

    def __init__(self):
        """Inicializa o console do Rich e configura o operador padrão."""
        self._console = Console()
        self._operador = Usuario("admin", "1234")
        self._veiculo: Optional[VeiculoCarga] = None

    def executar(self) -> None:
        """Executa o ciclo de vida completo do aplicativo com tratamento robusto de exceções."""
        try:
            self._limpar_tela()
            self._exibir_cabecalho()
            self._autenticar_operador()
            self._configurar_veiculo()
            self._loop_cadastro_cargas()
            self._exibir_relatorio_final()
            
        except KeyboardInterrupt:
            self._console.print("\n\n⚠️ [bold yellow]Operação interrompida pelo usuário (Ctrl+C). Encerrando com segurança...[/bold yellow]")
            sys.exit(0)
        except Exception as e:
            self._console.print(f"\n❌ [bold red]Ocorreu um erro inesperado na aplicação:[/bold red] {e}")
            sys.exit(1)

    def _limpar_tela(self) -> None:
        """Limpa o terminal antes da renderização."""
        self._console.clear()

    def _exibir_cabecalho(self) -> None:
        """Renderiza o painel principal de marca do sistema."""
        painel = Panel(
            "🚚 [bold white]SISTEMA DE LOGÍSTICA E DISTRIBUIÇÃO DE CARGAS[/bold white]\n"
            "[dim]Módulo de Carregamento, Pesagem e Distribuição de Frete[/dim]",
            border_style="blue",
            expand=False
        )
        self._console.print(painel)
        self._console.print()

    def _autenticar_operador(self) -> None:
        """Solicita autenticação do operador validando via Hash SHA-256 com tentativas ilimitadas."""
        self._console.print(Panel("🛡️ [bold]Autenticação de Operador[/bold]", style="cyan"))
        
        while True:
            try:
                login = Prompt.ask("👤 Login do Operador").strip()
                senha = Prompt.ask("🔑 Senha de Acesso", password=True).strip()

                with self._console.status("[bold green]Validando credenciais com Hashing SHA-256...[/bold green]"):
                    time.sleep(0.4)

                if login == self._operador.login and self._operador.verificar_senha(senha):
                    self._console.print("✅ [bold green]Acesso liberado com sucesso![/bold green]\n")
                    time.sleep(0.4)
                    break
                
                self._console.print("❌ [bold red]Credenciais inválidas! Tente novamente.[/bold red]\n")
            
            except Exception:
                self._console.print("⚠️ [red]Entrada inválida detectada. Tente novamente.[/red]\n")

    def _configurar_veiculo(self) -> None:
        """Cadastra as informações do veículo que receberá o carregamento."""
        self._console.print(Panel("🚚 [bold]Configuração do Veículo de Transporte[/bold]", style="yellow"))
        
        while True:
            try:
                placa = Prompt.ask("🏷️ Placa do Veículo (ex: ABC-1234)").strip()
                modelo = Prompt.ask("📦 Modelo do Veículo (ex: Caminhão Baú / Toco)").strip()
                capacidade = FloatPrompt.ask("🏋️ Capacidade Máxima de Carga (em Kg)")

                if capacidade <= 0:
                    self._console.print("⚠️ [red]A capacidade máxima deve ser um valor maior que zero.[/red]\n")
                    continue

                self._veiculo = VeiculoCarga(placa, modelo, capacidade)
                self._console.print(f"\n✅ [bold green]Veículo {modelo} ({placa}) configurado com limite de {capacidade:.2f} Kg![/bold green]\n")
                break
            except Exception:
                self._console.print("⚠️ [red]Entrada inválida. Por favor, insira um número válido para a capacidade.[/red]\n")

    def _loop_cadastro_cargas(self) -> None:
        """Realiza a inclusão contínua de pacotes monitorando limites de peso."""
        contador = 1
        
        while True:
            self._exibir_hud_status()
            self._console.print(f"[bold cyan]--- Inclusão do Pacote #{contador} ---[/bold cyan]")
            
            try:
                codigo = Prompt.ask("🏷️ Código de Rastreio / Nota").strip()
                if not codigo:
                    codigo = f"PAC-{contador:03d}"

                descricao = Prompt.ask("📦 Descrição do Item").strip()
                if not descricao:
                    descricao = "Mercadoria Diversa"

                peso = FloatPrompt.ask("⚖️ Peso do Pacote (Kg)")

                if peso <= 0:
                    self._console.print("⚠️ [red]O peso precisa ser maior que zero.[/red]\n")
                    continue

                pacote = Pacote(codigo, descricao, peso)

                if self._veiculo.cabe_carga(peso):
                    self._veiculo.adicionar_pacote(pacote)
                    self._console.print(f"✅ [bold green]Pacote '{descricao}' ({peso:.2f} Kg) adicionado ao manifesto![/bold green]\n")
                    contador += 1
                else:
                    self._console.print(
                        f"\n⚠️ [bold red]ATENÇÃO: ALERTA DE OVERWEIGHT![/bold red]\n"
                        f"O pacote de [yellow]{peso:.2f} Kg[/yellow] excede a margem disponível de "
                        f"[green]{self._veiculo.espaco_disponivel:.2f} Kg[/green] no veículo.\n"
                    )

                if self._veiculo.espaco_disponivel == 0:
                    self._console.print("⛔ [bold red]Veículo atingiu a capacidade MÁXIMA exata de carregamento![/bold red]\n")
                    break

                continuar = Confirm.ask("❓ Deseja cadastrar outro pacote?")
                if not continuar:
                    break

            except Exception:
                self._console.print("⚠️ [red]Erro na leitura dos dados do pacote. Tente novamente.[/red]\n")

    def _exibir_hud_status(self) -> None:
        """Exibe o painel visual atualizado de ocupação do veículo."""
        porcentagem = self._veiculo.percentual_ocupacao
        cor_barra = "green" if porcentagem < 75 else "yellow" if porcentagem < 95 else "red"

        texto_status = (
            f"[bold]Veículo:[/bold] {self._veiculo.modelo} ({self._veiculo.placa})\n"
            f"[bold]Capacidade Máxima:[/bold] {self._veiculo.capacidade_maxima:.2f} Kg\n"
            f"[bold]Peso Total Embarcado:[/bold] [{cor_barra}]{self._veiculo.peso_total:.2f} Kg[/{cor_barra}]\n"
            f"[bold]Espaço Restante:[/bold] {self._veiculo.espaco_disponivel:.2f} Kg\n"
            f"[bold]Taxa de Ocupação:[/bold] [{cor_barra}]{porcentagem:.1f}%[/{cor_barra}]"
        )
        
        self._console.print(Panel(texto_status, title="📈 Painel de Ocupação em Tempo Real", border_style=cor_barra))
        self._console.print()

    def _exibir_relatorio_final(self) -> None:
        """Renderiza o manifesto de carga final em formato de tabela elegante."""
        self._limpar_tela()
        self._exibir_cabecalho()
        
        with Status("[bold green]Gerando Manifesto de Carga e Relatório Final...[/bold green]"):
            time.sleep(1.0)

        self._console.print(Panel("📋 [bold white]MANIFESTO DE CARGA E DISTRIBUIÇÃO FINAL[/bold white]", border_style="green"))

        if not self._veiculo.cargas:
            self._console.print("⚠️ [bold yellow]Nenhuma carga foi embarcada no veículo.[/bold yellow]")
            return

        tabela = Table(title=f"Lista de Pacotes - Veículo {self._veiculo.placa}", show_header=True, header_style="bold magenta")
        tabela.add_column("Código", style="cyan", justify="center")
        tabela.add_column("Descrição", style="white")
        tabela.add_column("Peso (Kg)", justify="right", style="green")

        for pacote in self._veiculo.cargas:
            tabela.add_row(pacote.identificador, pacote.descricao, f"{pacote.peso:.2f}")

        self._console.print(tabela)

        mais_pesados = self._veiculo.obter_pacotes_mais_pesados()
        mais_leves = self._veiculo.obter_pacotes_mais_leves()

        nomes_pesados = ", ".join([f"'{p.descricao}' ({p.identificador})" for p in mais_pesados])
        nomes_leves = ", ".join([f"'{p.descricao}' ({p.identificador})" for p in mais_leves])

        resumo_painel = (
            f"[bold]Total de Pacotes Cadastrados:[/bold] {len(self._veiculo.cargas)}\n"
            f"[bold]Peso Total Bruto:[/bold] {self._veiculo.peso_total:.2f} Kg / {self._veiculo.capacidade_maxima:.2f} Kg\n"
            f"[bold]Maior Peso Registrado:[/bold] {mais_pesados[0].peso:.2f} Kg [dim](Item(ns): {nomes_pesados})[/dim]\n"
            f"[bold]Menor Peso Registrado:[/bold] {mais_leves[0].peso:.2f} Kg [dim](Item(ns): {nomes_leves})[/dim]\n"
            f"[bold]Sobra de Capacidade Segura:[/bold] {self._veiculo.espaco_disponivel:.2f} Kg"
        )

        self._console.print("\n", Panel(resumo_painel, title="📊 Resumo Estatístico do Carregamento", border_style="blue"))
        self._console.print("\n✅ [bold green]Operação concluída com sucesso. Boa viagem ao motorista![/bold green]\n")


if __name__ == "__main__":
    app = SistemaLogisticaHUD()
    app.executar()