import time
from typing import Generator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt


console = Console()


class PlanoTreinoPA:
    """
    Representa a regra de negócio da Progressão Aritmética adaptada 
    para cargas de treino e evolução de metas.
    """

    def __init__(self, exercicio: str, carga_inicial: int, incremento: int) -> None:
        """
        Configura os parâmetros básicos da progressão.
        """
        self.exercicio = exercicio
        self._carga_inicial = carga_inicial
        self._incremento = incremento

    @property
    def carga_inicial(self) -> int:
        """Retorna a carga inicial configurada."""
        return self._carga_inicial

    @property
    def incremento(self) -> int:
        """Retorna a razão de incremento por ciclo."""
        return self._incremento

    def gerador_progresso(self, inicio_ciclo: int, quantidade: int) -> Generator[tuple[int, int], None, None]:
        """
        Gerador (Yield) que calcula os termos da PA sob demanda.
        Retorna uma tupla contendo o número do ciclo e a meta de carga.
        """
        termo_atual = self._carga_inicial + (inicio_ciclo - 1) * self._incremento
        for ciclo in range(inicio_ciclo, inicio_ciclo + quantidade):
            yield (ciclo, termo_atual)
            termo_atual += self._incremento

    def calcular_volume_total(self, total_ciclos: int) -> int:
        """
        Calcula a soma total de cargas acumuladas usando a fórmula da Soma da PA:
        Sn = (n * (a1 + an)) / 2
        """
        ultimo_termo = self._carga_inicial + (total_ciclos - 1) * self._incremento
        soma = (total_ciclos * (self._carga_inicial + ultimo_termo)) // 2
        return soma


class SistemaTreinoCLI:
    """
    Gerencia a interface de usuário (HUD) via terminal, orquestrando 
    a execução com resiliência a falhas.
    """

    def _exibir_cabecalho(self) -> None:
        """Renderiza o painel principal da HUD no terminal."""
        console.clear()
        console.print(
            Panel.fit(
                "⚡ [bold cyan]SYSTEM FIT[/bold cyan] ⚡\n"
                "🏋️  [yellow]Gerenciador de Metas Progressivas (PA)[/yellow] 📈",
                border_style="magenta",
                padding=(1, 4)
            )
        )

    def _animar_carregamento(self, mensagem: str) -> None:
        """Exibe uma animação de carregamento rápida de exatamente 1 segundo."""
        with console.status(f"[bold blue]{mensagem}[/bold blue]", spinner="dots"):
            time.sleep(1.0)

    def executar(self) -> None:
        """
        Loop principal de execução da aplicação CLI.
        """
        try:
            self._exibir_cabecalho()

            exercicio = Prompt.ask("\n🎯 [bold yellow]Qual o exercício/meta?[/bold yellow] [dim](Ex: Flexões, Corrida em min, Agachamentos)[/dim]")
            
            carga_inicial = IntPrompt.ask(
                "🚀 [bold yellow]Qual a carga inicial no 1º ciclo?[/bold yellow]",
                default=10
            )
            
            incremento = IntPrompt.ask(
                "➕ [bold yellow]Qual o ganho por ciclo (Razão da PA)?[/bold yellow]",
                default=5
            )

            plano = PlanoTreinoPA(exercicio, carga_inicial, incremento)

            ciclo_atual = 1
            quantidade_solicitada = 10
            total_ciclos_gerados = 0

            while quantidade_solicitada > 0:
                self._animar_carregamento("⚙️  Gerando evolução do plano de treino...")

                table = Table(
                    title=f"\n📋 [bold underline]Planilha de Evolução: {plano.exercicio}[/bold underline] 📊",
                    show_header=True,
                    header_style="bold magenta",
                    border_style="bright_blue"
                )
                table.add_column("📅 Ciclo (Semana/Série)", style="cyan", justify="center")
                table.add_column("💪 Meta de Carga / Repetições", style="green", justify="right")

                novos_termos = list(plano.gerador_progresso(ciclo_atual, quantidade_solicitada))

                for ciclo, meta in novos_termos:
                    table.add_row(f"Ciclo {ciclo}", f"{meta} {plano.exercicio}")

                total_ciclos_gerados += quantidade_solicitada
                ciclo_atual += quantidade_solicitada

                console.print(table)

                volume_total = plano.calcular_volume_total(total_ciclos_gerados)
                media_por_ciclo = volume_total / total_ciclos_gerados

                painel_metricas = (
                    f"🔄 [bold cyan]Ciclos planejados:[/bold cyan] [bold white]{total_ciclos_gerados}[/bold white]\n"
                    f"🔥 [bold red]Volume total acumulado:[/bold red] [bold yellow]{volume_total} {plano.exercicio}[/bold yellow]\n"
                    f"📊 [bold green]Média por ciclo:[/bold green] [bold white]{media_por_ciclo:.1f} {plano.exercicio}[/bold white]"
                )
                
                console.print(
                    Panel(
                        painel_metricas, 
                        title="🏆 [bold gold1]Resumo de Desempenho Acumulado[/bold gold1]", 
                        border_style="yellow"
                    )
                )

                try:
                    mais = IntPrompt.ask(
                        "\n➕ [bold yellow]Deseja adicionar quantos ciclos a mais ao planejamento?[/bold yellow] [dim](Digite 0 para finalizar)[/dim]",
                        default=0
                    )
                    quantidade_solicitada = mais
                except (KeyboardInterrupt, EOFError):
                    break

            self._encerrar_sistema()

        except (KeyboardInterrupt, EOFError):
            self._encerrar_sistema()
        except Exception as e:
            console.print(f"\n❌ [bold red]Ocorreu um erro inesperado no sistema:[/bold red] {e}")

    def _encerrar_sistema(self) -> None:
        """Finaliza a execução do programa com uma mensagem amigável."""
        self._animar_carregamento("🔒 Salvando sessão e finalizando...")
        console.print("\n👋 [bold red]Encerrando o programa de forma segura...[/bold red]")
        console.print("💯 [bold green]Treino planejado com sucesso. Mantenha o foco e até a próxima![/bold green] 🏋️\n")


if __name__ == "__main__":
    app = SistemaTreinoCLI()
    app.executar()