import sys
sys.path += ['./']
from Lib.TextProcessingAndContextCreation import TextProcessingAndContextCreation
from Lib.QGPipeline import QGPipeline
from Lib.QA import QA

class Main :

    qg = QGPipeline()
    qa = QA()

    @classmethod
    def get_questions_and_contexts_given_the_doc(cls, doc_name) :

        contexts = TextProcessingAndContextCreation.get_context_chunks(doc_name)
        generated_questions_and_contexts = []
        for i in contexts :
            questions = cls.qg(i)
            for j in questions :
                generated_questions_and_contexts.append([j['question'], i])

        return generated_questions_and_contexts

    @classmethod
    def get_answer_given_the_question_and_context_list(cls, question_context_list) :

        answers = []
        for i in question_context_list :
            answers.append(cls.qa.answer(i[0], i[1]))

        return answers



