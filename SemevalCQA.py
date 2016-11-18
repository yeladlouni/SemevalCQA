import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from lxml import etree
from collections import OrderedDict


# Loading test set

tree = etree.parse("SemEval2016-Task3-CQA-MD-test.xml")

# {QID, Qtext} dictionary for questions
questions = {}

# {QID, [(QAquestion, QAanswer)]} dictionary for question/answer pairs
pairs = {}
qid_qaid = {}
for question in tree.xpath('Question'):
    # construct questions dictionary
    qid = question.get('QID')
    qtext = question.xpath('Qtext')[0].text
    questions[qid] = qtext
    
    qapairs = []
    qid_qaid[qid] = []
    #construct {question, answer} pairs
    for qapair in question.xpath('QApair'):
        qaid = qapair.get('QAID')
        qaquestion = qapair.xpath('QAquestion')[0].text
        qaanswer = qapair.xpath('QAanswer')[0].text
        
        qapairs.append((qaquestion, qaanswer))
        qid_qaid[qid].append(qaid)
        
        pairs[qid] = qapairs
		
import nltk


# construct a stemmer using ISRI from nltk
stemmer = nltk.stem.isri.ISRIStemmer()

# construct a list of stopwords by concatenating both Khoja and ISRI
khoja_stopwords = []
khoja_stopword_file = open('stopwords.txt')

for word in khoja_stopword_file.readlines():
    khoja_stopwords.append(word)

stoplist = khoja_stopwords + stemmer.stop_words

# tokenize question using the stemmer and the stoplist constructed above
processed_questions = dict([(qid,list(set([stemmer.stem(token) # stemming
                                      for token in question.split() #tokenization
                                      if token not in stoplist]))) #removal of stopword list
                            for qid,question in questions.iteritems()])
							
processed_qaquestion = dict([(qid, [list(set([stemmer.stem(question_token) 
                                 for question_token in question.split()
                                 if question_token not in stoplist]))
                               for question, _ in pair]) 
                        for qid, pair in pairs.iteritems()])
						
processed_qaanswer = dict([(qid, [list(set([stemmer.stem(answer_token) 
                                 for answer_token in answer.split()
                                 if answer_token not in stoplist]))
                               for _, answer in pair]) 
                        for qid, pair in pairs.iteritems()])
						
from gensim import corpora

#generating dict files for QAquestions
for qid in processed_qaquestion.keys():
    dictionary = corpora.Dictionary(processed_qaquestion[qid])
    dictionary.save('data/qaquestions/' + qid + ".dict")

#generating Market Matrix 'MM' files for QAquestions
for qid in processed_qaquestion.keys():
    corpus = [dictionary.doc2bow(text) for text in processed_qaquestion[qid]]
    corpora.MmCorpus.serialize('data/qaquestions/'+qid+'.mm', corpus)
	
from gensim import similarities
from gensim import models

#creating models for each QAquestion

corpus_tfidf = {}
sims = {}
for qid in processed_qaquestion.keys():
    dictionary =  corpora.Dictionary.load('data/qaquestions/'+qid+'.dict')
    corpus = corpora.MmCorpus('data/qaquestions/'+qid+'.mm')
    
    #generate tfidf model for each QAquestion
    model = models.TfidfModel(corpus)
    model.save('data/qaquestions/'+qid+'.tfidf')
    corpus_tfidf[qid] = model[corpus]
 
    lsi = models.LsiModel(corpus, num_topics=30)
    
    query = processed_questions[qid]
    
    query_tokens = list(set([token for token in query if token not in stoplist]))
  
    vec_bow = dictionary.doc2bow(query_tokens)
    vec_tfidf = model[vec_bow]
    #vec_lsi = model[vec_bow]
    vec_lsi = lsi[vec_bow]

    index = similarities.MatrixSimilarity(lda[corpus])
    index.save('data/qaquestions/'+qid+'.index')
    
    sims[qid] = index[vec_lda]
    
    sims[qid] = sorted(zip(qid_qaid[qid],sims[qid]), key=lambda item: -item[1])

with open('results.csv', 'w') as results:
    for qid in processed_questions.keys():
        i = 1
        for qaid,score in sims[qid]:
            results.write(qid + ';' + qaid + ';' + str(i) + ';' + str(score) + ';' + ('true' if i <= 6 else 'false') + '\n')
            i += 1
