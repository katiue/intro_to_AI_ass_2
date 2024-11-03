from evaluate import eval_clause
def forward_chaining(kb, query, symbols):
    """Forward chaining algorithm that evaluates all logical expressions."""
    inferred = set()
    agenda = [clause for clause in kb if '=>' not in clause or eval_clause(clause, dict.fromkeys(symbols, True))]
    
    while agenda:
        p = agenda.pop()
        if p not in inferred:
            inferred.add(p)
            for clause in kb:
                if '=>' in clause:
                    premises, conclusion = clause.split('=>')
                    premises_satisfied = all(eval_clause(premise.strip(), dict.fromkeys(inferred, True)) for premise in premises.split('&'))
                    if premises_satisfied:
                        if conclusion.strip() not in inferred:
                            if conclusion.strip() == query:
                                return f"YES: {', '.join(inferred)}"
                            agenda.append(conclusion.strip())
                elif eval_clause(clause, dict.fromkeys(inferred, True)):
                    if clause not in inferred:
                        inferred.add(clause)
                        if clause == query:
                            return f"YES: {', '.join(inferred)}"
    return "NO"