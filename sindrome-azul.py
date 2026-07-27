from dataclasses import dataclass, field
import random
import time
import math

@dataclass
class Personagem:
    nome: str
    nome_abr: str #nome abreviado, exibido no tabuleiro
    afi: str #afiliação: jogador (J) ou adversário (A)
    posicao_atual_linha: int
    posicao_atual_coluna: int
    pm_max: int #pm: pontos de moral (HP)
    pm_atual: int = field(init=False) #hp atual
    tec: int #tec: técnica (ATK)
    det: int #det: determinação (DEF/RES)
    rec: int #rec: reação (SPD/AGI)
    status_defendendo: bool = False #flag que checa se o personagem está defendendo em seu turno
    
    def __post_init__(self):
        self.pm_atual = self.pm_max #automaticamente seta o pm atual como o valor do pm máximo na instanciação

# Carregando atributos iniciais dos jogadores
jogador1 = Personagem(
    nome = "Catarina",
    nome_abr = "J1",
    afi = "J",
    posicao_atual_linha = 0,
    posicao_atual_coluna = 0,
    pm_max = 54,
    tec = 10,
    det = 2,
    rec = 7
)
        
adversario1 = Personagem(
    nome = "Aniratac",
    nome_abr = "A1",
    afi = "A",
    posicao_atual_linha = 1,
    posicao_atual_coluna = 1,
    pm_max = 45,
    tec = 14,
    det = 5,
    rec = 1
)

adversario2 = Personagem(
    nome = "Haras",
    nome_abr = "A2",
    afi = "A",
    posicao_atual_linha = 0,
    posicao_atual_coluna = 0,
    pm_max = 45,
    tec = 14,
    det = 5,
    rec = 3
)

adversario3 = Personagem(
    nome = "Anilorac",
    nome_abr = "A3",
    afi = "A",
    posicao_atual_linha = 2,
    posicao_atual_coluna = 2,
    pm_max = 45,
    tec = 14,
    det = 5,
    rec = 4
)

jogadores = [jogador1]
adversarios = [adversario1, adversario2, adversario3]

def movimentar_personagem(personagem, linha = None, coluna = None):
    personagem_jogador = personagem.afi == 'J'
    tabuleiro_selecionado = tabuleiro_jogador if personagem_jogador else tabuleiro_adversario
    
    if not personagem_jogador: #gera aleatoriamente para adversários
        posicoes_vazias = []
        for i, linha_selecionada in enumerate(tabuleiro_adversario):
            for j, coluna_selecionada in enumerate(linha_selecionada):
                if coluna_selecionada == '□':
                    posicoes_vazias.append((i, j))
        linha, coluna = random.choice(posicoes_vazias)
    else: #verifica se o informado pelo jogador é válido
        if (linha < 0 or linha > 2 or coluna < 0 or coluna > 2):
            if personagem_jogador:
                print("Opção inválida para linha e/ou coluna! [Apenas 0-2]")
            return False
        elif (linha == personagem.posicao_atual_linha and coluna == personagem.posicao_atual_coluna):
            if personagem_jogador:
                print("Mas você já está nessa posição...")
            return False
  
    linha_original = personagem.posicao_atual_linha
    coluna_original = personagem.posicao_atual_coluna
    tabuleiro_selecionado[linha_original][coluna_original] = '□'
    tabuleiro_selecionado[linha][coluna] = personagem.nome_abr
    personagem.posicao_atual_linha = linha
    personagem.posicao_atual_coluna = coluna
    print(personagem.nome + " se moveu!")
    return True

def tocar_partitura(atacante, alvo):
    dano = max(atacante.tec - alvo.det, 0) #+ futuros outros modificadores
    if (alvo.status_defendendo): # inicialmente reduz em 15% o dano recebido
        dano *= 0.85
    dano = math.floor(dano + 0.5)
    alvo.pm_atual -= dano
    print(f"{atacante.nome} ataca! {alvo.nome} sofreu {dano} de dano!\n")
    if alvo.pm_atual <= 0:
        print(f"{alvo.nome} perdeu toda a sua moral!\n")
        alvo.pm_atual = 0

