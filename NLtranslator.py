import re
from nltk import word_tokenize, pos_tag

# Extend mapping dictionary with logical symbols
mapping = {
    "and": "&",
    "or": "||",
    "not": "~",
    "if": "",            # No direct mapping for 'if', handled in logic below
    "then": "=>",
    "implies": "=>",
    "iff": "<=>",
    "biconditional": "<=>",
    "implication": "=>"
}

dictionary = dict()

# Function to translate sentences to logical expressions
def translate(sentence):
    words = sentence.split()
    for i, word in enumerate(words):
        if word in dictionary:
            words[i] = dictionary[word]
    return ' '.join(words)

# Function to process sentence with logic translation
def process_sentence(sentence):
    # Remove punctuations for consistent parsing
    sentence.strip()
    sentence = sentence.replace(",", "").replace(".", "").replace(";", "")
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    
    # Substitute words with logical symbols
    logic_expr = []
    skip_next = False
    for i, word in enumerate(tokens):
        # Check if word is a logical keyword
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
    
    # Process logical expression to handle variables uniquely
    clause = ''
    current_word = ''

    # Iterate over words in logic expression
    for word in logic_expr:
        if current_word != '' and word != '' and word in mapping.values():
            # Add current word to dictionary if not already present
            if current_word not in dictionary.values():
                unique_id = str(len(dictionary) + 1)
                clause += ' ' + unique_id + ' '
                dictionary[unique_id] = current_word.strip()
            # Translate logical symbol to corresponding keyword
            else:
                for key, value in dictionary.items():
                    if value == current_word.strip():
                        clause += ' ' + key + ' '
            if word != '':
                clause += word + ' '
            current_word = ''
        else:
            current_word += word + ' '
    # Add last word to dictionary if not already present
    if current_word.strip() and current_word not in dictionary.values():
        unique_id = str(len(dictionary) + 1)
        clause += ' ' + unique_id + ' '
        dictionary[unique_id] = current_word.strip()

    return clause.strip(), dictionary

# Function to determine sentence type and apply relevant parsing
def process_input(sentence):
    sentence = sentence.strip()
    
    if sentence.endswith('.'):
        # Knowledge base entry
        logic_expr, dict_map = process_sentence(sentence[:-1])
    elif sentence.endswith(';'):
        # Complex conditional statement
        logic_expr, dict_map = process_sentence(sentence[:-1])
    elif sentence.endswith('?'):
        # Query
        logic_expr, dict_map = process_sentence(sentence[:-1])
    else:
        # Default handling if not ending with punctuation
        logic_expr, dict_map = process_sentence(sentence)

    return logic_expr, dict_map

# Test paragraph
# paragraph = "If it rains and it rains, then the ground is wet. The sky is blue. It is sunny and warm; Is the ground wet?"
paragraph = "if I'm happy then I win. If I win then You Loose. if you play then you have fun. If I have fun and you have fun then It's a good day. If It's a good day and I dance then you dance. If you loose, you are broke. If you loose and I win then you play. You have fun. I'm millionaire. I have fun. I'm happy."
# Split the paragraph by ".", ";", or "?" and keep the delimiters
sentences = re.split(r'([.;?])\s*', paragraph)

# Combine sentences with their delimiters and process each one
processed_sentences = []
for i in range(0, len(sentences) - 1, 2):
    sentence = sentences[i].strip() + sentences[i + 1]  # sentence + delimiter
    processed_sentences.append(sentence)

# Process each complete sentence
for s in processed_sentences:
    if s:  # Ensure the sentence is not empty
        logic_epxr, _ = process_input(s)
        print(logic_epxr)
        print(translate(logic_epxr))
