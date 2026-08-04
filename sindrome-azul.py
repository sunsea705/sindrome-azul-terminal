from dataclasses import dataclass, field
from enum import Enum
from itertools import zip_longest
import random
import time
import math
import os


class Status(Enum):
    SEM_STATUS = ""
    DEFENDENDO = "DEFENDENDO"
    DERROTADO = "DERROTADO"

    def __str__(self):
        if self != self.SEM_STATUS:
            return f"[{self.value}]"
        else:
            return ""

class ClassificacaoPartitura(Enum):
    ATAQUE = "ATAQUE"
    CURA_PM = "CURA_PM"
    BUFF_TECNICA = "BUFF_TECNICA"
    BUFF_DETERMINACAO = "BUFF_DETERMINACAO"
    DEBUFF_TECNICA = "DEBUFF_TECNICA"
    DEBUFF_DETERMINACAO = "DEBUFF_DETERMINACAO"

    def __str__(self):
        return f"[{self.value}]"

class Atributo(Enum):
    TECNICA = "TÉCNICA"
    DETERMINACAO = "DETERMINAÇÃO"

    def __str__(self):
        return f"[{self.value}]"
    
@dataclass
class Batalha:
    pontos_de_empolgacao_jogador_atual: int = 0
    pontos_de_empolgacao_jogador_max: int = 10
    pontos_de_empolgacao_adversario: int = 0
    pontos_de_empolgacao_adversario_max: int = 10

    def conceder_pe(self, afiliacao, valor_pe):
        if afiliacao == "J":
            self.pontos_de_empolgacao_jogador_atual = min(
                self.pontos_de_empolgacao_jogador_atual + valor_pe,
                self.pontos_de_empolgacao_jogador_max
            )
        else:
            self.pontos_de_empolgacao_adversario = min(
                self.pontos_de_empolgacao_adversario + valor_pe,
                self.pontos_de_empolgacao_adversario_max
            )
            
    def exibir_pe(self):
        exibicao_pe_jogador = (
            f"PE: {self.pontos_de_empolgacao_jogador_atual}/"
            f"{self.pontos_de_empolgacao_jogador_max}"
        )
        exibicao_pe_adversario = (
            f"PE: {self.pontos_de_empolgacao_adversario}/"
            f"{self.pontos_de_empolgacao_adversario_max}"
        )
        print(f"{exibicao_pe_jogador:<40}{exibicao_pe_adversario}")
        print()

@dataclass
class Partitura:
    nome: str
    descricao: str
    classificacao: ClassificacaoPartitura #serve pra diferenciar entre os tipos de partitura (ataque, cura, etc...)
    alcance: int #range, indo de 1-All
    alvos: int #targets, indo de 1-3
    pe_minimo: int #número mínimo de PEs (Pontos de Empolgação) necessários para executar esta partitura
    modificador: float #modificador usado no cálculo das fórmulas
    bonus: int #bonificador usado para adicionar no valor final da fórmula
    tocar_partitura: callable #função chamada que executa a partitura

@dataclass
class Personagem:
    nome: str
    nome_abr: str #nome abreviado, exibido no tabuleiro
    afi: str #afiliação: jogador (J) ou adversário (A)
    posicao_atual_linha: int
    posicao_atual_coluna: int
    pm_max: int #pm: pontos de moral (HP)
    pm_atual: int = field(init = False) #hp atual
    tec: int #tec: técnica (ATK)
    det: int #det: determinação (DEF/RES)
    rec: int #rec: reação (SPD/AGI)
    status: str = Status.SEM_STATUS #flag que guarda status do personagem, como DEFENDENDO, DERROTADO, etc.
    atributo_buffado: Atributo | None = None #identificador de algum atributo que esteja com modificador no momento
    valor_buff: float = 1 #valor do modificador para aquele buff em questão
    defendendo: bool = False
    partituras_equipadas: list[Partitura] = field(default_factory = list) # instancia uma nova lista para cada objeto novo criado. pq python por padrão é comunista :p
    
    def __post_init__(self):
        self.pm_atual = self.pm_max #automaticamente seta o pm atual como o valor do pm máximo na instanciação

    @property
    def derrotado(self):
        return self.pm_atual <= 0

