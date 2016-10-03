import random
import tkinter as tk
from model import Model

class Application(tk.Frame):
	def __init__(self, model, master=None):
		self.model = model

		tk.Frame.__init__(self, master)
		self.pack()

		self.INPUT = tk.Text(self)
		self.INPUT.pack()

		self.chars = ['qwertyuiop',
					  'asdfghjkl',
					  'zxcvbnm,.',
					  ' ']

		self.KEYS = tk.Frame(self)
		for row in self.chars:
			r = tk.Frame(self.KEYS)
			for w in row:
				# trick to make button sized in pixels
				f = tk.Frame(r, height=32)
				b = tk.Button(f, text=w, command=lambda w=w: self.press(w))
				b.pack(fill=tk.BOTH, expand=1)
				f.pack(side=tk.LEFT)
				f.pack_propagate(False)
			r.pack()
		self.KEYS.pack()

		self.TOOLBAR = tk.Frame()

		self.BEST = tk.Button(self.TOOLBAR, text='Best', command=self.best, 
							  repeatdelay=500, repeatinterval=1)
		self.BEST.pack(side=tk.LEFT)

		self.WORST = tk.Button(self.TOOLBAR, text='Worst', command=self.worst, 
							   repeatdelay=500, repeatinterval=1)
		self.WORST.pack(side=tk.LEFT)

		self.RANDOM = tk.Button(self.TOOLBAR, text='Random', command=self.random, 
								repeatdelay=500, repeatinterval=1)
		self.RANDOM.pack(side=tk.LEFT)

		self.QUIT = tk.Button(self.TOOLBAR, text='Quit', command=self.quit)
		self.QUIT.pack(side=tk.LEFT)

		self.TOOLBAR.pack()

		self.update()
		self.resize_keys()

	def resize_keys(self):
		for bs, ws in zip(self.KEYS.winfo_children(), self.chars):
			wds = [150*self.model.prob(w)+15 for w in ws]
			wds = [int(wd+0.5) for wd in wds]

			for b, wd in zip(bs.winfo_children(), wds):
				b.config(width=wd)

	def press(self, w):
		self.INPUT.insert(tk.END, w)
		self.INPUT.see(tk.END)
		self.model.read(w)
		self.resize_keys()

	def best(self):
		_, w = max((p, w) for (w, p) in self.model.probs().items())
		self.press(w)

	def worst(self):
		_, w = min((p, w) for (w, p) in self.model.probs().items())
		self.press(w)

	def random(self):
		s = 0.
		r = random.random()
		p = self.model.probs()
		for w in p:
			s += p[w]
			if s > r:
				break
		self.press(w)

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("ngrams", type=int, help="n-grams to use in predicting next word")
	parser.add_argument(dest='train')
	args = parser.parse_args()

	m = Model(args.ngrams)
	m.train(args.train)
	m.start()

	root = tk.Tk()
	app = Application(m, master=root)
	app.mainloop()
	root.destroy()
