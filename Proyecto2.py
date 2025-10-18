#!/usr/bin/env python3
"""
Analizador sintáctico CYK con conversión automática a Forma Normal de Chomsky
"""
import argparse
import collections
import itertools
import time
import re
from typing import Dict, List, Set, Tuple, Optional, Iterator
from dataclasses import dataclass, field


TokenType = str
ProductionRHS = Tuple[TokenType, ...]
RuleMapping = Dict[TokenType, List[ProductionRHS]]


@dataclass(frozen=True)
class Rule:
    """Representa una regla de producción A -> α"""
    lhs: TokenType
    rhs: ProductionRHS


@dataclass
class ParseNode:
    """Nodo del árbol de análisis sintáctico"""
    symbol: TokenType
    start_pos: int
    end_pos: int
    lexeme: Optional[str] = None
    left_child: Optional['ParseNode'] = None
    right_child: Optional['ParseNode'] = None

    def render_bracketed(self) -> str:
        """Genera representación con paréntesis del árbol"""
        if self.lexeme is not None:
            return f"({self.symbol} {self.lexeme})"
        left_str = self.left_child.render_bracketed()
        right_str = self.right_child.render_bracketed()
        return f"({self.symbol} {left_str} {right_str})"

    def generate_graphviz(self, id_gen: Iterator[int]) -> Tuple[str, int]:
        """Genera representación DOT para Graphviz"""
        current_id = next(id_gen)
        node_label = self.symbol if self.lexeme is None else f"{self.symbol}\\n'{self.lexeme}'"
        lines = [f"  node{current_id} [label=\"{node_label}\", shape=ellipse];"]
        
        if self.lexeme is None:
            left_graph, left_id = self.left_child.generate_graphviz(id_gen)
            right_graph, right_id = self.right_child.generate_graphviz(id_gen)
            lines.append(left_graph)
            lines.append(right_graph)
            lines.append(f"  node{current_id} -> node{left_id};")
            lines.append(f"  node{current_id} -> node{right_id};")
        
        return "\n".join(lines), current_id


@dataclass
class ParseResult:
    """Resultado del análisis CYK"""
    is_valid: bool
    parse_time_ms: float
    parse_trees: List[ParseNode] = field(default_factory=list)


