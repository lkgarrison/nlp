# Luke Garrison
# Hw4, part 2
# Takes a sentence and grammar as input and outputs the highest probability parse

import re
import sys
import math
import argparse
from timeit import default_timer as timer
from collections import defaultdict, Counter

# hw4_utilities was provided for this assignment
from hw4_utilities.tree import Tree

import get_probabilistic_cfg as get_cfg


# try parsing the line using vertical markovization. if that fails, use standard parsing
def parse_lines_vm(trees_file, sentences_file, parse_tree_out_filename, probabilistic_cfg, probabilistic_cfg_vm):
	outfile = open(parse_tree_out_filename, "w")

	with open(sentences_file) as f:
		for line_index, line in enumerate(f):
			line = line.strip()
			tree_list = list()
			tree_string = str()

			# try with vertical markovization and standard parsing
			final_back_pointer_vm, back_pointers_vm, best_vm = viterbi_cky(line, probabilistic_cfg_vm)
			final_back_pointer_std, back_pointers_std, best_std = viterbi_cky(line, probabilistic_cfg)

			# if both vertical markovizatin and standard were possible, use the parse with the larger probability
			if final_back_pointer_vm[2] is None and final_back_pointer_std[2] is not None:
				get_tree_list(final_back_pointer_std, back_pointers_std, line.split(' '), tree_list)
				tree_string = ''.join(tree_list)
			elif final_back_pointer_std[2] is None and final_back_pointer_vm[2] is not None:
				get_tree_list(final_back_pointer_vm, back_pointers_vm, line.split(' '), tree_list)
				t = Tree.from_str(''.join(tree_list))
				t.undo_vertical_markovization()
				tree_string = str(t)
			elif final_back_pointer_std[2] is not None and final_back_pointer_vm[2] is not None and final_back_pointer_std[2] > final_back_pointer_vm[2]:
				get_tree_list(final_back_pointer_std, back_pointers_std, line.split(' '), tree_list)
				tree_string = ''.join(tree_list)
			elif final_back_pointer_std[2] is not None and final_back_pointer_vm[2] is not None and final_back_pointer_std[2] <= final_back_pointer_vm[2]:
				get_tree_list(final_back_pointer_vm, back_pointers_vm, line.split(' '), tree_list)
				t = Tree.from_str(''.join(tree_list))
				t.undo_vertical_markovization()
				tree_string = str(t)
			else:
				# unable to parse the line
				pass

			tree_string += '\n'

			outfile.write(tree_string)


	outfile.close()
	print("parser output located in:", parse_tree_out_filename)


# use viterbi-cky algorithm to parse each sentence
def parse_lines(trees_file, sentences_file, parse_tree_out_filename, probabilistic_cfg):
	outfile = open(parse_tree_out_filename, "w")

	with open(sentences_file) as f:
		for line_index, line in enumerate(f):
			line = line.strip()
			tree_list = list()
			tree_string = str()

			final_back_pointer, back_pointers, best = viterbi_cky(line, probabilistic_cfg)

			# if both vertical markovizatin and standard were possible, use the parse with the larger probability
			if final_back_pointer[2] is not None:
				get_tree_list(final_back_pointer, back_pointers, line.split(' '), tree_list)
				tree_string = ''.join(tree_list)
			else:
				# unable to parse the line
				pass

			tree_string += '\n'

			outfile.write(tree_string)


	outfile.close()
	print("parser output located in:", parse_tree_out_filename)


def get_tree_list(back_pointer, back_pointers, sentence_list, tree_list):
	cell = back_pointers[back_pointer[0]][back_pointer[1]][back_pointer[2]]

	# if cell contains a string, it is a terminal corresponding to a word
	if isinstance(cell, str):
		tree_list.append('(')
		tree_list.append(back_pointer[2] + " " + sentence_list[back_pointer[0]])
		tree_list.append(")")
	else:
		tree_list.append('(')
		tree_list.append(back_pointer[2] + " ")
		get_tree_list(cell[0], back_pointers, sentence_list, tree_list)
		get_tree_list(cell[1], back_pointers, sentence_list, tree_list)
		tree_list.append(")")
	

