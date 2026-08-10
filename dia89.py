import time
import sys
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.theme import Theme

# Configuracao visual em Preto e Laranja
console = Console(theme=Theme({
    "primary": "bold orange1",
    "secondary": "orange3",
    "background": "on black",
    "text": "grey89",
    "accent": "dark_orange",
    "alert": "bold red"
}))


def carregar(msg: str, tempo: float = 0.3) -> None:
    """Exibe animação de carregamento rápido no terminal."""
    with console.status(f"[secondary]{msg}[/secondary]", spinner="dots"):
        time.sleep(tempo)


class Categoria:
    """Modela as regras de tarifacao por categoria de veiculo."""
    def __init__(self, nome: str, diaria: float, taxa_km: float, franquia_km: float):
        self._nome, self._diaria = nome, diaria
        self._taxa_km, self._franquia_km = taxa_km, franquia_km

    @property
    def nome(self) -> str: return self._nome
    @property
    def diaria(self) -> float: return self._diaria
    @property
    def taxa_km(self) -> float: return self._taxa_km
    @property
    def franquia_km(self) -> float: return self._franquia_km


class Veiculo:
    """Representa uma unidade da frota operacional."""
    def __init__(self, placa: str, modelo: str, marca: str, odometro: float, categoria: Categoria):
        self._placa, self._modelo, self._marca = placa, modelo, marca
        self._odometro, self._categoria, self._disponivel = odometro, categoria, True

    @property
    def placa(self) -> str: return self._placa
    @property
    def modelo(self) -> str: return self._modelo
    @property
    def marca(self) -> str: return self._marca
    @property
    def odometro(self) -> float: return self._odometro
    @property
    def categoria(self) -> Categoria: return self._categoria
    @property
    def disponivel(self) -> bool: return self._disponivel

    def atualizar_odometro(self, km: float) -> None:
        if km >= self._odometro: self._odometro = km

    def set_disponivel(self, st: bool) -> None: self._disponivel = st


class Cliente:
    """Entidade que armazena os dados do locatario."""
    def __init__(self, cpf: str, nome: str, telefone: str):
        self._cpf, self._nome, self._telefone = cpf, nome, telefone

    @property
    def cpf(self) -> str: return self._cpf
    @property
    def nome(self) -> str: return self._nome
    @property
    def telefone(self) -> str: return self._telefone

    def atualizar_dados(self, nome: str, telefone: str) -> None:
        """Atualiza informações de contato do cliente."""
        self._nome = nome
        self._telefone = telefone


class Contrato:
    """Representa a locacao e processa o fechamento financeiro."""
    def __init__(self, cliente: Cliente, veiculo: Veiculo, dias: int):
        self._cliente, self._veiculo, self._dias = cliente, veiculo, dias
        self._km_inicial = veiculo.odometro
        self._ativo = True
        self._veiculo.set_disponivel(False)

    @property
    def cliente(self) -> Cliente: return self._cliente
    @property
    def veiculo(self) -> Veiculo: return self._veiculo
    @property
    def dias(self) -> int: return self._dias
    @property
    def ativo(self) -> bool: return self._ativo

    def liquidar(self, km_final: float) -> Dict[str, float]:
        """Calcula o acerto financeiro e encerra a locacao."""
        self._veiculo.atualizar_odometro(km_final)
        self._veiculo.set_disponivel(True)
        self._ativo = False

        km_rodados = max(0.0, km_final - self._km_inicial)
        franquia = self._dias * self._veiculo.categoria.franquia_km
        excedente = max(0.0, km_rodados - franquia)

        v_diarias = self._dias * self._veiculo.categoria.diaria
        v_km = excedente * self._veiculo.categoria.taxa_km
        return {
            "diarias": v_diarias, "km_rodados": km_rodados, "franquia": franquia,
            "excedente": excedente, "v_km": v_km, "total": v_diarias + v_km
        }


