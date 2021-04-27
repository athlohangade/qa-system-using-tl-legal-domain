import os
import sys 
sys.path += ['../']
import json
from Lib.TextProcessingAndContextCreation import TextProcessingAndContextCreation
from Lib.QGPipeline import QGPipeline
from Lib.QA import QA

def get_questions_and_answers_given_the_context(context) :
    generated_questions = qg(context)    
    qas = []
    for i in range(len(generated_questions)) :
        question = generated_questions[i]['question']
        answer = qa.answer(question, context)
        ans_startindex = context.find(answer)
        ans_endindex = ans_startindex + len(answer)
        entry = {'question': question, 'answer': [{'ans_startindex': ans_startindex, 'ans_endindex': ans_endindex}]}
        qas.append(entry)

    return qas


qg = QGPipeline()
qa = QA()
legal_docs_names = os.listdir('../legal_docs/')
dataset = dict()

dataset['doccnt'] = len(legal_docs_names)
dataset['data'] = []
for i in range(len(legal_docs_names)) :
    dataset['data'].append({'title': legal_docs_names[i], 'paragraphs': []})

    legal_docs_names[i] = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname( \
        os.path.abspath(__file__))), "legal_docs", legal_docs_names[i]))

    contexts = TextProcessingAndContextCreation.get_context_chunks(legal_docs_names[i])
    for context in contexts :
        qas = get_questions_and_answers_given_the_context(context)
        dataset['data'][i]['paragraphs'].append({'context': context, 'qas': qas})




with open("dataset.json", 'w') as outfile :
    json.dump(dataset, outfile, indent=4)

# print(dataset)
