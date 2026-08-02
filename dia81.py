import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt
from rich.theme import Theme

# Configuração de tema visual corporativo e equilibrado
TEMA_CORPORATIVO = Theme({
    "titulo": "bold white on #1e3d59",
    "subtitulo": "bold #1e3d59",
    "destaque": "bold #17b978",
    "alerta": "bold #d9534f",
    "neutro": "#8d99ae",
    "rotulo": "bold #333333",
    "valor_antigo": "#7f8c8d",
    "valor_novo": "#27ae60",
    "diferenca": "#d35400"
})

console = Console(theme=TEMA_CORPORATIVO)


class CalculadoraFolha:
    """
    Calculadora responsável pelas regras de negócio de folha de pagamento,
    reajustes salariais, descontos fiscais (INSS/IRRF) e encargos patronais.
    """

    def __init__(self, salario_atual: float, percentual_aumento: float):
        """
        Inicializa os dados básicos para o cálculo de reajuste.

        Args:
            salario_atual (float): Salário atual do funcionário em R$.
            percentual_aumento (float): Porcentagem de aumento a ser aplicada.
        """
        self._salario_atual = salario_atual
        self._percentual_aumento = percentual_aumento

    @property
    def salario_novo(self) -> float:
        """
        Calcula o novo salário bruto após o reajuste.

        Returns:
            float: Valor do novo salário bruto.
        """
        return self._salario_atual * (1 + self._percentual_aumento / 100)

    @property
    def aumento_bruto(self) -> float:
        """
        Calcula o valor absoluto do aumento concedido.

        Returns:
            float: Valor em R$ referente ao aumento.
        """
        return self.salario_novo - self._salario_atual

    def calcular_inss(self, salario: float) -> float:
        """
        Calcula a alíquota progressiva do INSS com base nas faixas vigentes.

        Args:
            salario (float): Valor da base salarial.

        Returns:
            float: Valor do desconto do INSS.
        """
        if salario <= 1412.00:
            return salario * 0.075
        elif salario <= 2666.68:
            return (1412.00 * 0.075) + ((salario - 1412.00) * 0.09)
        elif salario <= 4000.03:
            return (1412.00 * 0.075) + ((2666.68 - 1412.00) * 0.09) + ((salario - 2666.68) * 0.12)
        elif salario <= 7786.02:
            return (1412.00 * 0.075) + ((2666.68 - 1412.00) * 0.09) + ((4000.03 - 2666.68) * 0.12) + ((salario - 4000.03) * 0.14)
        return 908.85

    def calcular_irrf(self, salario: float, inss: float) -> float:
        """
        Calcula o Imposto de Renda Retido na Fonte (IRRF) a partir da base deduzida do INSS.

        Args:
            salario (float): Salário bruto.
            inss (float): Valor do INSS já descontado.

        Returns:
            float: Valor do IRRF retido.
        """
        base_calculo = salario - inss

        if base_calculo <= 2259.20:
            return 0.0
        elif base_calculo <= 2826.65:
            return (base_calculo * 0.075) - 169.44
        elif base_calculo <= 3751.05:
            return (base_calculo * 0.15) - 381.44
        elif base_calculo <= 4664.68:
            return (base_calculo * 0.225) - 662.77
        else:
            return (base_calculo * 0.275) - 896.00

    def calcular_custo_patronal(self, salario: float) -> dict:
        """
        Projeta os custos totais e encargos trabalhistas para a empresa sobre o salário.

        Args:
            salario (float): Salário do funcionário.

        Returns:
            dict: Dicionário contendo FGTS, Provisão de 13º, Férias e Custo Total.
        """
        fgts = salario * 0.08
        provisao_13 = salario / 12
        provisao_ferias = (salario / 12) * 1.3333
        custo_total = salario + fgts + provisao_13 + provisao_ferias

        return {
            "fgts": fgts,
            "provisao_13": provisao_13,
            "provisao_ferias": provisao_ferias,
            "custo_total": custo_total
        }


