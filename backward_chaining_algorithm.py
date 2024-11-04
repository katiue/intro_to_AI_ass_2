from evaluate import eval_clause, eval_expr
def backward_chaining(kb, query, symbols, goal=None, inferred=None):
    """Backward chaining algorithm with support for complex expressions."""
    if inferred is None:
        inferred = set()
    if goal is None:
        goal = query
    if goal in inferred:
        return True
    inferred.add(goal)

    for clause in kb:
        if '=>' in clause:
            premises, conclusion = clause.split('=>')
            if conclusion.strip() == goal:
                if all(backward_chaining(kb, query, symbols, premise.strip(), inferred) for premise in premises.split('&')):
                    return f"YES: {', '.join(inferred)}"
        elif '<=>' in clause:
            lhs, rhs = clause.split('<=>')
            if backward_chaining(kb, query, symbols, lhs.strip(), inferred) and backward_chaining(kb, query, symbols, rhs.strip(), inferred):
                return f"YES: {', '.join(inferred)}"
        else:
            if eval_clause(clause, dict(zip(symbols, [True]*len(symbols)))):
                inferred.add(clause)
            if goal == clause:
                return f"YES: {', '.join(inferred)}"
    return "NO"