import networkx as nx
import matplotlib.pyplot as plt
import graphviz as gv

class ThompsonConstructor:
    def __init__(self):
        self.state_count = 0

    def new_state(self):
        state_label = str(self.state_count)
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
            if op1 not in precedence or op2 not in precedence:
                return False
            return precedence[op1] >= precedence[op2]

        operators_stack = []
        operands_stack = []
        for char in regex:
            if char.isalpha():
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
        dot = gv.Digraph(engine='neato')

        for node in graph.nodes():
            node_label = node
            if node == start:
                dot.node(node_label, shape='circle', style='filled', fillcolor='lightblue', penwidth='2.0')
            elif node in ends:
                dot.node(node_label, shape='doublecircle', style='filled', fillcolor='lightblue')
            else:
                dot.node(node_label, shape='circle', style='filled', fillcolor='lightblue')

        for edge in graph.edges(data=True):
            dot.edge(edge[0], edge[1], label=edge[2]['label'])

        dot.render(filename, format='png', cleanup=True)
        dot.view()


# Ejemplo de uso
regex = "(a.b + b.a)*"
constructor = ThompsonConstructor()
nfa_graph, start_state, end_state = constructor.regex_to_nfa(regex)
constructor.draw_automaton(nfa_graph, start_state, {end_state}, 'nfa_graph')

# Comentario: Omitir la determinización del NFA para evitar problemas