# Ordenação pelo maior valor de REC. Personagens com RECs iguais são escolhidos aleatoriamente, igual em Pokémon
def ordenar_personagens(personagens: list[Personagem]):
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

def exibir_tabuleiro(batalha_atual: Batalha):
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

    batalha_atual.exibir_pe()
    
def movimentar_personagem(personagem: Personagem, linha: int | None = None, coluna: int | None = None):
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

# O que se entende por ataque básico é a forma mais simples de se efetuar dano, sem efeitos adicionais.
def ataque_basico(batalha_atual: Batalha, partitura: Partitura, atacante: Personagem, alvo: Personagem):
    tecnica_atacante = atacante.tec
    if (atacante.atributo_buffado == Atributo.TECNICA):
        tecnica_atacante *= atacante.valor_buff
    dano = max(((tecnica_atacante * partitura.modificador) + partitura.bonus) - alvo.det, 0)
    if alvo.defendendo: # por padrão reduz em 15% o dano recebido
        dano *= 0.85
    if alvo.atributo_buffado == Atributo.DETERMINACAO:
        dano *= alvo.valor_buff
    dano = math.floor(dano + 0.5)
    alvo.pm_atual -= dano
    print(f"{atacante.nome} toca [{partitura.nome}] em {alvo.nome}!")
    print(f"{alvo.nome} sofreu {dano} de dano!\n")
    if alvo.pm_atual <= 0:
        print(f"{alvo.nome} perdeu toda a sua moral!\n")
        alvo.pm_atual = 0
        alvo.status = Status.DERROTADO
        alvo.defendendo = False
    batalha_atual.conceder_pe(atacante.afi, 4)

# Cura básica é baseada no PM máx. do alvo através dos valores de modificador e bônus da partitura
def cura_basica(batalha_atual: Batalha, partitura: Partitura, atacante: Personagem, alvo: Personagem):
    pm_recuperado = round(alvo.pm_max * partitura.modificador) + partitura.bonus
    alvo.pm_atual = min(alvo.pm_atual + pm_recuperado, alvo.pm_max)
    print(f"{atacante.nome} toca [{partitura.nome}] em {alvo.nome}!")
    mensagem_recuperacao_pm = f"{alvo.nome} recuperou {pm_recuperado} PM!"
    if alvo.pm_atual == alvo.pm_max:
        mensagem_recuperacao_pm += f" {alvo.nome} teve todo seu PM recuperado!"
    print(mensagem_recuperacao_pm)
    batalha_atual.conceder_pe(atacante.afi, 2)

# Função simples e genérica para concender buffs
def partitura_basica_conceder_buff(batalha_atual: Batalha, partitura: Partitura, atacante: Personagem, alvo: Personagem):
    match partitura.classificacao:
        case ClassificacaoPartitura.BUFF_TECNICA:
            alvo.atributo_buffado = Atributo.TECNICA
        case ClassificacaoPartitura.BUFF_DETERMINACAO:
            alvo.atributo_buffado = Atributo.DETERMINACAO
        case _:
            alvo.atributo_buffado = None
    alvo.valor_buff = partitura.modificador
    print(f"{atacante.nome} toca [{partitura.nome}] em {alvo.nome}!")
    print(f"{alvo.nome} teve {alvo.atributo_buffado} aumentado pelo resto da rodada!")
    batalha_atual.conceder_pe(atacante.afi, 2)
 
def defender(batalha_atual: Batalha, personagem: Personagem):
    personagem.defendendo = True
    personagem.status = Status.DEFENDENDO
    batalha_atual.conceder_pe(personagem.afi, 2)
    print(f"{personagem.nome} se preparou para defender!\n")

def resetar_status(personagens: list[Personagem]):
    for personagem in personagens:
        personagem.defendendo = False
        if personagem.derrotado:
            continue
        personagem.status = Status.SEM_STATUS
        personagem.atributo_buffado = None
        personagem.valor_buff = 1
        
