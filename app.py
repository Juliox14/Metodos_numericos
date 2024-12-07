from flask import Flask, render_template, request
from gauss_jordan import GaussJordan, convertirAFraccion, verificarInconsistencia
from simplex import resolverSimplex
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('inicio.html')

@app.route('/gauss')
def gauss():
    return render_template('gauss.html')

@app.route('/caluladora_gauss')
def calculadora_gauss():
    return render_template('calculadora_gauss.html')

@app.route('/solucion', methods=['POST', 'GET'])
def solucion():
    resultados = []
    matriz = []
    matricesProcesadas = {}
    error = False

    if request.method == 'POST':
        filas = int(request.form['numero_filas'])
        columnas = int(request.form['numero_columnas'])
        
        for i in range(filas):
            fila = []
            for j in range(columnas):
                fila.append(int(request.form['matriz_'+ str(i) + '_' + str(j) + '']))
            matriz.append(fila)
        
        inconsistencia = verificarInconsistencia(matriz)
        if inconsistencia:
            resultados.append("El sistema que has ingresado es inconsistente.")
            error = True
        else:
            try:
                matricesProcesadas["Matriz Inicial"] = convertirAFraccion(matriz)
                matrizFinal = convertirAFraccion(GaussJordan(matriz, matricesProcesadas))
                for i in range(columnas - 1):
                    resultados.append(f"x{i+1} = {matrizFinal[i][len(matrizFinal[0]) - 1]}")
            except:
                error = True
                resultados.append("Algo salió mal, por favor verifica que los datos ingresados sean correctos.")

    return render_template('solucion.html', matricesProcesadas=matricesProcesadas, resultados=resultados, error=error, numero_filas=filas, numero_columnas=columnas)

    
    
@app.route('/simplex')
def simplex():
    return render_template('simplex.html')

@app.route('/caluladora_simplex')
def calculadora_simplex():
    return render_template('calculadora_simplex.html')


@app.route('/solucion_simplex', methods=['POST'])
def solucion_simplex():
    # Obtener datos del formulario
    numero_variables = int(request.form['numero_variables'])
    numero_restricciones = int(request.form['numero_restricciones'])
    opt = request.form['objetivo'].lower()[:3]

    # Función objetivo
    Z = [int(request.form[f'funcion_objetivo_x{i}']) for i in range(numero_variables)]
    Z.append(0)

    # Restricciones
    Res = []
    for i in range(numero_restricciones):
        restriccion = [int(request.form[f'matriz_{i}_{j}']) for j in range(numero_variables)]
        tipo = request.form[f'tipo_restriccion_{i}']
        b = int(request.form[f'matriz_{i}_b'])
        restriccion.extend([tipo, b])
        Res.append(restriccion)

    def convertir_a_formato(Z, Res, opt):
        entradaUsuario = []
        funcion_objetivo = f"{opt.capitalize()}imizar: Z = "
        funcion_objetivo += " + ".join(f"{coef}X{i+1}" for i, coef in enumerate(Z[:-1]))
        entradaUsuario.append(funcion_objetivo)
        entradaUsuario.append("Sujeto a:")
        for restriccion in Res:
            expresion = " + ".join(f"{coef}X{i+1}" for i, coef in enumerate(restriccion[:-2]))
            signo = restriccion[-2]
            valor = restriccion[-1]
            entradaUsuario.append(f"{expresion} {signo} {valor}")
        
        return entradaUsuario
    
    entradaUsuario = convertir_a_formato(Z, Res, opt)


    historial, resultados, variables, variablesDeEntrada, variablesDeSalida = resolverSimplex(Res, Z, opt, numero_variables)
    
    def ingresarCoeficientesZ(matriz):
        
        for i in range(len(matriz)):
            if i == 0:
                matriz[i].insert(0, '1')
            else:
                matriz[i].insert(0, '0')

        matriz[0].insert(0, 'Z')
        return matriz
    
    def agregarCondicionNoNegatividad(entradaUsuario, variables):
        cadena = ", ".join(variables) + " >= 0"
        entradaUsuario.append(cadena)
        return entradaUsuario
    
    entradaUsuario = agregarCondicionNoNegatividad(entradaUsuario, variables)
        


    def obtenerVariableBasica(matriz, variables):
        variables = variables[1:]

        for i, fila in enumerate(matriz[1:]):
            try:
                posicion = fila.index('1')
                fila.insert(0, variables[posicion-1])
            except ValueError:
                fila.insert(0, 'Ninguna')
        return matriz

    historial = [ingresarCoeficientesZ(matriz) for matriz in historial]

    variables.insert(0, 'Z')
    for matriz in historial:
        matriz = obtenerVariableBasica(matriz, variables)
        print(matriz)
    
    def obtener_valores_salidas(matrices, variablesDeSalida):
        resultados = []

        for i, matriz in enumerate(matrices):
            # Verificamos si la fila de la variable de salida corresponde a la última columna
            for fila in matriz:
                if fila[-1] == variablesDeSalida[i]:  # Compara con la variable de salida correspondiente
                    resultados.append(fila[0])  # Retorna el primer valor de esa fila
                    break  # Salimos del bucle si encontramos la variable de salida

        return resultados
        
    
    variablesDeSalidaFinales = obtener_valores_salidas(historial[:-1], variablesDeSalida)
    
    matricesProcesadas = {
    ("Entrada" if i == 0 else f"Iteración {i+1}"): matriz 
    for i, matriz in enumerate(historial)
    }
    return render_template('solucion_simplex.html', 
        matricesProcesadas=matricesProcesadas, 
        resultados=resultados, 
        opt=opt, 
        numero_variables=numero_variables, 
        numero_restricciones=numero_restricciones, 
        variables=variables, 
        entradaUsuario=entradaUsuario,
        variablesDeEntrada = variablesDeEntrada,
        variablesDeSalida = variablesDeSalidaFinales,
        variablesDeSalidaJson = json.dumps(variablesDeSalidaFinales)
    )

# @app.route('/granM')
# def GranM():
#     return render_template('granM.html')

# @app.route('/caluladora_granM')
# def calculadora_granM():
#     return render_template('calculadora_granM.html')


# @app.route('/solucion_granM', methods=['POST', 'GET'])
# def solucion_granM():
#     return render_template('solucion_granM.html')
    

    


if __name__ == '__main__':
    app.run(debug=True)