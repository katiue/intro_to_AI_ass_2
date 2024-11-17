import sys
import itertools
import re
import os
from NLtranslator import process_prompt, translate

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

    def eval_expr(self, expr, model):
        expr = expr.strip()
        # Replace each symbol with its truth value from the model
        for symbol in sorted(self.symbols, key=lambda s: -len(s)):
            expr = re.sub(r'\b{}\b'.format(re.escape(symbol)), str(model.get(symbol, False)), expr)

        # Wrap negations (~) with parentheses around variables and parenthesized expressions
        expr = re.sub(r'~([^\s()&|]+)', r'(~\1)', expr)   # Single variable negation, e.g., ~p -> (~p)
        expr = re.sub(r'~(\([^()]+\))', r'(~\1)', expr)    # Parenthesized expression negation, e.g., ~(a&b) -> (~(a&b))

        # Iteratively replace implications and biconditionals until none remain
        previous_expr = None
        while previous_expr != expr:
            previous_expr = expr

            # Replace the first occurrence of a biconditional (<=>)
            expr = re.sub(r'([^\s()]+)\s*<=>\s*([^\s()]+)', r'((\1 and \2) or ((not \1) and (not \2)))', expr, count=1)
            expr = re.sub(r'\(([^()]+)\)\s*<=>\s*\(([^()]+)\)', r'((\1 and \2) or ((not \1) and (not \2)))', expr, count=1)
            expr = re.sub(r'\(([^()]+)\)\s*<=>\s*([^\s()]+)', r'((\1 and \2) or ((not \1) and (not \2)))', expr, count=1)
            expr = re.sub(r'([^\s()]+)\s*<=>\s*\(([^()]+)\)', r'((\1 and \2) or ((not \1) and (not \2)))', expr, count=1)

            # Replace the first occurrence of an implication (=>)
            expr = re.sub(r'([^\s()]+)\s*=>\s*([^\s()]+)', r'(not \1 or \2)', expr, count=1)
            expr = re.sub(r'\(([^()]+)\)\s*=>\s*\(([^()]+)\)', r'(not (\1) or (\2))', expr, count=1)
            expr = re.sub(r'\(([^()]+)\)\s*=>\s*([^\s()]+)', r'(not (\1) or \2)', expr, count=1)
            expr = re.sub(r'([^\s()]+)\s*=>\s*\(([^()]+)\)', r'(not \1 or (\2))', expr, count=1)

        # Replace logical negation, conjunction, and disjunction
        expr = expr.replace('~', ' not ')
        expr = expr.replace('&', ' and ').replace('||', ' or ')

        # Remove extra whitespace
        expr = ' '.join(expr.split())

        try:
            return eval(expr)
        except Exception as e:
            return False
    
    def tt_entails(self):
        # Truth Table Method for Entailment
        count = 0
        for model in self.generate_models():
            if self.is_kb_true(model):
                count += 1
                if self.eval_expr(self.query, model):
                    return "YES", count
        return "NO", 0

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
        details = ', '.join(self.facts)
        return ("YES", details) if self.eval_expr(self.query, {fact: True for fact in known_facts}) else ("NO", 0)


    def backward_chain(self, goal=None, visited=None):
        """Backward chaining to determine if the goal can be satisfied."""
        if goal is None:
            goal = self.query

        goal = goal.replace(' ', '')

        if visited is None:
            visited = set()

        if goal.startswith('~'):
            goal = goal[1:]
            if goal in self.facts:
                return not self.backward_chain(goal, visited)
            
        # Check if the goal is a fact
        if goal in self.facts:
            details = ', '.join(self.facts)
            return True, details

        if goal in visited:
            return False, "" # Avoid infinite loops
        visited.add(goal)

        # Check if the goal can be inferred from rules
        for rule in self.rules:
            if '<=>' not in rule and '=>' not in rule:
                continue
            if '<=>' in rule:
                premise, conclusion = map(str.strip, rule.split('<=>'))
            else:
                premise, conclusion = map(str.strip, rule.split('=>'))
            conclusion = conclusion.replace(' ', '')
            if conclusion == goal:
                # Split the premise into sub-goals
                if '||' in premise:
                    sub_goals = [g.strip() for g in premise.split('||') if g.strip()]
                    if any(self.backward_chain(sub_goal, visited) for sub_goal in sub_goals):
                        self.facts.append(goal)
                        details = ', '.join(self.facts)
                        return True, details
                else:
                    sub_goals = [g.strip() for g in premise.split('&') if g.strip()]
                    if all(self.backward_chain(sub_goal, visited) for sub_goal in sub_goals):
                        self.facts.append(goal)
                        details = ', '.join(self.facts)
                        return True, details

        # If no fact or rule supports the goal
        return False, ""

    def ask(self, method):
        # Main entry point to evaluate the query using the specified method
        if(not self.check_query_possible()):
            return "NO", ""
        if method == "TT":
            return self.tt_entails()
        elif method == "FC":
            return self.forward_chaining()
        elif method == "BC":
            return self.backward_chain()
        else:
            return "Unknown method", "N/A"