class ContextFreeGrammar:
    """Gramática Libre de Contexto con operaciones de normalización"""
    
    def __init__(self, axiom: TokenType, rules: List[Rule]):
        self.axiom = axiom
        self.productions: RuleMapping = collections.defaultdict(list)
        for rule in rules:
            self.productions[rule.lhs].append(rule.rhs)

    @classmethod
    def from_mapping(cls, axiom: TokenType, mapping: RuleMapping) -> 'ContextFreeGrammar':
        """Construye gramática desde un diccionario"""
        rules = [Rule(nt, tuple(prod)) for nt, prods in mapping.items() for prod in prods]
        return cls(axiom, rules)

    def get_nonterminals(self) -> Set[TokenType]:
        """Retorna conjunto de símbolos no terminales"""
        return set(self.productions.keys())

    def get_terminals(self) -> Set[TokenType]:
        """Retorna conjunto de símbolos terminales"""
        nonterminals = self.get_nonterminals()
        terminals: Set[TokenType] = set()
        for prod_list in self.productions.values():
            for prod in prod_list:
                for sym in prod:
                    if sym not in nonterminals:
                        terminals.add(sym)
        return terminals

    def duplicate(self) -> 'ContextFreeGrammar':
        """Crea una copia profunda de la gramática"""
        mapping = {nt: list(prods) for nt, prods in self.productions.items()}
        return ContextFreeGrammar.from_mapping(self.axiom, mapping)

    def eliminate_nonproductive_symbols(self) -> None:
        """Elimina símbolos no terminales que no generan cadenas terminales"""
        productive: Set[TokenType] = set()
        modified = True
        
        while modified:
            modified = False
            for nt, prod_list in self.productions.items():
                if nt in productive:
                    continue
                for prod in prod_list:
                    if all(s not in self.productions for s in prod):
                        productive.add(nt)
                        modified = True
                        break
                    if all((s in productive or s not in self.productions) for s in prod):
                        productive.add(nt)
                        modified = True
                        break
        
        removable = [nt for nt in self.productions if nt not in productive and nt != self.axiom]
        for nt in removable:
            del self.productions[nt]
        
        for nt in list(self.productions.keys()):
            self.productions[nt] = [
                prod for prod in self.productions[nt] 
                if all((s in self.productions or s not in self.productions) for s in prod)
            ]

    def eliminate_inaccessible_symbols(self) -> None:
        """Elimina símbolos no alcanzables desde el axioma"""
        accessible: Set[TokenType] = {self.axiom}
        modified = True
        
        while modified:
            modified = False
            for nt in list(accessible):
                for prod in self.productions.get(nt, []):
                    for sym in prod:
                        if sym in self.productions and sym not in accessible:
                            accessible.add(sym)
                            modified = True
        
        for nt in list(self.productions.keys()):
            if nt not in accessible:
                del self.productions[nt]

    def eliminate_epsilon_productions(self) -> None:
        """Elimina producciones vacías (ε-producciones)"""
        annulable: Set[TokenType] = set()
        modified = True
        
        while modified:
            modified = False
            for nt, prod_list in self.productions.items():
                if nt in annulable:
                    continue
                for prod in prod_list:
                    if len(prod) == 0:
                        annulable.add(nt)
                        modified = True
                        break
                    if all(s in annulable for s in prod):
                        annulable.add(nt)
                        modified = True
                        break
        
        updated_prods: RuleMapping = collections.defaultdict(list)
        for nt, prod_list in self.productions.items():
            for prod in prod_list:
                if len(prod) == 0:
                    continue
                nullable_positions = [idx for idx, s in enumerate(prod) if s in annulable]
                
                for bitmask in range(1 << len(nullable_positions)):
                    modified_prod = list(prod)
                    for bit_idx, pos in enumerate(nullable_positions):
                        if (bitmask >> bit_idx) & 1:
                            modified_prod[pos] = None
                    modified_prod = tuple(s for s in modified_prod if s is not None)
                    
                    if len(modified_prod) > 0 and modified_prod not in updated_prods[nt]:
                        updated_prods[nt].append(modified_prod)
        
        if self.axiom in annulable:
            if () not in updated_prods[self.axiom]:
                updated_prods[self.axiom].append(())
        
        self.productions = updated_prods

    def eliminate_unit_productions(self) -> None:
        """Elimina producciones unitarias (A -> B)"""
        unit_closure: Dict[TokenType, Set[TokenType]] = {nt: {nt} for nt in self.productions}
        
        for nt in self.productions:
            modified = True
            while modified:
                modified = False
                for reachable_nt in list(unit_closure[nt]):
                    for prod in self.productions.get(reachable_nt, []):
                        if len(prod) == 1 and prod[0] in self.productions:
                            target_nt = prod[0]
                            if target_nt not in unit_closure[nt]:
                                unit_closure[nt].add(target_nt)
                                modified = True
        
        updated_prods: RuleMapping = collections.defaultdict(list)
        for nt in self.productions:
            collected: Set[ProductionRHS] = set()
            for reachable_nt in unit_closure[nt]:
                for prod in self.productions.get(reachable_nt, []):
                    if len(prod) == 1 and prod[0] in self.productions:
                        continue
                    collected.add(prod)
            updated_prods[nt] = list(collected)
        
        self.productions = updated_prods

    def convert_to_chomsky_normal_form(self) -> None:
        """Convierte la gramática a Forma Normal de Chomsky"""
        new_axiom = self.axiom + "_START"
        while new_axiom in self.productions:
            new_axiom += "_"
        self.productions[new_axiom] = [(self.axiom,)]
        self.axiom = new_axiom

        self.eliminate_epsilon_productions()
        self.eliminate_unit_productions()
        self.eliminate_nonproductive_symbols()
        self.eliminate_inaccessible_symbols()

        terminal_wrappers: Dict[TokenType, TokenType] = {}
        
        def get_terminal_wrapper(terminal: TokenType) -> TokenType:
            if terminal not in terminal_wrappers:
                wrapper = f"TERM_{terminal}"
                counter = 1
                while wrapper in self.productions:
                    counter += 1
                    wrapper = f"TERM_{terminal}_{counter}"
                terminal_wrappers[terminal] = wrapper
                self.productions[wrapper] = [(terminal,)]
            return terminal_wrappers[terminal]

        for nt in list(self.productions.keys()):
            updated_prods: List[ProductionRHS] = []
            for prod in self.productions[nt]:
                if len(prod) >= 2:
                    new_prod: List[TokenType] = []
                    for sym in prod:
                        if sym in self.productions:
                            new_prod.append(sym)
                        else:
                            new_prod.append(get_terminal_wrapper(sym))
                    updated_prods.append(tuple(new_prod))
                else:
                    updated_prods.append(prod)
            self.productions[nt] = updated_prods

        def split_long_production(prod: ProductionRHS) -> List[ProductionRHS]:
            if len(prod) <= 2:
                return [prod]
            
            symbols = list(prod)
            chain_head = symbols[0]
            remaining = symbols[1:]
            
            for idx in range(len(remaining) - 1):
                next_sym = remaining[idx]
                intermediate_nt = f"CHAIN_{chain_head}_{next_sym}_{idx}"
                counter = 1
                while intermediate_nt in self.productions:
                    counter += 1
                    intermediate_nt = f"CHAIN_{chain_head}_{next_sym}_{idx}_{counter}"
                self.productions[intermediate_nt] = [(chain_head, next_sym)]
                chain_head = intermediate_nt
            
            return [(chain_head, remaining[-1])]

        for nt in list(self.productions.keys()):
            current_prods = self.productions[nt]
            updated_prods: List[ProductionRHS] = []
            for prod in current_prods:
                if len(prod) > 2:
                    updated_prods.extend(split_long_production(prod))
                else:
                    updated_prods.append(prod)
            self.productions[nt] = updated_prods

        self.eliminate_unit_productions()
        self.eliminate_inaccessible_symbols()

    def build_terminal_index(self) -> Dict[TokenType, Set[TokenType]]:
        """Construye índice invertido: terminal -> {no terminales que lo producen}"""
        index: Dict[TokenType, Set[TokenType]] = collections.defaultdict(set)
        nonterminals = set(self.productions.keys())
        for nt, prod_list in self.productions.items():
            for prod in prod_list:
                if len(prod) == 1 and prod[0] not in nonterminals:
                    index[prod[0]].add(nt)
        return index

    def build_binary_index(self) -> Dict[Tuple[TokenType, TokenType], Set[TokenType]]:
        """Construye índice: (B, C) -> {A | A -> BC}"""
        index: Dict[Tuple[TokenType, TokenType], Set[TokenType]] = collections.defaultdict(set)
        for nt, prod_list in self.productions.items():
            for prod in prod_list:
                if len(prod) == 2:
                    index[(prod[0], prod[1])].add(nt)
        return index

    def __str__(self) -> str:
        """Representación textual de la gramática"""
        lines = [f"Axioma: {self.axiom}"]
        for nt in sorted(self.productions.keys()):
            alternatives = " | ".join([" ".join(p) if p else "ε" for p in self.productions[nt]])
            lines.append(f"{nt} → {alternatives}")
        return "\n".join(lines)


