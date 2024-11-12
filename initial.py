import sys
import itertools
import re
import os

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
            clause = clause.replace(" ", "").strip()
            if '=>' in clause or '<=>' in clause:
                self.rules.append(clause)
            elif clause:
                self.facts.append(clause)
            self.extract_symbols(clause)

    def extract_symbols(self, expression):
        # Extract unique symbols from the expression
        tokens = re.findall(r'\w+', expression)
        self.symbols.update(tokens)

    def eval_expr(self, expr, model):
        # Replace logical symbols with Python boolean operators
        expr.strip()
        expr = expr.replace("<=>", "==").replace("=>", "<=").replace("&", " and ").replace("||", " or ").replace("~", " not ")
        # Replace each symbol in the expression with its truth value from the model
        for symbol in self.symbols:
            expr = re.sub(r'\b' + symbol + r'\b', str(model.get(symbol, False)), expr)
        try:
            return eval(expr)
        except Exception as e:
            print(self.filename)
            print(f"Error evaluating expression: {expr}, Error: {e}")
            return False

    def tt_entails(self):
        # Truth Table Method for Entailment
        for model in self.generate_models():
            if self.is_kb_true(model) and not self.eval_expr(self.query, model):
                return "NO"
        return "YES"

    def generate_models(self):
        # Generate all possible truth assignments
        return [dict(zip(self.symbols, vals)) for vals in itertools.product([True, False], repeat=len(self.symbols))]

    def is_kb_true(self, model):
        # Check if knowledge base is true under a given model
        return all(self.eval_expr(fact, model) for fact in self.facts) and all(self.eval_expr(rule, model) for rule in self.rules)

    def forward_chaining(self):
        # Forward Chaining Method
        known_facts = set(fact for fact in self.facts if self.eval_expr(fact, {fact: True}))
        while True:
            added = False
            for rule in self.rules:
                lhs, rhs = rule.split("=>")
                lhs, rhs = lhs.strip(), rhs.strip()
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
            lhs, rhs = rule.split("=>")
            rhs = rhs.strip()
            if rhs == goal:
                if all(self.bc_recursive(sym.strip(), inferred) for sym in lhs.split("&")):
                    return True
        return False

    def ask(self, method):
        # Main entry point to evaluate the query using the specified method
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
        ask_part, expext_part = other_part.split('EXPECT')
        tell_part = tell_part.replace("TELL", "").strip()
        ask_part = ask_part.strip()
        expext_part = expext_part.strip()
    return tell_part, ask_part, expext_part

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
        print("Usage: python main.py <folder_path> <method>")
    else:
        folder_path = sys.argv[1]
        method = sys.argv[2]
        run_all_tests_in_folder(folder_path, method)
