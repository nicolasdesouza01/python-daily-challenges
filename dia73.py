import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class LeituraMeteorologica:
    """Representa os dados termodinâmicos básicos coletados na superfície."""

    def __init__(self, temperatura: float, ponto_orvalho: float) -> None:
        """Inicializa a leitura com temperatura do ar e ponto de orvalho em Celsius."""
        self._temperatura = temperatura
        self._ponto_orvalho = ponto_orvalho

    @property
    def temperatura(self) -> float:
        """Retorna a temperatura do ar (°C)."""
        return self._temperatura

    @property
    def ponto_orvalho(self) -> float:
        """Retorna o ponto de orvalho (°C)."""
        return self._ponto_orvalho

    def calcular_indice_soma(self) -> float:
        """Calcula o índice de combinação convectiva simples baseado na soma T + Td."""
        return self._temperatura + self._ponto_orvalho

    def calcular_depressao(self) -> float:
        """Calcula a depressão do ponto de orvalho (diferença entre T e Td)."""
        return self._temperatura - self._ponto_orvalho


class AnalisadorConvectivo:
    """Realiza análises meteorológicas e prevê o potencial de tempo severo."""

    def __init__(self, leitura: LeituraMeteorologica) -> None:
        """Inicializa o analisador com uma leitura meteorológica válida."""
        self._leitura = leitura

    def diagnosticar_risco(self) -> dict:
        """Classifica o risco de convecção e tempo severo com base nos índices."""
        soma = self._leitura.calcular_indice_soma()
        depressao = self._leitura.calcular_depressao()

        if soma < 30.0:
            nivel = "BAIXO"
            descricao = "Massa de ar seca e estável. Risco insignificante de chuva."
            cor = "green"
            icone = ":sun:"
        elif soma < 45.0:
            nivel = "MODERADO"
            descricao = "Umidade presente. Possibilidade de chuvas leves ou isoladas."
            cor = "yellow"
            icone = ":cloud:"
        elif soma < 55.0:
            nivel = "ALTO"
            descricao = "Instabilidade moderada/alta. Risco de pancadas fortes e trovoadas."
            cor = "orange1"
            icone = ":cloud_with_rain:"
        else:
            nivel = "SEVERO"
            descricao = "Alta energia termodinâmica. Forte potencial para tempestades severas!"
            cor = "red"
            icone = ":zap:"

        return {
            "soma": soma,
            "depressao": depressao,
            "nivel": nivel,
            "descricao": descricao,
            "cor": cor,
            "icone": icone
        }


class InterfaceTerminal:
    """Gerencia a interface visual Rich e a interação segura com o usuário."""

    def __init__(self) -> None:
        """Inicializa o console Rich para renderização gráfica no terminal."""
        self._console = Console()

    def exibir_cabecalho(self) -> None:
        """Exibe o painel inicial de apresentação do sistema."""
        self._console.clear()
        painel = Panel(
            "[bold cyan]:thermometer: MONITOR DE INSTABILIDADE METEOROLÓGICA :droplet:[/bold cyan]\n"
            "[dim]Análise Termodinâmica de Convecção e Potencial de Tempestades[/dim]",
            border_style="cyan",
            expand=False
        )
        self._console.print(painel)

    def obter_numero_valido(self, mensagem: str, min_val: float = -50.0, max_val: float = 60.0) -> float:
        """Solicita e valida uma entrada numérica flutuante do usuário sem permitir exceções."""
        while True:
            try:
                entrada = self._console.input(f"[bold yellow]{mensagem}[/bold yellow]")
                valor = float(entrada.replace(",", "."))
                if min_val <= valor <= max_val:
                    return valor
                self._console.print(f"[bold red]:x: Por favor, insira um valor entre {min_val}°C e {max_val}°C.[/bold red]")
            except ValueError:
                self._console.print("[bold red]:x: Entrada inválida. Digite apenas números válidos.[/bold red]")

    def simular_processamento(self) -> None:
        """Simula o cálculo termodinâmico com um spinner visual do Rich."""
        with self._console.status("[bold green]Analisando estabilidade atmosférica...[/bold green]", spinner="dots"):
            time.sleep(1.2)

    def exibir_relatorio(self, leitura: LeituraMeteorologica, diagnostico: dict) -> None:
        """Apresenta o relatório final formatado em uma tabela estilizada e painel de alerta."""
        tabela = Table(title=":bar_chart: Parâmetros e Resultados", border_style="bold blue")
        tabela.add_column("Métrica", style="bold white")
        tabela.add_column("Valor Observado", justify="right", style="bold cyan")

        tabela.add_row("Temperatura do Ar (T)", f"{leitura.temperatura:.1f} °C")
        tabela.add_row("Ponto de Orvalho (Td)", f"{leitura.ponto_orvalho:.1f} °C")
        tabela.add_row("Índice de Soma (T + Td)", f"{diagnostico['soma']:.1f}")
        tabela.add_row("Depressão do Ponto de Orvalho", f"{diagnostico['depressao']:.1f} °C")

        self._console.print(tabela)

        cor = diagnostico["cor"]
        painel_resultado = Panel(
            f"[bold {cor}]{diagnostico['icone']} POTENCIAL DE TEMPESTADE: {diagnostico['nivel']}[/bold {cor}]\n\n"
            f"[white]{diagnostico['descricao']}[/white]",
            title="[bold white]Diagnóstico Convectivo[/bold white]",
            border_style=cor,
            expand=False
        )
        self._console.print(painel_resultado)

    def executar(self) -> None:
        """Fluxo principal de execução do aplicativo com tratamento total de interrupções."""
        try:
            self.exibir_cabecalho()
            
            temp = self.obter_numero_valido("\n:thermometer: Digite a Temperatura do Ar (°C): ")
            
            while True:
                orvalho = self.obter_numero_valido(":droplet: Digite o Ponto de Orvalho (°C): ")
                if orvalho <= temp:
                    break
                self._console.print("[bold red]:warning: O Ponto de Orvalho não pode ser maior que a Temperatura do Ar![/bold red]")

            leitura = LeituraMeteorologica(temp, orvalho)
            analisador = AnalisadorConvectivo(leitura)
            
            self.simular_processamento()
            diagnostico = analisador.diagnosticar_risco()
            
            self.exibir_relatorio(leitura, diagnostico)
            
            self._console.print("\n[dim green]Análise concluída com sucesso![/dim green]\n")

        except KeyboardInterrupt:
            self._console.print("\n\n[bold yellow]:door: Operação interrompida pelo usuário. Encerrando de forma segura...[/bold yellow]\n")
            sys.exit(0)
        except Exception as e:
            self._console.print(f"\n[bold red]:exclamation: Ocorreu um erro inesperado na execução: {e}[/bold red]\n")


if __name__ == "__main__":
    app = InterfaceTerminal()
    app.executar()