def avancar_rodada(posicao_atual: int, rodada_atual: int, personagens: list[Personagem]):
    posicao_atual += 1
    nova_rodada = False

    if posicao_atual >= len(personagens): # significa que todos os personagens já executaram suas ações
        posicao_atual = 0
        rodada_atual += 1
        resetar_status(personagens)
        nova_rodada = True
     
    return posicao_atual, rodada_atual, nova_rodada

# Criando partituras
partitura_brilha_estrelinha = Partitura(
    nome = "Brilha Brilha, Estrelinha ★",
    descricao = "Uma musiquinha simples amada por Carolina. É um ataque básico.",
    classificacao = ClassificacaoPartitura.ATAQUE,
    alcance = 1, alvos = 1, pe_minimo = 0, modificador = 1, bonus = 0,
    tocar_partitura = ataque_basico
)
partitura_parabens_pra_voce = Partitura(
    nome = "Parabéns Pra Você! 👏",
    descricao = "Você já deve ter ouvido antes perto de um bolo. É um ataque básico.",
    classificacao = ClassificacaoPartitura.ATAQUE,
    alcance = 1, alvos = 1, pe_minimo = 0, modificador = 1, bonus = 0,
    tocar_partitura = ataque_basico
)
partitura_beijinho_doce = Partitura(
    nome = "Beijinho Doce 💋 ",
    descricao = "Quem não adora um beijinho? Cura uma pequena quantidade de PM do alvo.",
    classificacao = ClassificacaoPartitura.CURA_PM,
    alcance = 1, alvos = 1, pe_minimo = 0, modificador = 0.1, bonus = 10,
    tocar_partitura = cura_basica
)
partitura_atencao_basica = Partitura(
    nome = "Atenção Básica! ⚠",
    descricao = "Atenção na contramão! Aumenta levemente a defesa do aliado, reduzindo levemente o dano recebido até o fim da rodada.",
    classificacao = ClassificacaoPartitura.BUFF_DETERMINACAO,
    alcance = 1, alvos = 1, pe_minimo = 0, modificador = 0.25, bonus = 0,
    tocar_partitura = partitura_basica_conceder_buff
)

# Carregando atributos iniciais dos jogadores e adversários
jogador1 = Personagem(
    nome = "Catarina", nome_abr = "J1", afi = "J",
    posicao_atual_linha = 0, posicao_atual_coluna = 0,
    pm_max = 42, tec = 10, det = 2, rec = 10,
    partituras_equipadas = [partitura_atencao_basica]
)
jogador2 = Personagem(
    nome = "Sarah", nome_abr = "J2", afi = "J",
    posicao_atual_linha = 1, posicao_atual_coluna = 2,
    pm_max = 55, tec = 12, det = 7, rec = 4,
    partituras_equipadas = [partitura_beijinho_doce]
)
jogador3 = Personagem(
    nome = "Carolina", nome_abr = "J3", afi = "J",
    posicao_atual_linha = 2, posicao_atual_coluna = 1,
    pm_max = 31, tec = 14, det = 1, rec = 17,
    partituras_equipadas = [partitura_brilha_estrelinha]
)
        
adversario1 = Personagem(
    nome = "Aniratac", nome_abr = "A1", afi = "A",
    posicao_atual_linha = 1, posicao_atual_coluna = 1,
    pm_max = 1, tec = 14, det = 5, rec = 1,
    partituras_equipadas = [partitura_parabens_pra_voce]
)
adversario2 = Personagem(
    nome = "Haras", nome_abr = "A2", afi = "A",
    posicao_atual_linha = 0, posicao_atual_coluna = 0,
    pm_max = 1, tec = 14, det = 3, rec = 3,
    partituras_equipadas = [partitura_parabens_pra_voce]
)
adversario3 = Personagem(
    nome = "Anilorac", nome_abr = "A3", afi = "A",
    posicao_atual_linha = 2, posicao_atual_coluna = 2,
    pm_max = 1, tec = 14, det = 0, rec = 6,
    partituras_equipadas = [partitura_parabens_pra_voce]
)

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