def viterbi_cky(sentence, probabilistic_cfg):
	# best = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: float())))
	best = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: float('-inf'))))
	back_pointers = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

	sentence = sentence.split(' ')
	sentence_length = len(sentence)

	# find all X such that X --> wi (x produces a terminal)
	nonterminals_producing_terminals = set()

	# find all X such that X --> Y Z (x produces two nonterminals)
	nonterminals_producing_nonterminals = set()

	terminals = set()

	for left_side in probabilistic_cfg:
		for right_side in probabilistic_cfg[left_side]:
			if len(right_side.split(' ')) == 1:
				nonterminals_producing_terminals.add(left_side)
				terminals.add(right_side)
			elif len(right_side.split(' ')) == 2:
				nonterminals_producing_nonterminals.add(left_side)

	for i in range(1, sentence_length + 1):
		word = sentence[i-1]
		if word not in terminals:
			terminal = '<unk>'
		else:
			terminal = word

		for X in probabilistic_cfg:
			# looking for rules in the form X --> wi
			if terminal not in probabilistic_cfg[X]:
				continue

			# ensure that this rule produces a terminal
			if len(terminal.split(' ')) > 1:
				continue

			p = math.log10(probabilistic_cfg[X][terminal])
			if p > best[i-1][i][X]:
				best[i-1][i][X] = p

				back_pointers[i-1][i][X] = word


	for l in range(2, sentence_length + 1):
		for i in range(0, sentence_length - l + 1):
			j = i + l
			for k in range(i + 1, j):
				for X in probabilistic_cfg:
					for right_side in probabilistic_cfg[X]:
						# ensure that this rule produces a nonterminal
						if len(right_side.split(' ')) != 2:
							continue

						Y, Z = right_side.split(' ')
						p = math.log10(probabilistic_cfg[X][right_side])
						p_prime = p + best[i][k][Y] + best[k][j][Z]

						if p_prime > best[i][j][X]:
							best[i][j][X] = p_prime
							back_pointers[i][j][X] = ((i, k, Y), (k, j, Z))

	# get largest probability in final cell of matrix
	final_cell_indices = 0, sentence_length
	final_cell = best[final_cell_indices[0]][final_cell_indices[1]]

	max_prob = -float('inf')
	max_prob_label = None
	for X in final_cell:
		if final_cell[X] > max_prob: 
			max_prob = final_cell[X]
			max_prob_label = X

	return (final_cell_indices[0], final_cell_indices[1], max_prob_label), back_pointers, best


def unknown_smoothing(rule_counts, delta):
	for left_side in rule_counts:
		rule_counts[left_side]['<unk>'] += delta

def add_delta_smoothing(rule_counts, delta):
	for left_side in rule_counts:
		for right_side in rule_counts[left_side]:
			rule_counts[left_side][right_side] += delta


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Outputs the highest probability parse given a probabilistic CFG and sentence')
	parser.add_argument("trees_file", type=str, help="File containing trees with CFG rules")
	parser.add_argument("sentences_file", type=str, help="File containing input sentences to parse")
	parser.add_argument('--vertical_markovization', action='store_true', help='Try to use vertical markovization for better parses')
	parser.add_argument('--unknowns', action='store_true', help='Put more weight on rules that produce <unk>')
	parser.add_argument('--add_delta', action='store_true', help='Apply add-delta smoothing to the model')

	args = parser.parse_args()

	trees_file = args.trees_file
	sentences_file = args.sentences_file
	use_vertical_markovization = args.vertical_markovization
	increase_unknowns = args.unknowns
	add_delta = args.add_delta

	is_test_file_re = re.compile('test\.strings$')
	if re.search(is_test_file_re, sentences_file):
		out_filename = 'test.parses'
	else:
		out_filename = 'dev.parses'

	# get cfg rule counts
	rule_counts = get_cfg.count_rules(trees_file)
	rule_counts_vertical_markovization = get_cfg.count_rules_vertical_markovization(trees_file)

	if increase_unknowns:
		# only use this if vertical markovization is not being used
		if not use_vertical_markovization:
			unknown_smoothing(rule_counts, 15)
		unknown_smoothing(rule_counts_vertical_markovization, 15)

	if add_delta:
		# only use this if vertical markovization is not being used
		if not use_vertical_markovization:
			add_delta_smoothing(rule_counts, 10)
		add_delta_smoothing(rule_counts_vertical_markovization, 10)

	# get cfg rule probabilities
	probabilistic_cfg = get_cfg.get_probabilistic_cfg(rule_counts)
	probabilistic_cfg_vm = get_cfg.get_probabilistic_cfg(rule_counts_vertical_markovization)

	if use_vertical_markovization:
		parse_lines_vm(trees_file, sentences_file, out_filename, probabilistic_cfg, probabilistic_cfg_vm)
	else:
		parse_lines(trees_file, sentences_file, out_filename, probabilistic_cfg)
