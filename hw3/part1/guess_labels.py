"""
Luke Garrison
guess_labels.py

This program will naively try to guess the label for each word based on the count of each label with respect to each word
"""

import sys
import os
import argparse
from collections import defaultdict, Counter

parser = argparse.ArgumentParser(description='Guesses the label for each word in the testing file')
parser.add_argument("training_file", type=str, help="A training file to train the model")
parser.add_argument("testing_file", type=str, help="A testing file to run against the model")

args = parser.parse_args()

def get_word_label_counts(train_filename):
	# for each word, counts the number of times each label was seen
	word_label_counts = defaultdict(Counter)

	# keep track of which labels have the highest count
	label_counts = Counter()

	with open(train_filename) as f:
		for line in f:
			line = line.strip().split(' ')

			for labeled_word in line:
				word, label = labeled_word.split('/')
				word_label_counts[word]
				word_label_counts[word][label] += 1

				label_counts[label] += 1

	return (word_label_counts, label_counts)

# takes in a dictionary of words mapped to a Counter of the possible labels
# returns a dictionary of words to their most commonly associated label
def get_word_label_predictions(word_label_counts):
	word_label_predictions = dict()

	for word in word_label_counts:
		# save the most common label
		word_label_predictions[word] = word_label_counts[word].most_common(1)[0][0]

	return word_label_predictions


def test_accuracy(word_label_predictions, most_common_label, test_filename):
	total_label_count = 0
	correct_label_guesses = 0
	line_count = 0

	with open(test_filename) as f:
		for line in f:
			line = line.strip().split(' ')

			purified_sentence_list = list()

			for labeled_word in line:
				# get word and label from file
				word, label = labeled_word.split('/')
				if word in word_label_predictions:
					label_guess = word_label_predictions[word]
				else:
					# if the word has not been seen before, guess the most frequently seen label
					label_guess = most_common_label

				if label_guess == label:
					correct_label_guesses += 1

				total_label_count += 1

				if label_guess == 'N':
					purified_sentence_list.append(word)

			line_count += 1

			if line_count == 2:
				print()
				print("2nd line in testing data after being purified:")
				print(' '.join(purified_sentence_list))

	print("Accuracy:", str(correct_label_guesses/total_label_count * 100) + "%")



if __name__ == "__main__":
	train_filename = args.training_file
	test_filename = args.testing_file

	if not os.path.isfile(train_filename):
		print("Training file does not exist")
		exit(1)
	elif not os.path.isfile(test_filename):
		print("Testing file does not exist")
		exit(1)

	word_label_counts, label_counts = get_word_label_counts(train_filename)

	word_label_predictions = get_word_label_predictions(word_label_counts)
	most_common_label = max(label_counts, key=label_counts.get)

	labels_for_you = word_label_counts['you']
	num_labels_for_you = sum(labels_for_you.values())
	for label in labels_for_you:
		print("p(" + label + " | you)", "=", labels_for_you[label] / num_labels_for_you)

	test_accuracy(word_label_predictions, most_common_label, test_filename)
