import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

console = Console()


def leia_int(mensagem=""):
    while True:
        try:
            entrada = console.input(f"[bold blue]{mensagem}[/]")
            
            if entrada.strip() == "":
                raise ValueError
                
            valor = int(entrada)
            return valor
            
        except (ValueError, TypeError):
            console.print("\n[bold red]:warning: ERRO! Por favor, digite um número inteiro válido.[/]\n")
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]:backhand_index_pointing_right: Usuário preferiu interromper a entrada de dados.[/]")
            return None


def voto(ano_nascimento):
    try:
        ano_atual = time.localtime().tm_year
        idade = ano_atual - ano_nascimento
        
        if status_carregamento("Analisando dados no sistema..."):
            return None
            
        if idade < 0:
            return f"Idade [red]inválida[/] ({idade} anos). O ano de nascimento fornecido está no futuro!"
            
        if status_carregamento("Calculando obrigatoriedade eleitoral..."):
            return None
            
        if idade < 16:
            return f"Com {idade} anos: [bold red]NÃO VOTA[/]."
        elif 16 <= idade < 18 or idade > 65:
            return f"Com {idade} anos: [bold yellow]VOTO OPCIONAL[/]."
        else:
            return f"Com {idade} anos: [bold green]VOTO OBRIGATÓRIO[/]."
            
    except Exception:
        return "[bold red]Erro ao processar a situação do voto.[/]"


def status_carregamento(mensagem_status):
    try:
        for passo in track(range(3), description=f"[bold cyan]{mensagem_status}[/]"):
            time.sleep(0.5)
        return False
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]:warning: Carregamento interrompido pelo usuário.[/]")
        return True


try:
    console.clear()
    
    status_carregamento("Inicializando o sistema de consulta...")
    console.print()
    
    interface_titulo = Panel(
        "[bold white]:framed_picture: SISTEMA VERIFICADOR DE SITUAÇÃO ELEITORAL :framed_picture:[/]",
        subtitle="[cyan]Consulta Automatizada[/]",
        style="bold turquoise2",
        expand=False
    )
    console.print(interface_titulo)
    console.print()
    
    while True:
        nascimento = leia_int("Digite o ano de nascimento: ")
        
        if nascimento is None:
            break
            
        if nascimento > 0:
            resultado_voto = voto(nascimento)
            
            if resultado_voto is None:
                break
                
            console.print()
            painel_resultado = Panel(
                f"{resultado_voto}",
                title="[bold text]Resultado da Consulta[/]",
                border_style="green",
                expand=False
            )
            console.print(painel_resultado)
            console.print()
            
        while True:
            try:
                resposta = console.input("[bold white]Quer continuar? [S/N]: [/]").strip().upper()
                if resposta in ("S", "N"):
                    break
                console.print("[bold red]Resposta inválida! Digite apenas S ou N.[/]\n")
            except (ValueError, TypeError):
                console.print("[bold red]Erro na leitura da resposta.[/]\n")
            except KeyboardInterrupt:
                resposta = "N"
                break
                
        if resposta == "N":
            break
            
        console.print("\n" + "—" * 50 + "\n")

except Exception as erro:
    console.print(f"\n[bold red]:cross_mark: Ocorreu um erro inesperado no sistema: {erro}[/]")

console.print()
box_final = Panel(
    "[bold magenta]:waving_hand: Programa finalizado com sucesso! Até logo.[/]",
    border_style="magenta",
    expand=False
)
console.print(box_final)
console.print()