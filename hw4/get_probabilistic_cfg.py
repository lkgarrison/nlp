# Luke Garrison
# Hw4, part 1
# Code to get the probabilistic CFG given the input data

import sys
import argparse
from collections import defaultdict, Counter

# hw4_data was provided for this assignment
from hw4_utilities.tree import Tree

parser = argparse.ArgumentParser(description='Builds a probabilistic CFG by reading in trees and counting all of the rules')
parser.add_argument("trees_file", type=str, help="File containing trees with CFG rules")

args = parser.parse_args()


def count_rules(trees_file):
	""" Returns a dictionary of Counters where the key of the outer dictionary is the left
	    half of the rule and the key of the inner dictionary is the right half of the rule.
	    The value of the inner dictionary is the number of times this rule was seen
	"""
	rule_counts = defaultdict(Counter)

	with open(trees_file) as f:
		for index, line in enumerate(f):
			line = line.strip()
			t = Tree.from_str(line)

			count_tree_rules(t.root, rule_counts)
	
	return rule_counts


def get_probabilistic_cfg(rule_counts):
	""" Get the probabilistic CFG given the rule counts of the CFG
	"""

	# instead of counts, get the probability for each rule
	probabilistic_cfg = defaultdict(lambda: defaultdict(lambda: float()))

	for left_side in rule_counts:
		# the number of times a production rule with the given left side was seen
		left_side_sum = sum(rule_counts[left_side].values())

		for right_side in rule_counts[left_side]:
			probabilistic_cfg[left_side][right_side] = rule_counts[left_side][right_side] / left_side_sum
	
	return probabilistic_cfg


def display_cfg(rule_counts, label='probability'):
	""" Displays the CFG encoded as a dictionary of dictionaries
	"""
	for left_side in rule_counts:
		for right_side in rule_counts[left_side]:
			print(left_side, '-->', right_side, '   ' + label + ":", rule_counts[left_side][right_side])


def count_tree_rules(root, rule_counts):
	if len(root.children) == 2:
		# 2 non-terminals
		right_side = ' '.join(node.label for node in root.children)
		rule_counts[root.label][right_side] += 1

		# recurse on left and right children
		count_tree_rules(root.children[0], rule_counts)
		count_tree_rules(root.children[1], rule_counts)
	elif len(root.children) == 1:
		# leaf node
		rule_counts[root.label][root.children[0].label] += 1


def display_most_common_rules(rule_counts, label='probability'):
	""" put rules into a 1D dictionary and then sort the dictionary based on the values (counts) """
	flattened_rule_counts = dict()

	for left_side in rule_counts:
		for right_side in rule_counts[left_side]:
			flattened_rule_counts[left_side + ' --> ' + right_side] = rule_counts[left_side][right_side]

	count = 0
	# sort the dictionary by the rule counts
	for rule in sorted(flattened_rule_counts, key=flattened_rule_counts.get, reverse=True):
		if count < 5:
			print(rule, '  ' + label + ':', flattened_rule_counts[rule])
		else:
			break

		count += 1


if __name__ == '__main__':
	trees_file = args.trees_file

	if trees_file is None:
		print("Plese specify a file containing trees representing CFG rules")
		sys.exit(1)

	rule_counts = count_rules(trees_file)
	print('Number of unique rules:', len(rule_counts))
	print('The top 5 most frequent rules:')
	display_most_common_rules(rule_counts, 'count')

	probabilistic_cfg = get_probabilistic_cfg(rule_counts)
	print()
	print('The top 5 most probable rules:')
	display_most_common_rules(probabilistic_cfg, 'probability')
	print()

	print('The probabilistic CFG:')
	display_cfg(probabilistic_cfg)
