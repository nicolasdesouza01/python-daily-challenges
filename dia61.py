import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.status import Status

console = Console()


class Funcionario:

    def __init__(self, nome: str, salario_atual: float):
        self._nome = nome
        self._salario_atual = salario_atual
        self._novo_salario = 0.0
        self.calcular_reajuste()

    @property
    def nome(self):
        return self._nome

    @property
    def salario_atual(self):
        return self._salario_atual

    @property
    def novo_salario(self):
        return self._novo_salario

    def calcular_reajuste(self):
        if self._salario_atual <= 1250.00:
            self._novo_salario = self._salario_atual * 1.15
        else:
            self._novo_salario = self._salario_atual * 1.10


class GerenciadorFolha:

    def __init__(self, nome_empresa: str):
        self._nome_empresa = nome_empresa
        self._funcionarios = []

    @property
    def nome_empresa(self):
        return self._nome_empresa

    @property
    def funcionarios(self):
        return self._funcionarios

    def adicionar_funcionario(self, funcionario: Funcionario):
        self._funcionarios.append(funcionario)

    def calcular_total_atual(self) -> float:
        return sum(f.salario_atual for f in self._funcionarios)

    def calcular_total_novo(self) -> float:
        return sum(f.novo_salario for f in self._funcionarios)


def obter_input_texto(mensagem: str) -> str:
    while True:
        try:
            valor = input(mensagem).strip()
            if not valor:
                raise ValueError("O campo de texto não pode ficar vazio.")
            return valor
        except ValueError as erro:
            console.print(f"[bold red]:warning: Erro: {erro}[/]")


def obter_input_float(mensagem: str) -> float:
    while True:
        try:
            valor = float(input(mensagem))
            if valor <= 0:
                raise ValueError("O valor precisa ser maior que zero.")
            return valor
        except ValueError:
            console.print("[bold red]:warning: Erro: Digite um valor numérico válido e maior que zero.[/]")


def main():
    console.print(
        Panel.fit(
            "[bold cyan]:briefcase: GERENCIADOR DE REAJUSTES DE FOLHA[/]\n"
            "[dim]Sistema de Recursos Humanos[/]",
            border_style="cyan"
        )
    )
    
    nome_empresa = obter_input_texto("Nome da sua Empresa: ")
    gerenciador = GerenciadorFolha(nome_empresa)
    
    with console.status("[bold green]Iniciando o sistema da " + nome_empresa + "...", spinner="dots"):
        time.sleep(1.5)
        
    while True:
        console.print("\n" + "=" * 40)
        console.print("[bold yellow]:clipboard: MENU PRINCIPAL[/]")
        console.print("1. Cadastrar Funcionário")
        console.print("2. Gerar Relatório de Folha de Pagamento")
        console.print("3. Sair")
        console.print("=" * 40 + "\n")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            nome = obter_input_texto("Nome do funcionário: ")
            salario = obter_input_float("Salário atual: R$")
            
            funcionario = Funcionario(nome, salario)
            
            with console.status("[bold yellow]Calculando reajuste para " + nome + "...", spinner="dots"):
                time.sleep(1.0)
                
            gerenciador.adicionar_funcionario(funcionario)
            console.print(f"[bold green]:white_check_mark: {nome} cadastrado com sucesso![/]")
            
        elif opcao == "2":
            if not gerenciador.funcionarios:
                console.print("[bold red]:warning: Nenhum funcionário cadastrado no momento.[/]")
                continue
                
            with console.status("[bold green]Compilando dados da folha de pagamento...", spinner="dots"):
                time.sleep(1.5)
                
            tabela = Table(title=f"Folha de Pagamento - {gerenciador.nome_empresa}", header_style="bold magenta")
            tabela.add_column("Funcionário", justify="left", style="cyan")
            tabela.add_column("Salário Antigo", justify="right", style="red")
            tabela.add_column("Aumento (%)", justify="center", style="yellow")
            tabela.add_column("Novo Salário", justify="right", style="green")
            
            for f in gerenciador.funcionarios:
                percentual = "15%" if f.salario_atual <= 1250.00 else "10%"
                tabela.add_row(
                    f.nome,
                    f"R$ {f.salario_atual:.2f}",
                    percentual,
                    f"R$ {f.novo_salario:.2f}"
                )
                
            console.print(tabela)
            
            total_antigo = gerenciador.calcular_total_atual()
            total_novo = gerenciador.calcular_total_novo()
            impacto = total_novo - total_antigo
            
            console.print(
                Panel(
                    f"[bold]Resumo Financeiro da Empresa:[/]\n"
                    f"Custo de Folha Anterior: [bold red]R$ {total_antigo:.2f}[/]\n"
                    f"Novo Custo de Folha: [bold green]R$ {total_novo:.2f}[/]\n"
                    f"Impacto Mensal Total: [bold yellow]:chart_with_upwards_trend: R$ {impacto:.2f}[/]",
                    title="[bold blue]:money_bag: Painel de Impacto Orçamentário[/]",
                    border_style="blue"
                )
            )
            
        elif opcao == "3":
            with console.status("[bold red]Fechando o sistema...", spinner="dots"):
                time.sleep(1.0)
            console.print("[bold green]:white_check_mark: Sistema finalizado com sucesso. Até mais![/]")
            break
            
        else:
            console.print("[bold red]:warning: Opção inválida! Escolha de forma correspondente ao menu.[/]")


if __name__ == "__main__":
    main()