import re

def eval_clause(clause, env):
    """Evaluate a clause with the given environment."""
    if '<=>' in clause:
        lhs, rhs = clause.split('<=>')
        return eval_expr(lhs.strip(), env) == eval_expr(rhs.strip(), env)
    elif '=>' in clause:
        lhs, rhs = clause.split('=>')
        return not eval_expr(lhs.strip(), env) or eval_expr(rhs.strip(), env)
    else:
        return eval_expr(clause, env)

def eval_expr(expr, env):
    """Evaluate an expression using the environment (truth values)."""
    expr = expr.strip()
    
    while '(' in expr:
        # Find innermost parentheses
        expr = re.sub(r'\(([^()]+)\)', lambda x: str(eval_expr(x.group(1), env)), expr)

    if '&' in expr:
        return all(eval_expr(subexpr.strip(), env) for subexpr in expr.split('&'))
    
    if '||' in expr:
        return any(eval_expr(subexpr.strip(), env) for subexpr in expr.split('||'))
    
    if expr.startswith('~'):
        return not eval_expr(expr[1:].strip(), env)
    
    # Base case: check for individual symbols or constants True/False
    return env.get(expr, expr == "True")  # default to False if symbol is not found