def defender(personagem):
    personagem.status_defendendo = True
    print(f"{personagem.nome} se preparou para defender!\n")

def resetar_status(personagens):
    for personagem in personagens:
        personagem.status_defendendo = False

def avancar_rodada(posicao_atual, rodada_atual, personagens):
    posicao_atual += 1

    if posicao_atual >= len(personagens):
        posicao_atual = 0
        rodada_atual += 1
        resetar_status(personagens)
        time.sleep(1)
        exibir_tabuleiro()

    return posicao_atual, rodada_atual

def exibir_tabuleiro():
    print()
    print(f"Rodada {rodada_atual}!\n")
    print(f"{jogador1.nome}'s BAND\t\t{adversario1.nome}'s BAND") 

    for i in range(3):
        linha_jogador = " ".join(tabuleiro_jogador[i])
        linha_adversario = " ".join(tabuleiro_adversario[i])
        print(linha_jogador + "\t\t\t" + linha_adversario)
        
    print(f"PM: {jogador1.pm_atual}/{jogador1.pm_max}")

# Criando tabuleiros
tabuleiro_jogador = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]
tabuleiro_adversario = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]

# Inicializando tabuleiros com as posições iniciais dos jogadores
tabuleiro_jogador[jogador1.posicao_atual_linha][jogador1.posicao_atual_coluna] = jogador1.nome_abr

tabuleiro_adversario[adversario1.posicao_atual_linha][adversario1.posicao_atual_coluna] = adversario1.nome_abr
tabuleiro_adversario[adversario2.posicao_atual_linha][adversario2.posicao_atual_coluna] = adversario2.nome_abr
tabuleiro_adversario[adversario3.posicao_atual_linha][adversario3.posicao_atual_coluna] = adversario3.nome_abr

rodada_atual = 1

posicao_atual = 0

comando_selecionado = ""

acoes_adversario = ['m', 't', 'd']

ordem_personagens = sorted(
    jogadores + adversarios,
    key=lambda personagem: personagem.rec,
    reverse=True
)

exibir_tabuleiro()

while True:

    personagem_atual = ordem_personagens[posicao_atual]

    print(f"* Turno de {personagem_atual.nome}!\n")

    # Ação do jogador
    if (personagem_atual.afi == 'J'):

        print("Escolha a ação:")
        print("m - Movimentar personagem")
        print("t - Tocar partitura")
        print("d - Defender")
        print("i - Usar item")
        print("e - Encerrar jogo")
        comando_selecionado = input('>> ')

        acao_realizada = False
        
        if (comando_selecionado == 'm'):
            while True:
                linha = int(input('Linha: '))
                coluna = int(input('Coluna: '))
                if (movimentar_personagem(jogador1, linha, coluna)):
                    acao_realizada = True
                    break
                
        elif (comando_selecionado == 't'):
            tocar_partitura(jogador1, adversario1)
            acao_realizada = True

        elif (comando_selecionado == 'd'):
            defender(jogador1)
            acao_realizada = True

        elif (comando_selecionado == 'e'):
            break

        else:
            print("Mas esse comando não existe...")

        if not acao_realizada:
            continue

        time.sleep(1)

        if (adversario1.pm_atual == 0):
            print(f"{jogador1.nome} venceu! yay :3")
            break

    # Ação do adversário
    else:
        while True:
            acao_adversario_escolhida = random.choice(acoes_adversario)
            if (acao_adversario_escolhida == 'm'):
                movimentar_personagem(adversario1)
                break
            elif (acao_adversario_escolhida == 't'):
                tocar_partitura(adversario1, jogador1)
                break
            elif (acao_adversario_escolhida == 'd'):
                if (posicao_atual + 1 == len(ordem_personagens)): #se ele for o último, não faz sentido defender
                    continue
                else:
                    defender(adversario1)
                    break
                
    # Avançamos a rodada                
    posicao_atual, rodada_atual = avancar_rodada(posicao_atual, rodada_atual, ordem_personagens)
    continue

    
