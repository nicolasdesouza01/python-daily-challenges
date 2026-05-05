class Tabuada:
    def __init__(self, numero):
        """
        Construtor: Aqui inicializamos o 'estado' do nosso objeto.
        """
        self.numero = numero

    def calcular_e_exibir(self):
        """
        Método que encapsula a lógica de exibição.
        """
        print('-' * 20)
        print(f'TABUADA DO {self.numero}')
        print('-' * 20)
        
        for i in range(1, 11):
            resultado = self.numero * i
            print(f'{self.numero} x {i:2} = {resultado}')
        
        print('-' * 20)

# --- Fluxo Principal (Main) ---
if __name__ == "__main__":
    try:
        num = int(input('Digite um número para ver sua tabuada: '))
        
        # Instanciando o objeto
        minha_tabuada = Tabuada(num)
        
        # Chamando o comportamento do objeto
        minha_tabuada.calcular_e_exibir()
        
    except ValueError:
        print("Erro: Por favor, digite um número inteiro válido.")