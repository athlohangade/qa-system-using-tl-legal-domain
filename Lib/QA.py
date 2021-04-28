#Importing ML Modules
import torch
#Importing the QA BERT Class and BERT Tokenizer
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

class QA() :
    def __init__(self) :
        #Defining the model with the tokenizer
        self.model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def answer(self, question, context) :
        #Tokenize the Question and the context
        #Concatenate the question and and context and add the special tokens
        #Encode the words into word embeddings
        input_ids = (self.tokenizer).encode(question, context)

        # If token sequence length is greater than 512
        if len(input_ids) > 512 :
            return ""

        #Converting the token_ids back to tokens to print the answer at the end
        tokens = (self.tokenizer).convert_ids_to_tokens(input_ids)

        #Creating the segment_id list to specify the segment embedding to be added to the word embedding
        #A(0) segment - Question, B(1) segment - Answer Ref Text
        sep_index = input_ids.index((self.tokenizer).sep_token_id)	#separator token index
        num_seg_a = sep_index + 1                 			#Segment A
        num_seg_b = len(input_ids) - num_seg_a    			#Segment B
        segment_ids = [0]*num_seg_a + [1]*num_seg_b  

        #Running the model on the given question and answer ref text, specifying the segment_ids alongside
        #Fetching the start and end scores after taking dot product with the start and end vectors
        scores = self.model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))
        start_scores = scores.start_logits
        end_scores = scores.end_logits  

        #Find the token index with the maximum start and end score by applying softmax activation (argmax function)
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)

        #If the start index is more than the end index
        if(start_index > end_index) :
            return "No answer"

        #Processing the subword characters added by BERT to get a well organised answer
        answer = tokens[start_index]
        for i in range(start_index + 1, end_index + 1):
            #subword token is added to the previous token to complete a word
            if tokens[i][0:2] == '##':
                answer += tokens[i][2:]

                #else add the token directly to the answer with a whitespace
            else:
                answer += ' ' + tokens[i]

        # If the answer is not found
        if answer == "[CLS]" :
            answer = "(Answer Not Found!)"

        #returning the answer
        return answer
