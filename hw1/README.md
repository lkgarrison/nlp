# Overview

This assignment uses a training file to train a model that will be used to predict the correct candidate given speech samples. I implemented two different approaches to predicting the correct candidate for each speech: Naive Bayes and Logistic Regression.


### 1. Naive Bayes:
```python3.5 1.py <training data file> <test data file>```

### 2. Logistic Regression
Prints out the requested information in 2b, 2c, and 2d

run the program with the following command:

```python3.5 2.py <training data file> <test data file>```

### 3. Features
For both programs 1.py and 2.py, you can use the ```--stems``` option to stem the words (feature 1) and the ```--no_stop_words``` option to remove stop words from the model (feature 2).

For example: ```python3.5 2.py data/train data/test --stems``` will run logistic regression on the test data and will use word stems

When running either program, you can always use the -h option to get help on what the required and optional arguments are.


## Requirements
* python 3.5+
* scipy
