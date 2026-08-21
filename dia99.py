import os
import re
import sys
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class RelatorioMeteorologico:
    """Entidade que armazena os dados consolidados do boletim meteorologico."""

    def __init__(self, texto: str) -> None:
        """Inicializa as estruturas de dados do relatorio."""
        self._raw: str = texto
        self._emissor: str = "Desconhecido"
        self._data: str = "N/A"
        self._regioes: List[Dict[str, str]] = []
        self._fenomenos: List[str] = []
        self._metricas: Dict[str, str] = {}
        self._alerta: str = "Normal"

    @property
    def emissor(self) -> str:
        """Retorna o emissor do boletim."""
        return self._emissor

    @property
    def data(self) -> str:
        """Retorna a data de emissao."""
        return self._data

    @property
    def regioes(self) -> List[Dict[str, str]]:
        """Retorna as condicoes especificas por regiao."""
        return self._regioes

    @property
    def fenomenos(self) -> List[str]:
        """Retorna os fenomenos detectados."""
        return self._fenomenos

    @property
    def metricas(self) -> Dict[str, str]:
        """Retorna as metricas como umidade e ventos."""
        return self._metricas

    @property
    def alerta(self) -> str:
        """Retorna o nivel de alerta global."""
        return self._alerta

    def atualizar(self, emissor: str, data: str, regioes: List[Dict[str, str]], 
                  fenomenos: List[str], metricas: Dict[str, str], alerta: str) -> None:
        """Atualiza os atributos extraidos do relatorio."""
        self._emissor, self._data = emissor, data
        self._regioes, self._fenomenos = regioes, fenomenos
        self._metricas, self._alerta = metricas, alerta


class SimeparParser:
    """Motor otimizado de extraçao e conversao de boletins textuais em dados."""

    def __init__(self) -> None:
        """Inicializa os mapeamentos de busca para parsing."""
        self._termos_alerta = {
            "Critico": ["tornado", "vendaval", "granizo severo", "supercelula"],
            "Atencao": ["alerta", "atencao", "temporal", "trovoadas", "baixa umidade", "rajadas"],
            "Informativo": ["estabilidade", "nevoa", "parcialmente nublado", "ceu claro"]
        }

    def processar(self, texto: str) -> RelatorioMeteorologico:
        """Realiza a varredura completa do texto fornecido."""
        relatorio = RelatorioMeteorologico(texto)
        
        emissor = self._match(r"EMISSOR:\s*(.+)", texto, "SIMEPAR / N/A")
        data = self._match(r"DATA DE EMISSÃO:\s*(.+)", texto, "N/A")
        regioes = self._extrair_regioes(texto)
        fenomenos = self._extrair_fenomenos(texto.lower())
        metricas = self._extrair_metricas(texto)
        alerta = self._calcular_alerta(texto.lower())

        relatorio.atualizar(emissor, data, regioes, fenomenos, metricas, alerta)
        return relatorio

    def _match(self, padrao: str, texto: str, default: str) -> str:
        """Auxiliar para busca rapida de padroes simples via Regex."""
        m = re.search(padrao, texto, re.IGNORECASE)
        return m.group(1).strip() if m else default

    def _extrair_regioes(self, texto: str) -> List[Dict[str, str]]:
        """Extrai blocos de regioes, temperaturas minimas e maximas."""
        regioes = []
        padrao = r"-\s*([^:]+):\s*(.*?)(?:Mínima de (\d+°C) e máxima de (\d+°C))"
        for match in re.finditer(padrao, texto, re.IGNORECASE):
            regioes.append({
                "nome": match.group(1).strip(),
                "desc": match.group(2).strip(),
                "temp": f"{match.group(3)} / {match.group(4)}"
            })
        return regioes

    def _extrair_fenomenos(self, texto_lc: str) -> List[str]:
        """Identifica palavras-chave de eventos meteorologicos no texto."""
        base = ["pancadas de chuva", "trovoadas", "nevoa umida", "rajadas de vento", "tempo seco", "estabilidade"]
        return [f.title() for f in base if f in texto_lc]

    def _extrair_metricas(self, texto: str) -> Dict[str, str]:
        """Extrai indicadores quantitativos como Umidade Relativa e Rajadas de Vento."""
        m = {}
        umidade = re.search(r"variando entre\s*(\d+%\s*e\s*\d+%)", texto, re.IGNORECASE)
        vento = re.search(r"até\s*(\d+\s*km/h)", texto, re.IGNORECASE)
        
        m["Umidade Relativa"] = umidade.group(1) if umidade else "Nao informada"
        m["Vento Maximo"] = vento.group(1) if vento else "Nao informado"
        return m

    def _calcular_alerta(self, texto_lc: str) -> str:
        """Determina o nivel de gravidade do boletim."""
        for nivel, termos in self._termos_alerta.items():
            if any(t in texto_lc for t in termos):
                return nivel
        return "Normal"


