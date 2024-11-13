from nltk import word_tokenize, pos_tag

def process_sentence(sentence):
    # Tokenize and tag the sentence
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    
    # Example translation mapping (extend as needed)
    mapping = {
        "and": "&",
        "or": "|",
        "not": "~",
        "if": "",
        "then": "=>"
    }
    
    # Substitute words with logical symbols
    logic_expr = []
    skip_next = False
    for i, word in enumerate(tokens):
        if word.lower() in mapping:
            logic_expr.append(mapping[word.lower()])
        elif word.lower() == "if" and i + 2 < len(tokens) and tokens[i + 2].lower() == "then":
            # Special handling for "if ... then"
            logic_expr.append("(")
        elif word.lower() == "then":
            logic_expr.append(")=>")
            skip_next = True
        elif not skip_next:
            logic_expr.append(word)
        else:
            skip_next = False
    print(logic_expr)
    return ' '.join(logic_expr)

# Test with a sample sentence
sentence = "If it rains and it is cold, then the ground is wet."
logic_output = process_sentence(sentence)
print("Logical Expression:", logic_output)
