import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class Endereco:
    """Representa a estrutura de um endereço retornado por consulta de CEP."""
    cep: str
    logradouro: str
    bairro: str
    localidade: str
    uf: str

    def formatar_resumido(self) -> str:
        """Retorna a localização formatada no padrão 'Cidade/UF'."""
        return f"{self.localidade}/{self.uf}"


class ServicoViaCEP:
    """Responsável por integrar e consultar a API pública do ViaCEP."""

    _URL_BASE: str = "https://viacep.com.br/ws/{}/json/"

    def buscar_cep(self, cep: str) -> Optional[Endereco]:
        """Consulta os dados geográficos de um CEP na API do ViaCEP."""
        cep_limpo = "".join(filter(str.isdigit, cep))
        if len(cep_limpo) != 8:
            return None

        try:
            resposta = requests.get(self._URL_BASE.format(cep_limpo), timeout=5.0)
            if resposta.status_code != 200:
                return None

            dados = resposta.json()
            if "erro" in dados:
                return None

            return Endereco(
                cep=dados.get("cep", cep_limpo),
                logradouro=dados.get("logradouro", "Não informado"),
                bairro=dados.get("bairro", "Não informado"),
                localidade=dados.get("localidade", "Desconhecida"),
                uf=dados.get("uf", "EX")
            )
        except Exception:
            return None


class MotorFreteViaCEP:
    """Motor de precificação e estimativa de prazo baseado em cruzamento geográfico de CEPs."""

    _TAXA_BASE_OPERACIONAL: float = 18.00
    _ADICIONAL_PESO_KG: float = 3.20

    def estimar_rota_e_prazo(self, origem: Endereco, destino: Endereco) -> Tuple[float, int, str]:
        """Determina a distância aproximada, o prazo em dias e a categoria da rota."""
        if origem.localidade.lower() == destino.localidade.lower() and origem.uf == destino.uf:
            return 25.0, 1, "Entregas Locais (Mesma Cidade)"
        if origem.uf == destino.uf:
            return 180.0, 3, "Estadual (Intra-estado)"
        return 650.0, 6, "Interestadual (Nacional)"

    def processar_cotacao(self, origem: Endereco, destino: Endereco, peso_kg: float) -> Dict[str, Any]:
        """Calcula o frete completo unindo a busca por CEP, peso e matriz geográfica."""
        if peso_kg <= 0:
            raise ValueError("O peso precisa ser maior que zero.")

        distancia, prazo, categoria = self.estimar_rota_e_prazo(origem, destino)
        custo_distancia = distancia * 0.75
        custo_peso = peso_kg * self._ADICIONAL_PESO_KG
        total = self._TAXA_BASE_OPERACIONAL + custo_distancia + custo_peso

        return {
            "origem": origem, "destino": destino, "categoria_rota": categoria,
            "distancia_estimada": distancia, "prazo_dias": prazo, "peso_kg": peso_kg,
            "taxa_operacional": self._TAXA_BASE_OPERACIONAL,
            "custo_distancia": custo_distancia, "custo_peso": custo_peso, "total": total
        }


