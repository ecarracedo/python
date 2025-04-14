import random


def adivina_el_numero(x):
    print("=======================")
    print("= Bienvenido al juego =")
    print("=======================")
    print("Tu meta es adivinar el numero")

    numero_aleatorio = random.randint(1, x)

    prediccion = 0

    while prediccion != numero_aleatorio:

        # El usuario ingresa numero
        prediccion = int(input(f"Adivina un numero ente 1 y {x}: "))

        if prediccion < numero_aleatorio:

            print("El numero que ingresaste es pequeño")

        elif prediccion > numero_aleatorio:

            print("el numero ingresaste es alto")

    print(f"Felicitaciones, adivinaste el numero {numero_aleatorio} correctamente")


adivina_el_numero(10)
