import sys
import itertools
import re
import os

def split_clauses(clause):
    clauses = []
    depth = 0
    current_clause = ''
    for char in clause:
        if char == '(':
            depth += 1
            current_clause += char
        elif char == ')':
            depth -= 1
            current_clause += char
        elif char == '&' and depth == 0:
            clauses.append(current_clause.strip())
            current_clause = ''
        else:
            current_clause += char
    if current_clause.strip():
        clauses.append(current_clause.strip())
    return clauses

class InferenceEngine:
    def __init__(self, kb, query, filename):
        self.filename = filename
        self.kb = kb
        self.query = query
        self.symbols = set()
        self.rules = []
        self.facts = []
        self.parse_kb()

    def parse_kb(self):
        # Split knowledge base by clauses and identify rules and facts
        for clause in self.kb.split(";"):
            clause = clause.strip()
            if not clause:
                continue
            # Use the custom split_clauses function
            sub_clauses = split_clauses(clause)
            for sub_clause in sub_clauses:
                sub_clause = sub_clause.strip()
                sub_clause = sub_clause.replace(' ', '')  # Corrected line
                if not sub_clause:
                    continue
                self.extract_symbols(sub_clause)
                if '=>' in sub_clause or '<=>' in sub_clause:
                    self.rules.append(sub_clause)
                else:
                    self.facts.append(sub_clause)

    def check_query_possible(self):
        expression = re.sub(r'[&|~()<=>]', ' ', self.query)
        tokens = expression.split()
        for token in tokens:
            if token not in self.symbols:
                return False
        return True

    def extract_symbols(self, expression):
        # Remove logical operators and parentheses
        expression = re.sub(r'[&|~()<=>]', ' ', expression)
        tokens = expression.split()
        self.symbols.update(tokens)

    def add_parentheses(self, expr):
        # Add parentheses around expressions based on operator precedence
        expr = expr.replace('~', ' not ')
        # Handle negations
        expr = re.sub(r'not\s+(\w+)', r'(not \1)', expr)
        
        # Handle conjunctions
        expr = re.sub(r'(\w+)\s*&\s*(\w+)', r'(\1 and \2)', expr)
        
        # Handle disjunctions
        expr = re.sub(r'(\w+)\s*\|\|\s*(\w+)', r'(\1 or \2)', expr)
        
        # Handle implications and biconditionals
        # Add parentheses to ensure correct precedence
        return expr

    def eval_expr(self, expr, model):
        expr = expr.strip()
        # Replace each symbol with its truth value from the model
        for symbol in sorted(self.symbols, key=lambda s: -len(s)):
            expr = re.sub(r'\b{}\b'.format(re.escape(symbol)), str(model.get(symbol, False)), expr)
        # Replace logical negation
        expr = expr.replace('~', ' not ')
        # Replace logical conjunction and disjunction
        expr = expr.replace('&', ' and ').replace('||', ' or ')

        # Iteratively replace implications and biconditionals
        while '<=>' in expr or '=>' in expr:
            # Replace biconditionals
            expr = re.sub(r'([^\s()]+)\s*<=>\s*([^\s()]+)', r'((\1 and \2) or ((not \1) and (not \2)))', expr)
            expr = re.sub(r'\(([^()]+)\)\s*<=>\s*\(([^()]+)\)', r'((\1 and \2) or ((not \1) and (not \2)))', expr)
            expr = re.sub(r'\(([^()]+)\)\s*<=>\s*([^\s()]+)', r'((\1 and \2) or ((not \1) and (not \2)))', expr)
            expr = re.sub(r'([^\s()]+)\s*<=>\s*\(([^()]+)\)', r'((\1 and \2) or ((not \1) and (not \2)))', expr)

            # Replace implications
            expr = re.sub(r'([^\s()]+)\s*=>\s*([^\s()]+)', r'(not \1 or \2)', expr)
            expr = re.sub(r'\(([^()]+)\)\s*=>\s*\(([^()]+)\)', r'(not (\1) or (\2))', expr)
            expr = re.sub(r'\(([^()]+)\)\s*=>\s*([^\s()]+)', r'(not (\1) or \2)', expr)
            expr = re.sub(r'([^\s()]+)\s*=>\s*\(([^()]+)\)', r'(not \1 or (\2))', expr)
        # Remove extra whitespace
        expr = ' '.join(expr.split())

        try:
            return eval(expr)
        except Exception as e:
            print(self.filename)
            print(f"Error evaluating expression: {expr}, Error: {e}")
            return False

    def tt_entails(self):
        # Truth Table Method for Entailment
        for model in self.generate_models():
            if self.is_kb_true(model) and self.eval_expr(self.query, model):
                    return "YES"
        return "NO"

    def generate_models(self):
        # Generate all possible truth assignments
        return [dict(zip(self.symbols, vals)) for vals in itertools.product([True, False], repeat=len(self.symbols))]

    def is_kb_true(self, model):
        # Check if knowledge base is true under a given model
        return all(self.eval_expr(fact, model) for fact in self.facts) and all(self.eval_expr(rule, model) for rule in self.rules)

    def forward_chaining(self):
        # Forward Chaining Method
        known_facts = set(self.facts)
        while True:
            added = False
            for rule in self.rules:
                lhs, rhs = re.split(r'\s*=>\s*|\s*<=>\s*', rule, 1)
                lhs = lhs.strip()
                rhs = rhs.strip()
                # Evaluate lhs with the current known facts
                if self.eval_expr(lhs, {fact: True for fact in known_facts}) and rhs not in known_facts:
                    known_facts.add(rhs)
                    added = True
            if not added:
                break
        return "YES" if self.eval_expr(self.query, {fact: True for fact in known_facts}) else "NO"

    def backward_chaining(self):
        # Backward Chaining Method
        return "YES" if self.bc_recursive(self.query, set()) else "NO"

    def bc_recursive(self, goal, inferred):
        # Recursive helper for backward chaining
        if goal in inferred:
            return False
        inferred.add(goal)
        if goal in self.facts:
            return True
        for rule in self.rules:
            lhs, rhs = re.split(r'\s*=>\s*|\s*<=>\s*', rule, 1)
            lhs = lhs.strip()
            rhs = rhs.strip()
            if rhs == goal:
                # Split lhs into premises considering conjunctions
                premises = split_clauses(lhs)
                if all(self.bc_recursive(premise.strip(), inferred) for premise in premises):
                    return True
        return False

    def ask(self, method):
        # Main entry point to evaluate the query using the specified method
        if(not self.check_query_possible()):
            return "NO"
        if method == "TT":
            return self.tt_entails()
        elif method == "FC":
            return self.forward_chaining()
        elif method == "BC":
            return self.backward_chaining()
        else:
            return "Unknown method"

