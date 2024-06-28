import networkx as nx
import graphviz as gv

class NFAConstructor:
    def __init__(self): # inicializa los atributos
        self.state_count = 0  # Variable que cuenta los estados que se generan

    def new_state(self):
        state_label = 'q' + str(self.state_count)  # Se crea una etiqueta de estado
        self.state_count += 1  # Se va incrementando el contador de los estados
        return state_label

    def er_a_nfa(self, expresionReg): # funcion que transfroma la ER en NFA
        stack = []  # Se crea la pila vacia
        operators = set(['*', '+', '.', '(', ')'])  # Conjunto de operadores que pueden aparecer en una ER
        precedence = {'*': 3, '.': 2, '+': 1} # arranca del 3 para abajo

        def apply_operator(operators, operands): # se le mandan dos pilas operators_stack y operands_stack
            operator = operators.pop()  # Va extrayendo cada operador de la pila para luego saber que hacer
            if operator == '*':  # Si se lee *
                start1, end1, graph1 = operands.pop()  # Se extrae la ultima tupla y se definen el estado inicial, final y el grafo asociado
                start = self.new_state()
                end = self.new_state()
                graph = nx.DiGraph()
                graph.add_edges_from(graph1.edges(data=True))  # Aristas del grafo1 al grafo nuevo
                graph.add_edge(start, start1, label='ε')  # Arista desde el estado nuevo al estado original transición ε
                graph.add_edge(end1, start1, label='ε')  # Arista desde el estado final original al esatdo inicial original
                graph.add_edge(end1, end, label='ε')  # Arista del estado final original al nuevo estado final
                graph.add_edge(start, end, label='ε')  # Arista del estado inicial nuevo al estado final nuevo
                operands.append((start, end, graph))  # Agrega una nueva tupla al final de la lista
            elif operator == '+':  # Si se lee +
                start2, end2, graph2 = operands.pop()  # Se extraen 2 tuplas b + b, ahi tendria que procesar, a por un lado y b por el otro
                start1, end1, graph1 = operands.pop()
                start = self.new_state()
                end = self.new_state()
                graph = nx.DiGraph()
                graph.add_edges_from(graph1.edges(data=True))
                graph.add_edges_from(graph2.edges(data=True))
                graph.add_edge(start, start1, label='ε')
                graph.add_edge(start, start2, label='ε')
                graph.add_edge(end1, end, label='ε')
                graph.add_edge(end2, end, label='ε')
                operands.append((start, end, graph))
            elif operator == '.':
                start2, end2, graph2 = operands.pop()
                start1, end1, graph1 = operands.pop()
                graph1.add_edges_from(graph2.edges(data=True))
                graph1.add_edge(end1, start2, label='ε')
                operands.append((start1, end2, graph1))

        def higher_precedence(op1, op2):
            return precedence[op1] > precedence[op2]  # Compara la jerarquia de los operandos

        operators_stack = []  # pila que se usa para guardar los operadores mientras se procesa la ER
        operands_stack = []  # pila que se usa para guardar los operadores mientras se va CONSTRUYENDO el automata

        def concatenacion(expresionReg):  # Agrega implicitamente el operando . para la concatenacion
            nueva_er = []
            for i in range(len(expresionReg) - 1):  # Itera sobre cada caracter menos el ultimo
                nueva_er.append(expresionReg[i])
                if ((expresionReg[i] not in operators and expresionReg[i + 1] not in operators) or \
                    # ab -> a.b esto porque ese punto lo pone implicitamente
                   (expresionReg[i] not in operators and expresionReg[i + 1] == '(') or \
                    # a(b dice  q hay una concatenacio implicita
                   (expresionReg[i] == ')' and expresionReg[i + 1] not in operators) or \
                    # a)b lo mismo con el otro parentesis
                   (expresionReg[i] == '*' and expresionReg[i + 1] not in operators) or \
                    # a*b
                   (expresionReg[i] == '*' and expresionReg[i + 1] == '(')):
                    # a*(b+c)
                    nueva_er.append('.')  # Si alguna de las condiciones se cumple se agrega . y se realiza la concatenacion
            nueva_er.append(expresionReg[-1])
            return ''.join(nueva_er)

        expresionReg = concatenacion(expresionReg)

        i = 0
        while i < len(expresionReg):  # Itera sobre cada caracter de la ER
            char = expresionReg[i]  # declara un char
            if char not in operators:  # Se maneja la representacion de un estado a otro cuando el caracter no es un operando
                start = self.new_state()
                end = self.new_state()
                graph = nx.DiGraph()
                graph.add_edge(start, end, label=char)
                operands_stack.append((start, end, graph))
            elif char in operators:  # Se maneja la representacion de un estado a otro cuando el caracter ES un operando
                if char == '(':
                    operators_stack.append(char)  # Esto es para manjernara las subexpresion reg que haya dentro de los parentesis
                elif char == ')': #a(a+b)b* va leyendo caracteer por caracter y se fija en los parentesisi para resolverlos en una pila
                    while operators_stack and operators_stack[-1] != '(':
                        apply_operator(operators_stack, operands_stack)
                    operators_stack.pop()
                else:
                    while (operators_stack and operators_stack[-1] != '(' and  # mientras no haya parentesis va a ir viendo la jerarquia
                           higher_precedence(operators_stack[-1], char)): # de los simbolos y va a ir aplicando los operadores
                        apply_operator(operators_stack, operands_stack)
                    operators_stack.append(char)
            i += 1

        while operators_stack:
            apply_operator(operators_stack, operands_stack)  # mientras haya operados en la operators va a segiuir iterando

        start, end, graph = operands_stack.pop()  # una vez que todos los operandos fueron procesados se los saca de la pila
        return graph, start, end  # retorna el resultado

    def dibujarAutomata(self, graph, start, ends, filename):  # visaalizacion
        dot = gv.Digraph(engine='dot')  # crea un objeto de tipo digraph
        dot.attr(rankdir='LR', size='8,5', margin='0.2', nodesep='0.5', ranksep='1')  # Ajustar apariencia

        for node in graph.nodes():
            node_label = node
            if node == start:
                dot.node(node_label, shape='circle', style='filled', fillcolor='lightblue', penwidth='2.0', fontsize='10')
            elif node in ends:
                dot.node(node_label, shape='doublecircle', style='filled', fillcolor='lightblue', fontsize='10')
            else:
                dot.node(node_label, shape='circle', style='filled', fillcolor='lightblue', fontsize='10')

        for edge in graph.edges(data=True):
            dot.edge(edge[0], edge[1], label=edge[2]['label'], fontsize='10')

        dot.render(filename, format='png', cleanup=True)  # se guarda el diagrama en un archivo
        dot.view()

