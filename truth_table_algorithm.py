from itertools import product
from evaluate import eval_clause

def tt_check(kb, query, symbols):
        """Truth Table checking to determine if query is entailed by KB."""
        models_count = 0

        for model in product([False, True], repeat=len(symbols)):
            env = dict(zip(symbols, model))
            kb_satisfied = all(eval_clause(clause, env) for clause in kb)
            if kb_satisfied:
                print(f"Model {models_count + 1}: {env}")
                models_count += 1
                # If KB is satisfied in this environment, check if the query is also satisfied
                if eval_clause(query, env):
                    return f"YES: {models_count}"
            
        return "NO"