def parse_file(filename):
    """Parse the KB and query from the input file."""
    with open(filename, 'r') as file:
        content = file.read()
        tell_part, other_part = content.split('ASK')
        ask_part, expect_part = other_part.split('EXPECT')
        tell_part = tell_part.replace("TELL", "").strip()
        ask_part = ask_part.strip()
        expect_part = expect_part.strip()
    return tell_part, ask_part, expect_part

def run(kb, query, method):
    engine = InferenceEngine(kb, query)
    result = engine.ask(method)
    print(f"RESULT\n{result}")

def run_all_tests_in_folder(folder_path, method):
    test_results = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Only process .txt files
            file_path = os.path.join(folder_path, filename)
            kb, query, expected_output = parse_file(file_path)
            engine = InferenceEngine(kb, query, filename)
            actual_output = engine.ask(method)
            result = (actual_output == expected_output)
            test_results.append((filename, result, actual_output, expected_output))

    # Display results
    print("\nTest Results Summary:")
    for test_file, result, actual, expected in test_results:
        status = "PASS" if result else "FAIL"
        print(f"File: {test_file} | Status: {status} | Expected: {expected} | Actual: {actual}")

    # Summary
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result, _, _ in test_results if result)
    print(f"\nTotal Tests: {total_tests} | Passed: {passed_tests} | Failed: {total_tests - passed_tests}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python initial.py <folder_path> <method>")
    else:
        folder_path = sys.argv[1]
        method = sys.argv[2]
        run_all_tests_in_folder(folder_path, method)
