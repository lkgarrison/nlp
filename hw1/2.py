# Luke Garrison
# HW1, #2 Logistic Regression

import sys
from collections import Counter, defaultdict
from scipy.misc import logsumexp
import math
import random

if len(sys.argv) < 3:
    print("Please specify a training file and a test data file")
    print("Example usage:")
    print("python3.5 1.py <training file> <test file>")
    sys.exit(1)

training_filename = sys.argv[1]
testing_filename = sys.argv[2]

def get_list_of_candidates(training_filename):
    set_of_candidates = set()

    with open(training_filename) as f:
        for doc in f:
            set_of_candidates.add(doc.split()[0])

    return list(set_of_candidates)


# calculate s(k, d)
def s_of_k_d(model, doc, candidate):
    result = model[candidate]['<bias>']

    for word in doc:
        result += model[candidate][word]

    return result


# calculate p(k | d)
def get_p_k_given_d(model, doc, candidate):
    arr = list()
    for k in candidates:
        arr.append(s_of_k_d(model, doc, k))

    return math.exp(s_of_k_d(model, doc, candidate) - logsumexp(arr))


def get_model_accuracy(model, testing_filename):
    with open(testing_filename) as f:
        total_docs = 0
        num_predicted_correctly = 0
        for doc in f:
            actual_candidate = doc.split()[0]
            doc = doc.split()[1:]

            if total_docs == 0:
                print("p(k | d) for each candidate for first document:")

            p_candidates = dict()
            for k in candidates:
                p_candidates[k] = get_p_k_given_d(model, doc, k)
                if total_docs == 0:
                    print("\t", k, p_candidates[k])

            predicted_candidate = max(p_candidates, key=p_candidates.get)

            if actual_candidate == predicted_candidate:
                num_predicted_correctly += 1

            total_docs += 1

    return num_predicted_correctly / total_docs


def get_list_of_docs(training_filename):
    list_of_docs = list()
    with open(training_filename) as f:
        for doc in f:
            list_of_docs.append(doc)

    return list_of_docs


def get_sum_neg_log_probability_of_train(training_filename, model):
    sum_log_p = 0
    with open(training_filename) as f:
        for doc in f:
            correct_candidate = doc.split()[0]
            doc = doc.split()[1:]
            sum_log_p -= math.log(get_p_k_given_d(model, doc, correct_candidate))

    return sum_log_p


def build_model(training_filename, model):
    num_iterations = 15
    learning_rate = .07

    # get an array of the documents so the file doesn't have to be read in multiple times
    list_of_docs = get_list_of_docs(training_filename)

    for i in range(num_iterations):
        # shuffle order of docs (improves learning)
        random.shuffle(list_of_docs)

        for doc in list_of_docs:
            doc = doc.split()
            actual_candidate = doc[0]

            # add the word '<bias>' once to each document in order to calculate lambda(k)
            doc[0] = '<bias>'

            # get the p(k | d) for each candidate
            p_k_given_d_dict = dict()
            for k in candidates:
                p_k_given_d_dict[k] = get_p_k_given_d(model, doc, k)

            for word in doc:
                # train model on correct candidate
                model[actual_candidate][word] = model[actual_candidate][word] + learning_rate

                # adjust model so that it reduces the probability of selecting other candidates
                for k in candidates:
                    model[k][word] = model[k][word] - learning_rate*p_k_given_d_dict[k]

        # print out useful training stats for this iteration
        print("negative log probability of training set:", get_sum_neg_log_probability_of_train(training_filename, model))

        print("Accuracy after", i+1, "iterations is", str(100 * get_model_accuracy(model, testing_filename)) + "%")
        print()

        # slightly reduce the learning rate with each iteration
        learning_rate *= 0.9

    # output for 2b
    print("lambda(trump):", model['trump']['<bias>'])
    print("lambda(trump, country):", model['trump']['country'])
    print("lambda(trump, president):", model['trump']['president'])
    print("lambda(clinton):", model['clinton']['<bias>'])
    print("lambda(clinton, country):", model['clinton']['country'])
    print("lambda(clinton, president):", model['clinton']['president'])


if __name__ == "__main__":
    candidates = get_list_of_candidates(training_filename)
    model = defaultdict(lambda: defaultdict(float))
    build_model(training_filename, model)
