import sys
from time import sleep
from typing import List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme


class LoteAtivos:
    """Representa um lote de ativos industriais e executa calculos operacionais.

    Esta classe encapsula a coleção de valores numéricos de um lote e provê
    métodos para auditoria, projeções e agregações estatísticas.
    """

    def __init__(self, valores_iniciais: Optional[List[float]] = None) -> None:
        """Inicializa o lote de ativos com uma lista opcional de valores."""
        self._valores: List[float] = valores_iniciais if valores_iniciais else []
        self._historico_operacoes: List[str] = []

    @property
    def valores(self) -> List[float]:
        """Retorna uma cópia da lista de valores do lote atual."""
        return self._valores.copy()

    @property
    def historico(self) -> List[str]:
        """Retorna o histórico de operações executadas no lote."""
        return self._historico_operacoes.copy()

    def atualizar_lote(self, novos_valores: List[float]) -> None:
        """Substitui o lote de dados atual por uma nova lista de valores numéricos."""
        self._valores = novos_valores.copy()
        self._registrar_historico(f"Lote redefinido com {len(novos_valores)} ativo(s).")

    def somar_valores(self) -> float:
        """Calcula a soma total acumulada do lote de ativos."""
        resultado = sum(self._valores)
        self._registrar_historico(f"Soma total calculada: {resultado:.2f}")
        return resultado

    def aplicar_fator_multiplicador(self, fator: float) -> List[float]:
        """Aplica um fator multiplicador uniforme a todos os ativos do lote."""
        self._valores = [val * fator for val in self._valores]
        self._registrar_historico(f"Fator multiplicador {fator:.2f} aplicado ao lote.")
        return self.valores

    def obter_extremos_e_media(self) -> Tuple[float, float, float]:
        """Retorna o maior valor, menor valor e a média aritmética do lote."""
        if not self._valores:
            return 0.0, 0.0, 0.0
        maior = max(self._valores)
        menor = min(self._valores)
        media = sum(self._valores) / len(self._valores)
        self._registrar_historico(f"Análise de extremos realizada (Maior: {maior:.2f}).")
        return maior, menor, media

    def _registrar_historico(self, descricao: str) -> None:
        """Registra uma entrada no histórico interno de auditoria."""
        self._historico_operacoes.append(descricao)


class VisualizadorIndustrial:
    """Gerencia a apresentação gráfica no terminal utilizando a biblioteca Rich.

    Aplica um tema corporativo baseado em tons de azul, preto e branco para
    ambientes industriais de alta visibilidade.
    """

    def __init__(self) -> None:
        """Inicializa o console com configurações customizadas de tema."""
        self._tema = Theme({
            "primary": "bold blue",
            "secondary": "cyan",
            "dark_bg": "on #001122",
            "highlight": "bold white on #003366",
            "alert": "bold red",
            "muted": "dim white"
        })
        self._console = Console(theme=self._tema)

    def exibir_banner(self) -> None:
        """Renderiza o cabeçalho principal da aplicação no terminal."""
        self._console.clear()
        texto = Text("SISTEMA DE AUDITORIA DE ATIVOS E CALCULADORA INDUSTRIAL", style="bold white on #002244", justify="center")
        subtexto = Text("Módulo de Processamento Numérico e Métricas de Produção", style="italic cyan", justify="center")
        conteudo = Text.assemble(texto, "\n", subtexto)
        painel = Panel(conteudo, border_style="blue", padding=(1, 2))
        self._console.print(painel)

    def exibir_menu(self) -> None:
        """Renderiza a tabela do menu de opções do sistema."""
        tabela = Table(title="PAINEL DE CONTROLE DE OPERAÇÕES", border_style="#004488", header_style="bold white on #002244")
        tabela.add_column("Código", justify="center", style="bold cyan", width=10)
        tabela.add_column("Operação Operacional", justify="left", style="white")

        tabela.add_row("[1]", "Calcular Agregação Total (Soma do Lote)")
        tabela.add_row("[2]", "Aplicar Fator Multiplicador (Ajuste de Escala/Taxa)")
        tabela.add_row("[3]", "Análise de Picos e Média (Maior, Menor e Média)")
        tabela.add_row("[4]", "Redefinir Lote de Ativos Numéricos")
        tabela.add_row("[5]", "Exibir Histórico de Auditoria")
        tabela.add_row("[6]", "Encerrar Sessão do Módulo")

        self._console.print(tabela)

    def exibir_lote_atual(self, valores: List[float]) -> None:
        """Apresenta os valores atualmente carregados no sistema."""
        str_valores = ", ".join([f"{v:.2f}" for v in valores]) if valores else "Nenhum dado cadastrado"
        painel = Panel(f"[bold cyan]Lote Atual:[/bold cyan] [white]{str_valores}[/white]", border_style="#003366")
        self._console.print(painel)

    def exibir_mensagem(self, texto: str, estilo: str = "white") -> None:
        """Exibe uma mensagem genérica estilizada no console."""
        self._console.print(f"[{estilo}]{texto}[/{estilo}]")

    def exibir_resultado_operacao(self, titulo: str, detalhes: str) -> None:
        """Exibe o resultado de uma operação em um painel destacado em azul."""
        painel = Panel(detalhes, title=f"[bold white]{titulo}[/bold white]", border_style="bold blue")
        self._console.print(painel)

    def aguardar_confirmacao(self) -> None:
        """Pausa a execução até que o usuário pressione Enter."""
        self._console.print("\nPressione [bold cyan]ENTER[/bold cyan] para continuar...", style="dim white")
        input()


