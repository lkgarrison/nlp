# Luke Garrison
# chinese_test.py
# This driver program will use model.py to train an n-gram language model on the specified training data and use the language model to predict each character in the test file

import math
import argparse
from model import Model
from collections import defaultdict

parser = argparse.ArgumentParser(description='Predict next character based on previous n characters')
parser.add_argument("ngrams", type=int, help="n-grams to use in predicting next word")
parser.add_argument("training_file", type=str, help="A training file to train the model")
parser.add_argument("testing_file", type=str, help="A testing file to run against the model")
parser.add_argument("charmap", type=str, help="A file mapping chinese characters to their pronunciation")
parser.add_argument("pin", type=str, help="A file that is the simulation of what the user might type")

args = parser.parse_args()

# read in charmap file and return a dictionary of pronunciations mapped to possible symbols
def get_pronunciation_to_symbols(charmap_filename):
	with open(charmap_filename) as f:
		pronunciation_to_symbols = defaultdict(set)

		for line in f:
			symbol, pronunciation = line.split()
			pronunciation_to_symbols[pronunciation].add(symbol)

	# single characters can convert to themselves
	for key in pronunciation_to_symbols.keys():
		if len(key) == 1:
			pronunciation_to_symbols[key].add(key)

	# <space> maps to space
	pronunciation_to_symbols['<space>'].add(' ')

	return pronunciation_to_symbols


# reads in test_file as a list of lists (the inner list is a list of the characters in each line)
def get_test_file(testing_filename):
	test_file = list()
	with open(testing_filename) as f:
		for line in f:
			test_file.append([c for c in line.rstrip()])

	return test_file


# reads in the pin file and returns a list of lists (the inner list is a list of pronunciations)
def get_pin_file(pin_filename):
	pin_file = list()
	with open(pin_filename) as f:
		for line in f:
			pin_file.append(line.split())

	return pin_file


if __name__ == "__main__":
	ngrams = args.ngrams
	training_filename = args.training_file
	testing_filename = args.testing_file
	charmap_filename = args.charmap
	pin_filename = args.pin

	pronunciation_to_symbols = get_pronunciation_to_symbols(charmap_filename)
	print('characters possible for pronunciation "yi":', len(pronunciation_to_symbols['yi']))

	# initialize n-gram model on training data
	model = Model(ngrams)
	model.train(training_filename)
	print("model training complete")

	# read in both the test file and the accompanying pin file
	test_file = get_test_file(testing_filename)
	pin_file = get_pin_file(pin_filename)

	# test accuracy on testing file
	num_correct = 0;
	num_characters = 0

	for line_num in range(len(test_file)):
		model.start()

		for index in range(len(test_file[line_num])):
			test_char = test_file[line_num][index]
			pronunciation = pin_file[line_num][index]

			possible_symbols = pronunciation_to_symbols[pronunciation]

			# if pronunciation is a single symbol, that symbol is a possibility (it can be converted to itself)
			if len(pronunciation) == 1:
				possible_symbols.add(pronunciation)

			# get probability associated with each possible next char
			possibilities = dict()
			for symbol in possible_symbols:
				possibilities[symbol] = model.prob(symbol)

			# guess the char with the highest probability
			guess = max(possibilities, key=possibilities.get)

			if guess == test_char:
				num_correct += 1

			# adds char to the sliding context window
			model.read(test_char)

			num_characters += 1

	print("Accuracy: %s%%" % (round(num_correct / num_characters * 100, 2)))
