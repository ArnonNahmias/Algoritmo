import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


class ThompsonConstructor:
    def __init__(self):
        self.state_count = 0

    def new_state(self):
        self.state_count += 1
        return self.state_count

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
                    operators_stack.pop()  # Remove '(' from stack
                else:
                    while (operators_stack and operators_stack[-1] != '(' and
                           higher_precedence(operators_stack[-1], char)):
                        apply_operator(operators_stack, operands_stack)
                    operators_stack.append(char)

        while operators_stack:
            apply_operator(operators_stack, operands_stack)

        start, end, graph = operands_stack.pop()
        return graph, start, end

    def draw_nfa(self, graph, start, end):
        pos = graphviz_layout(graph, prog='dot')
        labels = nx.get_edge_attributes(graph, 'label')

        # Dibujar los nodos
        nx.draw_networkx_nodes(graph, pos, nodelist=graph.nodes(), node_color='lightblue', node_size=500)

        # Resaltar el estado inicial
        nx.draw_networkx_nodes(graph, pos, nodelist=[start], node_color='green', node_size=700)

        # Resaltar el estado final
        nx.draw_networkx_nodes(graph, pos, nodelist=[end], node_color='red', node_size=700)

        # Dibujar las aristas
        nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color='black')

        # Dibujar las etiquetas de los nodos
        nx.draw_networkx_labels(graph, pos)

        # Dibujar las etiquetas de las aristas
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

        plt.show()


# Ejemplo de uso
regex = "(ab+ba)*"
constructor = ThompsonConstructor()
nfa_graph, start_state, end_state = constructor.regex_to_nfa(regex)
constructor.draw_nfa(nfa_graph, start_state, end_state)
