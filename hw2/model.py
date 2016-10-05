from collections import defaultdict, Counter, deque

class Context():
	# newest char in context is pushed to the right end of the deque
	# oldest char is removed from left end of the deque
	def __init__(self, context_length):
		self.context = deque()
		self.context_length = context_length

	def update_context(self, char):
		if self.is_window_full():
			# slide context window
			self.context.append(char)
			self.context.popleft()
		else:
			self.context.append(char)

	# returns True/False if context window is full or not
	def is_window_full(self):
		return len(self.context) == self.context_length

	# clears the context deque
	def reset(self):
		self.context.clear()

	# convert content of context deque to a string
	def __str__(self):
		data = list()
		for char in self.context:
			data.append(char)

		return ''.join(data)


class Model(object):
	def __init__(self, mgrams):
		self.vocab = set()
		self.mgrams = mgrams
		self.c_u_dot_memoization = dict()
		self.context = Context(self.mgrams)

	def train(self, filename):
		"""Train the model on a text file."""

		# counts[m-gram size][context u][char w]
		self.counts = defaultdict(lambda: defaultdict(Counter))

		with open(filename) as f:
			# split on newlines but keep them in the lines
			filedata = f.read().splitlines(1)

		for m in range(self.mgrams + 1):
			print("training model on %s-gram" % (m))
			for doc in filedata:
				# sliding window of the context
				# push next char onto right end, pop from left end
				context = Context(m)

				for c in doc:
					# build up a set of the vocabulary seen (only need to do this once)
					if m == 0:
						self.vocab.add(c)

					## get word, which should be next char after context
					if context.is_window_full():
						context_str = str(context)

						self.counts[m][context_str][c] += 1

						# update context for next char
						context.update_context(c)
					else:
						context.update_context(c)

	# recursively calculate p(w | u) using recursive smoothing
	# p(w | u) = lambda(u) * (c(uw) / c(u dot)) + (1 - lambda(u))*(p(w | u bar))
	def p_w_given_u(self, w, u, already_done_uniform=False):
		# base case
		if already_done_uniform:
			return 0

		lambda_u = self.lambda_u(u)
		c_u_dot = self.c_u_dot(u)

		if c_u_dot == 0:
			# avoid divide by 0
			first_term = 0
		else:
			first_term = lambda_u * (self.counts[len(u)][u][w] / c_u_dot)


		if len(u) == 0:
			already_done_uniform = True

		return first_term + ((1 - lambda_u) * self.p_w_given_u(w, u[1:], already_done_uniform))


	# calculate lambda(u)
	def lambda_u(self, u):
		c_u_dot = self.c_u_dot(u)

		# avoid divide by 0
		if c_u_dot == 0:
			return 0

		return (c_u_dot) / (c_u_dot + len(self.counts[len(u)][u]))

	
	# u = context
	def c_u_dot(self, u):
		# if this value hasn't already been calculated, calculate it and save it
		if u not in self.c_u_dot_memoization:
			sum_counts = 0
			for char in self.counts[len(u)][u]:
				sum_counts += self.counts[len(u)][u][char]

			self.c_u_dot_memoization[u] = sum_counts


		return self.c_u_dot_memoization[u]


	# The following two methods make the model work like a finite
	# automaton.

	def start(self):
		"""Resets the state."""
		self.context.reset()

	def read(self, w):
		"""Reads in character w, updating the state."""
		self.context.update_context(w)


	# The following two methods add probabilities to the finite automaton.

	def prob(self, w):
		"""Returns the probability of the next character being w given the
		current state."""
		return self.p_w_given_u(w, str(self.context))

	def probs(self):
		"""Returns a dict mapping from all characters in the vocabulary to the
probabilities of each character."""
		return {w: self.prob(w) for w in self.vocab}
