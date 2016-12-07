"""
Luke Garrison
hmm-viterbi.py

"""

import sys
import os
import math
import argparse
from collections import defaultdict, Counter

parser = argparse.ArgumentParser(description='Guesses the label for each word in the testing file utilizing a 1st order hidden markov model and the Verterbi algorithm')
parser.add_argument("training_file", type=str, help="A training file to train the model")
parser.add_argument("testing_file", type=str, help="A testing file to run against the model")

args = parser.parse_args()


# convert tag counts to probabilities
# input: dictionary of dictionaries where outter dictionary's key is the current tag
#   and the inner key is the preceeding tag and the value is the count of that tag
def convert_counts_to_probabilities(tprime_given_t_counts):
	p_tprime_given_t = defaultdict(lambda: defaultdict(lambda: 0.0))

	for current_tag in tprime_given_t_counts:
		preceeding_tag_counts = tprime_given_t_counts[current_tag]
		num_preceeding_tags_for_current_tag = sum(preceeding_tag_counts.values())

		for preceeding_tag in preceeding_tag_counts:
			p_tprime_given_t[current_tag][preceeding_tag] = preceeding_tag_counts[preceeding_tag] / num_preceeding_tags_for_current_tag

	return p_tprime_given_t


# for each tag, return the probability of tag X preceding it, p(t' | t)
# also return p(word | t) and the set of tags for each word
def get_probabilities_given_t(train_filename):
	# for each tag, count how many times each tag occurs before it
	tprime_given_t_counts = defaultdict(Counter)
	word_given_t_counts = defaultdict(Counter)

	# keep track of the tags associated with each word
	tags_given_word = defaultdict(set)

	with open(train_filename) as f:
		# initialize previous tag to start tag

		for line in f:
			line = line.strip().split(' ')
			previous_tag = '<s>'

			for word_tag_combo in line:
				word, current_tag = word_tag_combo.split('/')
				tprime_given_t_counts[previous_tag][current_tag] += 1
				word_given_t_counts[current_tag][word] += 1
				tags_given_word[word].add(current_tag)
				
				# update previous tag - current tag becomes previous tag
				previous_tag = current_tag

			tprime_given_t_counts[previous_tag]['</s>'] += 1

	# apply add-1 smoothing to word counts given tag
	word_given_t_counts = smooth_p_word_given_t(word_given_t_counts)
	
	return convert_counts_to_probabilities(tprime_given_t_counts), convert_counts_to_probabilities(word_given_t_counts), tags_given_word


def get_predicted_tags(back_pointers, final_viterbi_node_key):
	"""
	input: the back pointers from the viterbi algorithm
		     format: dict where key = (word_num, tag), value = (prev_word_num, prev_tag)
           the key to the final node in the viterbi algorithm
	returns: the list of predicted tag pointers
	"""
	current_node = final_viterbi_node_key
	predicted_tags = list()

	# backtrack the best path using the back pointers
	while True:
		word_index, tag = current_node
		predicted_tags.append(tag)

		# move to the previous node in the best path
		current_node = back_pointers[(word_index, tag)]
		# print(current_node)

		if current_node is None or word_index == 0:
			break

	# the predicted tags were added in the reverse order relative to the sentence
	predicted_tags.reverse()

	return predicted_tags


def get_p_word_given_tag(p_word_given_t, word, tag):
	""" returns p(word | tag) utilizing the smoothing that was performed
		handles unknown words
	"""

	if word in p_word_given_t[tag]:
		return p_word_given_t[tag][word]
	else:
		return p_word_given_t[tag]['<unk>']


