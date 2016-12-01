# Guess the label of words in text

This is a naive, baseline implementation that predicts a word's label by counting the number of times each label was associated with each word. For unknown words, the label that was seen the most times in the training data was always selected.


## How To Run
```python3 ./guess_labels.py <training filename> <testing filename>```

You can also type ```python3 ./guess_labels.py -h``` for more help on running the program


## Requirements
- python3
