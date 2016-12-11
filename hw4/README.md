# Build and improve a simple parser trained from the ATIS portion of the Penn Treebank

## Getting the Probabilistic CFG (Part 1)
First, the input data must be read in and used to build a tree. This tree is then used to build up the CFG. By counting the number of times each rule appears, a probabilistic CFG is returned.


#### How To Run
```python3 ./get_probabilistic_cfg.py <training filename>```

You can also type ```python3 ./get_probabilistic_cfg.py -h``` for more help on running the program


## Parsing Sentences

First, the training data must be given to viterbi_cky.py which will use get_probabilistic_cfg.py to generate a probabilistic_cfg using the training data. Then, each sentence from dev.strings is read in and the best parse is found for each sentence using the viterbi-cky algorithm. The parsed sentence is output to the file dev.parses. This output should then be run through the postprocess script and saved as dev.parses.post. Then, the evalb.py script can be used to compare dev.parses.post to dev.trees for precesion, recall, and an F1 score.


#### How To Run

	python3 viterbi_cky.py train.trees.pre.unk hw4_data/dev.strings
	python3 hw4_utilities/postprocess.py dev.parses > dev.parses.post
	python3 hw4_utilities/evalb.py dev.parses.post hw4_data/dev.trees


## Requirements
- python3
