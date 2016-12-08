# Build and improve a simple parser trained from the ATIS portion of the Penn Treebank

## Getting the Probabilistic CFG
First, the input data must be read in and used to build a tree. This tree is then used to build up the CFG. By counting the number of times each rule appears, a probabilistic CFG is returned.


#### How To Run
```python3 ./get_probabilistic_cfg.py <training filename>```

You can also type ```python3 ./get_probabilistic_cfg.py -h``` for more help on running the program


## Requirements
- python3
