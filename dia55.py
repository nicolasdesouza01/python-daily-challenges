import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Pessoa:

    def __init__(self, nome: str, matricula: int):
        self._nome = nome
        self._matricula = matricula


    def obter_nome(self) -> str:
        return self._nome


    def obter_matricula(self) -> int:
        return self._matricula


    def alterar_nome(self, novo_nome: str):
        self._nome = novo_nome


    def alterar_matricula(self, nova_matricula: int):
        self._matricula = nova_matricula


class SistemaRegistroMatriculas:

    def __init__(self):
        self._lista_pessoas = []


    def executar(self):
        console.print(
            Panel.fit(
                "[bold blue]Sistema de Registro e Auditoria de Matrículas[/bold blue]\n[white]Módulo de Homologação de Dados Cadastrais[/white]",
                title="[bold white]Controle de Acesso[/bold white]"
            )
        )

        contador = 1
        executando = True

        while executando:
            console.print(f"\n[bold cyan]Entrada de Dados - Registro Número {contador}:[/bold cyan]")
            
            nome_input = input("Digite o nome completo: ").strip()
            nome = nome_input if nome_input else f"Colaborador {contador}"

            while True:
                try:
                    matricula_input = input("Digite o número de matrícula (até 5 dígitos): ").strip()
                    matricula = int(matricula_input)

                    if matricula <= 0 or matricula > 99999:
                        raise ValueError

                    break

                except ValueError:
                    console.print("\n[bold red]Erro: A matrícula deve ser um número inteiro positivo de até 5 dígitos (1 a 99999).[/bold red]\n")
                
                except KeyboardInterrupt:
                    console.print("\n\n[bold yellow]Operação cancelada pelo operador do sistema.[/bold yellow]")
                    return

            console.print(f"\n[bold yellow]Revisão de segurança do Registro {contador}:[/bold yellow]")
            console.print(f"Nome Atual: [green]{nome}[/green] | Matrícula Atual: [green]{matricula}[/green]\n")

            while True:
                corrigir_matricula = input("Deseja alterar a matrícula digitada? [S/N]: ").strip().upper()
                
                if corrigir_matricula in ("S", "N"):
                    if corrigir_matricula == "S":
                        while True:
                            try:
                                nova_mat_input = input("Digite o novo número de matrícula (até 5 dígitos): ").strip()
                                matricula = int(nova_mat_input)
                                
                                if matricula <= 0 or matricula > 99999:
                                    raise ValueError
                                break
                            except ValueError:
                                console.print("\n[bold red]Erro: Digite uma matrícula válida (1 a 99999).[/bold red]\n")
                    break
                else:
                    console.print("[bold red]Opção inválida. Digite apenas S ou N.[/bold red]")

            while True:
                corrigir_nome = input("Deseja alterar o nome digitado? [S/N]: ").strip().upper()
                
                if corrigir_nome in ("S", "N"):
                    if corrigir_nome == "S":
                        novo_nome_input = input("Digite o novo nome completo: ").strip()
                        nome = novo_nome_input if novo_nome_input else nome
                    break
                else:
                    console.print("[bold red]Opção inválida. Digite apenas S ou N.[/bold red]")

            nova_pessoa = Pessoa(nome, matricula)
            self._lista_pessoas.append(nova_pessoa)
            contador += 1

            while True:
                console.print("\nDeseja continuar inserindo novos registros? [S/N]: ", end="")
                prosseguir = input().strip().upper()

                if prosseguir in ("S", "N"):
                    if prosseguir == "N":
                        executando = False
                    break
                else:
                    console.print("[bold red]Opção inválida. Digite apenas S para Sim ou N para Não.[/bold red]")

        console.print("\n")
        
        with console.status("[bold green]Sincronizando banco de dados e gerando relatórios...[/bold green]"):
            time.sleep(1.5)

        console.print("\n")

        tabela = Table(title="[bold white]Relatório Final de Matrículas Homologadas[/bold white]", show_lines=True)
        tabela.add_column("Índice", justify="center", style="magenta")
        tabela.add_column("Nome do Cadastrado", justify="left", style="cyan")
        tabela.add_column("Código de Matrícula", justify="center", style="green")

        for indice, pessoa in enumerate(self._lista_pessoas, start=1):
            tabela.add_row(
                str(indice),
                pessoa.obter_nome(), 
                f"{pessoa.obter_matricula():05d}"
            )

        console.print(tabela)

        console.print("\n")

        total_registros = len(self._lista_pessoas)
        resumo_dados = f"[bold green]Total de registros processados com sucesso neste lote: {total_registros}[/bold green]"

        console.print(Panel(resumo_dados, title="[bold white]Consolidação de Lote[/bold white]", expand=False))


if __name__ == "__main__":
    sistema = SistemaRegistroMatriculas()
    sistema.executar()