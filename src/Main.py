# Import required libraries
import sys
sys.path += ['./']
from Lib.TextProcessingAndContextCreation import TextProcessingAndContextCreation
from Lib.QGPipeline import QGPipeline
from Lib.QA import QA

class Main :

    # Instantiate the models
    qg = QGPipeline()
    qa = QA()

    @classmethod
    def get_contexts_given_the_doc(cls, doc_name) :

        # Call the backend to generate the contexts
        contexts = TextProcessingAndContextCreation.get_context_chunks(doc_name)
        return contexts


    @classmethod
    def get_questions_given_the_contexts(cls, context_list) :

        generated_questions_and_contexts = []

        # Do the following for each context
        for context in context_list :
            # Generate the questions
            questions = cls.qg(context)
            # Append the generated questions along with its context to the list
            for j in questions :
                generated_questions_and_contexts.append([j['question'], context])

        return generated_questions_and_contexts


    @classmethod
    def get_answer_given_the_question_and_context_list(cls, question_context_list) :

        answers = []
        # Get the answers. Return only the answer text
        for i in question_context_list :
            answers.append(cls.qa.answer([i[0]], [i[1]])[0])

        return answers


    @classmethod
    def get_answer_for_single_question_given_context_list(cls, question, context_list) :

        # Duplicate the questions number of contexts times (required for the backend)
        repeated_question_list = [question] * len(context_list)
        # Get the answers, its corresponding context and the confidence value of the answer
        answer = cls.qa.answer(repeated_question_list, context_list)
        return answer