# Prints de visualizacion
print("====== Ejemplos de Expresiones Regulares ======")
print("Para concatenar se utiliza el punto implícito (no es necesario escribirlo explícitamente)")
print("Para cerradura de Kleene se utiliza el asterisco (*)")
print("Para la unión se utiliza el signo de suma (+)")
print("Para agrupar se utilizan paréntesis ()")
print("\nEjemplos:")
print("1. (ab+ba)*  => Cerradura de Kleene sobre 'ab' o 'ba'")
print("2. (a.b)*    => Cerradura de Kleene sobre 'a' concatenado con 'b'")
print("3. (a+b)*    => Cerradura de Kleene sobre 'a' o 'b'")
print("4. (a+b)     => 'a' o 'b'")
print("5. (a.b)+    => 'a' concatenado con 'b' uno o más veces")
print("6. (a+b).a   => 'a' o 'b' concatenado con 'a'")
print("7. (a+b).a.b => 'a' o 'b' concatenado con 'a' y luego con 'b'")
print("===============================================")

expresionReg = input("Ingrese la expresión regular a graficar: ") # input de la expresion regular que va a ingresar el usuario
constructor = NFAConstructor()  # Se instancia un objeto de la clase
nfa_graph, start_state, end_state = constructor.er_a_nfa(expresionReg)  # se llama al metodo y se le envia por parametro la ER
constructor.dibujarAutomata(nfa_graph, start_state, {end_state}, 'nfa_graph')  # se llama al metodo para la visualizaicion del AFN