def parse_file(filename):
    """Parse the KB and query from the input file."""
    with open(filename, 'r') as file:
        content = file.read()
        tell_part, ask_part = content.split('ASK')
        ask_part = ask_part.strip()
        tell_part = tell_part.replace("TELL", "").strip()
    return tell_part, ask_part

def run(kb, query, method, filename):
    engine = InferenceEngine(kb, query, filename)
    result, detail = engine.ask(method)
    detail = str(detail)
    if result == "YES" or result:
        result = "YES: " + detail
    else:
        result = "NO"
    print(f"RESULT\n{result}")

def run_all_tests_in_folder(folder_path, method):
    test_results = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Only process .txt files
            file_path = os.path.join(folder_path, filename)
            kb, query = parse_file(file_path)
            engine = InferenceEngine(kb, query, filename)
            actual_output, detail = engine.ask(method)
            if actual_output == True or actual_output == "YES":
                actual_output = "YES"
            else:
                actual_output = "NO"
            test_results.append((filename, actual_output, detail))

    # Display results
    for test_file, result, detail in test_results:
        print(f"File: {test_file} | Result: {result} | Details: {detail}")

    # Summary
    print("\nTest Results Summary:")
    total_tests = len(test_results)
    YES_tests = sum(1 for _, result, _ in test_results if result == "YES")
    NO_tests = total_tests - YES_tests
    print(f"\nTotal Tests: {total_tests} | YES: {YES_tests} | NO: {NO_tests}")
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Allowed inputs:")
        print("Usage: python initial.py <filename> <method>")
        print("Usage: python initial.py -f <folder_path> <method>")
        print("Usage: python initial.py -nl <filename> <method>")
    else:
        if sys.argv[1] == "-f":
            if os.path.isdir(sys.argv[2]):
                folder_path = sys.argv[2]
                method = sys.argv[3]
                run_all_tests_in_folder(folder_path, method)
            else:
                print("Invalid folder path.")
        elif sys.argv[1] == "-nl":
            if not os.path.isfile(sys.argv[2]):
                print("Invalid file path.")
            else:
                filename = sys.argv[2]
                method = sys.argv[3]
                kb, query, dictionary = process_prompt(filename)
                engine = InferenceEngine(kb, query, filename)
                result, detail = engine.ask(method)
                if(result == "YES" or result):
                    result = "YES: " + translate(detail, dictionary)
                else:
                    result = "NO"
                print(f"RESULT\n{result}")
        else:
            if not os.path.isfile(sys.argv[1]):
                print("Invalid file path.")
            else:
                filename = sys.argv[1]
                method = sys.argv[2]
                kb, query = parse_file(filename)
                run(kb, query, method, filename)
