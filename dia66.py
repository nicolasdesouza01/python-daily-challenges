import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class TriagemPublica:

    def __init__(self):
        self._peso = 0.0
        self._altura = 0.0
        self._imc = 0.0
        self._classificacao = ""
        self._perfil_atleta = ""
        self._console = Console()


    def coletar_dados(self):
        self._console.clear()
        self._console.print(Panel("[bold cyan]:hospital: SISTEMA NACIONAL DE TRIAGEM - MINISTÉRIO DA SAÚDE :hospital:[/bold cyan]", expand=False))
        
        while True:
            try:
                entrada_peso = input('Qual seu peso? (Kg): ').strip().replace(',', '.')
                self._peso = float(entrada_peso)
                
                if self._peso < 15.0 or self._peso > 500.0:
                    raise ValueError("O peso deve ser um valor biológico realista entre 15 Kg e 500 Kg.")
                    
                break
            except ValueError as erro:
                mensagem = str(erro) if "realista" in str(erro) else "Digite um valor numérico válido para o peso."
                self._console.print(f"[bold red]:warning: Erro: {mensagem}[/bold red]")

        while True:
            try:
                entrada_altura = input('Qual sua altura? (m): ').strip().replace(',', '.')
                self._altura = float(entrada_altura)
                
                if self._altura < 0.50 or self._altura > 2.80:
                    raise ValueError("A altura deve ser um valor biológico realista entre 0,50 m e 2,80 m.")
                    
                break
            except ValueError as erro:
                mensagem = str(erro) if "realista" in str(erro) else "Digite um valor numérico válido para a altura."
                self._console.print(f"[bold red]:warning: Erro: {mensagem}[/bold red]")

        while True:
            resposta = input('Você pratica musculação intensa ou é atleta de alto rendimento? [S/N]: ').strip().upper()
            if resposta in ['S', 'N']:
                self._perfil_atleta = resposta
                break
            self._console.print("[bold red]:warning: Erro: Responda apenas com S para Sim ou N para Não.[/bold red]")


    def _calcular_imc(self):
        self._imc = self._peso / (self._altura ** 2)


    def _definir_classificacao(self):
        if self._imc < 18.5:
            self._classificacao = 'Abaixo do peso'
        elif 18.5 <= self._imc < 25:
            self._classificacao = 'Peso ideal'
        elif 25 <= self._imc < 30:
            self._classificacao = 'Sobrepeso'
        elif 30 <= self._imc < 40:
            self._classificacao = 'Obesidade'
        else:
            self._classificacao = 'Obesidade mórbida'


    def executar_sistema(self):
        self.coletar_dados()
        
        with self._console.status("[bold green]Processando dados e gerando indicadores epidemiológicos...[/bold green]"):
            self._calcular_imc()
            self._definir_classificacao()
            time.sleep(2)
            
        self._exibir_painel_saude()


    def _exibir_painel_saude(self):
        self._console.clear()
        
        tabela = Table(title=":bar_chart: Boletim de Vigilância Nutricional", title_style="bold magenta")
        tabela.add_column("Indicador Sanitário", justify="left", style="bold white")
        tabela.add_column("Dados Coletados", justify="center", style="green")
        
        tabela.add_row("Massa Corporal", f"{self._peso:.1f} Kg")
        tabela.add_row("Estatura", f"{self._altura:.2f} m")
        tabela.add_row("Índice de Massa Corporal (IMC)", f"{self._imc:.1f}")
        tabela.add_row("Classificação Preliminar", self._classificacao)
        tabela.add_row("Praticante de Atividade Intensa", "Sim" if self._perfil_atleta == "S" else "Não")
        
        self._console.print(tabela)
        
        if self._perfil_atleta == 'S' and self._imc >= 25:
            alerta_medico = (
                "[bold yellow]:heavy_exclamation_mark: NOTA DE ATENÇÃO À DIRETRIZ CLÍNICA:[/bold yellow]\n\n"
                "O paciente possui histórico de atividade física intensa. O cálculo isolado do IMC "
                "pode apresentar falsa indicação de sobrepeso/obesidade devido ao peso de massa magra (músculos).\n"
                "Encaminhamento gerado para: [bold]Avaliação de Composição Corporal (Adipometria) na UBS mais próxima.[/bold]"
            )
            self._console.print(Panel(alerta_medico, border_style="yellow"))
            
        else:
            if self._imc < 18.5:
                conduta = "Encaminhamento automático: Grupo de Orientação Nutricional e Combate à Desnutrição."
            elif 18.5 <= self._imc < 25:
                conduta = "Paciente dentro dos parâmetros ideais. Manter rotina e repetir triagem em 12 meses."
            elif 25 <= self._imc < 30:
                conduta = "Encaminhamento automático: Monitoramento preventivo e Oficina de Reeducação Alimentar."
            else:
                conduta = "[bold red]ALERTA DE PRIORIDADE MÉDIA/ALTA:[/bold red]\nAgendamento prioritário com clínico geral e nutricionista do NASF."
                
            self._console.print(Panel(f"[bold blue]:heartpulse: CONDUTA DO SISTEMA PÚBLICO DE SAÚDE:[/bold blue]\n\n{conduta}", border_style="blue"))


if __name__ == "__main__":
    sistema = TriagemPublica()
    sistema.executar_sistema()