class AtendimentoControlador:
    """Gerencia a operacao e os fluxos do sistema da locadora."""
    def __init__(self):
        self._clientes: Dict[str, Cliente] = {}
        self._frota: Dict[str, Veiculo] = {}
        self._contratos: List[Contrato] = []
        self._boot()

    def _boot(self) -> None:
        """Popula o catalogo inicial da locadora."""
        c_eco = Categoria("Econômico", 90.0, 0.35, 100.0)
        c_esp = Categoria("Esportivo", 250.0, 0.80, 120.0)
        c_uti = Categoria("Utilitário", 210.0, 0.65, 150.0)

        frota = [
            Veiculo("FIT-2026", "Fit", "Honda", 45000.0, c_eco),
            Veiculo("LNC-2008", "Lancer", "Mitsubishi", 32000.0, c_esp),
            Veiculo("F15-2025", "F-150", "Ford", 18000.0, c_uti)
        ]
        for v in frota: self._frota[v.placa] = v

    def _topo(self) -> None:
        console.clear()
        console.print(Panel("[primary]SIMAS RENT A CAR[/primary]\n[accent]Sistema Integrado de Gestão de Frota[/accent]", style="primary"))

    def cadastrar_cliente(self) -> None:
        self._topo()
        try:
            cpf = Prompt.ask("[secondary]CPF do Cliente[/secondary]")
            if cpf in self._clientes:
                console.print("\n[alert]Erro: Cliente já cadastrado.[/alert]")
            else:
                nome = Prompt.ask("[secondary]Nome Completo[/secondary]")
                tel = Prompt.ask("[secondary]Telefone[/secondary]")
                carregar("Registrando cliente")
                self._clientes[cpf] = Cliente(cpf, nome, tel)
                console.print("\n[primary]Cliente cadastrado com sucesso![/primary]")
        except Exception as e:
            console.print(f"\n[alert]Falha no cadastro: {e}[/alert]")
        Prompt.ask("\nPressione Enter para voltar")

    def atualizar_cliente(self) -> None:
        self._topo()
        try:
            cpf = Prompt.ask("[secondary]Informe o CPF do cliente[/secondary]")
            if cpf not in self._clientes:
                console.print("\n[alert]Cliente não localizado.[/alert]")
            else:
                cli = self._clientes[cpf]
                console.print(f"[accent]Atualizando dados de: {cli.nome}[/accent]")
                novo_nome = Prompt.ask("[secondary]Novo Nome[/secondary]", default=cli.nome)
                novo_tel = Prompt.ask("[secondary]Novo Telefone[/secondary]", default=cli.telefone)
                carregar("Atualizando cadastro")
                cli.atualizar_dados(novo_nome, novo_tel)
                console.print("\n[primary]Dados atualizados com sucesso![/primary]")
        except Exception as e:
            console.print(f"\n[alert]Falha na atualização: {e}[/alert]")
        Prompt.ask("\nPressione Enter para voltar")

    def listar_frota(self) -> None:
        self._topo()
        tb = Table(title="FROTA OPERACIONAL", header_style="primary", border_style="secondary")
        for col in ["Placa", "Modelo", "Marca", "Categoria", "Diária (R$)", "Status"]:
            tb.add_column(col)
        for v in self._frota.values():
            st = "Disponível" if v.disponivel else "Alugado"
            tb.add_row(v.placa, v.modelo, v.marca, v.categoria.nome, f"{v.categoria.diaria:.2f}", st)
        console.print(tb)
        Prompt.ask("\nPressione Enter para voltar")

    def abrir_locacao(self) -> None:
        self._topo()
        try:
            cpf = Prompt.ask("[secondary]CPF do Cliente[/secondary]")
            if cpf not in self._clientes:
                console.print("\n[alert]Cliente não cadastrado.[/alert]")
            else:
                placa = Prompt.ask("[secondary]Placa do Veículo[/secondary]").upper()
                v = self._frota.get(placa)
                if not v or not v.disponivel:
                    console.print("\n[alert]Veículo indisponível ou não localizado.[/alert]")
                else:
                    dias = IntPrompt.ask("[secondary]Dias de Aluguel[/secondary]")
                    if dias > 0:
                        carregar("Emitindo contrato")
                        self._contratos.append(Contrato(self._clientes[cpf], v, dias))
                        console.print("\n[primary]Contrato ativado com sucesso![/primary]")
        except Exception as e:
            console.print(f"\n[alert]Erro ao emitir contrato: {e}[/alert]")
        Prompt.ask("\nPressione Enter para voltar")

    def encerrar_locacao(self) -> None:
        self._topo()
        try:
            placa = Prompt.ask("[secondary]Placa do Veículo para Devolução[/secondary]").upper()
            ct = next((c for c in self._contratos if c.veiculo.placa == placa and c.ativo), None)
            if not ct:
                console.print("\n[alert]Nenhum contrato ativo encontrado.[/alert]")
            else:
                km_f = FloatPrompt.ask(f"[secondary]Odômetro Final (Inicial: {ct.veiculo.odometro:.1f} km)[/secondary]")
                if km_f >= ct.veiculo.odometro:
                    carregar("Calculando acerto financeiro")
                    res = ct.liquidar(km_f)
                    
                    tb = Table(title="DEMONSTRATIVO DE FECHAMENTO", border_style="primary")
                    tb.add_column("Descrição", style="secondary")
                    tb.add_column("Valor / Detalhes", justify="right")
                    tb.add_row("Cliente", ct.cliente.nome)
                    tb.add_row("Veículo", f"{ct.veiculo.modelo} ({ct.veiculo.placa})")
                    tb.add_row("Custo Diárias", f"R$ {res['diarias']:.2f}")
                    tb.add_row("Excedente Km", f"R$ {res['v_km']:.2f}")
                    tb.add_row("[primary]Total Final[/primary]", f"[primary]R$ {res['total']:.2f}[/primary]")
                    console.print(tb)
                else:
                    console.print("\n[alert]Quilometragem inválida.[/alert]")
        except Exception as e:
            console.print(f"\n[alert]Erro ao encerrar locação: {e}[/alert]")
        Prompt.ask("\nPressione Enter para voltar")

    def menu(self) -> None:
        while True:
            try:
                self._topo()
                console.print("[primary]MENU OPERACIONAL[/primary]\n")
                console.print("[secondary]1.[/secondary] Cadastrar Cliente")
                console.print("[secondary]2.[/secondary] Atualizar Dados do Cliente")
                console.print("[secondary]3.[/secondary] Consultar Frota")
                console.print("[secondary]4.[/secondary] Abrir Contrato de Locação")
                console.print("[secondary]5.[/secondary] Encerrar Locação e Gerar Fatura")
                console.print("[secondary]6.[/secondary] Sair")

                op = Prompt.ask("\n[secondary]Selecione uma opção[/secondary]", choices=["1", "2", "3", "4", "5", "6"])
                if op == "1": self.cadastrar_cliente()
                elif op == "2": self.atualizar_cliente()
                elif op == "3": self.listar_frota()
                elif op == "4": self.abrir_locacao()
                elif op == "5": self.encerrar_locacao()
                elif op == "6":
                    carregar("Encerrando aplicação")
                    sys.exit(0)
            except KeyboardInterrupt:
                console.print("\n\n[alert]Aplicação interrompida pelo usuário.[/alert]")
                sys.exit(0)


if __name__ == "__main__":
    AtendimentoControlador().menu()