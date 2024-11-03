from evaluate import eval_clause
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
                premises_satisfied = all(backward_chaining(premise.strip(), inferred) for premise in premises.split('&'))
                if premises_satisfied:
                    return f"YES: {', '.join(inferred)}"
        elif eval_clause(clause, dict.fromkeys(inferred, True)):
            inferred.add(clause)
            if goal == clause:
                return f"YES: {', '.join(inferred)}"
    return "NO"