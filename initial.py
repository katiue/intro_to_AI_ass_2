import sys
from itertools import product

class InferenceEngine:
    def __init__(self, filename):
        self.filename = filename
        self.kb = []
        self.query = ""
        self.symbols = set()
        self.parse_file()

    def parse_file(self):
        """Parse the KB and query from the input file."""
        with open(self.filename, 'r') as file:
            content = file.read()
            tell_part, ask_part = content.split('ASK')
            self.query = ask_part.strip()
            tell_part = tell_part.replace("TELL", "").strip()
            clauses = tell_part.split(';')
            for clause in clauses:
                clause = clause.strip()
                if clause:
                    self.kb.append(clause)
                    self.extract_symbols(clause)

    def extract_symbols(self, clause):
        """Extract unique symbols from a clause for truth table purposes."""
        for symbol in clause.replace('&', ' ').replace('=>', ' ').split():
            if symbol:
                self.symbols.add(symbol)

    def tt_check(self):
        """Truth Table checking to determine if query is entailed by KB."""
        models_count = 0
        for model in product([False, True], repeat=len(self.symbols)):
            models_count += 1
            env = dict(zip(self.symbols, model))
            
            # Check if KB is satisfied in this environment
            kb_satisfied = all(self.eval_clause(clause, env) for clause in self.kb)
            
            if kb_satisfied:
                query_result = self.eval_clause(self.query, env)
                if query_result:
                    return f"YES: {models_count}"
        
        # If no environment satisfies both KB and query
        return "NO"

    def eval_clause(self, clause, env):
        """Evaluate a clause with the given environment."""
        if '=>' in clause:
            lhs, rhs = clause.split('=>')
            return not self.eval_expr(lhs.strip(), env) or self.eval_expr(rhs.strip(), env)
        else:
            return self.eval_expr(clause, env)

    def eval_expr(self, expr, env):
        """Evaluate an expression using the environment (truth values)."""
        if '&' in expr:
            return all(self.eval_expr(subexpr.strip(), env) for subexpr in expr.split('&'))
        return env.get(expr.strip(), False)  # Return False if the key is not found

    def forward_chaining(self):
        """Forward chaining algorithm."""
        inferred = set()
        agenda = [clause for clause in self.kb if '=>' not in clause]
        while agenda:
            p = agenda.pop()
            if p not in inferred:
                inferred.add(p)
                for clause in self.kb:
                    if '=>' in clause:
                        premises, conclusion = clause.split('=>')
                        if all(premise.strip() in inferred for premise in premises.split('&')):
                            if conclusion.strip() not in inferred:
                                if conclusion.strip() == self.query:
                                    return f"YES: {', '.join(inferred)}"
                                agenda.append(conclusion.strip())
        return "NO"

    def backward_chaining(self, goal=None, inferred=None):
        """Backward chaining algorithm."""
        if inferred is None:
            inferred = set()
        if goal is None:
            goal = self.query
        if goal in inferred:
            return True
        inferred.add(goal)

        for clause in self.kb:
            if '=>' in clause:
                premises, conclusion = clause.split('=>')
                if conclusion.strip() == goal:
                    if all(self.backward_chaining(premise.strip(), inferred) for premise in premises.split('&')):
                        return f"YES: {', '.join(inferred)}"
            else:
                return True
        if(inferred == goal):
            return "NO"

    def run(self, method):
        """Run the selected inference method."""
        if method == "TT":
            result = self.tt_check()
        elif method == "FC":
            result = self.forward_chaining()
        elif method == "BC":
            result = self.backward_chaining()
        else:
            result = "Invalid method. Choose TT, FC, or BC."
        print(result)

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python initial.py <filename> <method>")
    else:
        filename = sys.argv[1]
        method = sys.argv[2]
        engine = InferenceEngine(filename)
        engine.run(method)
