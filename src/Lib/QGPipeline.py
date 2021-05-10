import itertools

from nltk import sent_tokenize

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Model for question generation and answer extraction
PIPELINE_SETTINGS = {
    #"model": "valhalla/t5-base-qg-hl",
    "model": "mrm8488/t5-base-finetuned-question-generation-ap",    # Question Generation model
    "ans_model": ["valhalla/t5-base-qa-qg-hl"]                      # List of Ans extraction models. We can add more than one.
}

class QGPipeline:

    def __init__(self, pipeline_settings: dict = PIPELINE_SETTINGS, use_cuda: bool = True) :

        # Define the models and tokenizer
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

        # Split the input string into list of words and join them back using space
        # to get rid off unwanted characters like newline, tab, trailing spaces
        input_text = " ".join(text.split())
        # Extract possible answer spans from the input text
        answers = self._extract_answers(input_text)
        # If no possible answer span is found, return empty list
        if len(answers) == 0:
          return []

        # Generate the questions given the list of answer spans and input context
        questions = self._generate_questions(answers, input_text)
        # Form a list of question and their answers and return it
        question_answers_list = []
        for question, answer in zip(questions, answers) :
            question_answers_list.append({'question': question, 'answer': answer})
        return question_answers_list


    def _extract_answers(self, context):

        # Prepare inputs for answer extraction.
        # Each input is of the form "s1 s2 si <hl> ans_sent <hl> sj sn". Here
        # 'si' represents ith sentence.
        inputs = self._prepare_inputs_for_ans_extraction(context)
        # Tokenize the inputs, i.e. convert the alphanumeric tokens to numeric token_ids
        inputs = self._tokenize(inputs, padding=True, truncation=True)

        # Pass the inputs to every ans model for extracting answers.
        answers = []
        for i in range(len(self.ans_model)) :
            # Run the model
            # Pass the input ids to the model and attention mask that represents
            # whether the token is the actual content token or the padded token
            # Maximum answer length considered is 64
            outs = self.ans_model[i].generate(
                input_ids=inputs['input_ids'].to(self.device),
                attention_mask=inputs['attention_mask'].to(self.device),
                max_length=64,
            )

            # Decode the model output, i.e. convert back ids to words
            # Don't skip the special tokens, as we need them to explicitly separate
            # the actual answer and the padding tokens present in the output
            dec = [self.ans_tokenizer[i].decode(ids, skip_special_tokens=False) for ids in outs]
            decoded_output = [item.split('<sep>') for item in dec]
            decoded_output = [i[0] for i in decoded_output]
            answers.extend(decoded_output)

        # Delete the <pad> tokens in the answers
        for i in range(len(answers)) :
            answers[i] = answers[i].replace("<pad> ", "")
        # Delete any duplicate answers if any and return the list of answers
        answers = list(set(answers))
        return answers


    def _prepare_inputs_for_ans_extraction(self, text):

        # Divide the paragraph into sentences using nltk's recommended sentence tokenizer
        # Default one is Punkt Tokenizer
        sents = sent_tokenize(text)

        # For each sentence in the paragraph, highlight that sentence using <hl>
        # markers to tell the ans extraction model that which sentence of the para
        # should be focused for extracting the answer.
        inputs = []
        for i in range(len(sents)) :
            # Append the text 'extract answers' to each sample
            source_text = "extract answers:"
            for j, sent in enumerate(sents):
                # Highlight the required sentence in each iteration
                if i == j:
                    sent = "<hl> %s <hl>" % sent
                # Keep on appending the sentences to the input sample para.
                source_text = "%s %s" % (source_text, sent)
                source_text = source_text.strip()

            # Add the end marker </s> denoting the end of sample.
            source_text = source_text + " </s>"
            inputs.append(source_text)

        # Return the samples
        return inputs


    def _tokenize(self, inputs, padding=True, truncation=True, add_special_tokens=True, max_length=512):

        # Main tokenizer function to convert tokens to their corresponding token_ids.
        # Padding means to bring the inputs of variable length to the same length (generally)
        # equal to the length of largest input) by appending the required number of
        # pad tokens to the sentences.
        # Here maximum length consider is 512 tokens
        # Add_special_tokens means to allow converting tokens like <hl>, </s>, etc.
        # into their token_ids, though they are not actual text content tokens.
        # Truncation allowed if the input is greater than 512
        # Return value is the tensor matrix.
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

        # For each answer in the answer list, generate the question by passing every
        # sample through the model.
        questions = []
        for answer in answers :
            # Prepare the input having the form :
            # "answer: 'ans_text'  context: 'context_text'"
            input_text = "answer: %s  context: %s </s>" % (answer, context)
            # Tokenize the inputs, i.e. convert the alphanumeric tokens to numeric token_ids
            inputs = self._tokenize([input_text], padding=True, truncation=True)

            # Generate the questions
            # Maximum question length is 64
            # About num_beams, read here-> https://huggingface.co/blog/how-to-generate#beam-search
            outs = self.model.generate(
                input_ids=inputs['input_ids'].to(self.device),
                attention_mask=inputs['attention_mask'].to(self.device),
                max_length=64,
                num_beams=4,
            )
            # Decode the output. We can skip the special tokens as there are no padding
            # tokens present in the ouput, as the output is just a single sentence
            # Add the question to the questions list
            questions.extend([self.tokenizer.decode(ids, skip_special_tokens=True) for ids in outs])

        # Remove the 'question: ' token present in the output
        for i in range(len(questions)) :
            questions[i] = questions[i].replace("question: ", "")
        # Return the questions list
        return questions