def cyk_algorithm(tokens: List[str], grammar: ContextFreeGrammar, tree_limit: int = 3) -> ParseResult:
    """
    Implementa el algoritmo CYK para análisis sintáctico
    """
    token_count = len(tokens)
    if token_count == 0:
        return ParseResult(False, 0.0, [])

    terminal_idx = grammar.build_terminal_index()
    binary_idx = grammar.build_binary_index()

    chart: List[List[Set[TokenType]]] = [[set() for _ in range(token_count)] for _ in range(token_count)]
    derivations: Dict[Tuple[int, int, TokenType], List[ParseNode]] = collections.defaultdict(list)

    start_time = time.perf_counter()

    # Fase 1: procesar tokens individuales
    for pos, token in enumerate(tokens):
        for nt in terminal_idx.get(token, set()):
            chart[pos][pos].add(nt)
            derivations[(pos, pos, nt)].append(ParseNode(nt, pos, pos, lexeme=token))

    # Fase 2: procesar subcadenas de longitud creciente
    for span_length in range(2, token_count + 1):
        for start_idx in range(0, token_count - span_length + 1):
            end_idx = start_idx + span_length - 1
            
            for split_point in range(start_idx, end_idx):
                left_set = chart[start_idx][split_point]
                right_set = chart[split_point + 1][end_idx]
                
                if not left_set or not right_set:
                    continue
                
                for left_nt in left_set:
                    for right_nt in right_set:
                        for parent_nt in binary_idx.get((left_nt, right_nt), set()):
                            if parent_nt not in chart[start_idx][end_idx]:
                                chart[start_idx][end_idx].add(parent_nt)
                            
                            for left_node in derivations.get((start_idx, split_point, left_nt), []):
                                for right_node in derivations.get((split_point + 1, end_idx, right_nt), []):
                                    if len(derivations[(start_idx, end_idx, parent_nt)]) < tree_limit:
                                        derivations[(start_idx, end_idx, parent_nt)].append(
                                            ParseNode(parent_nt, start_idx, end_idx, 
                                                    left_child=left_node, right_child=right_node)
                                        )

    elapsed_time = (time.perf_counter() - start_time) * 1000.0
    is_accepted = grammar.axiom in chart[0][token_count - 1]
    trees = derivations.get((0, token_count - 1, grammar.axiom), []) if is_accepted else []
    
    return ParseResult(is_accepted, elapsed_time, trees)


