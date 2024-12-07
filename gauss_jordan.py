import copy
from fractions import Fraction

def verificarInconsistencia(matriz):
    filas = len(matriz)
    columnas = len(matriz[0])
    for i in range(filas):
        if all(matriz[i][j] == 0 for j in range(columnas - 1)) and matriz[i][columnas - 1] != 0:
            return True
    for i in range(filas):
        for k in range(i + 1, filas):
            if matriz[i][:columnas - 1] == matriz[k][:columnas - 1] and matriz[i][columnas - 1] != matriz[k][columnas - 1]:
                return True
    return False

def convertirAFraccion(matriz):
    fraccionada = copy.deepcopy(matriz)
    for i in range(len(fraccionada)):
        for j in range(len(fraccionada[0])):
            fraccionada[i][j] = str(Fraction(fraccionada[i][j]).limit_denominator())
    return fraccionada

def GaussJordan(matriz, matricesProcesadas):
    filas = len(matriz)
    columnas = len(matriz[0])

    def verificarUnos(matriz):
        for i in range(len(matriz)):
            if matriz[i][0] == 1:
                pos1 = 0
                pos2 = i
                matriz[pos1], matriz[pos2] = matriz[pos2], matriz[pos1]
                if pos1 != pos2:
                    matricesProcesadas[f"Intercambiamos F1 con F{pos2+1}"] = convertirAFraccion(matriz)
        return matriz

    matriz = verificarUnos(matriz)
    
    for i in range(columnas - 1):
        pivot = 0
        if matriz[i][i] != 1:
            pivot = matriz[i][i]
            for j in range(columnas):
                matriz[i][j] /= pivot
            matricesProcesadas[f"F{i+1} / {str(Fraction(pivot).limit_denominator())}"] = convertirAFraccion(matriz)
        else:
            pivot = matriz[i][i]
            matricesProcesadas[f"F{matriz[i][i]} ya posee un 1"] = convertirAFraccion(matriz)
                
        for k in range(filas):
            factor = 0
            if k != i:
                factor = matriz[k][i]
                for j in range(columnas):
                    matriz[k][j] -= factor * matriz[i][j]

                if factor > 0:
                    matricesProcesadas[f"F{k+1} - {str(Fraction(factor).limit_denominator())} F{i+1}"] = convertirAFraccion(matriz)
                    
                else:
                    matricesProcesadas[f"F{k+1} + {str(Fraction(-factor).limit_denominator())} F{i+1}"] =  convertirAFraccion(matriz)
                
    return matriz
