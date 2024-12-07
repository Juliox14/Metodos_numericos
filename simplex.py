from fractions import Fraction
import copy

def resolverSimplex(Res, Z, opt, numero_variables):
    historial = []
    
    def obtenerVariables(matrices, numeroVariables):
        num_columnas = len(matrices[0]) - 1
        variables = []

        for i in range(num_columnas):
            if i < numeroVariables:
                variables.append(f"x{i+1}")
            else:
                variables.append(f"s{i - numeroVariables + 1}")
                
        return variables


    def agregarVariablesHolgura(Res):    
        for i in range(len(Res)):
            if Res[i][len(Res[i])-2] == "<=":
                Res[i].remove("<=")
                ind = Res[i].pop(len(Res[i])-1)
                for j in range(len(Res)):
                    if j == i:
                        Res[i].append(1)
                    else:
                        Res[i].append(0)
                Res[i].append(ind)
            else:
                None
        
        for i in range(len(Res)):
            Z.append(0)
        matriz = Res
        matriz.insert(0, Z)
        return matriz

    matriz = agregarVariablesHolgura(Res)

    def metodoSimplex(matriz):    

        def obtenerVarEntrada(matriz, opt):
            if opt == "min":
                VariableEntrada = max(matriz[0][:-1])
            elif opt == "max":
                VariableEntrada = min(matriz[0][:-1])

            if VariableEntrada == 0:
                return None
            indice_columna = matriz[0].index(VariableEntrada)
            return indice_columna

        indiceVarEntrada = obtenerVarEntrada(matriz, opt)   

        def obtenerVarSalida(matriz, varEntrada):
            proporciones = []
            for i in range(1, len(matriz)):  # Ignorar la fila de la función objetivo
                sol = matriz[i][-1]  # Última columna es la solución

                if matriz[i][varEntrada] > 0:  # Evitar división por cero
                    razon = sol / matriz[i][varEntrada]
                    proporciones.append(razon)
                else:
                    proporciones.append(float('inf'))  # Ignorar variables que no pueden salir
            varSalida = min(proporciones)
            indiceVarSalida = proporciones.index(varSalida)  # Retornar índice de la variable de salida
            return indiceVarSalida + 1  # Retornar índice de la variable de salida

        indiceVarSalida = obtenerVarSalida(matriz, indiceVarEntrada)

        pivote = matriz[indiceVarSalida][indiceVarEntrada]
        

        variables = obtenerVariables(matriz, numero_variables)

        def obtenerVarEntradaSalida(variables, indiceVarEntrada, indiceVarSalida, matrices):
            indice_columna = indiceVarEntrada
            indice_fila = indiceVarSalida
            variableEntrada = variables[indice_columna]
            variableSalida = matrices[indice_fila][-1]
            return variableEntrada, variableSalida
            
        variableEntrada, variableSalida = obtenerVarEntradaSalida(variables, indiceVarEntrada, indiceVarSalida, matriz)

        def obtenerCeros(matriz, varSalida):
            for i in range(len(matriz[varSalida])):
                matriz[varSalida][i] /= pivote
            
            for i in range(len(matriz)):
                if i != varSalida:
                    factor = matriz[i][indiceVarEntrada]
                    for j in range(len(matriz[i])):
                        matriz[i][j] -= factor * matriz[varSalida][j]

        obtenerCeros(matriz, indiceVarSalida)

        matrizFraccionada = convertirAFraccion(matriz)
        return matrizFraccionada, variableEntrada, variableSalida


    def convertirAFraccion(matriz):
            fraccionada = copy.deepcopy(matriz) 
            for i in range(len(fraccionada)):
                for j in range(len(fraccionada[0])):
                    fraccionada[i][j] = str(Fraction(fraccionada[i][j]).limit_denominator())
            return fraccionada

    def despejarZ(Z):
        for i in range(len(Z)):
            Z[i] *= -1
        return Z

    def obtenerResultados(matricesFinales, numeroVariables):
        resultados = {}
        variables = []

        primer_array = matricesFinales[0]
        resultados['Z'] = primer_array[-1] 
        
        num_columnas = len(matricesFinales[0]) - 1

        for i in range(num_columnas):
            if i < numeroVariables:
                variables.append(f"x{i+1}")
            else:
                variables.append(f"s{i - numeroVariables + 1}")

        for var in variables:
            resultados[var] = 0

        for m in matricesFinales[1:]: 
            for i in range(len(variables)):
                if m[i] == '1':  
                    resultados[variables[i]] = m[-1]

        return resultados, variables

    variablesDeSalida = []
    variablesDeEntrada = []
    
    if opt == "max":
        Z = despejarZ(Z)
        historial.append(convertirAFraccion(matriz))
        while True:
            matrizSimplex, variableEntrada, variableSalida = metodoSimplex(matriz)
            historial.append(matrizSimplex)
            variablesDeEntrada.append(variableEntrada)
            variablesDeSalida.append(str(Fraction(variableSalida).limit_denominator()))
            resultados, variables = obtenerResultados(historial[-1], numero_variables)
            todos_positivos = all(x >= 0 for x in matriz[0][:-1])
            if todos_positivos:
                break
            
        
        
    elif opt == "min":
        Z = despejarZ(Z)
        historial.append(convertirAFraccion(matriz))
        while True:
            matrizSimplex, variableEntrada, variableSalida = metodoSimplex(matriz)
            historial.append(matrizSimplex)
            variablesDeEntrada.append(variableEntrada)
            variablesDeSalida.append(variableSalida)
            resultados, variables = obtenerResultados(historial[-1], numero_variables)
            todos_negativos = all(x <= 0 for x in matriz[0])
            if todos_negativos:
                break
        

    return historial, resultados, variables, variablesDeEntrada, variablesDeSalida
