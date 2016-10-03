# Luke Garrison
# english_test.py
# This driver program will use model.py to train an n-gram language model on the specified training data and use the language model to predict each character in the test file

import argparse
from model import Model

parser = argparse.ArgumentParser(description='Predict next character based on previous n characters')
parser.add_argument("ngrams", type=int, help="n-grams to use in predicting next word")
parser.add_argument("training_file", type=str, help="A training file to train the model")
parser.add_argument("testing_file", type=str, help="A testing file to run against the model")

args = parser.parse_args()

if __name__ == "__main__":
	ngrams = args.ngrams
	training_filename = args.training_file
	testing_filename = args.testing_file

	# initialize n-gram model on training data
	model = Model(ngrams)
	model.train(training_filename)
	print("model training complete")

	# test accuracy on testing file
	num_correct = 0;
	num_guesses = 0

	with open(testing_filename) as f:
		for doc in f:
			model.start()

			for c in doc:
				# get probability associated with each possible next char
				possibilities = model.probs()

				# guess the char with the highest probability
				guess = max(possibilities, key=possibilities.get)

				if guess == c:
					num_correct += 1

				# adds char to the sliding context window
				model.read(c)

				num_guesses += 1

	print("Accuracy: %s%%" % (round(num_correct / num_guesses * 100, 2)))
