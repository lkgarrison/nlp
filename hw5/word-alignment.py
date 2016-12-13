# Luke Garrison
# NLP, Homework 5
# Word Alignment

import math
import itertools
from collections import defaultdict

ENGLISH_FIRST_WORD = 'NULL'

def get_training_data(training_file):
	""" returns the training file as a list of lines """
	data = list()
	with open(training_file) as f:
		for line in f:
			line = line.strip()
			chinese_sentence, english_sentence = line.split('\t')
			chinese_sentence = chinese_sentence.split(' ')
			english_sentence = english_sentence.split(' ')

			# add NULL as the first word of each english sentence
			english_sentence.insert(0, ENGLISH_FIRST_WORD)

			data.append((chinese_sentence, english_sentence))

	return data


def get_log_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence):
	return math.log(get_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence))


def get_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence):
	""" compute p(f | e) using the forward algorithm"""

	m = len(chinese_sentence)
	l = len(english_sentence)

	forward = defaultdict(lambda: float())
	forward[0] = 1
	
	for j in range(1, m + 1):
		forward[j] = 0

		for i in range(1, l + 1):
			forward[j] += (forward[j - 1] * ((1 / (l + 1)) * get_t_f_given_e(lambda_f_given_e, chinese_sentence[j - 1], english_sentence[i - 1])))

	forward[m] *= 1/100

	return forward[m]


def get_t_f_given_e(lambda_f_given_e, chinese_word, english_word):
	numerator = math.exp(lambda_f_given_e[english_word][chinese_word])
	denominator = sum([math.exp(lambda_f_given_e[english_word][f]) for f in lambda_f_given_e[english_word]])

	return numerator / denominator


def display_log_p_f_given_e_output(training_file, training_data, lambda_f_given_e):
	print("ln(P(f | e)) for the first 5 lines of", training_file)
	for index, line in enumerate(training_data):
		if index <= 5:
			chinese_sentence, english_sentence = line

			log_p_f_given_e = get_log_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence)
			print('\t', log_p_f_given_e)

	print()


def train_model(training_file):
	training_data = get_training_data(training_file)
	lambda_f_given_e = defaultdict(lambda: defaultdict(lambda: float()))

	display_log_p_f_given_e_output(training_file, training_data, lambda_f_given_e)


if __name__ == '__main__':
	train_model('data/episode1.zh-en')

