from dataclasses import dataclass, field
import random
import time

'''

  
    rec: int #rec: reação (SPD/AGI)
    det: int #det: determinação (DEF/RES)
'''

@dataclass
class Jogador:
    nome: str
    nome_abr: str
    posicao_atual_linha: int
    posicao_atual_coluna: int
    pm_max: int #pm: pontos de moral (HP)
    pm_atual: int = field(init=False) #hp atual
    tec: int #tec: técnica (ATK)

    def __post_init__(self):
        self.pm_atual = self.pm_max #automaticamente seta o pm atual como o valor do pm máximo
  
def movimentar_personagem(linha, coluna):
    if (linha < 0 or linha > 2 or coluna < 0 or coluna > 2):
        print("Opção inválida para linha e/ou coluna! [Apenas 0-2]")
        return False
    elif (linha == jogador1.posicao_atual_linha and coluna == jogador1.posicao_atual_coluna):
        print("Mas você já está nessa posição...")
        return False
    else:
        linhaOriginal = jogador1.posicao_atual_linha
        colunaOriginal = jogador1.posicao_atual_coluna
        tabuleiroJogador[linhaOriginal][colunaOriginal] = '□'
        tabuleiroJogador[linha][coluna] = jogador1.nome_abr
        jogador1.posicao_atual_linha = linha
        jogador1.posicao_atual_coluna = coluna
        print(jogador1.nome + " se moveu!")
        return True

def movimentar_adversario():
    linha, coluna = random.randint(0, 2), random.randint(0, 2)
    while linha == adversario1.posicao_atual_linha and coluna == adversario1.posicao_atual_coluna:
        linha, coluna = random.randint(0, 2), random.randint(0, 2)
        
    linhaOriginal = adversario1.posicao_atual_linha
    colunaOriginal = adversario1.posicao_atual_coluna
    tabuleiroAdversario[linhaOriginal][colunaOriginal] = '□'
    tabuleiroAdversario[linha][coluna] = adversario1.nome_abr
    adversario1.posicao_atual_linha = linha
    adversario1.posicao_atual_coluna = coluna
    print(adversario1.nome + " se moveu!")


def tocar_partitura_jogador():
    dano = jogador1.tec #+ futuros outros modificadores
    adversario1.pm_atual -= dano
    print(f"{jogador1.nome} ataca! {adversario1.nome} sofreu {dano} de dano!")
    if adversario1.pm_atual <= 0:
        print(f"{adversario1.nome} perdeu toda a sua moral!")
        adversario1.pm_atual = 0
    
# Carregando atributos iniciais dos jogadores
jogador1 = Jogador(
    nome = "Catarina",
    nome_abr = "J1",
    posicao_atual_linha = 0,
    posicao_atual_coluna = 0,
    pm_max = 54,
    tec = 10)
        
adversario1 = Jogador(
    nome = "Aniratac",
    nome_abr = "A1",
    posicao_atual_linha = 1,
    posicao_atual_coluna = 1,
    pm_max = 45,
    tec = 14)

# Criando tabuleiros
tabuleiroJogador = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]
tabuleiroAdversario = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]

# Inicializando tabuleiros com as posições iniciais dos jogadores
tabuleiroJogador[jogador1.posicao_atual_linha][jogador1.posicao_atual_coluna] = jogador1.nome_abr
tabuleiroAdversario[adversario1.posicao_atual_linha][adversario1.posicao_atual_coluna] = adversario1.nome_abr

turno_atual = 1

comando = ""

# Exibindo o tabuleiro na tela
while True:
    
    print()
    print(f"Turno {turno_atual}!\n")
    print(f"{jogador1.nome}'s BAND\t\t{adversario1.nome}'s BAND") 

    for i in range(3):
        linhaTabuleiro = " ".join(tabuleiroJogador[i])
        linhaAdversário = " ".join(tabuleiroAdversario[i])
        print(linhaTabuleiro + "\t\t\t" + linhaAdversário)
        
    print(f"PM: {jogador1.pm_atual}/{jogador1.pm_max}\t\tPM: {adversario1.pm_atual}/{adversario1.pm_max}\n")
    
    print("Escolha a ação:")
    print("m - Movimentar personagem")
    print("t - Tocar partitura")
    print("d - Defender")
    print("i - Usar item")
    print("e - Encerrar jogo")
    comando = input('>> ')

    acao_realizada = False
    
    if (comando == 'm'):
        while True:
            linha = int(input('Linha: '))
            coluna = int(input('Coluna: '))
            if (movimentar_personagem(linha, coluna)):
                acao_realizada = True
                break
            
    elif (comando == 't'):
        tocar_partitura_jogador()
        acao_realizada = True

    elif (comando == 'e'):
        break

    else:
        print("Mas esse comando não existe...")

    if not acao_realizada:
        continue

    time.sleep(1)
    
    if (adversario1.pm_atual == 0):
        print(f"{jogador1.nome} venceu! yay :3")
        break

    movimentar_adversario()

    time.sleep(1)
    
    turno_atual += 1