class InterfaceHUD:
    """Gerencia a interface de usuário no terminal usando componentes do Rich."""

    def __init__(self) -> None:
        """Inicializa o console do Rich."""
        self._console: Console = Console()

    def exibir_banner(self) -> None:
        """Renderiza o painel principal do sistema."""
        self._console.clear()
        self._console.print(Panel.fit(
            "[bold cyan]🚚 FRETEEXPRESS - CONSULTA LOGÍSTICA DE FRETE 📦[/bold cyan]\n"
            "[dim]Cotação Automática por CEP | Módulo de Mercado[/dim]",
            border_style="cyan"
        ))

    def simular_carregamento(self, mensagem: str) -> None:
        """Exibe animação de processamento para buscas de rede ou cálculos."""
        with Progress(SpinnerColumn(), TextColumn("[bold yellow]{task.description}"), transient=True, console=self._console) as progress:
            progress.add_task(description=mensagem, total=None)
            time.sleep(1.0)

    def capturar_endereco_por_cep(self, servico: ServicoViaCEP, tipo: str) -> Endereco:
        """Solicita o CEP ao usuário, realiza a busca na API ViaCEP e valida a resposta."""
        while True:
            cep_input = Prompt.ask(f"Digite o CEP de [bold magenta]{tipo}[/bold magenta] (ex: 01001-000)")
            self.simular_carregamento(f"Consultando CEP {cep_input}...")
            endereco = servico.buscar_cep(cep_input)
            
            if endereco:
                self._console.print(f"[bold green]✔️ Endereço Encontrado:[/bold green] {endereco.logradouro} - {endereco.bairro} ({endereco.formatar_resumido()})")
                return endereco
            self._console.print("[bold red]❌ CEP não encontrado ou falha de conexão. Tente novamente.[/bold red]")

    def ler_peso(self) -> float:
        """Solicita e valida o peso da encomenda."""
        while True:
            try:
                peso = FloatPrompt.ask("Peso total da encomenda (Kg)")
                if peso > 0:
                    return peso
                self._console.print("[bold red]❌ O peso deve ser maior que zero.[/bold red]")
            except Exception:
                self._console.print("[bold red]❌ Entrada inválida. Digite um número válido.[/bold red]")

    def exibir_resultado(self, dados: Dict[str, Any]) -> None:
        """Renderiza as tabelas de rota e custos da cotação."""
        origem, destino = dados["origem"], dados["destino"]

        tabela_rota = Table(title="🗺️ ROTA PROCESSADA", header_style="bold cyan")
        tabela_rota.add_column("Ponto", style="bold white")
        tabela_rota.add_column("CEP", style="yellow")
        tabela_rota.add_column("Cidade/UF", style="green")
        tabela_rota.add_column("Logradouro", style="dim")
        tabela_rota.add_row("Origem", origem.cep, origem.formatar_resumido(), origem.logradouro)
        tabela_rota.add_row("Destino", destino.cep, destino.formatar_resumido(), destino.logradouro)

        tabela_valores = Table(title="📋 COMPOSIÇÃO DO VALOR E PRAZO", header_style="bold magenta")
        tabela_valores.add_column("Descrição", style="bold white")
        tabela_valores.add_column("Detalhe", justify="center", style="dim")
        tabela_valores.add_column("Valor (R$)", justify="right", style="green")
        tabela_valores.add_row("🏠 Taxa Operacional Fixa", "Processamento e Coleta", f"{dados['taxa_operacional']:.2f}")
        tabela_valores.add_row("📍 Custo de Deslocamento", f"{dados['categoria_rota']} (~{dados['distancia_estimada']:.0f} Km)", f"{dados['custo_distancia']:.2f}")
        tabela_valores.add_row("⚖️ Adicional por Carga", f"{dados['peso_kg']:.2f} Kg", f"{dados['custo_peso']:.2f}")

        self._console.print("\n", tabela_rota, "\n", tabela_valores)
        self._console.print(Panel(
            f"[bold white]VALOR TOTAL DO FRETE:[/bold white] [bold green]R$ {dados['total']:.2f}[/bold green]\n"
            f"[bold white]PRAZO ESTIMADO DE ENTREGA:[/bold white] [bold yellow]{dados['prazo_dias']} dia(s) útil(eis)[/bold yellow]",
            border_style="green", expand=False
        ))

    def exibir_mensagem(self, texto: str, estilo: str = "white") -> None:
        """Imprime uma mensagem formatada no terminal."""
        self._console.print(f"[{estilo}]{texto}[/{estilo}]")


class AplicacaoSistema:
    """Classe principal de controle da execução da aplicação."""

    def __init__(self) -> None:
        """Inicializa todos os módulos do sistema."""
        self._hud = InterfaceHUD()
        self._servico_via_cep = ServicoViaCEP()
        self._motor_frete = MotorFreteViaCEP()

    def executar(self) -> None:
        """Executa o loop principal com tratamento de interrupções e erros."""
        try:
            self._hud.exibir_banner()

            while True:
                self._hud.exibir_mensagem("\n[bold yellow]--- NOVA COTAÇÃO DE FRETE ---[/bold yellow]")
                origem = self._hud.capturar_endereco_por_cep(self._servico_via_cep, "ORIGEM")
                destino = self._hud.capturar_endereco_por_cep(self._servico_via_cep, "DESTINO")
                peso = self._hud.ler_peso()

                self._hud.simular_carregamento("Calculando matrizes de frete e prazos...")
                resultado = self._motor_frete.processar_cotacao(origem, destino, peso)
                self._hud.exibir_resultado(resultado)

                if Prompt.ask("\nDeseja realizar outra cotação?", choices=["s", "n"], default="s").lower() != "s":
                    break

            self._hud.exibir_mensagem("\n👋 Sessão encerrada. Até a próxima!", "bold cyan")
        except KeyboardInterrupt:
            self._hud.exibir_mensagem("\n\n⚠️ Operação interrompida pelo usuário. Sistema encerrado.", "yellow")
        except Exception as erro:
            self._hud.exibir_mensagem(f"\n❌ Ocorreu um erro na execução: {erro}", "bold red")


if __name__ == "__main__":
    app = AplicacaoSistema()
    app.executar()