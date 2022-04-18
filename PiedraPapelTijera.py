# Juego de piedra papel o tijera

import random


def jugar():
    usuario = input("Escoge una opcion: 'pi' para piedra, 'pa' para papel y 'ti para tijeras. \n").lower()
    computadora = random.choice(['pi', 'pa', 'ti'])

    if usuario == computadora:
        resultado = 'Empate'
        return resultado_final(resultado, usuario, computadora)

    if gano_el_jugador(usuario, computadora):
        resultado = 'Ganaste'
        return resultado_final(resultado, usuario, computadora)

    return resultado_final('Perdiste', usuario, computadora)


def gano_el_jugador(jugador, oponente):
    if ((jugador == 'pi' and oponente == 'ti')
            or (jugador == 'ti' and oponente == 'pa')
            or (jugador == 'pa' and oponente == 'pi')):
        return True
    else:
        return False


def resultado_final(resultado, usuario, computadora):
    return print(f"!{resultado}¡. La computadora selecciono {computadora} y tu seleccion fue {usuario}")


print(jugar())
