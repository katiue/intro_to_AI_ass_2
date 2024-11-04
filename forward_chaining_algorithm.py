def forward_chaining(kb, query, symbols):
    """Forward chaining algorithm."""
    inferred = set()
    agenda = [clause for clause in kb if '=>' not in clause]
    while agenda:
        p = agenda.pop()
        if p not in inferred:
            inferred.add(p)
            for clause in kb:
                if '=>' in clause:
                    premises, conclusion = clause.split('=>')
                    if all(premise.strip() in inferred for premise in premises.split('&')):
                        if conclusion.strip() not in inferred:
                            if conclusion.strip() == query:
                                return f"YES: {', '.join(inferred)}"
                            agenda.append(conclusion.strip())
    return "NO"