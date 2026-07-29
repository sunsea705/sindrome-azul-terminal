from dataclasses import dataclass, field
from itertools import zip_longest
import random
import time
import math
import os

STATUS_DEFENDENDO = "[DEFENDENDO]"
STATUS_DERROTADO = "[DERROTADO]"

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
    status: str = "" #flag que guarda status do personagem, como DEFENDENDO, DERROTADO, etc.
    defendendo: bool = False
    
    def __post_init__(self):
        self.pm_atual = self.pm_max #automaticamente seta o pm atual como o valor do pm máximo na instanciação

    @property
    def derrotado(self):
        return self.pm_atual <= 0

# Ordenação pelo maior valor de REC. Personagens com RECs iguais são escolhidos aleatoriamente, igual em Pokémon
def ordenar_personagens(personagens):
    random.shuffle(personagens)
    personagens_ordenados = sorted(
        personagens,
        key=lambda personagem: personagem.rec,
        reverse=True
    )
    return personagens_ordenados

# atualmente só funciona no linux e se executado num terminal nativo...
def limpar_tela():
    os.system("clear")

def exibir_tabuleiro():
    limpar_tela()
    print()
    print(f"Rodada {rodada_atual}!\n")
    
    lado_jogador = f"Banda de {jogador1.nome}"
    lado_adversario = f"Banda de  {adversario1.nome}"
    print(f"{lado_jogador:<40}{lado_adversario}")
    
    for i in range(3):
        # adiciona um espaço de até 25 caracteres entre os tabuleiros
        print(
            f'{" ".join(tabuleiro_jogador[i]):<40}'
            f'{" ".join(tabuleiro_adversario[i])}'
        )

    print()
   
    for jogador, adversario in zip_longest(jogadores, adversarios):
        
        exibicao_detalhes_jogadores = (
            f"({jogador.nome_abr}) {jogador.nome} {jogador.status} PM: {jogador.pm_atual}/{jogador.pm_max} "
            if jogador else ""
        )
        
        exibicao_detalhes_adversarios = (
            f"({adversario.nome_abr}) {adversario.nome} {adversario.status} PM: {adversario.pm_atual}/{adversario.pm_max} "
            if adversario else ""
        )

        print(f"{exibicao_detalhes_jogadores:<40}{exibicao_detalhes_adversarios}")

    print()

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
            print("Opção inválida para linha e/ou coluna! [Apenas 0-2]")
            return False
        if (linha == personagem.posicao_atual_linha and coluna == personagem.posicao_atual_coluna):
            print("Mas você já está nessa posição...")
            return False
        if tabuleiro_selecionado[linha][coluna] != "□":
            print("Mas já existe alguém nessa posição...")
            return False
       
    linha_original = personagem.posicao_atual_linha
    coluna_original = personagem.posicao_atual_coluna
    tabuleiro_selecionado[linha_original][coluna_original] = '□'
    tabuleiro_selecionado[linha][coluna] = personagem.nome_abr
    personagem.posicao_atual_linha = linha
    personagem.posicao_atual_coluna = coluna
    print(f"{personagem.nome} se moveu!")
    return True

def tocar_partitura(atacante, alvo):
    dano = max(atacante.tec - alvo.det, 0) #+ futuros outros modificadores
    if alvo.defendendo: # inicialmente reduz em 15% o dano recebido
        dano *= 0.85
    dano = math.floor(dano + 0.5)
    alvo.pm_atual -= dano
    print(f"{atacante.nome} ataca {alvo.nome}! {alvo.nome} sofreu {dano} de dano!\n")
    if alvo.pm_atual <= 0:
        print(f"{alvo.nome} perdeu toda a sua moral!\n")
        alvo.pm_atual = 0
        alvo.status = STATUS_DERROTADO
        alvo.defendendo = False

def defender(personagem):
    personagem.defendendo = True
    personagem.status = STATUS_DEFENDENDO
    print(f"{personagem.nome} se preparou para defender!\n")

def resetar_status(personagens):
    for personagem in personagens:
        personagem.defendendo = False
        if personagem.derrotado:
            continue
        personagem.status = ""
        
def avancar_rodada(posicao_atual, rodada_atual, personagens):
    posicao_atual += 1
    nova_rodada = False

    if posicao_atual >= len(personagens): # significa que todos os personagens já executaram suas ações
        posicao_atual = 0
        rodada_atual += 1
        resetar_status(personagens)
        nova_rodada = True
     
    return posicao_atual, rodada_atual, nova_rodada

# Carregando atributos iniciais dos jogadores e adversários
jogador1 = Personagem(nome = "Catarina", nome_abr = "J1", afi = "J", posicao_atual_linha = 0, posicao_atual_coluna = 0, pm_max = 1, tec = 10, det = 2, rec = 10)
jogador2 = Personagem(nome = "Sarah", nome_abr = "J2", afi = "J", posicao_atual_linha = 1, posicao_atual_coluna = 2, pm_max = 1, tec = 12, det = 7, rec = 4)
jogador3 = Personagem(nome = "Carolina", nome_abr = "J3", afi = "J", posicao_atual_linha = 2, posicao_atual_coluna = 1, pm_max = 1, tec = 14, det = 1, rec = 17)
        
