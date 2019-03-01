"""Simple QT app for searching in Karamshoev and Zarubin dictionaries"""
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize    
import json

with open('karamshoev-zarubin.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

def translate(word, output='z'):
    """Translates from Karamshoev to Zarubin graphics systems

    Parameter word: str
        Word how it is in Karamshoev dictionary.
    Returns result: str
        Word how it should be in Zarubin dictionary.
    """
    if output == 'k':
        return word
    result = ''
    for sym in word:
        try:
            result += mapping[sym]
        except KeyError:
            result += sym
    return result

def fynd(word):
    """Finds the word in the dictionaries.

    Parameter word: str
        Word in Karamshoev or Zarubin graphics.
    Returns result: list
        [
            'karamshoev_data': dict({
                'russian': list of variants with examples,
                'gender': str,
            }),
            'zarubin_data': dict({
                <<example, I don't know what all this exactly is>>
                "shughni": "parwárθ",
                "easy_shughni": "parwarθ,parwuxt,parwaxt,parwarθt,parwuxč,parwixc,parwaxč,parwaxt,parwixc,parwixtow",
                "pst": "parwúx̌t",
                "pst.pl": "parwax̌t",
                "prs.3sg": "parwárθt",
                "ptcp": "parwúx̌č",
                "ptcp.f": "parwíx̌c, parwáx̌č",
                "ptcp.pl": "parwáx̌t, parwíx̌c",
                "inf": "parwix̌tṓw",
                "russian": "соскальзывать, падать в воду с меха для плавания (мало употребителен)"
                <<end example>>
            }),
            ...
        ]
    """
    word = word.lower()
    result = []
    with open('matched.json', 'r', encoding='utf-8') as f:
        js = json.load(f)
    for document in js:
        translated = translate(word)
        if document['bingo'] == 1:
            if document['lexeme'] == word or document['lexeme_z'] == word or document['lexeme_z'] == translated:
                result.append({'karamshoev_data': document['karamshoev_data'], 'zarubin_data': document['zarubin_data']})
        else:
            try:
                if document['lexeme'] == word:
                    result.append({'karamshoev_data': document['karamshoev_data'], 'zarubin_data': ''})
            except KeyError:
                if document['lexeme_z'] == word or document['lexeme_z'] == translated:
                    result.append({'karamshoev_data': '', 'zarubin_data': document['zarubin_data']})
    return result

def make_readable(search_result):
    """Makes the results human readable. Preserves only translation

    Parameter search_result: dict
        The dictionary returned by the fynd function
    Returns: str
        Karamshoev:
        1) first translation
        2) second translation
        ...

        Zarubin:
        1) first translation
        2) second translation
        ...
    """
    k = []
    z = []
    for result in search_result:
        if result['karamshoev_data']:
            k.append(';\n'.join(result['karamshoev_data']['russian']))
        if result['zarubin_data']:
            z.append(result['zarubin_data']['russian'])
    find_output = ''
    if k:
        #А что вы хотели? Это самый быстрый способ создать список с уникальными значениями.
        used = []
        k = [x for x in k if x not in used and (used.append(x) or True)]
        find_output += 'Карамшоев:\n'
        i = 1
        for el in k:
            find_output += '    ' + str(i) + ')  ' + el + '\n'
            i += 1
        find_output += '\n'
    if z:
        used = []
        z = [x for x in z if x not in used and (used.append(x) or True)]
        find_output += 'Зарубин:\n'
        i = 1
        for el in z:
            find_output += '    ' + str(i) + ')  ' + el + '\n'
            i += 1
    return find_output
            

class MainWindow(QMainWindow):
    """Class with simple QT window

    Bases on QMainWindow.
    Contains:
        name_label: a QLabel saying: 'Word:'
        line: an input QLineEdit
        button: a QPushButton that triggers the search method
        result_label: a QLabel with the search result
        search: method
            Takes line.text, processes it with fynd and make_readable functions and sets result_label to search result.
    """
    def __init__(self):
        """Initializing the window"""
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(920, 540))    
        self.setWindowTitle("Shungan Dictionaries") 

        self.name_label = QLabel(self)
        self.name_label.setText('Word:')
        self.line = QLineEdit(self)

        self.line.move(80, 20)
        self.line.resize(200, 32)
        self.name_label.move(20, 20)

        button = QPushButton('Search', self)
        button.clicked.connect(self.search)
        button.resize(200,32)
        button.move(80, 60)

        self.result_label = QLabel(self)
        self.result_label.move(80, 100)
        self.result_label.resize(800, 400)

    def search(self):
        """Finding the result"""
        search_result = fynd(self.line.text())
        find_output = make_readable(search_result)
        self.result_label.setText(find_output)
        
        

#print(len(fynd('x̌ufčak')))
#print(make_readable(fynd('йайа')))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


