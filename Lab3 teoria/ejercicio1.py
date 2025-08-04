#!/usr/bin/env python3

import sys
from typing import List, Tuple, Optional
import graphviz
from dataclasses import dataclass

@dataclass
class ASTNode:
    """Clase para representar un nodo del árbol sintáctico abstracto"""
    value: str
    left: Optional['ASTNode'] = None
    right: Optional['ASTNode'] = None
    node_id: int = 0
    
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None
    
    def is_unary(self) -> bool:
        return self.left is not None and self.right is None
    
    def is_binary(self) -> bool:
        return self.left is not None and self.right is not None

class ShuntingYardRegex:
    def __init__(self):
        self.precedences = {
            '(': 1,
            '|': 2,
            '.': 3,
            '?': 4,
            '*': 4, 
            '+': 4,
            '^': 5
        }
        
        self.binary_operators = ['|', '.', '^']
        self.unary_operators = ['*', '+', '?']
        self.all_operators = ['|', '?', '+', '*', '^', '.']
        self.steps = []
    
    def get_precedence(self, char: str) -> int:
        return self.precedences.get(char, 0)
    
    def is_escaped(self, regex: str, index: int) -> bool:
        if index == 0:
            return False
        
        backslash_count = 0
        i = index - 1
        while i >= 0 and regex[i] == '\\':
            backslash_count += 1
            i -= 1
        
        return backslash_count % 2 == 1
    
    def expand_extensions(self, regex: str) -> str:
        result = []
        i = 0
        
        while i < len(regex):
            char = regex[i]
            
            if self.is_escaped(regex, i):
                result.append(char)
                i += 1
                continue
            
            # Expansión de + (a+ = aa*)
            if char == '+' and i > 0:
                if result and result[-1] == ')':
                    # Manejar expresiones entre paréntesis: (expr)+ = (expr)(expr)*
                    paren_count = 1
                    j = len(result) - 2
                    while j >= 0 and paren_count > 0:
                        if result[j] == ')':
                            paren_count += 1
                        elif result[j] == '(':
                            paren_count -= 1
                        j -= 1
                    
                    expr = ''.join(result[j+1:])  # La expresión completa (expr)
                    result = result[:j+1]  # Todo antes de la expresión
                    result.extend(list(expr + expr + '*'))  # (expr)(expr)*
                else:
                    # Carácter simple: a+ = aa*
                    if result:
                        last_char = result[-1]
                        result.append(last_char)
                        result.append('*')
            
            # Expansión de ? (a? = (a|ε))
            elif char == '?':
                if result and result[-1] == ')':
                    # Manejar expresiones entre paréntesis: (expr)? = ((expr)|ε)
                    paren_count = 1
                    j = len(result) - 2
                    while j >= 0 and paren_count > 0:
                        if result[j] == ')':
                            paren_count += 1
                        elif result[j] == '(':
                            paren_count -= 1
                        j -= 1
                    
                    expr = ''.join(result[j+1:])  # La expresión completa (expr)
                    result = result[:j+1]  # Todo antes de la expresión
                    result.extend(list('(' + expr + '|ε)'))  # ((expr)|ε)
                else:
                    # Carácter simple: a? = (a|ε)
                    if result:
                        last_char = result.pop()
                        result.extend(list('(' + last_char + '|ε)'))
            
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def add_concatenation(self, regex: str) -> str:
        if not regex:
            return regex
        
        result = []
        
        for i in range(len(regex)):
            c1 = regex[i]
            result.append(c1)
            
            if i + 1 < len(regex):
                c2 = regex[i + 1]
                
                if self.is_escaped(regex, i) or self.is_escaped(regex, i + 1):
                    continue
                
                should_concat = False
                
                # Casos donde se necesita concatenación
                if (c1 not in self.all_operators and c1 not in ['(', ')'] and
                    c2 not in self.all_operators and c2 not in ['(', ')']):
                    should_concat = True
                
                if (c1 not in self.all_operators and c1 not in ['(', ')'] and c2 == '('):
                    should_concat = True
                
                if (c1 == ')' and c2 not in self.all_operators and c2 not in ['(', ')']):
                    should_concat = True
                
                if (c1 == ')' and c2 == '('):
                    should_concat = True
                
                if (c1 in self.unary_operators and 
                    c2 not in self.all_operators and c2 not in ['(', ')']):
                    should_concat = True
                
                if (c1 in self.unary_operators and c2 == '('):
                    should_concat = True
                
                if c1 == 'ε' and c2 not in [')', '|'] + self.unary_operators:
                    should_concat = True
                if (c1 not in ['(', '|'] and c2 == 'ε'):
                    should_concat = True
                
                if should_concat:
                    result.append('.')
        
        return ''.join(result)
    
    def infix_to_postfix(self, regex: str) -> Tuple[str, List[str]]:
        self.steps = []
        output = []
        operator_stack = []
        
        expanded = self.expand_extensions(regex)
        formatted = self.add_concatenation(expanded)
        
        self.steps.append(f"Expresión original: {regex}")
        if expanded != regex:
            self.steps.append(f"Después de expandir extensiones: {expanded}")
        if formatted != expanded:
            self.steps.append(f"Después de insertar concatenaciones: {formatted}")
        
        self.steps.append("Iniciando algoritmo Shunting Yard:")
        
        for i, token in enumerate(formatted):
            if self.is_escaped(formatted, i):
                output.append(token)
                self.steps.append(f"  '{token}' (escapado) -> salida")
                
            elif token == '(':
                operator_stack.append(token)
                self.steps.append(f"  '{token}' -> pila")
                
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    op = operator_stack.pop()
                    output.append(op)
                    self.steps.append(f"  pop '{op}' -> salida")
                
                if operator_stack:
                    operator_stack.pop()
                    self.steps.append(f"  remover '(' de pila")
                
            elif token in self.all_operators:
                current_prec = self.get_precedence(token)
                
                while (operator_stack and 
                       operator_stack[-1] != '(' and 
                       self.get_precedence(operator_stack[-1]) >= current_prec):
                    op = operator_stack.pop()
                    output.append(op)
                    self.steps.append(f"  pop '{op}' -> salida")
                
                operator_stack.append(token)
                self.steps.append(f"  '{token}' -> pila")
                
            elif token == 'ε':
                output.append(token)
                self.steps.append(f"  '{token}' -> salida")
                
            else:
                output.append(token)
                self.steps.append(f"  '{token}' -> salida")
            
            self.steps.append(f"    salida: {''.join(output)}, pila: {operator_stack}")
        
        while operator_stack:
            op = operator_stack.pop()
            output.append(op)
            self.steps.append(f"  pop '{op}' -> salida")
        
        result = ''.join(output)
        self.steps.append(f"Resultado final: {result}")
        
        return result, self.steps