adversario1 = Personagem(nome = "Aniratac", nome_abr = "A1", afi = "A", posicao_atual_linha = 1, posicao_atual_coluna = 1, pm_max = 1, tec = 14, det = 5, rec = 1)
adversario2 = Personagem(nome = "Haras", nome_abr = "A2", afi = "A", posicao_atual_linha = 0, posicao_atual_coluna = 0, pm_max = 1, tec = 14, det = 3, rec = 3)
adversario3 = Personagem(nome = "Anilorac", nome_abr = "A3", afi = "A", posicao_atual_linha = 2, posicao_atual_coluna = 2, pm_max = 1, tec = 14, det = 0, rec = 6)

# Criando tabuleiros
tabuleiro_jogador = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]
tabuleiro_adversario = [["□", "□", "□"], ["□", "□", "□"], ["□", "□", "□"]]

# Inicializando tabuleiros com as posições iniciais dos jogadores
tabuleiro_jogador[jogador1.posicao_atual_linha][jogador1.posicao_atual_coluna] = jogador1.nome_abr
tabuleiro_jogador[jogador2.posicao_atual_linha][jogador2.posicao_atual_coluna] = jogador2.nome_abr
tabuleiro_jogador[jogador3.posicao_atual_linha][jogador3.posicao_atual_coluna] = jogador3.nome_abr

tabuleiro_adversario[adversario1.posicao_atual_linha][adversario1.posicao_atual_coluna] = adversario1.nome_abr
tabuleiro_adversario[adversario2.posicao_atual_linha][adversario2.posicao_atual_coluna] = adversario2.nome_abr
tabuleiro_adversario[adversario3.posicao_atual_linha][adversario3.posicao_atual_coluna] = adversario3.nome_abr

jogadores = [jogador1, jogador2, jogador3]
adversarios = [adversario1, adversario2, adversario3]
personagens = ordenar_personagens(jogadores + adversarios)

rodada_atual = 1

posicao_atual = 0

comando_selecionado = ""

acoes_adversario = ['m', 't', 'd']

exibir_tabuleiro()

while True:

    # Checagens de fim de jogo
    if all(adversario.derrotado for adversario in adversarios):
        print(f"{jogador1.nome}'s BAND venceu! yay :3")
        print(f"{jogador1.nome}'s BAND venceu! yay :3")
        break
    
    elif all(jogador.derrotado for jogador in jogadores):
        print(f"{jogador1.nome}'s BAND PERDEU! game over :")
        break

    personagem_atual = personagens[posicao_atual]

    if not personagem_atual.derrotado:
        
        print(f"* Turno de {personagem_atual.nome}!")

        # Ação do jogador
        if (personagem_atual.afi == 'J'):

            print()
            print("Escolha a ação:")
            print("m - Movimentar personagem")
            print("t - Tocar partitura")
            print("d - Defender")
            print("i - Usar item")
            print("e - Encerrar jogo")
            comando_selecionado = input(">> ")

            acao_realizada = False
            
            if (comando_selecionado == 'm'):
                while True:
                    linha = int(input('Linha: '))
                    coluna = int(input('Coluna: '))
                    if (movimentar_personagem(personagem_atual, linha, coluna)):
                        acao_realizada = True
                        break
                    
            elif (comando_selecionado == 't'):
                while True:
                    print("Escolha o adversário:")
                    for i, adversario in enumerate(adversarios):
                        if adversario.derrotado:
                            continue
                        print(f"{i + 1}. ({adversario.nome_abr}) {adversario.nome}")
                    indice = int(input(">> "))
                    if indice < 1 or indice > len(adversarios):
                        print("Mas esse adversário não existe...")
                    else:
                        tocar_partitura(personagem_atual, adversarios[indice - 1])
                        acao_realizada = True
                        break
        
            elif (comando_selecionado == 'd'):
                defender(personagem_atual)
                acao_realizada = True

            elif (comando_selecionado == 'e'):
                print("Obrigada pelo feedback!\nVejo você em breve!")
                break

            else:
                print("Mas esse comando não existe...")

            if not acao_realizada:
                continue

            time.sleep(2)
            exibir_tabuleiro()

        # Ação do adversário
        else:
            while True:
                acao_adversario_escolhida = random.choice(acoes_adversario)
                if (acao_adversario_escolhida == 'm'):
                    movimentar_personagem(personagem_atual)
                    break
                elif (acao_adversario_escolhida == 't'):
                    tocar_partitura(personagem_atual, random.choice(jogadores))
                    break
                elif (acao_adversario_escolhida == 'd'):
                    if (posicao_atual + 1 == len(personagens)): #se ele for o último, não faz sentido defender
                        continue
                    else:
                        defender(personagem_atual)
                        break
            time.sleep(2)
            exibir_tabuleiro()
         
    # Avançamos a rodada                
    posicao_atual, rodada_atual, nova_rodada = avancar_rodada(posicao_atual, rodada_atual, personagens)
    
    if nova_rodada:
        time.sleep(2)
        exibir_tabuleiro()
        
    continue