def load_grammar_from_file(filepath: str) -> ContextFreeGrammar:
    """Lee una gramática desde un archivo de texto"""
    rules: List[Rule] = []
    starting_symbol: Optional[str] = None
    
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            cleaned_line = line.strip()
            if not cleaned_line or cleaned_line.startswith('#') or cleaned_line.startswith('//'):
                continue
            
            match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*->\s*(.+)$", cleaned_line)
            if not match:
                continue
            
            lhs = match.group(1)
            if starting_symbol is None:
                starting_symbol = lhs
            
            rhs_text = match.group(2)
            for alternative in rhs_text.split('|'):
                alternative = alternative.strip()
                if alternative == 'e':
                    rules.append(Rule(lhs, tuple()))
                else:
                    symbols = [tok for tok in alternative.split() if tok]
                    rules.append(Rule(lhs, tuple(symbols)))
    
    if starting_symbol is None:
        raise ValueError('El archivo de gramática está vacío o tiene formato inválido')
    
    return ContextFreeGrammar(starting_symbol, rules)


OPERATOR_TOKENS = set(['(', ')', '+', '*'])


def tokenize_input(text: str) -> List[str]:
    """Tokeniza una cadena de entrada"""
    text = text.strip()
    if ' ' in text:
        return [tok for tok in text.split() if tok]
    
    result: List[str] = []
    idx = 0
    while idx < len(text):
        char = text[idx]
        if char.isspace():
            idx += 1
            continue
        if char in OPERATOR_TOKENS:
            result.append(char)
            idx += 1
            continue
        
        end_idx = idx
        while end_idx < len(text) and (text[end_idx].isalnum() or text[end_idx] == '_'):
            end_idx += 1
        result.append(text[idx:end_idx])
        idx = end_idx
    
    return result


def export_to_graphviz(tree: ParseNode) -> str:
    """Exporta un árbol de análisis a formato DOT de Graphviz"""
    id_generator = itertools.count(0)
    tree_body, root_id = tree.generate_graphviz(id_generator)
    return (
        "digraph ParseTree {\n"
        "  rankdir=TB;\n"
        "  node [shape=ellipse, fontsize=12];\n"
        f"{tree_body}\n"
        "}\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description='Analizador CYK: convierte CFG a CNF y analiza cadenas'
    )
    parser.add_argument('--grammar', type=str, required=True,
                       help='Archivo con la gramática en formato CFG')
    parser.add_argument('--string', type=str, required=True,
                       help='Cadena a analizar')
    parser.add_argument('--tree', type=str, default='',
                       help='Archivo de salida para el árbol en formato DOT')
    parser.add_argument('--show-cnf', action='store_true',
                       help='Mostrar la gramática convertida a CNF')
    parser.add_argument('--max_trees', type=int, default=2,
                       help='Número máximo de árboles de análisis a generar')
    
    args = parser.parse_args()

    cfg = load_grammar_from_file(args.grammar)
    cfg.convert_to_chomsky_normal_form()
    
    if args.show_cnf:
        print('=' * 50)
        print('Gramática en Forma Normal de Chomsky')
        print('=' * 50)
        print(cfg)
        print('=' * 50)

    token_sequence = tokenize_input(args.string)
    result = cyk_algorithm(token_sequence, cfg, tree_limit=args.max_trees)

    status = 'ACEPTADA' if result.is_valid else 'RECHAZADA'
    print(f"\nCadena analizada: {' '.join(token_sequence)}")
    print(f"Estado: {status}")
    print(f"Tiempo de análisis: {result.parse_time_ms:.3f} ms")
    
    if result.is_valid and result.parse_trees:
        print('\nÁrbol de análisis (notación con paréntesis):')
        print(result.parse_trees[0].render_bracketed())
        
        if args.tree:
            graphviz_output = export_to_graphviz(result.parse_trees[0])
            with open(args.tree, 'w', encoding='utf-8') as output_file:
                output_file.write(graphviz_output)
            print(f'\nÁrbol exportado a: {args.tree}')


if __name__ == '__main__':
    main()