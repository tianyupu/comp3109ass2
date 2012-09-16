class Grammar(object):
  EPSILON = 'epsilon'
  DERIVE_SYM = '::='
  INPUT_END = '$'

  def __init__(self, fname):
    from collections import defaultdict
    try:
      self.fname = fname
      grammar_file = open(fname, 'rU')
    except IOError, e:
      print 'The given file name could not be found'
      sys.exit(-1)
    rules = grammar_file.read().splitlines()
    self.terminals = set()
    self.nonterminals = set()
    self.start_sym = ''
    self.firsts = defaultdict(set)
    self.follows = defaultdict(set)
    self.__processrules(rules)

  def __processrules(self, rule_list):
    from collections import defaultdict
    self.rules = defaultdict(list)
    for i in xrange(len(rule_list)):
      rule = rule_list[i]
      nonterm, body = rule.split(self.DERIVE_SYM)
      nonterm = nonterm.strip()
      if i == 0:
        self.start_sym = nonterm
      self.rules[nonterm].append(body.strip())
      self.nonterminals.add(nonterm)

  def __compute_firsts(self):
    while True:
      prev_count = sum([len(s) for s in self.firsts.values()])
      for sym in self.nonterminals:
        self.firsts[sym].update(self.first(sym))
      curr_count = sum([len(s) for s in self.firsts.values()])
      if prev_count == curr_count:
        return self.firsts

  def first(self, sym):
    temp_first = set()
    if sym == self.EPSILON:
      temp_first.add(sym)
      return temp_first
    # a terminal's first is just itself
    elif sym not in self.nonterminals:
      self.terminals.add(sym)
      return set(sym)
    # for each production associated with this symbol
    for rule_body in self.rules[sym]:
      # split the rule into its separate token symbols
      tokens = rule_body.split()
      k = 0
      cont = True
      while cont and k < len(tokens):
        # examine each token in turn
        curr_sym = tokens[k]
        if curr_sym == sym: # otherwise we get infinite recursion!
          cont = False
          break
        t = self.first(curr_sym)
        if self.EPSILON not in t:
          cont = False
        if self.EPSILON in t:
          t.remove(self.EPSILON)
        temp_first.update(t)
        k += 1
      if cont:
        temp_first.add(self.EPSILON)
    return temp_first

  def first_sent(self, sent):
    temp_first = set()
    sentence = sent.split()
    n = len(sentence)
    if n == 1:
      sym = sentence[0]
      return self.first(sym)
    for i in xrange(n):
      sym = sentence[i]
      t = self.first(sym)
      if self.EPSILON in t:
        t.remove(self.EPSILON)
        temp_first.update(t)
        newsent = ' '.join(sentence[i+1:])
        if newsent:
          temp_first.update(self.first_sent(newsent))
        return temp_first
      return t

  def get_firsts(self, sym=''):
    if self.firsts:
      if sym:
        return self.firsts[sym]
      return self.firsts
    return self.__compute_firsts()

  def __compute_follows(self):
    self.follows[self.start_sym].add(self.INPUT_END)
    while True:
      prev_count = sum([len(s) for s in self.follows.values()])
      for sym in self.nonterminals:
        self.follow(sym)
      curr_count = sum([len(s) for s in self.follows.values()])
      if prev_count == curr_count: # nothing to add, so finish
        return self.follows

  def follow(self, sym):
    for rule_body in self.rules[sym]:
      tokens = rule_body.split()
      k = 0
      n = len(tokens)
      while k < n:
        curr_sym = tokens[k]
        if curr_sym in self.nonterminals:
          if k == n-1:
            self.follows[curr_sym].update(self.follows[sym])
          else:
            sentence = ' '.join(tokens[k+1:])
            f = self.first_sent(sentence)
            if self.EPSILON in f:
              self.follows[curr_sym].update(self.follows[sym])
              f.remove(self.EPSILON)
            self.follows[curr_sym].update(f)
        k += 1
    return self.follows[sym]

  def get_follows(self, sym=''):
    if self.follows:
      if sym:
        return self.follows[sym]
      return self.follows
    return self.__compute_follows()
