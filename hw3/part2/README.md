# Predict the label of words in text

## Naive

This is a naive, baseline implementation that predicts a word's label by counting the number of times each label was associated with each word. For unknown words, the label that was seen the most times in the training data was always selected.


#### How To Run
```python3 ./guess_labels.py <training filename> <testing filename>```

You can also type ```python3 ./guess_labels.py -h``` for more help on running the program


## 1st Order Markov Model

This approach utilizes a first order hidden markov model to make more accurate predictions. From the training data, a table of p(t' | t) is built up, where tag t immediately preceedes t'. p(word | t) is also built up from the training data, and add-one smoothing is used to combat the situation when a word appeared in the training data but was never associated with a particular tag and thus p(word | t) would be 0 for some tag t. The Viterbi algorithm is then used as the decoder to efficiently determine the most probable tag sequence for each line of text in the testing data.


#### How To Run
```python3 ./hmm-viterbi.py <training filename> <testing filename>```

You can also type ```python3 ./hmm-viterbi.py -h``` for more help on running the program


## Requirements
- python3
