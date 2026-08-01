import sys
import time
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.table import Table


class FileHandler:
    """Classe responsável pelo manuseio seguro de arquivos de texto no sistema."""

    def __init__(self, filepath: str) -> None:
        """Inicializa o gerenciador com o caminho do arquivo fornecido."""
        self._filepath = Path(filepath)

    def read_content(self) -> str:
        """Lê e retorna o conteúdo textual do arquivo com suporte a UTF-8.

        Returns:
            str: Conteúdo do arquivo de texto.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            IsADirectoryError: Se o caminho apontar para uma pasta.
            PermissionError: Se não houver permissão de leitura.
            Exception: Para erros genéricos na leitura do arquivo.
        """
        if not self._filepath.exists():
            raise FileNotFoundError(
                f"O arquivo '{self._filepath}' não foi encontrado."
            )

        if self._filepath.is_dir():
            raise IsADirectoryError(
                f"O caminho '{self._filepath}' aponta para uma pasta, não para um arquivo."
            )

        try:
            with open(self._filepath, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            with open(self._filepath, "r", encoding="latin-1") as file:
                return file.read()
        except PermissionError:
            raise PermissionError(
                f"Sem permissão para ler o arquivo '{self._filepath}'."
            )
        except Exception as error:
            raise Exception(f"Erro ao ler o arquivo: {error}")


class TextAnalyzer:
    """Classe especialista na análise linguística e extração de vogais de um texto."""

    _VOWELS = "aeiou"

    def __init__(self, raw_text: str) -> None:
        """Inicializa o analisador sanitizando o texto de entrada."""
        self._raw_text = raw_text
        self._words = self._extract_words(raw_text)

    @property
    def words(self) -> List[str]:
        """Retorna a lista de palavras extraídas do texto."""
        return self._words

    def _normalize_char(self, char: str) -> str:
        """Remove acentos de um caractere individual para análise precisa."""
        normalized = unicodedata.normalize("NFD", char)
        return "".join(
            c for c in normalized if unicodedata.category(c) != "Mn"
        )

    def _extract_words(self, text: str) -> List[str]:
        """Limpa o texto e extrai palavras válidas ignorando pontuações."""
        clean_text = "".join(
            char if char.isalnum() or char.isspace() else " " for char in text
        )
        return [word for word in clean_text.split() if word.isalpha()]

    def extract_vowels_from_word(self, word: str) -> List[str]:
        """Extrai todas as vogais encontradas em uma palavra específica preservando acentos originais."""
        return [
            char
            for char in word
            if self._normalize_char(char).lower() in self._VOWELS
        ]

    def get_vowel_frequencies(self) -> Dict[str, int]:
        """Calcula a frequência total de cada vogal no texto analisado."""
        frequencies = {vowel: 0 for vowel in self._VOWELS}
        for word in self._words:
            for char in word:
                normalized_char = self._normalize_char(char).lower()
                if normalized_char in frequencies:
                    frequencies[normalized_char] += 1
        return frequencies

    def analyze_full_dataset(self) -> List[Tuple[str, List[str], int]]:
        """Gera uma lista com a palavra, suas vogais e o total de vogais encontradas."""
        analysis = []
        for word in self._words:
            vowels = self.extract_vowels_from_word(word)
            analysis.append((word, vowels, len(vowels)))
        return analysis


class CLIInterface:
    """Classe responsável por gerenciar a Interface de Linha de Comando (HUD)."""

    def __init__(self) -> None:
        """Inicializa o console Rich e configurações visuais."""
        self._console = Console()

    def show_header(self) -> None:
        """Exibe o cabeçalho estilizado do programa."""
        self._console.clear()
        banner = Panel(
            "[bold cyan]:speech_balloon: ANALISADOR AVANÇADO DE VOGAIS E TEXTOS[/bold cyan]\n"
            "[dim]Sistemas de Inspeção Textual e Leitura de Arquivos[/dim]",
            border_style="cyan",
            expand=False,
        )
        self._console.print(banner)

    def display_error(self, message: str) -> None:
        """Exibe mensagens de erro formatadas em painéis vermelhos."""
        error_panel = Panel(
            f"[bold red]:x: ERRO:[/bold red] {message}",
            border_style="red",
            title="[bold white]Falha na Operação[/bold white]",
        )
        self._console.print(error_panel)

    def display_results(
        self,
        analysis_data: List[Tuple[str, List[str], int]],
        frequencies: Dict[str, int],
        source_name: str,
    ) -> None:
        """Apresenta os dados analisados em tabelas e estatísticas estilizadas."""
        self._console.print(
            f"\n[bold green]:white_check_mark: Análise concluída com sucesso para:[/bold green] [bold yellow]{source_name}[/bold yellow]\n"
        )

        table = Table(
            title=":notebook: Detalhamento por Palavra",
            header_style="bold magenta",
            border_style="blue",
        )
        table.add_column("Palavra", style="bold white")
        table.add_column("Vogais Encontradas", style="cyan")
        table.add_column("Total de Vogais", justify="right", style="green")

        for word, vowels, count in analysis_data[:50]:
            vowels_str = ", ".join(vowels) if vowels else "[dim]Nenhuma[/dim]"
            table.add_row(word, vowels_str, str(count))

        self._console.print(table)

        if len(analysis_data) > 50:
            self._console.print(
                f"[dim]:information_source: Exibindo as primeiras 50 palavras de um total de {len(analysis_data)}.[/dim]\n"
            )

        freq_table = Table(
            title=":bar_chart: Frequência Geral de Vogais",
            header_style="bold yellow",
            border_style="yellow",
        )
        freq_table.add_column("Vogal", justify="center", style="bold cyan")
        freq_table.add_column("Ocorrências", justify="right", style="bold green")

        for vowel, count in frequencies.items():
            freq_table.add_row(vowel.upper(), str(count))

        self._console.print(freq_table)

    def run(self) -> None:
        """Executa o loop principal da aplicação e interage com o usuário."""
        self.show_header()

        try:
            self._console.print(
                "[bold]Escolha o modo de entrada de dados:[/bold]"
            )
            self._console.print("1. Digitar/Colar um texto diretamente")
            self._console.print("2. Ler de um arquivo de texto (.txt)")
            self._console.print("3. Sair\n")

            option = Prompt.ask(
                ":gear: Opção desejada", choices=["1", "2", "3"], default="1"
            )

            if option == "3":
                self._console.print(
                    "\n[bold cyan]:wave: Encerrando o programa. Até logo![/bold cyan]"
                )
                return

            text_content = ""
            source_name = ""

            if option == "1":
                text_content = Prompt.ask(
                    "\n:pencil: Digite ou cole o texto para análise"
                )
                source_name = "Texto Inserido Manualmente"
                if not text_content.strip():
                    self.display_error("Nenhum texto foi digitado.")
                    return

            elif option == "2":
                file_path = Prompt.ask(
                    "\n:file_folder: Digite o caminho do arquivo (ex: texto.txt)"
                )
                with Status(
                    "[bold green]:hourglass_flowing_sand: Lendo arquivo...[/bold green]",
                    spinner="dots",
                ):
                    time.sleep(0.5)
                    handler = FileHandler(file_path)
                    text_content = handler.read_content()
                source_name = file_path

            with Status(
                "[bold cyan]:gear: Processando e analisando estrutura textual...[/bold cyan]",
                spinner="dots",
            ):
                time.sleep(0.5)
                analyzer = TextAnalyzer(text_content)
                if not analyzer.words:
                    self.display_error(
                        "O texto fornecido não contém palavras válidas para análise."
                    )
                    return
                analysis_data = analyzer.analyze_full_dataset()
                frequencies = analyzer.get_vowel_frequencies()

            self.display_results(analysis_data, frequencies, source_name)

        except KeyboardInterrupt:
            self._console.print(
                "\n\n[bold yellow]:warning: Operação interrompida pelo usuário (Ctrl+C). Encerrando com segurança...[/bold yellow]"
            )
            sys.exit(0)
        except Exception as error:
            self.display_error(str(error))


if __name__ == "__main__":
    app = CLIInterface()
    app.run()