class SistemaRH:
    """
    Gerencia a interface de usuário no terminal, garantindo apresentações
    visuais organizadas, tabelas e tratamento rigoroso de exceções.
    """

    def _simular_processamento(self, mensagem: str):
        """
        Exibe um indicador de processamento temporário no terminal.

        Args:
            mensagem (str): Descrição da etapa em execução.
        """
        with console.status(f"[subtitulo]{mensagem}...[/subtitulo]", spinner="line"):
            time.sleep(0.8)

    def exibir_cabecalho(self):
        """
        Renderiza o painel superior do sistema.
        """
        console.clear()
        console.print(Panel(
            "[white]MÓDULO DE SIMULAÇÃO DE REAJUSTE SALARIAL E ENCARGOS PATRONAIS[/white]\n"
            "[neutro]Departamento de Recursos Humanos & Controladoria[/neutro]",
            style="#1e3d59",
            expand=False
        ))

    def executar_simulacao(self):
        """
        Coleta dados do operador, realiza o processamento financeiro e exibe os relatórios.
        """
        try:
            console.print("\n[subtitulo]=== ENTRADA DE DADOS ===[/subtitulo]\n")

            salario = FloatPrompt.ask("[rotulo]Informe o salário atual (R$)[/rotulo]")
            while salario <= 0:
                console.print("[alerta]O valor do salário deve ser estritamente maior que zero.[/alerta]")
                salario = FloatPrompt.ask("[rotulo]Informe o salário atual (R$)[/rotulo]")

            porcentagem = FloatPrompt.ask("[rotulo]Informe o percentual de reajuste (%)[/rotulo]")
            while porcentagem < 0:
                console.print("[alerta]O percentual de reajuste não pode ser negativo.[/alerta]")
                porcentagem = FloatPrompt.ask("[rotulo]Informe o percentual de reajuste (%)[/rotulo]")

            self._simular_processamento("Calculando retenções fiscais e provisões trabalhistas")

            calc = CalculadoraFolha(salario, porcentagem)

            inss_antigo = calc.calcular_inss(salario)
            irrf_antigo = calc.calcular_irrf(salario, inss_antigo)
            liquido_antigo = salario - inss_antigo - irrf_antigo

            inss_novo = calc.calcular_inss(calc.salario_novo)
            irrf_novo = calc.calcular_irrf(calc.salario_novo, inss_novo)
            liquido_novo = calc.salario_novo - inss_novo - irrf_novo

            custo_antigo = calc.calcular_custo_patronal(salario)
            custo_novo = calc.calcular_custo_patronal(calc.salario_novo)

            # Tabela do Colaborador (Visão Líquida)
            tabela_colaborador = Table(
                title="DEMONSTRATIVO DE IMPACTO NO SALÁRIO LÍQUIDO",
                header_style="bold white on #1e3d59",
                border_style="#8d99ae"
            )
            tabela_colaborador.add_column("Item / Descrição", style="bold")
            tabela_colaborador.add_column("Anterior", style="valor_antigo", justify="right")
            tabela_colaborador.add_column("Reajustado", style="valor_novo", justify="right")
            tabela_colaborador.add_column("Variação Absoluta", style="diferenca", justify="right")

            tabela_colaborador.add_row(
                "Salário Bruto",
                f"R$ {salario:.2f}",
                f"R$ {calc.salario_novo:.2f}",
                f"+ R$ {calc.aumento_bruto:.2f}"
            )
            tabela_colaborador.add_row(
                "Retenção INSS",
                f"R$ {inss_antigo:.2f}",
                f"R$ {inss_novo:.2f}",
                f"+ R$ {inss_novo - inss_antigo:.2f}"
            )
            tabela_colaborador.add_row(
                "Retenção IRRF",
                f"R$ {irrf_antigo:.2f}",
                f"R$ {irrf_novo:.2f}",
                f"+ R$ {irrf_novo - irrf_antigo:.2f}"
            )
            tabela_colaborador.add_row(
                "Salário Líquido Estimado",
                f"R$ {liquido_antigo:.2f}",
                f"R$ {liquido_novo:.2f}",
                f"+ R$ {liquido_novo - liquido_antigo:.2f}",
                end_section=True
            )

            # Tabela da Empresa (Visão de Custos)
            tabela_patronal = Table(
                title="PROJEÇÃO DE CUSTO TOTAL EMPREGADOR (MENSAL)",
                header_style="bold white on #2c3e50",
                border_style="#8d99ae"
            )
            tabela_patronal.add_column("Encargo / Provisão Trabalhista", style="bold")
            tabela_patronal.add_column("Custo Anterior", style="valor_antigo", justify="right")
            tabela_patronal.add_column("Custo Reajustado", style="valor_novo", justify="right")
            tabela_patronal.add_column("Aumento de Custo", style="diferenca", justify="right")

            tabela_patronal.add_row(
                "FGTS (8%)",
                f"R$ {custo_antigo['fgts']:.2f}",
                f"R$ {custo_novo['fgts']:.2f}",
                f"+ R$ {custo_novo['fgts'] - custo_antigo['fgts']:.2f}"
            )
            tabela_patronal.add_row(
                "Provisão 13º Salário",
                f"R$ {custo_antigo['provisao_13']:.2f}",
                f"R$ {custo_novo['provisao_13']:.2f}",
                f"+ R$ {custo_novo['provisao_13'] - custo_antigo['provisao_13']:.2f}"
            )
            tabela_patronal.add_row(
                "Provisão Férias (+ 1/3)",
                f"R$ {custo_antigo['provisao_ferias']:.2f}",
                f"R$ {custo_novo['provisao_ferias']:.2f}",
                f"+ R$ {custo_novo['provisao_ferias'] - custo_antigo['provisao_ferias']:.2f}"
            )
            tabela_patronal.add_row(
                "CUSTO TOTAL MENSAL",
                f"R$ {custo_antigo['custo_total']:.2f}",
                f"R$ {custo_novo['custo_total']:.2f}",
                f"+ R$ {custo_novo['custo_total'] - custo_antigo['custo_total']:.2f}",
                end_section=True
            )

            console.clear()
            self.exibir_cabecalho()
            console.print("\n")
            console.print(tabela_colaborador)
            console.print("\n")
            console.print(tabela_patronal)
            console.print("\n")

            Prompt.ask("[neutro]Pressione ENTER para retornar ao menu principal...[/neutro]")

        except ValueError:
            console.print("\n[alerta]Erro: Entrada de dados inválida. Por favor, utilize numeração válida.[/alerta]\n")
            time.sleep(2)

    def iniciar(self):
        """
        Inicia a execução do loop principal do sistema.
        """
        try:
            while True:
                self.exibir_cabecalho()
                console.print("\n[subtitulo]MENU PRINCIPAL[/subtitulo]\n")
                console.print("  [bold]1.[/bold] Simular Reajuste Salarial")
                console.print("  [bold]2.[/bold] Encerra Aplicação\n")

                opcao = Prompt.ask("[rotulo]Selecione a opção desejada[/rotulo]", choices=["1", "2"])

                if opcao == "1":
                    self.executar_simulacao()
                elif opcao == "2":
                    console.print("\n[destaque]Sessão encerrada com sucesso.[/destaque]\n")
                    break

        except KeyboardInterrupt:
            console.print("\n\n[alerta]Execução interrompida pelo operador. Sistema finalizado com segurança.[/alerta]\n")


if __name__ == "__main__":
    app = SistemaRH()
    app.iniciar()