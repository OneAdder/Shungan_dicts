import re
import json
from time import sleep
import sqlite3
import pandas

broken_symbols_check = {'H', '!', '7', 'R', 'B', '}', 'V', 'Ы', 'J', 'E', '́', '4', '£', 'Э', 'U', '-', '"', '„', '0', 'Ҳ', 'Щ', 'G', '*', '[', 'K', ':', '«', '^', '#', '+', 'С', 'Y', '%', '/', '_', '2', '°', '9', ')', 'S', '5', ']', '§', '>', '1', '<', 'Ё', '$', '̌', 'Я', 'Ю', '̊', '=', ';', '8', '“', 'O', '™', '\\', 'Ҙ', '?', 'P', '\xad', 'Ʒ', 'T', 'A', '6', '3', '|', '•', 'Z', '№', 'L', '(', 'D', 'I', '—', 'Q', '»', 'M', 'Ь', "'", '■', 'Х', '&', 'F', '®', '~'}

zarubin_csv = pandas.read_csv('zarubin_85-288.csv', delimiter='\t')
zarubin_lexemes = [lexeme.replace('-', '').replace('́', '') for lexeme in tuple(zarubin_csv.shughni)]
zarubin_csv = zarubin_csv.assign(lexeme=zarubin_lexemes)

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
            try:
                result += mapping[sym]
            except KeyError:
                result += sym
            #broken_symbols.append(sym)
        return result

    def get_shung_lex(self):
        line = self.line
        words = line.split()
        lexemes = [word for word in words if word.isupper() and not word.startswith('-') and not (len(word) == 2 and word.endswith(')'))]
        result = []
        for lexeme in lexemes:
            lexeme = re.sub('(\.|,| )', '', lexeme)
            lexeme = lexeme.lower()
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
        """
        """
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

            karamshoev_data = {}
            
            
            karamshoev_data['russian'] = [tr for tr in description if not (tr.startswith(' ш.') or tr.startswith(' б. ') or tr.startswith('ш.') or tr.startswith('б.'))]
            if karamshoev_data['russian']:
                if karamshoev_data['russian'][0].startswith(', '):
                    karamshoev_data['russian'][0] = karamshoev_data['russian'][0][2:]
            if gender:
                karamshoev_data['gender'] = gender[0]
            example_sh = [ex.replace(' ш. ', '') for ex in description if ex and (ex.startswith(' ш.') or ex.startswith('ш.'))]
            if example_sh:
                karamshoev_data['example_sh'] = example_sh
            example_b = [ex.replace(' б. ', '') for ex in description if ex and (ex.startswith(' б.') or ex.startswith('б.'))]
            if example_b:
                karamshoev_data['example_b'] = example_b
            
            js_line['lexeme'] = lex
            js_line['karamshoev_data'] = karamshoev_data

            zarubin_counterpart = get_zarubin_data(lex_z)
            if zarubin_counterpart:
                js_line['bingo'] = 1
                js_line['lexeme_z'] = lex_z
                js_line['zarubin_data'] = zarubin_counterpart
                if lex_z in zarubin_lexemes:
                    i = zarubin_lexemes.index(lex_z)
                    zarubin_lexemes.pop(i)
            else:
                js_line['bingo'] = 0
            
            js.append(js_line)
            js_line = {}

        
        return js

    def get_sql_query(self):
        query = "INSERT INTO karamshoev VALUES (NULL, ?, ?, ?, ?, ?, ?)"
        queries = []
        js = self.get_json()
        for line in js:
            lex = line['lexeme']
            lex_z = line['lexeme_z']
            rus = "; ".join(line["russian"])
            try:
                gender = line['gender']
            except KeyError:
                gender = ''
            try:
                example_shung = line['example_sh']
            except KeyError:
                example_shung = ''
            try:
                example_baj = line['example_b']
            except KeyError:
                example_baj = ''
            print(query)
            c.execute(query, (lex, lex_z, gender, rus, example_shung, example_baj))
            conn.commit()

def get_zarubin_data(karamshoev_lexeme):
    if karamshoev_lexeme in tuple(zarubin_csv.lexeme):
        data = zarubin_csv[zarubin_csv.lexeme == karamshoev_lexeme].to_dict()
        return prepare_zarubin_data(data)

def prepare_zarubin_data(data):
    result = {}
    keys = data.keys()
    for key in keys:
        value = tuple(data[key].values())[0]
        if isinstance(value, str) and not key == 'lexeme':
            result[key] = value
    return result

def to_json():
    j = []
    for line in lines:
        jso = Karamshoev_line(line).get_json()
        if jso:
            j += jso

    for zarubin_lexeme in zarubin_lexemes:
        doc = {}
        doc['bingo'] = 0
        doc['lexeme_z'] = zarubin_lexeme
        data = zarubin_csv[zarubin_csv.lexeme == zarubin_lexeme].to_dict()
        doc['zarubin_data'] = prepare_zarubin_data(data)
        j.append(doc)
    
    with open('matched.json', 'w') as f:
        json.dump(j, f, indent=4, ensure_ascii=False)

to_json()

'''
def to_sql():
    for line in lines:
        Karamshoev_line(line).get_sql_query()
        break
'''

#print(get_zarubin_data('lawāk'))

#for line in lines:
#    print(Karamshoev_line(line).get_json())
#print(set(broken_symbols))
"""
conn = sqlite3.connect('shungan.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS karamshoev')
conn.commit()
c.execute('''
          CREATE TABLE karamshoev (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          lexeme TEXT,
          lezeme_zarubin TEXT,
          gender TEXT,
	  lexeme_russian TEXT,
	  example_shung TEXT,
	  example_baj TEXT
	  )
          ''')
#c.execute('pragma table_info(karamshoev);')
#print(c.fetchall())
to_sql()
"""
