#Evaluation Metric Function
import re
from collections import Counter

#Function to compute the Accuracy and the F1 score
#Predictions -> Predictions by the model
#References -> Reference items, to compare with the predictions
def compute(predictions, references):
    predictions_score = 0
    common_cnt = 0
    predicted_cnt = 0
    reference_cnt = 0
    sample_pred = list(predictions)
    sample_ref = list(references)
    class_cnt = [0, 0, 0, 0, 0]

    for i in range(len(references)) :
        #Converting all the lower case
        sample_ref[i] = sample_ref[i].lower()
        sample_pred[i] = sample_pred[i].lower()

        #Removing the punctuations
        sample_ref[i] = re.sub(r'[^\w\s]', ' ', sample_ref[i])
        sample_pred[i] = re.sub(r'[^\w\s]', ' ', sample_pred[i])

        #Fetching the individual tokens
        sample_ref[i] = sample_ref[i].split()
        sample_pred[i] = sample_pred[i].split()

        #Finding the number of common words between the predicted item and the reference item
        cnt_common = sum(( Counter(sample_ref[i]) & Counter(sample_pred[i]) ).values())

        #Evaluating the difference counts for f1 measurement
        common_cnt += cnt_common
        predicted_cnt += len(sample_pred[i])
        reference_cnt += len(sample_ref[i])
        #Evaluating the match fraction of the prediction with the reference
        match_ratio = cnt_common / len(sample_ref[i])

        #Evaluating the scores based on the amount of match
        if match_ratio >= 0.25 and match_ratio < 0.5 :
            predictions_score += 1
            class_cnt[1] += 1
        elif match_ratio >= 0.5 and match_ratio < 0.75 :
            predictions_score += 2
            class_cnt[2] += 1
        elif match_ratio >= 0.75 and match_ratio < 1 :
            predictions_score += 3
            class_cnt[3] += 1
        elif match_ratio == 1 :
            predictions_score += 4
            class_cnt[4] += 1
        else :
            class_cnt[0] += 1

    #Total score for references
    reference_score = 4 * len(sample_ref)

    #Various Evaluation Metrics
    accuracy = predictions_score / reference_score * 100
    precision = common_cnt / predicted_cnt
    recall = common_cnt / reference_cnt
    F1 = ((2 * precision * recall) / (precision + recall)) * 100

    #Sending the result
    metric = dict()
    metric['accuracy'] = accuracy
    metric['precision'] = precision
    metric['recall'] = recall
    metric['f1'] = F1
    metric['class_cnt'] = class_cnt
    return metric