class ASTConstructor:
    """Clase para construir un AST a partir de una expresión en notación postfix"""
    
    def __init__(self):
        self.node_counter = 0
        self.binary_operators = ['|', '.', '^']
        self.unary_operators = ['*', '+', '?']
    
    def create_node(self, value: str, left: Optional[ASTNode] = None, right: Optional[ASTNode] = None) -> ASTNode:
        """Crea un nuevo nodo del AST con un ID único"""
        self.node_counter += 1
        return ASTNode(value, left, right, self.node_counter)
    
    def postfix_to_ast(self, postfix: str) -> Tuple[ASTNode, List[str]]:
        """Convierte una expresión postfix a un AST utilizando una pila"""
        stack = []
        steps = []
        
        # Información de depuración inicial
        print(f"DEBUG: Recibiendo postfix: '{postfix}'")
        print(f"DEBUG: Longitud: {len(postfix)}")
        print(f"DEBUG: Caracteres: {list(postfix)}")
        print(f"DEBUG: Operadores binarios reconocidos: {self.binary_operators}")
        print(f"DEBUG: Operadores unarios reconocidos: {self.unary_operators}")
        
        steps.append(f"Construyendo AST desde postfix: {postfix}")
        steps.append("Proceso paso a paso:")
        
        for i, token in enumerate(postfix):
            steps.append(f"\nPaso {i+1}: Procesando '{token}'")
            print(f"DEBUG: Procesando token '{token}' en posición {i}")
            
            if token in self.binary_operators:
                print(f"DEBUG: '{token}' es operador binario")
                # Operador binario: necesita dos operandos
                if len(stack) < 2:
                    steps.append(f"  ERROR: operador binario '{token}' necesita dos operandos, pero solo hay {len(stack)} en la pila")
                    steps.append(f"  Pila actual: [{', '.join([n.value + f'({n.node_id})' for n in stack])}]")
                    raise ValueError(f"Error: operador binario '{token}' necesita dos operandos")
                
                right = stack.pop()
                left = stack.pop()
                node = self.create_node(token, left, right)
                stack.append(node)
                
                steps.append(f"  Operador binario '{token}': combina dos nodos")
                steps.append(f"  Nodo izquierdo: {left.value} (ID: {left.node_id})")
                steps.append(f"  Nodo derecho: {right.value} (ID: {right.node_id})")
                steps.append(f"  Nuevo nodo: {token} (ID: {node.node_id})")
                
            elif token in self.unary_operators:
                print(f"DEBUG: '{token}' es operador unario")
                # Operador unario: necesita un operando
                if len(stack) < 1:
                    steps.append(f"  ERROR: operador unario '{token}' necesita un operando, pero la pila está vacía")
                    raise ValueError(f"Error: operador unario '{token}' necesita un operando")
                
                child = stack.pop()
                node = self.create_node(token, child)
                stack.append(node)
                
                steps.append(f"  Operador unario '{token}': opera sobre un nodo")
                steps.append(f"  Nodo hijo: {child.value} (ID: {child.node_id})")
                steps.append(f"  Nuevo nodo: {token} (ID: {node.node_id})")
                
            else:
                print(f"DEBUG: '{token}' es operando/símbolo")
                # Operando (símbolo terminal)
                node = self.create_node(token)
                stack.append(node)
                
                steps.append(f"  Símbolo '{token}': crear nodo hoja")
                steps.append(f"  Nuevo nodo: {token} (ID: {node.node_id})")
            
            steps.append(f"  Pila actual: [{', '.join([n.value + f'({n.node_id})' for n in stack])}]")
            print(f"DEBUG: Pila después del paso {i+1}: {[n.value for n in stack]}")
        
        steps.append(f"\nEstado final de la pila:")
        steps.append(f"  Número de elementos: {len(stack)}")
        print(f"DEBUG: Estado final - {len(stack)} elementos en la pila")
        for j, node in enumerate(stack):
            steps.append(f"  Elemento {j+1}: {node.value} (ID: {node.node_id})")
            print(f"DEBUG: Elemento {j+1}: {node.value}")
        
        if len(stack) != 1:
            steps.append(f"\nERROR: La expresión postfix no es válida.")
            steps.append(f"Una expresión postfix correcta debe dejar exactamente 1 elemento en la pila.")
            steps.append(f"Actualmente hay {len(stack)} elementos.")
            print(f"DEBUG: ERROR - Se esperaba 1 elemento, se encontraron {len(stack)}")
            raise ValueError(f"Error: la pila debería tener exactamente un elemento al final, tiene {len(stack)}")
        
        root = stack[0]
        steps.append(f"\nAST construido exitosamente. Raíz: {root.value} (ID: {root.node_id})")
        
        return root, steps
    
    def visualize_ast(self, root: ASTNode, filename: str = "ast") -> str:
        """Crea una visualización del AST usando Graphviz o texto como alternativa"""
        try:
            dot = graphviz.Digraph(comment='Abstract Syntax Tree')
            dot.attr(rankdir='TB')  # Top to bottom
            
            def add_nodes_edges(node: ASTNode):
                if node is None:
                    return
                
                # Configurar forma y color del nodo según su tipo
                if node.is_leaf():
                    # Nodos hoja (operandos)
                    dot.node(str(node.node_id), 
                            f"{node.value}\\nID:{node.node_id}", 
                            shape='ellipse', 
                            style='filled', 
                            fillcolor='lightblue')
                else:
                    # Nodos internos (operadores)
                    color = 'lightcoral' if node.value in self.binary_operators else 'lightgreen'
                    dot.node(str(node.node_id), 
                            f"{node.value}\\nID:{node.node_id}", 
                            shape='box', 
                            style='filled', 
                            fillcolor=color)
                
                # Agregar aristas a los hijos
                if node.left:
                    dot.edge(str(node.node_id), str(node.left.node_id), label='L')
                    add_nodes_edges(node.left)
                
                if node.right:
                    dot.edge(str(node.node_id), str(node.right.node_id), label='R')
                    add_nodes_edges(node.right)
            
            add_nodes_edges(root)
            
            # Guardar y renderizar
            output_path = dot.render(filename, format='png', cleanup=True)
            print(f"AST guardado como: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"Error con Graphviz: {e}")
            print("Generando visualización alternativa en texto...")
            return self.visualize_ast_text(root, filename)
    
    def visualize_ast_text(self, root: ASTNode, filename: str = "ast") -> str:
        """Crea una visualización del AST en formato texto"""
        lines = []
        
        def print_tree(node: ASTNode, prefix: str = "", is_tail: bool = True):
            if node is None:
                return
            
            # Símbolo para la conexión
            connector = "└── " if is_tail else "├── "
            
            # Información del nodo
            node_info = f"{node.value} (ID:{node.node_id})"
            if node.is_leaf():
                node_info += " [HOJA]"
            elif node.is_unary():
                node_info += " [UNARIO]"
            else:
                node_info += " [BINARIO]"
            
            lines.append(prefix + connector + node_info)
            
            # Preparar prefijo para hijos
            extension = "    " if is_tail else "│   "
            new_prefix = prefix + extension
            
            # Mostrar hijos (derecho primero para que izquierdo aparezca último)
            children = []
            if node.right:
                children.append(('R', node.right))
            if node.left:
                children.append(('L', node.left))
            
            for i, (side, child) in enumerate(children):
                is_last = (i == len(children) - 1)
                lines.append(new_prefix + ("└── " if is_last else "├── ") + f"[{side}]")
                print_tree(child, new_prefix + ("    " if is_last else "│   "), True)
        
        lines.append("ÁRBOL SINTÁCTICO ABSTRACTO:")
        lines.append("=" * 50)
        print_tree(root)
        
        # Guardar en archivo
        text_filename = f"{filename}.txt"
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # Mostrar en consola
        for line in lines:
            print(line)
        
        print(f"\nAST guardado como texto en: {text_filename}")
        return text_filename

def main():
    converter = ShuntingYardRegex()
    ast_constructor = ASTConstructor()
    
    # Leer expresiones del archivo
    with open('expresiones.txt', 'r', encoding='utf-8') as file:
        expressions = [line.strip() for line in file.readlines() if line.strip()]
    
    print("Leyendo expresiones desde archivo expresiones.txt:")
    
    for i, regex in enumerate(expressions, 1):
        print("="*80)
        print(f"EXPRESIÓN {i}: {regex}")
        print("="*80)
        
        # Paso 1: Convertir infix a postfix
        print("\n1. CONVERSIÓN INFIX A POSTFIX:")
        postfix, conversion_steps = converter.infix_to_postfix(regex)
        
        for step in conversion_steps:
            print(step)
        
        print(f"\nExpresión postfix: {postfix}")
        print(f"Longitud de postfix: {len(postfix)}")
        print(f"Caracteres individuales: {[c for c in postfix]}")
        
        # Paso 2: Construir AST desde postfix
        print("\n2. CONSTRUCCIÓN DEL AST:")
        ast_root, ast_steps = ast_constructor.postfix_to_ast(postfix)
        
        for step in ast_steps:
            print(step)
        
        # Paso 3: Visualizar AST
        print("\n3. VISUALIZACIÓN DEL AST:")
        filename = f"ast_expression_{i}"
        ast_constructor.visualize_ast(ast_root, filename)
        
        print(f"\nProcesamiento completado para expresión {i}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()