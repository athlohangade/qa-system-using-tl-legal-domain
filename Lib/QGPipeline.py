import itertools

from nltk import sent_tokenize

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

PIPELINE_SETTINGS = {
    #"model": "valhalla/t5-base-qg-hl",
    "model": "mrm8488/t5-base-finetuned-question-generation-ap",
    "ans_model": ["valhalla/t5-base-qa-qg-hl"] 
}

class QGPipeline:

    def __init__(self, pipeline_settings: dict = PIPELINE_SETTINGS, use_cuda: bool = True) :

        self.model = AutoModelForSeq2SeqLM.from_pretrained(pipeline_settings['model'])
        self.tokenizer = AutoTokenizer.from_pretrained(pipeline_settings['model'], use_fast=False)

        self.ans_model = []
        self.ans_tokenizer = []
        for i in range(len(pipeline_settings['ans_model'])) :
            self.ans_model.append(AutoModelForSeq2SeqLM.from_pretrained(pipeline_settings['ans_model'][i]))
            self.ans_tokenizer.append(AutoTokenizer.from_pretrained(pipeline_settings['ans_model'][i], use_fast=False))

        self.device = "cuda" if torch.cuda.is_available() and use_cuda else "cpu"
        self.model.to(self.device)

        for i in range(len(self.ans_model)) :
            if self.ans_model[i] is not self.model:
                self.ans_model[i].to(self.device)

    def __call__(self, text : str):
        input_text = " ".join(text.split())
        answers = self._extract_answers(input_text)
        # print(sents)
        # print(answers)
        if len(answers) == 0:
          return []

        questions = self._generate_questions(answers, input_text)
        question_answers_list = []
        for question, answer in zip(questions, answers) :
            question_answers_list.append({'question': question, 'answer': answer})
        return question_answers_list

    def _extract_answers(self, context):
        inputs = self._prepare_inputs_for_ans_extraction(context)
        inputs = self._tokenize(inputs, padding=True, truncation=True)

        answers = []
        for i in range(len(self.ans_model)) :
            outs = self.ans_model[i].generate(
                input_ids=inputs['input_ids'].to(self.device), 
                attention_mask=inputs['attention_mask'].to(self.device), 
                max_length=32,
            )
            
            dec = [self.ans_tokenizer[i].decode(ids, skip_special_tokens=False) for ids in outs]
            decoded_output = [item.split('<sep>') for item in dec]
            decoded_output = [i[0] for i in decoded_output]
            answers.extend(decoded_output)
        
        for i in range(len(answers)) :
            answers[i] = answers[i].replace("<pad> ", "")

        answers = list(set(answers))
        return answers
 
    def _prepare_inputs_for_ans_extraction(self, text):
        sents = sent_tokenize(text)

        inputs = []
        for i in range(len(sents)):
            source_text = "extract answers:"
            for j, sent in enumerate(sents):
                if i == j:
                    sent = "<hl> %s <hl>" % sent
                source_text = "%s %s" % (source_text, sent)
                source_text = source_text.strip()
            
            source_text = source_text + " </s>"
            inputs.append(source_text)

        return inputs
  
    def _tokenize(self, inputs, padding=True, truncation=True, add_special_tokens=True, max_length=512):
        inputs = self.ans_tokenizer[0].batch_encode_plus(
            inputs, 
            max_length=max_length,
            add_special_tokens=add_special_tokens,
            truncation=truncation,
            padding="max_length" if padding else False,
            pad_to_max_length=padding,
            return_tensors="pt"
        )
        return inputs
    
    def _generate_questions(self, answers, context):
        questions = []
        for answer in answers :
            input_text = "answer: %s  context: %s </s>" % (answer, context)
            inputs = self._tokenize([input_text], padding=True, truncation=True)
        
            outs = self.model.generate(
                input_ids=inputs['input_ids'].to(self.device), 
                attention_mask=inputs['attention_mask'].to(self.device), 
                max_length=64,
                num_beams=4,
            )
            questions.extend([self.tokenizer.decode(ids, skip_special_tokens=True) for ids in outs])

        for i in range(len(questions)) :
            questions[i] = questions[i].replace("question: ", "")

        return questions
