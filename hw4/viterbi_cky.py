# Luke Garrison
# Hw4, part 2
# Takes a sentence and grammar as input and outputs the highest probability parse

import sys
import math
import argparse
from collections import defaultdict, Counter

# hw4_utilities was provided for this assignment
from hw4_utilities.tree import Tree

import get_probabilistic_cfg as get_cfg


def parse_lines(trees_file, sentences_file, probabilistic_cfg):
	terminals, nonterminals = get_terminals_nonterminals(trees_file)
	# print(terminals)
	# print()
	# print(nonterminals)

	outfile = open("dev.parses", "w")
	

	with open(sentences_file) as f:
		for line_index, line in enumerate(f):
			if line_index == 0:
				line = line.strip()
				# line = 'Does this flight server dinner ?' 
				print(len(line.split(' ')))
				print(line)	
				final_cell_entry, back_pointers = viterbi_cky(line, probabilistic_cfg, terminals, nonterminals)
				# labels = dict()
				# get_parsed_line(final_cell_entry, back_pointers, labels)
				tree_list = list()
				tree_list.append("(TOP")
				get_tree_list(final_cell_entry, back_pointers, line.split(' '), tree_list)
				tree_list.append(")")
				# print(''.join(tree_list))
				outfile.write(''.join(tree_list) + '\n')

				# for k in labels:
				# 	print(k, labels[k])

	outfile.close()


def get_tree_list(cell_entry, back_pointers, sentence_list, tree_list):
	cell = back_pointers[cell_entry[0]][cell_entry[1]][cell_entry[2]]
	# print('(', end="")
	if isinstance(cell, str):
		# print('here 1')
		# print(cell)
		# print(cell_entry)
		# print('here 2')
		# print()
		# print(cell_entry[2], sentence_list[cell_entry[0]], end="")
		tree_list.append('(')
		tree_list.append(cell_entry[2] + " " + sentence_list[cell_entry[0]])
		tree_list.append(")")
		# labels[cell_entry[0]] = cell_entry[2]
	else:
		# print(cell[0][2])
		tree_list.append('(')
		tree_list.append(cell[0][2])
		get_tree_list(cell[0], back_pointers, sentence_list, tree_list)
		tree_list.append(")")
		# print(cell[1][2])
		tree_list.append('(')
		tree_list.append(cell[1][2])
		get_tree_list(cell[1], back_pointers, sentence_list, tree_list)
		tree_list.append(")")
	
	# print(")")


def get_parsed_line(cell_entry, back_pointers, labels):
	cell = back_pointers[cell_entry[0]][cell_entry[1]][cell_entry[2]]
	if isinstance(cell, str):
		print('here 1')
		# print(cell)
		print(cell_entry)
		print('here 2')
		print()
		labels[cell_entry[0]] = cell_entry[2]
	else:
		print(cell)
		get_parsed_line(cell[0], back_pointers, labels)
		get_parsed_line(cell[1], back_pointers, labels)



