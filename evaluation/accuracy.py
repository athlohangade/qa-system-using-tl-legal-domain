import re
from collections import Counter

def calculate_accuracy(true, predictions) :

    predictions_score = 0
    true_score = 0

    for i in range(len(true)) :
        true[i] = true[i].lower()
        predictions[i] = predictions[i].lower()

        true[i] = re.sub(r'[^\w\s]', '', true[i])
        predictions[i] = re.sub(r'[^\w\s]', '', predictions[i])

        true[i] = true[i].split()
        predictions[i] = predictions[i].split()

        match_len = len(list((Counter(true[i]) & Counter(predictions[i])).elements())) 
        match_ratio = match_len / len(true[i])

        if match_ratio >= 0.25 and match_ratio < 0.5 :
            predictions_score += 1
        elif match_ratio >= 0.5 and match_ratio < 0.75 :
            predictions_score += 2
        elif match_ratio >= 0.75 and match_ratio < 1 :
            predictions_score += 3
        elif match_ratio == 1 :
            predictions_score += 4

    true_score = 4 * len(true)
    accuracy = predictions_score / true_score
    return accuracy


if __name__ == '__main__' :

    true = ['My , name is Atharva', 'I like to play football.']
    predictions = ['My ; name is Vishal', 'I like tennis;']
    acc = calculate_accuracy(true, predictions)
    print(acc)