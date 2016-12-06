 # coding=UTF-8
import re
import codecs
from nltk.corpus import stopwords

class ArabicPreprocessor(object):
    regex_noise = ur'[^ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهويى0-9a-zA-Z ]'
    regex_diacritics = ur'[ًٌٍَُِّْـ]'
    regex_alef = ur'[ي]'
    regex_light = ur'[آأإ]'
    regex_aggressive = ur'[ءآأؤإئ]'
    regex_tokens = ur'[\s،\"\'\.\*!؟\(\)\[\]\{\},\\\\#\$\^%&\-\+;=_~\|\?]+'
    regex_lemmas = ur'^([وفب]ال|[بيلمتوسن]ت|[بلوكف]م|[ال]ل|[ولسف]ي|[وفلب]ا|)(.+?)(ات|وا|تا|ون|وه|ان|تي|ته|تم|كم|ه[نم]|ها|ية|تك|نا|ي[نه]|[ةهيا]|)$'
    
    stopwords_list = []
    #with codecs.open('stopwords.txt', encoding='utf-8') as f:
    #    stopwords_list.append(f.readline())

    stopwords_list += stopwords.words('arabic')
    stopwords_list = set(stopwords_list)
    
    regex_stopwords = r'\b(' + r'|'.join(stopwords_list) + r')\b\s*'


    def deNoise(self, word):
        p = re.compile(self.regex_noise, re.U)
        return p.sub(u'', word)
    def removeDiacritics(self, word):
        p = re.compile(self.regex_diacritics, re.U)
        return p.sub(u'', word)
    def normalizeAlef(self, word):
        p = re.compile(self.regex_alef, re.U)
        return p.sub(u'ى', word)
    def normalizeLight(self, word):
        p = re.compile(self.regex_light, re.U)
        return p.sub(u'ا', word)
    def normalizeAggressive(self, word):
        p = re.compile(self.regex_aggressive, re.U)
        return p.sub(u'ا', word)
    def tokenize(self, text):
        p = re.compile(self.regex_tokens, re.U)
        return p.split(text)
    def lemmatize(self, word):
        p = re.compile(self.regex_lemmas, re.U)
        match = p.search(word)
        if match:
            return match.group(2)
        else:
            return word
    def removeStopwords(self, text):
        p = re.compile(self.regex_stopwords, re.U)
        return p.sub('', text)

    def transliterate(self, text):
        converted_text = text
        buckwalterMod = {
            'ء': 'c', 'ا': 'A', 'إ': 'A',
            'أ': 'A', 'آ': 'A', 'ب': 'b',
            'ة': 'o', 'ت': 't', 'ث': 'v',
            'ج': 'j', 'ح': 'H', 'خ': 'x',
            'د': 'd', 'ذ': 'V', 'ر': 'r',
            'ز': 'z', 'س': 's', 'ش': 'E',
            'ص': 'S', 'ض': 'D', 'ط': 'T',
            'ظ': 'Z', 'ع': 'C', 'غ': 'g',
            'ف': 'f', 'ق': 'q', 'ك': 'k',
            'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'ؤ': 'c', 'و': 'w',
            'ى': 'y', 'ئ': 'c', 'ي': 'y',
        }
        for k, v in buckwalterMod.items():
            converted_text = re.sub(k, v, converted_text)
        return(converted_text)