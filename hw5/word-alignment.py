# Luke Garrison
# NLP, Homework 5
# Word Alignment

import math
import random
import itertools
import argparse
import sys
import os
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


t_f_given_e_cache = defaultdict(lambda: dict())

def get_t_f_given_e(lambda_f_given_e, chinese_word, english_word):
	if chinese_word not in t_f_given_e_cache[english_word]:
		numerator = math.exp(lambda_f_given_e[english_word][chinese_word])
		denominator = sum([math.exp(lambda_f_given_e[english_word][f]) for f in lambda_f_given_e[english_word]])
	
		t_f_given_e_cache[english_word][chinese_word] = (numerator / denominator)

	return t_f_given_e_cache[english_word][chinese_word]


def display_log_p_f_given_e_output(training_file, training_data, lambda_f_given_e):
	print("ln(P(f | e)) for the first 5 lines of", training_file)
	for index, line in enumerate(training_data):
		reset_t_f_given_e_cache()

		if index < 5:
			chinese_sentence, english_sentence = line

			log_p_f_given_e = get_log_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence)
			print('\t', log_p_f_given_e)
		else:
			break

	print()


def initialize_context(lambda_f_given_e, training_data):
	for line in training_data:
		chinese_sentence, english_sentence = line

		for word_pair in itertools.product(english_sentence, chinese_sentence):
			english_word, chinese_word = word_pair
			lambda_f_given_e[english_word][chinese_word] = 0.0

def reset_t_f_given_e_cache():
	global t_f_given_e_cache

	# reset cache of t(f | e)
	t_f_given_e_cache = defaultdict(lambda: dict())


def align_words(lambda_f_given_e, training_file, alignments_output_file):
	training_data = get_training_data(training_file)
	print('The alignments for the first five lines:')

	with open(alignments_output_file, 'w') as alignments_outfile:
		# for each sentence
		for index, line in enumerate(training_data):
			chinese_sentence, english_sentence = line

			alignment_list = list()
			for j, chinese_word in enumerate(chinese_sentence):
				max_t_f_given_e = -1.0
				most_likely_english_word_index = None
				for i, english_word in enumerate(english_sentence):
					t_f_given_e = get_t_f_given_e(lambda_f_given_e, chinese_word, english_word)
					if t_f_given_e > max_t_f_given_e:
						max_t_f_given_e = t_f_given_e
						most_likely_english_word_index = i

				# write out the predicted alignmnet
				if most_likely_english_word_index > 0:
					# alignments_outfile.write(str(j) + '-' + str(most_likely_english_word_index-1))
					alignment_list.append(str(j) + '-' + str(most_likely_english_word_index-1))

					if j < len(chinese_sentence) - 1:
						alignment_list.append(' ')

			alignments_outfile.write(''.join(alignment_list) + '\n')

			if index < 5:
				print(''.join(alignment_list))



def train_model(training_file):
	training_data = get_training_data(training_file)
	lambda_f_given_e = defaultdict(lambda: defaultdict(lambda: float()))

	display_log_p_f_given_e_output(training_file, training_data, lambda_f_given_e)

	initialize_context(lambda_f_given_e, training_data)

	num_iterations = 15

	for iteration in range(1, num_iterations + 1):
		learning_rate = 1 / iteration
		log_likelihood = 0

		# shuffle order of docs (improves learning)
		random.shuffle(training_data)

		# for each sentence
		for index, line in enumerate(training_data):
			if index % 400 == 0:
				reset_t_f_given_e_cache()

			chinese_sentence, english_sentence = line

			log_likelihood += get_log_p_f_given_e(lambda_f_given_e, chinese_sentence, english_sentence)

			for j in range(1, len(chinese_sentence)):
				chinese_word = chinese_sentence[j]
				# calculate Z
				Z = sum([get_t_f_given_e(lambda_f_given_e, chinese_word, eng_word) for eng_word in english_sentence])

				for l in range(0, len(english_sentence)):
					english_word = english_sentence[l]
					p = get_t_f_given_e(lambda_f_given_e, chinese_word, english_word) / Z
					lambda_f_given_e[english_word][chinese_word] += (learning_rate * p)

					for f in lambda_f_given_e[english_word]:
						lambda_f_given_e[english_word][f] -= (learning_rate * p * get_t_f_given_e(lambda_f_given_e, f, english_word))


		print("iteration", iteration, '  log-likelihood:', log_likelihood)

		reset_t_f_given_e_cache()
		print('t("绝地 | jedi") =', get_t_f_given_e(lambda_f_given_e, '绝地', 'jedi'))
		print('t("机械人 | droid") =', get_t_f_given_e(lambda_f_given_e, '机械人', 'droid'))
		print('t("原力 | force") =', get_t_f_given_e(lambda_f_given_e, '原力', 'force'))
		print('t("原虫 | midi-chlorians") =', get_t_f_given_e(lambda_f_given_e, '原虫', 'midi-chlorians'))
		print('t("你 | yousa") =', get_t_f_given_e(lambda_f_given_e, '你', 'yousa'))
		print()

	return lambda_f_given_e


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Word alignment between Chinese and English translations of Star Wars. Uses unsupervised learning and stochastic gradient descent to predict the English word that each Chinese word corresponds to')
	parser.add_argument("training_file", type=str, help="A training file to train the model")
	parser.add_argument("alignments_output_file", type=str, help="A file to write the predicted alignments to")

	args = parser.parse_args()
	training_file = args.training_file
	alignments_output_file = args.alignments_output_file

	if not os.path.isfile(training_file):
		print("Training file does not exist")
		sys.exit(1)

	lambda_f_given_e = train_model(training_file)
	align_words(lambda_f_given_e, training_file, alignments_output_file)

