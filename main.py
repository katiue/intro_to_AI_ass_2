import sys
from read_file import parse_file
from truth_table_algorithm import tt_check
from forward_chaining_algorithm import forward_chaining
from backward_chaining_algorithm import backward_chaining

def run(kb, query, symbols, method):
    """Run the selected inference method."""
    if method == "TT":
        result = tt_check(kb, query, symbols)
    elif method == "FC":
        result = forward_chaining(kb, query, symbols)
    elif method == "BC":
        result = backward_chaining(kb, query, symbols)
    else:
        result = "Invalid method. Choose TT, FC, or BC."
    print(result)

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <filename> <method>")
    else:
        filename = sys.argv[1]
        method = sys.argv[2]
        kb, query, symbols = parse_file(filename)
        run(kb, query, symbols, method)