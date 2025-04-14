import random


def adivina_el_numero_computadora (x):

    print("=======================")
    print("= Bienvenido al juego =")
    print("=======================")
    print(f"Ingrese un numero del 1 al {x}")

    limite_inf = 1
    limite_sup = x

    respuesta = ""

    while respuesta != "c":
        # Generar prediccion
        if limite_inf != limite_sup:
            prediccion = random.randint(limite_inf, limite_sup)
        else:
            prediccion = limite_inf #tambien podria ser el limite superior

        # Obtener respuesta del usuario
        respuesta = input(f"Mi prediccion es {prediccion}. Si es muy alta ingresa (A). Si es muy baja ingresa (B). "
                          f"Si es correcta ingresa (C): ").lower()

        if respuesta == "a":
            limite_sup = prediccion - 1
        elif respuesta == "b":
            limite_inf = prediccion + 1

    print(f"Siii, la computadora adivino el numero {prediccion}")


adivina_el_numero_computadora(10)
