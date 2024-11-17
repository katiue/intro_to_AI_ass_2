import google.generativeai as genai

def translate(sentence, dictionary):
    if type(sentence) is int:
        return str(sentence)
    result = ''
    for word in sentence.split():
        if word in dictionary:
            result += dictionary[word] + ', '
    if result.endswith(', '):
        result = result[:-1]
    return result.strip()

def parse_prompt(content):
    if 'TELL' not in content or 'ASK' not in content or 'DICT' not in content:
        return None, None, None
    tell_part, other_part = content.split('ASK')
    ask_part, raw_dictionary = other_part.split('DICT')
    tell_part = tell_part.replace("TELL", "").strip()
    ask_part = ask_part.strip()
    raw_dictionary = raw_dictionary.strip()
    raw_dictionary = raw_dictionary.split(';')
    dictionary = dict()
    for items in raw_dictionary:
        key, value = items.split(':')
        dictionary[key.strip()] = value.strip()
    return tell_part, ask_part, dictionary

def process_prompt(filename):
    model = genai.GenerativeModel("gemini-1.5-flash")
    genai.configure(api_key="AIzaSyC3tYkpmfCZauuV_tfCYklFeMSeucvxVzw")
    sentence = ''
    with open(filename, 'r') as file:
        sentence = file.read()

    prompt = f"""could you help me translate this sentence into propositional logic:
    {sentence}
    rules are as follow: or means ||, and means & if ... then mean a => b. each sentence end with . and ; means it's a clause in knowledge base. "?" means it is ask. the rest like "it is raining" will transform into something like "a" : "it is raining" so that i can represent something as. "if it is raining, i bring umbrella" turns into "1 => 2" with "1" : "it is raining", "2": i bring umbrella"
    write it as something similar to 
    TELL
    a => b; b =>c; c => d; d;
    ASK
    d
    DICT
    a: it is raining; b: i bring umbrella; c: i am happy; d: i'm millionaire
    answer in short with no additional information just tell and ask. no additional expession like ``` or \\n"""

    response = model.generate_content(prompt)
    print(response.text)
    tell_part, ask_part, dictionary = parse_prompt(response.text)

    return tell_part, ask_part, dictionary