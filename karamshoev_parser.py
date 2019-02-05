import re
import json
from time import sleep

broken_symbols_check = {'H', '!', '7', 'R', 'B', '}', 'V', 'Ы', 'J', 'E', '́', '4', '£', 'Э', 'U', '-', '"', '„', '0', 'Ҳ', 'Щ', 'G', '*', '[', 'K', ':', '«', '^', '#', '+', 'С', 'Y', '%', '/', '_', '2', '°', '9', ')', 'S', '5', ']', '§', '>', '1', '<', 'Ё', '$', '̌', 'Я', 'Ю', '̊', '=', ';', '8', '“', 'O', '™', '\\', 'Ҙ', '?', 'P', '\xad', 'Ʒ', 'T', 'A', '6', '3', '|', '•', 'Z', '№', 'L', '(', 'D', 'I', '—', 'Q', '»', 'M', 'Ь', "'", '■', 'Х', '&', 'F', '®', '~'}

with open('karamshoev-zarubin.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)

with open('karamshoev.txt', 'r', encoding="UTF-8") as f:
    b_lines = f.readlines()
    b_lines[0] = b_lines[0].replace('\ufeff', '')
    lines = []
    for line in b_lines:
        new_line = ''
        for sym in line:
            if sym not in broken_symbols_check:
                new_line += sym
        lines.append(new_line)

broken_symbols = []

class Karamshoev_line(object):
    def __init__(self, line):
        self.line = line

    def translate(self, word, output='z'):
        if output == 'k':
            return word
        result = ''
        for sym in word:
            result += mapping[sym]
            broken_symbols.append(sym)
        return result

    def get_shung_lex(self):
        line = self.line
        words = line.split()
        lexemes = [word for word in words if word.isupper() and not word.startswith('-') and not (len(word) == 2 and word.endswith(')'))]
        result = []
        for lexeme in lexemes:
            lexeme = re.sub('(\.|,| )', '', lexeme)
            if re.findall('\(.*?\)', lexeme):
                #print(lexeme)
                lexeme1 = re.sub('\(.*?\)', '', lexeme), output
                lexeme2 = re.sub('(\(|\))', '', lexeme), output
                result.append(lexeme1)
                result.append(lexeme2)
            else:
                result.append(lexeme)
        return (result, map(self.translate, result))

    def get_data(self):
        lexemes = self.get_shung_lex()
        line = self.line
        words = []
        for word in line.split():
            if word.isupper():
                continue
            else:
                words.append(word)
        description = ' '.join(words)
        return description.split(';')

    def get_json(self):
        js = []
        js_line = {}
        lexemes = self.get_shung_lex()
        description = self.get_data()
        if not lexemes:
            return
        #print(lexemes)
        for lex, lex_z in zip(lexemes[0], lexemes[1]):
            #print(lex)
            gender = re.findall('м. ', description[0])
            description[0] = description[0].replace('м. ', '')
            js_line['lexeme'] = lex
            js_line['lexeme_z'] = lex_z
            js_line['russian'] = [tr for tr in description if not (tr.startswith(' ш.') or tr.startswith(' б. ') or tr.startswith('ш.') or tr.startswith('б.'))]
            if gender:
                js_line['gender'] = gender[0]
            example_sh = [ex.replace(' ш. ', '') for ex in description if ex and (ex.startswith(' ш.') or ex.startswith('ш.'))]
            if example_sh:
                js_line['example_sh'] = example_sh
            example_b = [ex.replace(' б. ', '') for ex in description if ex and (ex.startswith(' б.') or ex.startswith('б.'))]
            if example_b:
                js_line['example_b'] = example_b
            js.append(js_line)
            js_line = {}
        return js

    #В процессе
    def get_sql_query(self):
        query = 'INSERT INTO karamshoev VALUES (lexeme = {}, russian = {}, example_shung = {}, example_baj = {})'
        queries = []
        lexemes = self.get_shung_lex()
        description = self.get_data()
        if not lexemes:
            return
        for lex in lexemes:
            lex = "'" + lex + "'"
            russian = "'" + '; '.join([tr for tr in description if not (tr.startswith(' ш.') or tr.startswith(' б. ') or tr.startswith('ш.') or tr.startswith('б.'))]) + "'".replace('м. ', '')
            example_sh = "'" + '; '.join([ex.replace(' ш. ', '') for ex in description if ex and (ex.startswith(' ш.') or ex.startswith('ш.'))]) + "'"
            example_b = "'" + '; '.join([ex.replace(' б. ', '') for ex in description if ex and (ex.startswith(' б.') or ex.startswith('б.'))]) + "'"
            queries.append(query.format(lex, russian, example_sh, example_b))
        return queries


def to_json():
    j = []
    for line in lines:
        jso = Karamshoev_line(line).get_json()
        if jso:
            j += jso
    with open('karamshoev.json', 'w') as f:
        json.dump(j, f, indent=4, ensure_ascii=False)

def to_sql():
    for line in lines:
        print(Karamshoev_line(line).get_sql_query())

#for line in lines:
#    print(Karamshoev_line(line).get_json())
#print(set(broken_symbols))
to_json()
