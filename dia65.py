# AVISO: Código de demonstração de temperatura. Não possui funcionamento real.

import random
from time import sleep
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align


class MonitorTemperatura:
    """
    Classe para simular o monitoramento de temperatura de servidores de um Data Center.
    """

    def __init__(self, qtd_maquinas=5):
        """
        Inicializa o monitor definindo a quantidade de máquinas simuladas.
        """
        try:
            if not isinstance(qtd_maquinas, int) or qtd_maquinas <= 0:
                raise ValueError("A quantidade de máquinas precisa ser um número inteiro válido e maior que zero.")
            
            self._qtd_maquinas = qtd_maquinas
            self._console = Console()
            
        except Exception as erro:
            print(f"Ocorreu um erro ao inicializar a estrutura do sistema: {erro}")


    def _gerar_temperaturas(self):
        """
        Gera uma lista de temperaturas aleatórias simuladas em graus Celsius.
        Método interno protegido por convenção de nomenclatura (_).
        """
        try:
            temperaturas_geradas = []
            
            for _ in range(self._qtd_maquinas):
                temperaturas_geradas.append(random.randint(20, 105))
                
            return temperaturas_geradas
            
        except Exception as erro:
            self._console.print(f"[bold red]Erro ao tentar ler os sensores de temperatura:[/] {erro}")
            return []


    def _analisar_maior(self, temperaturas):
        """
        Processa o fluxo de dados para encontrar o maior valor térmico e sua respectiva máquina.
        Método interno protegido por convenção de nomenclatura (_).
        """
        try:
            if not temperaturas:
                return None, None
                
            maior_valor = temperaturas[0]
            indice_maior = 0
            
            for indice, valor in enumerate(temperaturas):
                if valor > maior_valor:
                    maior_valor = valor
                    indice_maior = indice
                    
            return indice_maior + 1, maior_valor
            
        except Exception as erro:
            self._console.print(f"[bold red]Erro interno ao processar a análise de pico térmico:[/] {erro}")
            return None, None


    def executar_simulacao(self):
        """
        Orquestra a execução da simulação, monta a interface visual no terminal e trata erros.
        """
        try:
            self._console.clear()
            
            titulo_centralizado = Align.center(
                "[bold cyan]SISTEMA DE MONITORAMENTO DE INFRAESTRUTURA[/]\n"
                "[dim white]Simulador de Telemetria Térmica de Servidores[/]"
            )
            
            self._console.print(Panel(titulo_centralizado, border_style="cyan"))
            self._console.print("\n[yellow]Conectando aos sensores das máquinas virtuais... Aguarde :hourglass_flowing_sand:[/]\n")
            
            sleep(1.5)
            
            dados_temperatura = self._gerar_temperaturas()
            
            if not dados_temperatura:
                return
                
            tabela_status = Table(title="Leituras Atuais do Cluster", show_header=True, header_style="bold blue")
            tabela_status.add_column("Identificação", justify="center")
            tabela_status.add_column("Temperatura", justify="center")
            tabela_status.add_column("Status Operacional", justify="center")
            
            for i, temp in enumerate(dados_temperatura):
                identificador = f"Máquina {i + 1}"
                
                if temp >= 80:
                    status_texto = "[bold red]CRÍTICO :fire:[/]"
                elif temp >= 50:
                    status_texto = "[bold yellow]ALERTA :warning:[/]"
                else:
                    status_texto = "[bold green]NORMAL :white_check_mark:[/]"
                    
                tabela_status.add_row(identificador, f"{temp}°C", status_texto)
                
            self._console.print(tabela_status)
            
            maquina_alvo, valor_pico = self._analisar_maior(dados_temperatura)
            
            if maquina_alvo is not None:
                mensagem_alerta = (
                    f"Total de ativos escaneados no cluster: [bold]{self._qtd_maquinas}[/]\n\n"
                    f"O pico máximo de temperatura registrado foi de [bold red]{valor_pico}°C[/].\n"
                    f"Hardware com maior sobrecarga térmica detectado: [bold yellow]Máquina {maquina_alvo}[/]"
                )
                
                self._console.print("\n" + "─" * 60 + "\n")
                self._console.print(Panel(mensagem_alerta, title="[bold red]Diagnóstico de Pico Térmico[/]", border_style="red"))
                
        except KeyboardInterrupt:
            self._console.print("\n[bold yellow]Rotina de monitoramento interrompida manualmente pelo operador.[/]")
            
        except Exception as erro:
            print(f"Ocorreu uma falha inesperada durante a execução do painel: {erro}")


if __name__ == "__main__":
    monitor = MonitorTemperatura(qtd_maquinas=5)
    monitor.executar_simulacao()