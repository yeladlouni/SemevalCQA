from gensim.corpora.wikicorpus import WikiCorpus

wiki = WikiCorpus('corpus/arwiki-latest-pages-articles.xml.bz2')


from gensim import utils

corpus = [{'id': 'doc_%i' % num, 'tokens': text}
    for num, text in enumerate(wiki.get_texts())]


from PyArabic import ArabicPreprocessor

preprocessor = ArabicPreprocessor()

class LabeledQID(object):
    def __init__(self, filename, qid):
        self.filename = filename
        self.qid = qid
    def __iter__(self):
        
        # Loading test set
        tree = etree.parse(self.filename)
        
        # {QID, Qtext} dictionary for questions
        questions = {}

 
        sentence = tree.xpath('Question[@QID=' + self.qid + ']/Qtext')[0].text
        uid = 0
        sentence = preprocessor.removeStopwords(sentence)
        tokens = preprocessor.tokenize(sentence)
        tokens = map(preprocessor.deNoise, tokens)
        devocalize_tokens = map(preprocessor.removeDiacritics, tokens)
        denoised_tokens = map(preprocessor.deNoise, devocalize_tokens)
        normalized_tokens = map(preprocessor.normalizeAlef, denoised_tokens)
        normalized_tokens = map(preprocessor.normalizeAggressive, normalized_tokens)
        lemmatized_tokens = map(preprocessor.lemmatize, normalized_tokens)

        yield LabeledSentence(words=[w for w in tokens], tags=['%s' % uid])

class LabeledQAPair(object):
    def __init__(self, filename, qid):
        self.filename = filename
        self.qid = qid
    def __iter__(self):
        
        # Loading test set
        tree = etree.parse(self.filename)
        
        # {QID, Qtext} dictionary for questions
        questions = {}

        for qapair in tree.xpath('Question[@QID=' + self.qid + ']/QApair'):
            qaid = qapair.get('QAID')
            qaquestion = qapair.xpath('QAquestion')[0].text
            qaanswer = qapair.xpath('QAanswer')[0].text
           
            qaquestion = preprocessor.removeStopwords(qaquestion)
            tokens = preprocessor.tokenize(qaquestion)
            tokens = map(preprocessor.deNoise, tokens)
            devocalize_tokens = map(preprocessor.removeDiacritics, tokens)
            denoised_tokens = map(preprocessor.deNoise, devocalize_tokens)
            normalized_tokens = map(preprocessor.normalizeAlef, denoised_tokens)
            normalized_tokens = map(preprocessor.normalizeAggressive, normalized_tokens)
            lemmatized_tokens = map(preprocessor.lemmatize, normalized_tokens)
        
            yield LabeledSentence(words=[w for w in tokens], tags=['%s' % qaid])

from gensim.models.doc2vec import LabeledSentence
from lxml import etree
from collections import OrderedDict

class LabeledQuestion(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        
        # Loading test set
        tree = etree.parse(self.filename)
        
        # {QID, Qtext} dictionary for questions
        questions = {}

        # {QID, [(QAquestion, QAanswer)]} dictionary for question/answer pairs
        pairs = {}
        qid_qaid = {}
        for question in tree.xpath('Question'):
            # construct questions dictionary
            qid = question.get('QID')
            qtext = question.xpath('Qtext')[0].text
            
            qtext = preprocessor.removeStopwords(qtext)
            tokens = preprocessor.tokenize(qtext)
            tokens = map(preprocessor.deNoise, tokens)
            devocalize_tokens = map(preprocessor.removeDiacritics, tokens)
            denoised_tokens = map(preprocessor.deNoise, devocalize_tokens)
            normalized_tokens = map(preprocessor.normalizeAlef, denoised_tokens)
            normalized_tokens = map(preprocessor.normalizeAggressive, normalized_tokens)
            lemmatized_tokens = map(preprocessor.lemmatize, normalized_tokens)
            
            yield LabeledSentence(words=[w for w in tokens], tags=['%s' % qid])

from simserver import SessionServer

service = SessionServer('tmp/')

service.train(corpus, method='lsi')


import sys

class QuestionPairSimilarity(object):

    def __iter__(self):
        
        qs = LabeledQuestion('input/SemEval2016-Task3-CQA-MD-test.xml')
        for q in qs:
            
            
            service.drop_index()
            qid = q.tags[0]
            print qid
            questions = LabeledQID('input/SemEval2016-Task3-CQA-MD-test.xml', qid)
            pairs = LabeledQAPair('input/SemEval2016-Task3-CQA-MD-test.xml', qid)

            for question in questions:
                pass

            query = [w for w in question.words]
            
            question_document = {}
            question_document['id'] = qid
            question_document['tokens'] = query
            
            #msg = repr([x.encode(sys.stdout.encoding) for x in query]).decode('string-escape')
            question_documents = []
            question_documents.append(question_document)
            service.index(question_documents)
            
            for index, pair in enumerate(pairs):
                
                qaid = pair.tags
                document = [w for w in pair.words]
                
                pair_document = {}
                pair_document['id'] = qaid[0]
                pair_document['tokens'] = document
                
                pair_documents = []
                pair_documents.append(pair_document)

                service.index(pair_documents)
                
            similarities = service.find_similar(qid)
                #msg = repr([x.encode(sys.stdout.encoding) for x in document]).decode('string-escape')
                #if len(query) > 0 and len(document) > 0:
                #     score = (model.n_similarity([w for w in query], [w for w in document]))
                #else:
                #    score = 0.0
            for qaid, score, _ in similarities:
                yield qid, qaid, score

scored_questions = QuestionPairSimilarity()

import numpy as np
from collections import defaultdict

scores = defaultdict(list)
for qid, qaid, score in scored_questions:
    scores[qid].append({'qaid': qaid, 'score':score})


percentiles = defaultdict(list)
data = []
myscores = defaultdict(lambda : defaultdict(int))
for qid in scores.keys():
    for dic in scores[qid]:
        qaid = dic['qaid']
        score = dic['score']
        data.append(score)
        myscores[qid][qaid] = dic['score']
    percentiles[qid].append(np.percentile(data, 75))
    percentiles[qid].append(np.percentile(data, 99))


#from lxml import etree
#tree = etree.parse('SemEval2016-Task3-CQA-MD-test-input-Arabic.xml')

with open('ouput/SemEval2016-Task3-CQA-MD-qa-subtaskD.xml.pred', 'w') as f:
    questions = LabeledQuestion('input/SemEval2016-Task3-CQA-MD-test.xml')
    for question in questions:
        qid = question.tags[0]
        pairs = LabeledQAPair('input/SemEval2016-Task3-CQA-MD-test.xml', qid)
        for pair in pairs:
            qaid = pair.tags[0]
            if qid <> qaid:
                relevance = 'false'
                if qid in myscores.keys():
                    score = myscores[qid][qaid]
                    if score > percentiles[qid][0]:
                        relevance = 'true'
                else:
                    score = 0
                f.write('%s\t%s\t0\t%f\t%s\n' % (qid, qaid, score, relevance))

