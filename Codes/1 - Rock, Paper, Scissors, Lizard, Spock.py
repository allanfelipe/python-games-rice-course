# Rock-paper-scissors-lizard-Spock

# ------- Regras ------- #
# Tesoura corta papel
# Papel cobre pedra
# Pedra esmaga lagarto
# Lagarto envenena Spock
# Spock esmaga tesoura
# Tesoura decapita lagarto
# Lagarto come papel
# Papel refuta Spock
# Spock vaporiza pedra
# Pedra amassa tesoura

# Imagine um círculo com os 5 elementos dispostos em sentido horário:
# 0 - pedra
# 1 - Spock
# 2 - papel
# 3 - lagarto
# 4 - tesoura
# Tomando qualquer elemento X como referência, note que os 2 elementos
# no sentido horário vencem X e os 2 elementos no sentido anti-horário
# perdem para X. O problema pode ser analizado observando o resultado de
# (N_jogador1 - N_jogador2) % 5. Se esse resultado é 0 houve empate, se
# é 1 ou 2 o jogador 1 venceu e se é 3 ou 4 o jogador 2 venceu.

import random

def names():
    names = ['pedra', 'spock', 'papel', 'lagarto', 'tesoura']
    return names

def name_to_number(guess):
    if guess.lower() in names():
        return names().index(guess.lower())
    else:
        return 'Inexistente'

def number_to_name(number):
    if number >= 0 and number < len(names()):
        return names()[number]
    else:
        return 'Inexistente'
    
def game(player_choice):
    if (player_choice.lower() in names()):
        player_choice_N = name_to_number(player_choice)
        computer_choice_N = random.randint(0,4)
        diff = (player_choice_N - computer_choice_N) % len(names())
        if diff == 0:
            msg = '** Empate! **'
        elif diff == 1 or diff == 2:
            msg = '** Você venceu! **'
        elif diff == 3 or diff == 4:
            msg = '** Você perdeu ;( **'
        print('\nVocê escolheu:', player_choice)
        print('O computador escolheu:', number_to_name(computer_choice_N))
        print(msg)
    else:
        print('\nNão é uma opção válida!')


def main():
    guess = input('\nDigite sua jogada: ')
    game(guess)

    joga = input('\nGostaria de jogar de novo? [S/N]: ')
    while joga.lower() != 's' and joga.lower() != 'n':
        joga = input('\nEscolha inválida. Gostaria de jogar de novo? [S/N]: ')
    if joga == 'N' or joga == 'n':
        return 0
    elif joga == 'S' or joga == 's':
        main()

main()

