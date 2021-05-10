#
#-----------Question Answering Module-----------
#
import torch
import numpy as np
import transformers
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
        

class QA() :

    def __init__(self) :
        #Defining the model with the tokenizer
        self.model_file = "bert-large-uncased-whole-word-masking-finetuned-squad"
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_file)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_file)
        assert isinstance(self.tokenizer, transformers.PreTrainedTokenizerFast)
        
    #Function to process a batch of contexts
    def answer_batch(self, questions, contexts, best_size=20, max_answer_length=100) :
        max_length = 480    #max length of input(question + context)
        doc_stride = 128    #length of overlap between consecutive features of the same example

        #Tokenize the question and context pair
        #Encode the words into word embeddings / encodings
        encodings = self.tokenizer(
                questions,
                contexts,
                truncation="only_second",
                max_length=max_length,
                stride=doc_stride,
                return_overflowing_tokens=True,
                return_offsets_mapping=True,
                return_attention_mask=True,
                padding="max_length"
            )
        
        #Sending the inputs to the cuda device
        cuda_device = torch.device("cuda")
        input_ids = torch.tensor(encodings.input_ids, device=cuda_device)
        token_type_ids=torch.tensor(encodings.token_type_ids, device=cuda_device)
        attention_mask=torch.tensor(encodings.attention_mask, device=cuda_device)
              
        #Running the QA model and fetching the output start and end scores of the tokens
        scores = self.model(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask);
        all_start_logits = (scores.start_logits).cpu()
        all_end_logits = (scores.end_logits).cpu()

        #Releasing the GPU Memory
        del input_ids
        del token_type_ids
        del attention_mask
        del scores

        #Finding the mapping between the features and the contexts to extract the answer from the respective context
        context_mapping = encodings.pop("overflow_to_sample_mapping")
        offset_mappings = encodings.pop("offset_mapping")
        context_features = dict()
        for i, c in enumerate(context_mapping):
            if(c not in context_features.keys()):
                context_features[c] = list()
            context_features[c].append(i)

        #Finding the best valid answers from all the features for all contexts
        best_answers = list()
        for c, context in enumerate(contexts):
            #list of valid answers in the context
            valid_answers = []
            #Feature indexes associated with the context
            feature_indices = context_features[c]

            #Looping through all features of the context
            for feature_index in feature_indices:
                # We grab the predictions of the model for this feature.
                start_logits = all_start_logits[feature_index]
                end_logits = all_end_logits[feature_index]

                #Fetching the offset mapping to find the answer in the context
                offset_mapping = offset_mappings[feature_index]

                #Finding the best best_size start and end logits.
                start_indexes = np.argsort(start_logits.detach().numpy())[-1 : -best_size - 1 : -1].tolist()
                end_indexes = np.argsort(end_logits.detach().numpy())[-1 : -best_size - 1 : -1].tolist()
                #Going through all combinations and processing all possible answers!
                for start_index in start_indexes:
                    for end_index in end_indexes:
                        # Don't consider out-of-scope answers, either because the indices are out of bounds or correspond
                        # to part of the input_ids that are not in the context.
                        if (
                            start_index >= len(offset_mapping)
                            or end_index >= len(offset_mapping)
                            or offset_mapping[start_index] is None
                            or offset_mapping[end_index] is None
                        ) : continue

                        # Don't consider answers with a length that is either < 0 or > max_answer_length.
                        if end_index < start_index or end_index - start_index + 1 > max_answer_length:
                            continue

                        #Finding the valid answer along with its score (start_logit + end_logit)
                        start_char = offset_mapping[start_index][0]
                        end_char = offset_mapping[end_index][1]
                        valid_answers.append(
                            {
                                "score": start_logits[start_index] + end_logits[end_index],
                                "text": context[start_char: end_char]
                            }
                        )
                  
            #Finding the best answer for the batch
            if len(valid_answers) > 0:
                best_answer = sorted(valid_answers, key=lambda x: x["score"], reverse=True)[0]
            #In the very rare edge case there may not be a single non-null prediction,
            #hence, we create a fake prediction to avoid failure.
            else:
                best_answer = {"text": "<no_answer>", "score": 0.0}
            best_answers.append(best_answer)

        #Returning the best batch of answers            
        return best_answers

    #Function to find the best possible answer among all contexts
    def answer(self, questions, contexts) :
        #Sending batch of 32 contexts to the model for answering
        batch_size = 32
        cnt_batches = len(contexts)//batch_size + (1 if len(contexts)%batch_size != 0 else 0)
        best_anss = []

        #Calling the cuda device to run the model for the batch
        self.model.cuda()

        for b in range(cnt_batches):
            #Clearing the cuda cache to run the incoming batch          
            torch.cuda.empty_cache()

            #predicting the best answer for the given batch
            with torch.no_grad() :
                result = self.answer_batch(questions[b*batch_size : (b+1)*batch_size], contexts[b*batch_size : (b+1)*batch_size])
            
            #appending the best batch answers to list of best answers for the question
            best_anss = best_anss + result

        #Finding the best answer among all the best batch answers
        answer = sorted(best_anss, key=lambda x: x["score"], reverse=True)[0]["text"]
        return answer
