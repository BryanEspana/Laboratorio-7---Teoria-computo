import re
import itertools
import sys

def read_grammar(filename):
    grammar = {}
    non_terminals = set()
    terminals = set()
    production_regex = r'^[A-Z]\s*→\s*((([A-Za-z0-9]+)|ε)(\s*\|\s*(([A-Za-z0-9]+)|ε))*)$'

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except IOError:
        print(f"Error al abrir el archivo {filename}")
        sys.exit(1)

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue  # Ignorar líneas vacías
        # Validar la línea con la expresión regular
        if not re.match(production_regex, line):
            print(f"Error de sintaxis en la línea {line_num}: '{line}'")
            sys.exit(1)

        # Separar LHS y RHS
        lhs, rhs = line.split('→')
        lhs = lhs.strip()
        rhs = rhs.strip()

        # Agregar el no-terminal al conjunto de no-terminales
        non_terminals.add(lhs)

        # Separar las producciones por '|'
        productions = [prod.strip() for prod in rhs.split('|')]

        # Agregar las producciones al diccionario de gramática
        if lhs not in grammar:
            grammar[lhs] = set()
        for prod in productions:
            grammar[lhs].add(prod)
            for symbol in prod:
                if symbol.isupper():
                    non_terminals.add(symbol)
                elif symbol.islower() or symbol.isdigit():
                    terminals.add(symbol)
                elif symbol == 'ε':
                    pass  # ε no se agrega a terminales ni no-terminales
                else:
                    print(f"Símbolo inválido '{symbol}' en la línea {line_num}")
                    sys.exit(1)

    return grammar, non_terminals, terminals

def find_nullable_non_terminals(grammar):
    nullable = set()
    # Inicialmente, agregar no-terminales que producen ε directamente
    for lhs in grammar:
        if 'ε' in grammar[lhs]:
            nullable.add(lhs)

    # Iterativamente, agregar no-terminales que producen cadenas de símbolos anulables
    changed = True
    while changed:
        changed = False
        for lhs in grammar:
            if lhs not in nullable:
                for prod in grammar[lhs]:
                    if all(symbol in nullable for symbol in prod if symbol.isupper()):
                        nullable.add(lhs)
                        changed = True
                        break
    print("\nSímbolos anulables:", nullable)
    return nullable

def remove_epsilon_productions(grammar, nullable):
    new_grammar = {}
    for lhs in grammar:
        new_productions = set()
        for prod in grammar[lhs]:
            if prod == 'ε':
                continue  # Eliminar producciones-ε
            else:
                # Encontrar posiciones de símbolos anulables
                positions = [i for i, symbol in enumerate(prod) if symbol in nullable]
                subsets = []
                for r in range(1, len(positions)+1):
                    subsets.extend(itertools.combinations(positions, r))
                # Generar nuevas producciones excluyendo combinaciones de símbolos anulables
                for subset in subsets:
                    new_prod = ''.join([symbol for i, symbol in enumerate(prod) if i not in subset])
                    if new_prod == '':
                        new_prod = 'ε'
                    new_productions.add(new_prod)
            new_productions.add(prod)
        new_grammar[lhs] = new_productions

    # Si el símbolo inicial es anulable, agregar producción S → ε
    start_symbol = list(grammar.keys())[0]
    if start_symbol in nullable:
        new_grammar[start_symbol].add('ε')

    return new_grammar

def print_grammar(grammar, title):
    print(f"\n{title}")
    for lhs in grammar:
        productions = ' | '.join(sorted(grammar[lhs], key=lambda x: (x != 'ε', x)))
        print(f"{lhs} → {productions}")

def main():
    # Seleccione el archivo de gramática
    filename = input("Ingrese el nombre del archivo de gramática (e.g., 'gramatica1.txt'): ")

    # Leer y validar la gramática
    grammar, non_terminals, terminals = read_grammar(filename)

    print_grammar(grammar, "Gramática original:")

    # Encontrar símbolos anulables
    nullable = find_nullable_non_terminals(grammar)

    # Eliminar producciones-ε
    new_grammar = remove_epsilon_productions(grammar, nullable)

    print_grammar(new_grammar, "Gramática sin producciones-ε:")

if __name__ == "__main__":
    main()
