# Overview

This assignment uses an n-gram model to predict each character in a test file given the n previous characters. The n-gram language model utilizing recursive Witten-Bell smoothing is applied to both English and Chinese data sets


### 1. English
```python3 english_test.py <n-grams> <training data file> <test data file>```

This program will use model.py to train the model on the training data and then use the model to predict the characters in the test file


### 2. Chinese
``` python3 chinese_test.py <n-grams> <training data> <testing data> <charmap> <test data pin file> ```

This program will use model.py to train the model on the training data and then use the .pin file and charmap to determine what Chinese symbols are possible given the next character's pronunciation (from the .pin file) and use the model (and implicitely the previous Chinese symbols in the test file) to select the corresponding symbol with the highest probability. 

The program accounts for three different token types in the .pin file:
1. a pronunciation, such as "yi", which can convert to one of the Chinese characters in the charmap
2. a single character, such as "o", which can convert to itself or a Chinese character in the charmap
3. &lt;space&gt;, which converts to a space


## Requirements
* python 3.5+


## Help
For help regarding the arguments to either english_test.py or chinese_test.py, simply run:
``` python3 english_test.py -h``` or ``` python3 chinese_test.py -h```
