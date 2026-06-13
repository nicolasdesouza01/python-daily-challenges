from datetime import date
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class AnalisadorEleitoral:

    def __init__(self, ano_nascimento):
        self._ano_nascimento = ano_nascimento
        self._ano_atual = 2026

    def _calcular_idade(self):
        return self._ano_atual - self._ano_nascimento

    def obter_relatorio(self):
        idade = self._calcular_idade()
        
        if idade < 0 or idade > 125:
            return "Inconsistente", ":alien: [bold red]ANO DE NASCIMENTO INVÁLIDO[/bold red]"
            
        if idade < 16:
            return f"{idade} anos", ":prohibited: [bold red]VOTO NEGADO[/bold red]"
        elif 16 <= idade < 18 or idade >= 70:
            return f"{idade} anos", ":envelope_with_arrow: [bold yellow]VOTO OPCIONAL[/bold yellow]"
        else:
            return f"{idade} anos", ":heavy_check_mark: [bold green]VOTO OBRIGATÓRIO[/bold green]"


console.print("\n")
console.print(Panel.fit(" :computer: [bold white]SISTEMA DE CONSULTA ELEITORAL PROFISSIONAL[/bold white] :computer: ", style="bold blue"))
console.print("\n")

while True:
    try:
        entrada = input("Digite o ano de nascimento (ou 'S' para sair): ").strip()

        if entrada.upper() == 'S':
            console.print("\n:wave: [bold cyan]Encerrando o sistema. Até a próxima![/bold cyan]\n")
            break

        if not entrada:
            console.print("\n:warning: [bold yellow]Atenção: Nenhuma informação foi digitada![/bold yellow]\n")
            continue

        nascimento = int(entrada)

        console.print("\n")
        with console.status("[bold green]Consultando base de dados nacional...[/bold green]", spinner="aesthetic"):
            sleep(1.2)

        analisador = AnalisadorEleitoral(nascimento)
        idade_formatada, status_voto = analisador.obter_relatorio()

        tabela = Table(title="[bold magenta]:page_facing_up: BOLETIM INFORMATIVO OFICIAL[/bold magenta]", show_header=True, header_style="bold cyan")
        
        tabela.add_column("Critério de Análise", justify="left", style="bold white")
        tabela.add_column("Resultado do Sistema", justify="center", style="bright_white")

        tabela.add_row("Idade Real do Cidadão", idade_formatada)
        tabela.add_row("Status da Obrigação", status_voto)

        console.print(tabela)
        console.print("\n" + "—" * 60 + "\n")

    except ValueError:
        console.print("\n:x: [bold red]ERRO DE ENTRADA:[/bold red] Por favor, insira um ano válido com 4 dígitos ou 'S' para sair.\n")

    except Exception as erro:
        console.print(f"\n:warning: [bold red]OCORREU UM PROBLEMA INESPERADO:[/bold red] {erro}\n")
