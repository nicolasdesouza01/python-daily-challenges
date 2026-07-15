import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


class EstacaoMeteorologica:

    def __init__(self):
        self._leituras = []


    def adicionar_leitura(self, valor):
        try:
            temperatura = float(valor)
            self._leituras.append(temperatura)
            return True
        except ValueError:
            return False


    def limpar_dados(self):
        self._leituras.clear()


    def obter_dados_externos(self):
        # =====================================================================
        # ENDPOINT DE INTEGRAÇÃO COM API / BANCO DE DADOS
        # =====================================================================
        # Para conectar a uma API meteorológica real (como OpenWeatherMap):
        # 1. Importe a biblioteca 'requests' no topo do arquivo.
        # 2. Substitua o gerador aleatório abaixo pela requisição HTTP:
        #    response = requests.get("SUA_URL_DA_API_AQUI")
        #    dados = response.json()
        #    self.adicionar_leitura(dados["main"]["temp"])
        # =====================================================================
        
        self.limpar_dados()
        
        for _ in range(5):
            temperatura_simulada = round(random.uniform(12.0, 38.0), 1)
            self.adicionar_leitura(temperatura_simulada)


    def analisar_extremos(self):
        if not self._leituras:
            return None

        maior = max(self._leituras)
        menor = min(self._leituras)

        posicoes_maior = []
        posicoes_menor = []

        for indice, valor in enumerate(self._leituras):
            if valor == maior:
                posicoes_maior.append(indice + 1)
            
            if valor == menor:
                posicoes_menor.append(indice + 1)

        return {
            "maior": maior,
            "posicoes_maior": posicoes_maior,
            "menor": menor,
            "posicoes_menor": posicoes_menor
        }


    def gerar_relatorio_visual(self):
        if not self._leituras:
            console.print("[bold red]:warning: Erro: Nenhuma leitura disponível para gerar relatório.[/]")
            return

        resultado = self.analisar_extremos()
        
        tabela = Table(title=":thermometer: Leituras Registradas na Estação", expand=True)
        tabela.add_column("Posição", justify="center", style="cyan")
        tabela.add_column("Temperatura", justify="right", style="magenta")
        tabela.add_column("Alerta de Extremo", justify="center")

        for indice, valor in enumerate(self._leituras):
            posicao = indice + 1
            alerta = ""
            estilo_linha = "white"

            if valor == resultado["maior"]:
                alerta = "[bold red]:fire: MÁXIMO DETECTADO[/]"
                estilo_linha = "bold red"
            
            elif valor == resultado["menor"]:
                alerta = "[bold blue]:snowflake: MÍNIMO DETECTADO[/]"
                estilo_linha = "bold blue"

            tabela.add_row(
                str(posicao), 
                f"{valor:.1f} °C", 
                alerta,
                style=estilo_linha
            )

        console.print(tabela)
        console.print("\n")

        texto_maior_posicoes = ", ".join(map(str, resultado["posicoes_maior"]))
        texto_menor_posicoes = ", ".join(map(str, resultado["posicoes_menor"]))

        painel_resumo = Panel(
            f"[bold red]:fire: MAIOR TEMPERATURA:[/] [bold]{resultado['maior']:.1f} °C[/]\n"
            f"[dim]Ocorrida nas posições: {texto_maior_posicoes}[/]\n\n"
            f"[bold blue]:snowflake: MENOR TEMPERATURA:[/] [bold]{resultado['menor']:.1f} °C[/]\n"
            f"[dim]Ocorrida nas posições: {texto_menor_posicoes}[/]",
            title="[bold green]:white_check_mark: Análise Espacial de Extremos[/]",
            border_style="green"
        )
        
        console.print(painel_resumo)


def iniciar_sistema():
    estacao = EstacaoMeteorologica()
    
    while True:
        console.print("\n")
        
        menu_principal = Panel(
            "[bold cyan]1.[/] Entrada Manual (Demonstração de Terminal)\n"
            "[bold cyan]2.[/] Simulação de Endpoint API (Leitura de Rede)\n"
            "[bold red]3.[/] Encerrar Estação",
            title=":cyclone: PAINEL DE CONTROLE METEOROLÓGICO",
            border_style="cyan"
        )
        console.print(menu_principal)
        
        try:
            opcao = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3"])
        
        except KeyboardInterrupt:
            console.print("\n[bold red]:warning: Operação interrompida pelo usuário. Desligando...[/]")
            break
        
        if opcao == "1":
            estacao.limpar_dados()
            console.print("\n[bold yellow]:hourglass: Iniciando módulo de coleta manual...[/]\n")
            
            for i in range(1, 6):
                while True:
                    try:
                        entrada = Prompt.ask(f"Digite a temperatura para a posição {i}")
                        entrada_normalizada = entrada.replace(",", ".")
                        
                        if estacao.adicionar_leitura(entrada_normalizada):
                            break
                        else:
                            console.print("[bold red]:warning: Entrada inválida! Digite apenas números.[/]")
                    
                    except Exception:
                        console.print("[bold red]:warning: Ocorreu um erro inesperado na leitura. Tente novamente.[/]")
            
            with console.status("[bold green]:hourglass: Processando dados da estação...", spinner="dots"):
                time.sleep(1.5)
            
            console.print("\n")
            estacao.gerar_relatorio_visual()
            
        elif opcao == "2":
            with console.status("[bold yellow]:hourglass: Conectando ao endpoint da API meteorológica...", spinner="dots"):
                time.sleep(2.0)
                estacao.obter_dados_externos()
                
            console.print("\n[bold green]:white_check_mark: Dados importados com sucesso da API![/]\n")
            estacao.gerar_relatorio_visual()
            
        elif opcao == "3":
            console.print("\n[bold yellow]:hourglass: Desligando sensores e salvando logs...[/]")
            time.sleep(1.0)
            console.print("[bold green]:white_check_mark: Estação finalizada com sucesso. Até logo![/]\n")
            break


if __name__ == "__main__":
    iniciar_sistema()