class AuditoriaApp:
    """Classe controladora que coordena a execução da calculadora industrial."""

    def __init__(self) -> None:
        """Inicializa os componentes de visão e de modelo de dados."""
        self._ui = VisualizadorIndustrial()
        self._lote = LoteAtivos()

    def inicializar_lote_padrao(self) -> None:
        """Solicita ao usuário a carga inicial de dados numéricos."""
        self._ui.exibir_banner()
        self._ui.exibir_mensagem("CARGA INICIAL DE DADOS DO LOTE", "bold blue")
        valores = self._capturar_lista_floats("Informe os valores do lote separados por vírgula (ex: 100.5, 200, 150.75): ")
        self._lote.atualizar_lote(valores)

    def executar(self) -> None:
        """Executa o laço principal da aplicação de auditoria."""
        try:
            self.inicializar_lote_padrao()
            
            while True:
                self._ui.exibir_banner()
                self._ui.exibir_lote_atual(self._lote.valores)
                self._ui.exibir_menu()

                opcao = self._capturar_inteiro("\nSelecione o código da operação desejada [1-6]: ", min_val=1, max_val=6)

                if opcao == 1:
                    soma = self._lote.somar_valores()
                    self._ui.exibir_resultado_operacao("AGREGAÇÃO TOTAL DO LOTE", f"A soma total dos ativos cadastrados é: [bold cyan]{soma:.2f}[/bold cyan]")
                    self._ui.aguardar_confirmacao()

                elif opcao == 2:
                    fator = self._capturar_float("Digite o fator multiplicador a ser aplicado: ")
                    novos_valores = self._lote.aplicar_fator_multiplicador(fator)
                    str_novos = ", ".join([f"{v:.2f}" for v in novos_valores])
                    self._ui.exibir_resultado_operacao("FATOR MULTIPLICADOR APLICADO", f"Lote reajustado com sucesso:\n[white]{str_novos}[/white]")
                    self._ui.aguardar_confirmacao()

                elif opcao == 3:
                    maior, menor, media = self._lote.obter_extremos_e_media()
                    detalhes = (
                        f"Maior Valor Encontrado: [bold cyan]{maior:.2f}[/bold cyan]\n"
                        f"Menor Valor Encontrado: [bold cyan]{menor:.2f}[/bold cyan]\n"
                        f"Média Aritmética do Lote: [bold cyan]{media:.2f}[/bold cyan]"
                    )
                    self._ui.exibir_resultado_operacao("ANÁLISE DE EXTREMOS E MÉDIA", detalhes)
                    self._ui.aguardar_confirmacao()

                elif opcao == 4:
                    novos_valores = self._capturar_lista_floats("Informe os NOVOS valores do lote separados por vírgula: ")
                    self._lote.atualizar_lote(novos_valores)
                    self._ui.exibir_mensagem("Lote atualizado com sucesso!", "bold cyan")
                    sleep(1)

                elif opcao == 5:
                    historico_str = "\n".join([f"- {item}" for item in self._lote.historico])
                    if not historico_str:
                        historico_str = "Nenhuma operação registrada até o momento."
                    self._ui.exibir_resultado_operacao("HISTÓRICO DE AUDITORIA", historico_str)
                    self._ui.aguardar_confirmacao()

                elif opcao == 6:
                    self._ui.exibir_mensagem("\nEncerrando módulo de auditoria industrial...", "bold blue")
                    sleep(1)
                    break

        except KeyboardInterrupt:
            self._ui.exibir_mensagem("\n\nOperação interrompida pelo usuário. Encerramento seguro concluído.", "bold red")
            sys.exit(0)
        except Exception as err:
            self._ui.exibir_mensagem(f"\nOcorreu um erro não esperado na aplicação: {err}", "bold red")
            sys.exit(1)

    def _capturar_inteiro(self, mensagem: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Captura um número inteiro garantindo validação de intervalo e ausência de exceções."""
        while True:
            try:
                entrada = input(mensagem).strip()
                valor = int(entrada)
                if min_val is not None and valor < min_val:
                    self._ui.exibir_mensagem(f"O valor deve ser maior ou igual a {min_val}.", "alert")
                    continue
                if max_val is not None and valor > max_val:
                    self._ui.exibir_mensagem(f"O valor deve ser menor ou igual a {max_val}.", "alert")
                    continue
                return valor
            except ValueError:
                self._ui.exibir_mensagem("Entrada inválida. Digite um número inteiro válido.", "alert")

    def _capturar_float(self, mensagem: str) -> float:
        """Captura um número decimal (float) tratando possíveis exceções de digitação."""
        while True:
            try:
                entrada = input(mensagem).strip().replace(',', '.')
                return float(entrada)
            except ValueError:
                self._ui.exibir_mensagem("Entrada inválida. Digite um número decimal válido (ex: 10.5).", "alert")

    def _capturar_lista_floats(self, mensagem: str) -> List[float]:
        """Captura uma sequência de números separados por vírgula no terminal."""
        while True:
            try:
                entrada = input(mensagem).strip()
                if not entrada:
                    self._ui.exibir_mensagem("A entrada não pode estar vazia.", "alert")
                    continue
                partes = entrada.split(',')
                valores = [float(p.strip().replace(',', '.')) for p in partes]
                return valores
            except ValueError:
                self._ui.exibir_mensagem("Formato inválido. Certifique-se de separar os números por vírgula.", "alert")


if __name__ == "__main__":
    app = AuditoriaApp()
    app.executar()