def viterbi_cky(sentence, probabilistic_cfg, terminals, nonterminals):
	# best = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: float())))
	best = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: float('-inf'))))
	back_pointers = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

	# sentence_length = len(sentence)
	sentence_length = len(sentence.split(' '))
	# print(terminals['<unk>'])

	# initialization
	# for i in range(sentence_length + 1):
	# 	for j in range(sentence_length + 1):
	# 		for X in nonterminals:
	# 			best[i][j][X] = 0
	# 			back_pointers[i][j][X] = None

	# find all X such that X --> wi (x produces a terminal)
	nonterminals_producing_terminals = set()

	# find all X such that X --> Y Z (x produces two nonterminals)
	nonterminals_producing_nonterminals = set()

	for left_side in probabilistic_cfg:
		for right_side in probabilistic_cfg[left_side]:
			if len(right_side.split(' ')) == 1:
				nonterminals_producing_terminals.add(left_side)
			elif len(right_side.split(' ')) == 2:
				nonterminals_producing_nonterminals.add(left_side)
	
	for i in range(1, sentence_length + 1):
		word = sentence[i-1]
		if word not in terminals:
			terminal = '<unk>'
		else:
			terminal = word

		for X in nonterminals_producing_terminals:
			for terminal in probabilistic_cfg[X]:
				# ensure that this rule produces a terminal
				if len(terminal.split(' ')) > 1:
					continue

				if X not in probabilistic_cfg:
					print("X:", X, "not in probabilistic cfg")
				if terminal not in probabilistic_cfg[X]:
					print("terminal:", termainal, "not in probabilistic cfg")


				p = math.log10(probabilistic_cfg[X][terminal])
				if p > best[i-1][i][X] or best[i-1][i][X] == 0:
					best[i-1][i][X] = p

					# TODO: what is the value????
					# back_pointers[i-1][i][X] = (i-1, i, X)
					back_pointers[i-1][i][X] = word


	for l in range(2, sentence_length + 1):
		for i in range(0, sentence_length - l + 1):
			j = i + l
			for k in range(i + 1, j):
				for X in nonterminals:
					for right_side in probabilistic_cfg[X]:
						# ensure that this rule produces a nonterminal
						if len(right_side.split(' ')) != 2:
							continue

						Y, Z = right_side.split(' ')
						p = math.log10(probabilistic_cfg[X][right_side])
						p_prime = p * best[i][k][Y] * best[k][j][Z]

						if p_prime > best[i][j][X] or best[i][j][X] == 0:
							best[i][j][X] = p_prime
							back_pointers[i][j][X] = ((i, k, Y), (k, j, Z))

	# get largest probability in final cell of matrix
	final_cell_indices = 0, sentence_length
	final_cell = best[final_cell_indices[0]][final_cell_indices[1]]

	print(final_cell)
	max_prob = -float('inf')
	max_prob_label = None
	for X in final_cell:
		if final_cell[X] > max_prob: 
			max_prob = final_cell[X]
			max_prob_label = X

	print(max_prob_label, max_prob)

	# for i in range(sentence_length + 1):
	# 	for j in range(sentence_length + 1):
	# 		# print(i, j, best[i][j])
	# 		for X in best[i][j]:
	# 			if best[i][j][X]:
	# 				print("p(", i, j, X, " )=", best[i][j][X])

	# print(best)
	# print()
	# print()
	# print(back_pointers)

	return (final_cell_indices[0], final_cell_indices[1], max_prob_label), back_pointers


def get_terminals_nonterminals(trees_file):
	""" get a set of the terminals and non-terminals """
	termainals = set()
	nonterminals = set()

	with open(trees_file) as f:
		for index, line in enumerate(f):
			line = line.strip()
			t = Tree.from_str(line)

			get_terminals_nonterminals_helper(t.root, termainals, nonterminals)
	
	return termainals, nonterminals


def get_terminals_nonterminals_helper(root, terminals, nonterminals):
	""" recursively iterate over the tree and add terminals, nonterminals to sets as they are found """
	if root is None:
		return

	nonterminals.add(root.label)

	if len(root.children) == 2:
		# 2 non-terminals
		right_side = ' '.join(node.label for node in root.children)

		# recurse on left and right children
		get_terminals_nonterminals_helper(root.children[0], terminals, nonterminals)
		get_terminals_nonterminals_helper(root.children[1], terminals, nonterminals)
	elif len(root.children) == 1:
		# leaf node, terminal
		terminals.add(root.children[0].label)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Outputs the highest probability parse given a probabilistic CFG and sentence')
	parser.add_argument("trees_file", type=str, help="File containing trees with CFG rules")
	parser.add_argument("sentences_file", type=str, help="File containing input sentences to parse")

	args = parser.parse_args()

	trees_file = args.trees_file
	sentences_file = args.sentences_file

	rule_counts = get_cfg.count_rules(trees_file)
	probabilistic_cfg = get_cfg.get_probabilistic_cfg(rule_counts)

	parse_lines(trees_file, sentences_file, probabilistic_cfg)
