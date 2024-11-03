def extract_symbols(clause, symbols):
    """Extract unique symbols from a clause for truth table purposes."""
    clause = clause.replace('&', ' ').replace('||', ' ').replace('=>', ' ').replace('<=>', ' ').replace('~', ' ').replace('(', ' ').replace(')', ' ')
    for symbol in clause.split():
        if symbol and symbol not in ["True", "False"]:  # Exclude boolean literals
            symbols.add(symbol)

def parse_file(filename):
    """Parse the KB and query from the input file."""
    kb = []
    query = ""
    symbols = set()
    with open(filename, 'r') as file:
        content = file.read()
        tell_part, ask_part = content.split('ASK')
        query = ask_part.strip()
        tell_part = tell_part.replace("TELL", "").strip()
        clauses = tell_part.split(';')
        for clause in clauses:
            clause = clause.strip()
            if clause:
                kb.append(clause)
                extract_symbols(clause, symbols)
    return kb, query, symbols