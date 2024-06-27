import networkx as nx
import graphviz as gv

class ThompsonConstructor:
    def __init__(self):
        self.state_count = 0

    def new_state(self):
        state_label = 'q' + str(self.state_count)
        self.state_count += 1
        return state_label

    def regex_to_nfa(self, regex):
        stack = []
        operators = set(['*', '+', '.', '(', ')'])
        precedence = {'*': 3, '.': 2, '+': 1}

        def apply_operator(operators, operands):
            operator = operators.pop()
            if operator == '*':
                start1, end1, graph1 = operands.pop()
                start = self.new_state()
                end = self.new_state()
                graph = nx.DiGraph()
                graph.add_edges_from(graph1.edges(data=True))
                graph.add_edge(start, start1, label='ε')
                graph.add_edge(end1, start1, label='ε')
                graph.add_edge(end1, end, label='ε')
                graph.add_edge(start, end, label='ε')
                operands.append((start, end, graph))
            elif operator == '+':
                start2, end2, graph2 = operands.pop()
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
            return precedence[op1] > precedence[op2]

        operators_stack = []
        operands_stack = []

        def add_concatenation(regex):
            new_regex = []
            for i in range(len(regex) - 1):
                new_regex.append(regex[i])
                if (regex[i] not in operators and regex[i + 1] not in operators) or \
                   (regex[i] not in operators and regex[i + 1] == '(') or \
                   (regex[i] == ')' and regex[i + 1] not in operators) or \
                   (regex[i] == '*' and regex[i + 1] not in operators) or \
                   (regex[i] == '*' and regex[i + 1] == '('):
                    new_regex.append('.')
            new_regex.append(regex[-1])
            return ''.join(new_regex)

        regex = add_concatenation(regex)

        for char in regex:
            if char not in operators:
                start = self.new_state()
                end = self.new_state()
                graph = nx.DiGraph()
                graph.add_edge(start, end, label=char)
                operands_stack.append((start, end, graph))
            elif char in operators:
                if char == '(':
                    operators_stack.append(char)
                elif char == ')':
                    while operators_stack and operators_stack[-1] != '(':
                        apply_operator(operators_stack, operands_stack)
                    operators_stack.pop()
                else:
                    while (operators_stack and operators_stack[-1] != '(' and
                           higher_precedence(operators_stack[-1], char)):
                        apply_operator(operators_stack, operands_stack)
                    operators_stack.append(char)

        while operators_stack:
            apply_operator(operators_stack, operands_stack)

        start, end, graph = operands_stack.pop()
        return graph, start, end

    def draw_automaton(self, graph, start, ends, filename):
        dot = gv.Digraph(engine='dot')
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

        dot.render(filename, format='png', cleanup=True)
        dot.view()

# Ejemplo de uso
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

regex = input("Ingrese la expresión regular a graficar: ")
constructor = ThompsonConstructor()
nfa_graph, start_state, end_state = constructor.regex_to_nfa(regex)
constructor.draw_automaton(nfa_graph, start_state, {end_state}, 'nfa_graph')