class SystemInterface:
    """Gerenciador de visualizacao do terminal baseado na biblioteca Rich."""

    def __init__(self) -> None:
        """Inicializa o console da interface."""
        self._console = Console()

    def limpar(self) -> None:
        """Limpa o console do sistema operativo."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def cabecalho(self) -> None:
        """Renderiza o painel superior da aplicacao."""
        p = Panel(
            "[bold cyan]PARSER DE BOLETIM METEOROLOGICO AMBIENTAL[/bold cyan]\n"
            "[dim]Extrator de Dados Multi-Regiao e Telemetria Textual[/dim]",
            border_style="cyan", expand=False
        )
        self._console.print(p)

    def ler_multilinha(self) -> str:
        """Captura multiplas linhas do terminal ate que uma linha vazia seja inserida."""
        self._console.print("\n[bold yellow]Cole o boletim completo abaixo. (Pressione ENTER em uma linha vazia para processar):[/bold yellow]\n")
        linhas = []
        while True:
            try:
                linha = input()
                if not linha.strip() and linhas:
                    break
                if linha.strip():
                    linhas.append(linha)
            except EOFError:
                break
        return "\n".join(linhas)

    def exibir_relatorio(self, r: RelatorioMeteorologico) -> None:
        """Renderiza as tabelas com os dados extraidos do boletim."""
        # Tabela Geral
        t_geral = Table(title=f"Boletim: {r.emissor} ({r.data})", border_style="bright_blue")
        t_geral.add_column("Indicador", style="bold white")
        t_geral.add_column("Dado Extraido", style="bold yellow")

        estilo_alerta = "bold red" if r.alerta == "Critico" else "bold yellow" if r.alerta == "Atencao" else "bold green"

        t_geral.add_row("Nivel de Alerta Global", f"[{estilo_alerta}]{r.alerta}[/{estilo_alerta}]")
        t_geral.add_row("Fenomenos Detectados", ", ".join(r.fenomenos) if r.fenomenos else "Nenhum")
        t_geral.add_row("Umidade Relativa Ar", r.metricas.get("Umidade Relativa", "N/A"))
        t_geral.add_row("Ventos de Pico", r.metricas.get("Vento Maximo", "N/A"))
        
        self._console.print("\n", t_geral)

        # Tabela Regional
        if r.regioes:
            t_reg = Table(title="Previsao Detalhada por Regiao", border_style="cyan")
            t_reg.add_column("Regiao / Setor", style="bold green", width=25)
            t_reg.add_column("Min / Max", style="bold magenta", width=15)
            t_reg.add_column("Condicao Prevista", style="white")

            for reg in r.regioes:
                t_reg.add_row(reg["nome"], reg["temp"], reg["desc"])

            self._console.print(t_reg)

    def msg_erro(self, msg: str) -> None:
        """Exibe mensagem de falha no terminal."""
        self._console.print(f"[bold red]Erro:[/bold red] {msg}")

    def msg_info(self, msg: str) -> None:
        """Exibe mensagem informativa."""
        self._console.print(f"[bold green]{msg}[/bold green]")


class Aplicacao:
    """Controlador principal do ciclo de vida do programa."""

    def __init__(self) -> None:
        """Instancia os componentes necessarios."""
        self._ui = SystemInterface()
        self._parser = SimeparParser()

    def executar(self) -> None:
        """Executa o loop de operacao da ferramenta."""
        try:
            while True:
                self._ui.limpar()
                self._ui.cabecalho()
                
                texto = self._ui.ler_multilinha()

                if not texto.strip():
                    self._ui.msg_erro("Nenhum texto fornecido.")
                else:
                    relatorio = self._parser.processar(texto)
                    self._ui.exibir_relatorio(relatorio)

                self._ui.msg_info("\nPressione ENTER para analisar outro texto ou Ctrl+C para sair...")
                input()

        except (KeyboardInterrupt, EOFError):
            self._ui.msg_info("\nEncerrando o monitor com seguranca.")
            sys.exit(0)
        except Exception as e:
            self._ui.msg_erro(f"Excecao operacional: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    app = Aplicacao()
    app.executar()