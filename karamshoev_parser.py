import re
import json
from time import sleep

with open('karamshoev.txt', 'r', encoding="UTF-8") as f:
    lines = f.readlines()
    lines[0] = lines[0].replace('\ufeff', '')

class Karamshoev_line(object):
    def __init__(self, line):
        self.line = line

    def get_shung_lex(self):
        line = self.line
        words = line.split()
        lexemes = [word for word in words if word.isupper() and not word.startswith('-') and not (len(word) == 2 and word.endswith(')'))]
        result = []
        for lexeme in lexemes:
            lexeme = re.sub('(\.|,| )', '', lexeme)
            if re.findall('\(.*?\)', lexeme):
                #print(lexeme)
                lexeme1 = re.sub('\(.*?\)', '', lexeme)
                lexeme2 = re.sub('(\(|\))', '', lexeme)
                result.append(lexeme1)
                result.append(lexeme2)
            else:
                result.append(lexeme)
        return result

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
        for lex in lexemes:
            #print(lex)
            gender = re.findall('м. ', description[0])
            description[0] = description[0].replace('м. ', '')
            js_line['lexeme'] = lex
            js_line['russian'] = [tr for tr in description if not (tr.startswith(' ш.') or tr.startswith(' б. '))]
            if gender:
                js_line['gender'] = gender[0]
            example_sh = [ex.replace(' ш. ', '') for ex in description if ex and ex.startswith(' ш.')]
            if example_sh:
                js_line['example_sh'] = example_sh
            example_b = [ex.replace(' б. ', '') for ex in description if ex and ex.startswith(' б.')]
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
            russian = "'" + '; '.join([tr for tr in description if not (tr.startswith(' ш.') or tr.startswith(' б. '))]) + "'".replace('м. ', '')
            example_sh = "'" + '; '.join([ex.replace(' ш. ', '') for ex in description if ex and ex.startswith(' ш.')]) + "'"
            example_b = "'" + '; '.join([ex.replace(' б. ', '') for ex in description if ex and ex.startswith(' б.')]) + "'"
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

print(to_json())
