def backward_chaining(kb, query, symbols, goal=None, inferred=None):
    """Backward chaining algorithm."""
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
                if all(backward_chaining(premise.strip(), inferred) for premise in premises.split('&')):
                    return f"YES: {', '.join(inferred)}"
    return "NO"