def test_accuracy(p_tprime_given_t, p_word_given_t, tags_given_word, test_filename):
	""" Use a 1st order markov model and the Viterbi algorithm to predict tag labels
	"""

	total_tag_count = 0
	correct_tag_guesses = 0
	line_number = 1

	with open(test_filename) as f:
		for line in f:
			# add stop symbol at the end of the line
			line = line.strip().split(' ')
			line.append("</s>")

			# key of viterbi matrix: pair (word number, tag)
			viterbi = defaultdict(lambda: float())
			viterbi[(-1, "<s>")] = 1.0
			back_pointers = dict()
			back_pointers[-1, '<s>'] = None
			final_viterbi_node_key = None

			# iterate over each word in the line
			for word_index, word_tag_combo in enumerate(line):
				is_last_node = False
				# if this is the "word" in the line, the tag and word are </s>
				if word_index >= len(line) - 1:
					is_lastNode = True
					word = '</s>'
				else:
					word, _ = word_tag_combo.split('/')

				possible_tags_for_word = tags_given_word[word]

				# if the word does not exist, then it is most likely a meaningful word
				if len(possible_tags_for_word) == 0:
					possible_tags_for_word = list(['N'])

				# iterate over q' for given word
				for possible_tag in possible_tags_for_word:
					p_current_word = get_p_word_given_tag(p_word_given_t, word, possible_tag)
					# handle first word edge case
					if word_index == 0:
						# must set this case manually for the first word
						possible_prev_tags= ['<s>']
					# elif word == ',':
					# 	possible_prev_tags = tags_given_word[line[word_index - 1]]
					else:
						possible_prev_tags = list(p_tprime_given_t.keys())
					
					# iterate over possible previous nodes/states q
					for prev_tag in possible_prev_tags:
						if word == "," and word_index != 0:
							if prev_tag != possible_tag:
								continue

						# calculate probability of path to node (word_index, current_tag)
						path_probability = viterbi[(word_index - 1, prev_tag)] * p_tprime_given_t[prev_tag][possible_tag]

						# the last node doesn't need to multiply by p_current_word
						if not is_last_node:
							path_probability *= p_current_word

						# if current node has a higher probability than previously seen
						if path_probability > viterbi[word_index, possible_tag]:
							viterbi[(word_index, possible_tag)] = path_probability
							back_pointers[(word_index, possible_tag)] = (word_index - 1, prev_tag)
							final_viterbi_node_key = (word_index, possible_tag)

			# get line's tags after finishing viterbi algorithm
			predicted_tags = get_predicted_tags(back_pointers, final_viterbi_node_key)

			# remove the appended </s> from the line
			line = line[:-1]
			for index, word_tag_combo in enumerate(line):
				# get word and tag from file
				word, correct_tag = word_tag_combo.split('/')

				if predicted_tags[index] == correct_tag:
					correct_tag_guesses += 1

				total_tag_count += 1

				# display requested output for line 2
				if line_number == 2:
					if index == 0:
						print()
						print("Output of HMM for line 2:")

					print("  " + word + "/" + predicted_tags[index])

					# display log probability for the predicted labels
					if index == len(line) - 1:
						print("Log probability of the above predicted labels:", math.log(viterbi[final_viterbi_node_key]))
						print()

			line_number += 1

	print("Accuracy:", str(correct_tag_guesses/total_tag_count * 100) + "%")


def smooth_p_word_given_t(word_given_t_counts):
	""" Use add-1 smoothing so that unknown words do not have a probability of 0
	"""
	for tag in word_given_t_counts:
		# add 1 count to every word that was associated with a tag
		for word in word_given_t_counts[tag]:
			word_given_t_counts[tag][word] += 1

		# add an unknown tag with a count of 1
		word_given_t_counts[tag]['<unk>'] = 1

	return word_given_t_counts


def display_tag_matrix(p_tprime_given_t):
	""" display matrix of probabilities of p(t' | t)
	"""

	print("p(t' | t):")
	print("row: t', column: t")

	# print the column labels
	print("        ", end="")
	for tag in p_tprime_given_t:
		print('{0: <8}'.format(tag), end="")
	print()

	# get possible next tags (including stop symbol)
	possible_next_tags = set()
	for prev_tag in p_tprime_given_t:
		for next_tag in p_tprime_given_t[prev_tag]:
			possible_next_tags.add(next_tag)

	# display p(t' | t) matrix
	for next_tag in possible_next_tags:
		print('{0: ^6}'.format(next_tag), end="")
		for prev_tag in p_tprime_given_t:
			print('{0:.4f}'.format(p_tprime_given_t[prev_tag][next_tag]), end="  ")
		print()

	print()


def display_word_tag_probabilities(word_to_display):
	""" Displays p(w | t) for the specified word
	"""

	print("p(" + word_to_display + " | t) for all tags t:")
	for prev_tag in p_word_given_t:
		for word in p_word_given_t[prev_tag]:
			if word == word_to_display:
				print("  p(" + word + " | " + prev_tag + " ) = " + str(p_word_given_t[prev_tag][word]))


if __name__ == "__main__":
	train_filename = args.training_file
	test_filename = args.testing_file

	if not os.path.isfile(train_filename):
		print("Training file does not exist")
		exit(1)
	elif not os.path.isfile(test_filename):
		print("Testing file does not exist")
		exit(1)

	# each of these dictionaries of dictionaries contain an outer and inner keys
	# the outer keys are the previous tags
	p_tprime_given_t, p_word_given_t, tags_given_word  = get_probabilities_given_t(train_filename)

	# display requested output
	display_tag_matrix(p_tprime_given_t)
	display_word_tag_probabilities('you')

	# set_of_possible_tags = get_possible_tags(p_tprime_given_t, p_word_given_t)
	test_accuracy(p_tprime_given_t, p_word_given_t, tags_given_word, test_filename)