batalha_atual = Batalha()

rodada_atual = 1

posicao_atual = 0

comando_selecionado = ""

acoes_adversario = ['t']

exibir_tabuleiro(batalha_atual)

while True:

    # Checagens de fim de jogo
    if all(adversario.derrotado for adversario in adversarios):
        print(f"Banda de {jogador1.nome} venceu! yay :3")
        print(f"O grupo inteiro ganhou 37 XP!")
        break
    
    elif all(jogador.derrotado for jogador in jogadores):
        print(f"Banda de {jogador1.nome} PERDEU! game over :(")
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
                partitura_escolhida = None
                # Escolha da partitura
                while True:
                    print("Escolha a partitura:")
                    for i, partitura in enumerate(personagem_atual.partituras_equipadas):
                        print(f"{i + 1}. {partitura.nome} ({partitura.descricao})")
                    indice_partitura = int(input(">> "))
                    if indice_partitura < 1 or indice_partitura > len(personagem_atual.partituras_equipadas):
                        print("Mas essa partitura não existe...")
                    else:
                        partitura_escolhida = personagem_atual.partituras_equipadas[indice_partitura - 1]
                        break
                # Escolha do alvo
                while True:
                    lista_alvos = None
                    alvo_escolhido = None
                    print("Escolha o alvo:")
                    match partitura_escolhida.classificacao:
                        case ClassificacaoPartitura.ATAQUE | ClassificacaoPartitura.DEBUFF_TECNICA | ClassificacaoPartitura.DEBUFF_DETERMINACAO:
                            lista_alvos = adversarios
                        case ClassificacaoPartitura.CURA_PM | ClassificacaoPartitura.BUFF_TECNICA | ClassificacaoPartitura.BUFF_DETERMINACAO:
                            lista_alvos = jogadores
                    for i, alvo in enumerate(lista_alvos):
                        if alvo.derrotado:
                            continue
                        print(f"{i + 1}. ({alvo.nome_abr}) {alvo.nome}")
                    indice_alvo = int(input(">> "))
                    if indice_alvo < 1 or indice_alvo > len(lista_alvos):
                        print("Mas esse alvo não existe...")
                    else:
                        alvo_escolhido = lista_alvos[indice_alvo - 1]
                        partitura_escolhida.tocar_partitura(batalha_atual, partitura_escolhida, personagem_atual, alvo_escolhido)
                        acao_realizada = True
                        break
        
            elif (comando_selecionado == 'd'):
                defender(batalha_atual, personagem_atual)
                acao_realizada = True

            elif (comando_selecionado == 'e'):
                print("Obrigada pelo feedback!\nVejo você em breve!")
                break

            else:
                print("Mas esse comando não existe...")

            if not acao_realizada:
                continue

            time.sleep(2)
            exibir_tabuleiro(batalha_atual)

        # Ação do adversário
        else:
            while True:
                acao_adversario_escolhida = random.choice(acoes_adversario)
                if (acao_adversario_escolhida == 'm'):
                    movimentar_personagem(personagem_atual)
                    break
                elif (acao_adversario_escolhida == 't'):
                    partitura_escolhida = random.choice(personagem_atual.partituras_equipadas)
                    partitura_escolhida.tocar_partitura(batalha_atual, partitura_escolhida, personagem_atual, random.choice(jogadores))

                    break
                elif (acao_adversario_escolhida == 'd'):
                    if (posicao_atual + 1 == len(personagens)): #se ele for o último, não faz sentido defender
                        continue
                    else:
                        defender(batalha_atual, personagem_atual)
                        break
            time.sleep(2)
            exibir_tabuleiro(batalha_atual)
         
    # Avançamos a rodada                
    posicao_atual, rodada_atual, nova_rodada = avancar_rodada(posicao_atual, rodada_atual, personagens)
    
    if nova_rodada:
        time.sleep(2)
        exibir_tabuleiro(batalha_atual)
        
    continue
