#!/usr/bin/env python3

import sys
from typing import List, Tuple

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
            
            if char == '+' and i > 0:
                if result and result[-1] == ')':
                    paren_count = 1
                    j = len(result) - 2
                    while j >= 0 and paren_count > 0:
                        if result[j] == ')':
                            paren_count += 1
                        elif result[j] == '(':
                            paren_count -= 1
                        j -= 1
                    
                    expr = ''.join(result[j+1:])
                    result = result[:j+1]
                    result.extend(list(expr + expr[:-1] + '*'))
                else:
                    if result:
                        last_char = result[-1]
                        result.append(last_char)
                        result.append('*')
            
            elif char == '?':
                if result and result[-1] == ')':
                    paren_count = 1
                    j = len(result) - 2
                    while j >= 0 and paren_count > 0:
                        if result[j] == ')':
                            paren_count += 1
                        elif result[j] == '(':
                            paren_count -= 1
                        j -= 1
                    
                    expr = ''.join(result[j+1:])
                    result = result[:j+1]
                    result.extend(list('(' + expr + '|ε)'))
                else:
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

def main():
    converter = ShuntingYardRegex()
    
    try:
        with open('expresiones.txt', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
        for i, regex in enumerate(lines, 1):
            print(f"Expresión {i}: {regex}")
            postfix, steps = converter.infix_to_postfix(regex)
            print(f"Postfix: {postfix}")
            print("Pasos:")
            for step in steps:
                print(step)
            print()
            
    except FileNotFoundError:
        print("Error: archivo expresiones.txt no encontrado")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()