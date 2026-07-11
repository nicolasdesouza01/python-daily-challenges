import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class SimuladorAdiabatico:

    def __init__(self, temperatura_superficie, tipo_gradiente):
        self._temperatura_superficie = temperatura_superficie
        self._tipo_gradiente = tipo_gradiente
        self._razao_termica = 0.0
        self._nome_gradiente = ""
        
        if self._tipo_gradiente == 1:
            self._razao_termica = -6.5
            self._nome_gradiente = "Padrão Internacional (ISA)"
        elif self._tipo_gradiente == 2:
            self._razao_termica = -9.8
            self._nome_gradiente = "Adiabático Seco (DALR)"
        elif self._tipo_gradiente == 3:
            self._razao_termica = -5.0
            self._nome_gradiente = "Adiabático Úmido (SALR)"

    def gerar_analise_vertical(self):
        tabela = Table(
            title=f":cloud: PERFIL TÉRMICO: {self._nome_gradiente} :cloud:", 
            style="bold blue",
            header_style="bold magenta"
        )
        
        tabela.add_column("Nível", justify="center", style="yellow")
        tabela.add_column("Altitude", justify="center", style="green")
        tabela.add_column("Temperatura", justify="center", style="cyan")

        for passo in range(1, 11):
            altitude = (passo - 1) * 1000
            
            temperatura_nivel = self._temperatura_superficie + (passo - 1) * self._razao_termica
            
            tabela.add_row(
                f"{passo}° Nível", 
                f"{altitude} m", 
                f"{temperatura_nivel:.1f} °C"
            )
            
        return tabela

def executar_sistema():
    console = Console()
    
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]:cyclone: SONDAGEM TÉRMICA SIMULADA - V 2.0 :cyclone:[/]\n[italic white]Modelagem Dinâmica de Decaimento de Temperatura[/]", 
            border_style="blue"
        )
    )
    console.print()
    
    while True:
        try:
            entrada_temp = console.input("[bold white]Digite a temperatura na superfície em °C (Inteiro): [/]")
            temp_inicial = int(entrada_temp)
            break
        except ValueError:
            console.print("[bold red]:warning: Erro de Entrada! Digite um número inteiro válido.[/]\n")

    console.print("\n[bold magenta]Selecione o Perfil Atmosférico para a PA:[/]")
    console.print("[yellow]1.[/] Gradiente Padrão Internacional (-6.5°C/km)")
    console.print("[yellow]2.[/] Gradiente Adiabático Seco - DALR (-9.8°C/km)")
    console.print("[yellow]3.[/] Gradiente Adiabático Úmido - SALR (-5.0°C/km)\n")

    while True:
        try:
            entrada_opcao = console.input("[bold white]Escolha uma opção (1 a 3): [/]")
            opcao = int(entrada_opcao)
            
            if opcao not in [1, 2, 3]:
                console.print("[bold red]:warning: Opção inválida! Escolha 1, 2 ou 3.[/]\n")
                continue
                
            break
        except ValueError:
            console.print("[bold red]:warning: Erro de Entrada! Digite apenas o número da opção.[/]\n")

    console.print()
    
    with console.status("[bold green]Coletando dados barométricos simulados...", spinner="earth"):
        time.sleep(1.2)
        
    with console.status("[bold yellow]Processando taxas termodinâmicas da parcela...", spinner="runner"):
        time.sleep(1.2)
        
    console.print()

    try:
        simulador = SimuladorAdiabatico(temp_inicial, opcao)
        tabela_resultados = simulador.gerar_analise_vertical()
        
        console.print(tabela_resultados)
        
        console.print()
        console.print(
            Panel(
                "[bold yellow]:glowing_star: NOTA DE ADVERTÊNCIA METEOROLÓGICA :glowing_star:[/]\n"
                "[white]Este programa é uma aproximação teórica linear baseada em Progressão Aritmética. "
                "A atmosfera real apresenta variações não-lineares, camadas de inversão térmica "
                "e interações dinâmicas que só podem ser medidas com radiossondagens reais (gibi Skew-T). "
                "Uso estritamente educacional.[/]",
                title="[bold red]AVISO[/]",
                border_style="yellow"
            )
        )
        
        console.print("\n[bold green]:sparkles: PROCESSO FINALIZADO COM SUCESSO :sparkles:\n")
        
    except Exception:
        console.print("[bold red]:warning: Erro crítico ao renderizar os perfis da troposfera.[/]\n")

if __name__ == "__main__":
    executar_sistema()