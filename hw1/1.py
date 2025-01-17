# Luke Garrison
# HW1, #1 Naive Bayes Classifier

import sys
from collections import Counter, defaultdict
from scipy.misc import logsumexp
import math
import argparse
from stemming.porter2 import stem

parser = argparse.ArgumentParser(description='Use Naive Bayes to predict which candidate said each speech')
parser.add_argument("training_file", type=str, help="A training file to train the model")
parser.add_argument("testing_file", type=str, help="A testing file to run against the model")
parser.add_argument("--stems", action='store_true', help="Uses word stems instead of raw words in model")
parser.add_argument("--no_stop_words", action='store_true', help="Ignores stop words in the model")

args = parser.parse_args()

training_filename = args.training_file
testing_filename = args.testing_file
use_stems = args.stems
no_stop_words = args.no_stop_words


# removes stop words from the given doc
def remove_stop_words(doc):
    stop_words = set(['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with'])

    return [word for word in doc if word not in stop_words]


# get counts c(k) and c(k, w) for all k
def get_counts(filename):
    # build counts for how many docs/candidate
    document_counts_per_candidate = Counter()
    # counts of each word for each candidate
    word_counts_per_candidate = defaultdict(Counter)

    with open(filename) as f:
        for doc in f:
            current_candidate = doc.split()[0]
            # update the counter for the current candidate
            document_counts_per_candidate.update({current_candidate: 1})

            doc = doc.split()[1:]

            if use_stems:
                doc = [stem(word) for word in doc]
            if no_stop_words:
                doc = remove_stop_words(doc)

            for word in doc:
                word_counts_per_candidate[current_candidate].update({word: 1})

        return (document_counts_per_candidate, word_counts_per_candidate)

    print("Error opening file: ", filename)
    exit(1)

# returns the total number of documents in the file
def get_num_docs(document_counts_per_candidate):
    num_documents = 0
    for candidate in document_counts_per_candidate:
        num_documents += document_counts_per_candidate[candidate]

    return num_documents

# returns a dictionary of p(k) for all k (all candidates)
def get_probabilies_of_candidates(document_counts_per_candidate):
    total_num_documents = get_num_docs(document_counts_per_candidate)
    candidate_probabilities = dict()

    for candidate in document_counts_per_candidate:
        candidate_probabilities[candidate] = document_counts_per_candidate[candidate] / total_num_documents

    return candidate_probabilities


# returns p(w | k) via a dictionary
# key: candidate
# value: Counter (dict)
#       key: word
#       value: probability
def get_dict_probability_word_given_candidate(word_counts_per_candidate, probability_unknown):
    dict_p_word_given_candidate = defaultdict(dict)
    for candidate in word_counts_per_candidate:
        candidate_words = word_counts_per_candidate[candidate]

        # count total words by candidate (ahead of time, for reuse)
        total_words_by_candidate = 0
        for word in candidate_words:
            total_words_by_candidate += candidate_words[word]

        # compute p(w | k) for each w said by candidate k
        for word in candidate_words:
            dict_p_word_given_candidate[candidate][word] = candidate_words[word] / total_words_by_candidate

        # add a "word" for unknown words that were not seen in the 
        # the training data
        dict_p_word_given_candidate[candidate]['<unk>'] = probability_unknown

    return dict_p_word_given_candidate


# calculate log(p(k, d)) for a given candidate and document (speech)
def get_log_p_candidate_and_doc(candidate, doc, candidate_probabilities, dict_p_word_given_candidate):
    sum_p = math.log(candidate_probabilities[candidate])

    for word in doc:
        if word in dict_p_word_given_candidate[candidate]:
            sum_p += math.log(dict_p_word_given_candidate[candidate][word])
        else:
            sum_p += math.log(dict_p_word_given_candidate[candidate]['<unk>'])

    return sum_p


# calculate p(k | d) for the specified candidate and document (speech)
def predict_candidate_given_doc(doc, candidate_probabilities, dict_p_word_given_candidate):
    # calculate this value once for reuse
    sum_prob_k_and_d = 0
    for candidate in candidate_probabilities:
        sum_prob_k_and_d += get_log_p_candidate_and_doc(candidate, doc, candidate_probabilities, dict_p_word_given_candidate)

    p_candidates = dict()
    for candidate in candidate_probabilities:
        p_candidates[candidate] = get_log_p_candidate_and_doc(candidate, doc, candidate_probabilities, dict_p_word_given_candidate)

    # find the candidate with the highest probability in the dictionary
    predicted_candidate = max(p_candidates, key=p_candidates.get)

    return predicted_candidate


def predict_candidates(test_data_file, candidate_probabilities, dict_p_word_given_candidate):
    with open(test_data_file) as f:
        total_correct = 0
        num_docs = 0
        for doc in f:
            correct_candidate = doc.split()[0]
            doc = doc.split()[1:]

            if use_stems:
                doc = [stem(word) for word in doc]
            if no_stop_words:
                doc = remove_stop_words(doc)

            num_docs += 1
            predicted_candidate = predict_candidate_given_doc(doc, candidate_probabilities, dict_p_word_given_candidate)
            if predicted_candidate == correct_candidate:
                total_correct += 1

        print("accuracy:", total_correct / num_docs * 100, "%")


# add one to the count of each word for each candidate
def add_one_smoothing(word_counts_per_candidate):
    for candidate in word_counts_per_candidate:
        candidate_word_counts = word_counts_per_candidate[candidate]
        for word in candidate_word_counts:
            candidate_word_counts[word] += 1


def get_probabily_unknown(word_counts_per_candidate):
    sum_words = 0
    for candidate in word_counts_per_candidate:
        candidate_word_counts = word_counts_per_candidate[candidate]
        for word in candidate_word_counts:
            sum_words += candidate_word_counts[word]

    return 1 / (sum_words) 



if __name__ == "__main__":
    document_counts_per_candidate, word_counts_per_candidate = get_counts(training_filename)

    # smoothing
    add_one_smoothing(word_counts_per_candidate)

    candidate_probabilities = get_probabilies_of_candidates(document_counts_per_candidate)

    probability_unknown = get_probabily_unknown(word_counts_per_candidate)

    dict_p_word_given_candidate = get_dict_probability_word_given_candidate(word_counts_per_candidate, probability_unknown)


    predict_candidates(testing_filename, candidate_probabilities, dict_p_word_given_candidate)

    # 1a
    # *********************
    # print("trump:")
    # print(document_counts_per_candidate['trump'])
    # print(word_counts_per_candidate['trump']['country'])
    # print(word_counts_per_candidate['trump']['president'])
    #
    # print("clinton")
    # print(document_counts_per_candidate['clinton'])
    # print(word_counts_per_candidate['clinton']['country'])
    # print(word_counts_per_candidate['clinton']['president'])


    # 1b
    # *********************
    # print("trump:")
    # print(candidate_probabilities['trump'])
    # print(dict_p_word_given_candidate['trump']['country'])
    # print(dict_p_word_given_candidate['trump']['president'])
    # print("clinton")
    # print(candidate_probabilities['clinton'])
    # print(dict_p_word_given_candidate['clinton']['country'])
    # print(dict_p_word_given_candidate['clinton']['president'])


