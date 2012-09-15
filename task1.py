#!/usr/bin/python

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
    for sym in self.nonterminals:
      self.firsts[sym].update(self.first(sym))
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

  def get_firsts(self):
    if self.firsts:
      return self.firsts
    return self.__compute_firsts()

  def __compute_follows(self):
    self.follows[self.start_sym].add(self.INPUT_END)
    for sym in self.nonterminals:
      if sym == self.start_sym:
        continue
      self.follows[sym].update(self.follows(sym))
    return self.follows

  def follows(self, sym):
    temp_follows = set()
    for rule_body in self.rules[sym]:
      tokens = rule_body.split()
      k = 0
      while k < len(tokens):
        curr_sym = tokens[k]
        if curr_sym in self.nonterminals:
          #temp_follows.update(
          pass

  def get_follows(self):
    if self.follows:
      return self.follows
    return self.__compute_follows()

if __name__ == '__main__':
  import sys
  try:
    grammar_def = sys.argv[1]
  except IndexError, e:
    print 'No grammar file supplied'
    sys.exit(-1)
  g = Grammar(grammar_def)
  print g.get_firsts()
#  print g.get_follows()
