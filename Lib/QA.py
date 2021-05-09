#
#-----------Question Answering Module-----------
#
import torch
# from transformers import BertModelForQuestionAnswering, BertTokenizer
from transformers import AutoModelForQuestionAnswering, AutoTokenizer


class QA() :

    def __init__(self) :
        #Defining the model with the tokenizer
        # self.model_file = "bert-large-uncased"
        # self.model = BertModelForQuestionAnswering.from_pretrained(self.model_file)
        # self.tokenizer = BertTokenizer.from_pretrained("bert-large-uncased")
        self.model_file = "bert-large-uncased-whole-word-masking-finetuned-squad"
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_file)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_file)

    #Function to answer the question
    def answer(self, questions, contexts) :
        #Tokenize the question and context pair
        #Encode the words into word embeddings / encodings
        encodings = self.tokenizer(questions, contexts, padding=True)

        #processing the data to make it ready for the model
        tokens = []
        attention_masks = []
        segment_ids = []
        for input_id in encodings.input_ids:
            #Handling inputs with length greater than 512
            if(len(input_id)) > 512 :
                continue

            #generating the attention mask for each sequence
            attention_masks.append([0 if (each == 0) else 1 for each in input_id])

            #generating the token list from the token_ids for each input sequence
            for each in self.tokenizer.convert_ids_to_tokens(input_id) :
                tokens.append(each)
    
            #Creating the segment_id list to specify the segment embedding to be added to the word embedding
            #A(0) segment - Question, B(1) segment - context
            sep_index = input_id.index(self.tokenizer.sep_token_id)	          #separator token index
            num_seg_a = sep_index + 1                 			              #Segment A
            num_seg_b = len(input_id) - num_seg_a                         #Segment B
            segment_ids.append(([0]*num_seg_a + [1]*num_seg_b))

        #Running the QA model for fetching the answers 
        scores = self.model(torch.tensor(encodings.input_ids), token_type_ids=torch.tensor(segment_ids), attention_mask=torch.tensor(attention_masks));
        #Finding the most probable start and end token for the answer
        start_index = torch.argmax(scores.start_logits)
        end_index = torch.argmax(scores.end_logits)

        #If the start index is greater than the end index for the answer
        if (start_index > end_index):
            return ("<no answer>", -1, -1)
          
        #Processing the answer spanning from the start_index to the end_index
        answer = tokens[start_index]
        for i in range(start_index + 1, end_index + 1) :
            #subword token is added to the previous token to complete a word
            if tokens[i][0:2] == '##':
                answer += tokens[i][2:]
            #else add the token directly to the answer with a whitespace
            else: 
                answer += ' ' + tokens[i]

        #If BERT sends the CLS token as result, then no answer was found by the model
        if answer[:5] == "[CLS]":
            return ("<no answer>", -1, -1)

        #Returning the final answer
        span_start = encodings.token_to_chars(start_index)
        span_end = encodings.token_to_chars(end_index)
        return (answer, span_start.start, span_end.end)