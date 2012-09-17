class Grammar(object):
  EPSILON = 'epsilon'
  DERIVE_SYM = '::='
  INPUT_END = '$'

  def __init__(self, fname):
    '''Create a new Grammar object.

    fname -- a string containing the path of the grammar definition file.'''
    from collections import defaultdict
    try:
      # open the text file with name fname
      self.fname = fname
      grammar_file = open(fname, 'rU')
    except IOError, e:
      print 'The given file name could not be found'
      sys.exit(-1)
    rules = grammar_file.read().splitlines()
    # define some instance attributes
    self.terminals = set()
    self.nonterminals = set()
    self.start_sym = ''
    self.firsts = defaultdict(set)
    self.follows = defaultdict(set)
    # process the grammar rules
    self.__processrules(rules)

  def __processrules(self, rule_list):
    '''Takes a list of strings, with each string corresponding to one rule in
    the grammar. Strings are of the form HEAD ::= BODY where HEAD denotes the
    nonterminal, ::= the derivation symbol, and BODY the sequence of terminals
    and nonterminals. Returns nothing, but stores the rules in self.rules.'''
    from collections import defaultdict
    # self.rules is a dictionary of rules, indexed by HEAD of the rule, with
    # values as a list of strings representing the BODY of each production
    self.rules = defaultdict(list)
    self.rule_order = {} # gives index no of rule
    self.rule_index = {} # gives rule at index no
    for i in xrange(len(rule_list)):
      rule = rule_list[i]
      self.rule_order[rule] = i
      self.rule_index[i] = rule
      nonterm, body = rule.split(self.DERIVE_SYM)
      nonterm = nonterm.strip()
      if i == 0: # if we're looking at the first symbol, that's the start symbol
        self.start_sym = nonterm
      self.rules[nonterm].append(body.strip())
      self.nonterminals.add(nonterm)
  
  def grammar_to_bnf(self):
    '''Takes the rules of this grammar and converts it to an equivalent BNF
    form.
    Returns the new dictionary of BNF rules.'''
    from collections import defaultdict
    self.bnf_rules = defaultdict(set)
    for head in self.rules:
      for body in self.rules[head]:
        # for every rule, process it using the rule_to_bnf method
        self.rule_to_bnf(head, body)
    return self.bnf_rules

  def rule_to_bnf(self, head, body):
    '''Takes a rule's head and body and processes it to expand any EBNF.'''
    from string import ascii_uppercase
    from random import choice
    unused = list(set(ascii_uppercase) - self.nonterminals)
    body_toks = body.split()
    k = 0
    start = None
    end = None
    kind = None
    newterm = None
    # scan through each character in the rule body
    while k < len(body_toks):
      curr = body_toks[k]
      if start is None and kind is None:
        # if we encounter an opening { or [
        if curr == '{':
          start = k + 1
          kind = 'curly'
        if curr == '[':
          start = k + 1
          kind = 'square'
        if curr == '|':
          # otherwise, split the string on both sides of the pipe
          # and process them separately
          left, right = body.split('|')
          left = left.strip()
          right = right.strip()
          # randomly choose a letter that hasn't been used before
          newterm = choice(unused) 
          # add it to the set of nonterminals of this grammar
          self.nonterminals.add(newterm)
          # the original rule is replaced by this new symbol
          body_toks = [newterm]
          newrule = ' '.join(body_toks)
          # update the rule in the grammar and remove the old one
          self.bnf_rules[head].add(newrule)
          # process the subrules
          self.rule_to_bnf(newterm, left)
          self.rule_to_bnf(newterm, right)
          return ''
      elif start and kind and end is None:
      # now that we have set the start, we look for the corresponding end
        if (curr == '}' and kind == 'curly') or (curr == ']' and kind == 'square'):
          end = k
          # choose a random unused nonterminal symbol
          newterm = choice(unused)
          # add it to the set of nonterminals of this grammar
          self.nonterminals.add(newterm)
          newbody = ' '.join(body_toks[start:end])
          del body_toks[start-1:end+1] # delete the surrounding {} or [] as well as the contents
          body_toks.insert(start-1, newterm)
          newrule = ' '.join(body_toks)
          self.bnf_rules[head].add(newrule)
          # process the subrule
          res = self.rule_to_bnf(newterm,newbody)
          # add different rules based on the type of expansion
          if kind == 'curly':
            self.bnf_rules[newterm].add('%s %s' % (newterm, res))
            self.bnf_rules[newterm].add(self.EPSILON)
          if kind == 'square':
            self.bnf_rules[newterm].add(res)
            self.bnf_rules[newterm].add(self.EPSILON)
      k += 1
    # we've scanned the entire string without hitting any EBNF symbol
    if not start and not end:
      #if body not in self.bnf_rules[head]:
        #self.bnf_rules[head].add(body)
      return body
    return head
    
  def __compute_firsts(self):
    '''Computes the first sets of each nonterminal in this grammar.'''
    while True: # we continue until we can't add anything more
      prev_count = sum([len(s) for s in self.firsts.values()])
      # keep trying to add things to the first sets of each nonterminal in turn
      for sym in self.nonterminals:
        self.firsts[sym].update(self.first(sym))
      curr_count = sum([len(s) for s in self.firsts.values()])
      if prev_count == curr_count: # no more changes can be made
        return self.firsts

  def first(self, sym):
    '''Computes the first set of the nonterminal indicated by sym.'''
    temp_first = set()
    # first(epsilon) = epsilon
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
        # if cont is still true at the end of the loop, then that means epsilon
        # exists in the first set of every symbol we looked at. so we add epsilon
        # to the first set of sym
        temp_first.add(self.EPSILON)
    return temp_first

  def first_sent(self, sent):
    '''Computes the first set of arbitary sentences.
    Takes a string of symbols as an argument, with each symbol separated by spaces.'''
    temp_first = set()
    sentence = sent.split() # split the string into symbols
    n = len(sentence)
    if n == 1: # if the string only has 1 character, then just call first() on it
      sym = sentence[0]
      return self.first(sym)
    for i in xrange(n):
      sym = sentence[i]
      t = self.first(sym)
      if self.EPSILON in t: # if epsilon in first(X_i), then do first_sent(X_(i+1))
        t.remove(self.EPSILON)
        temp_first.update(t)
        newsent = ' '.join(sentence[i+1:])
        if newsent:
          temp_first.update(self.first_sent(newsent))
        return temp_first
      return t # else just return first(X_i) if first(X_i) doesn't contain epsilon

  def get_firsts(self, sym=''):
    '''Returns the first set of this grammar.
    Takes an optional symbol argument if we want to get the first set of a particular
    symbol.
    If the symbol doesn't exist, return all the first sets in the grammar.'''
    if self.firsts:
      if sym:
        # if the first sets have been computed and there's one for this symbol
        # then just do a dictionary lookup!
        return self.firsts[sym]
      return self.firsts
    # otherwise, compute the first sets
    self.__compute_firsts()
    if sym: # and then attempt to lookup the symbol
      return self.firsts[sym]
    return self.firsts

  def __compute_follows(self):
    '''Compute the follow sets of this grammar.'''
    self.follows[self.start_sym].add(self.INPUT_END)
    while True:
      prev_count = sum([len(s) for s in self.follows.values()])
      for sym in self.nonterminals:
        self.follow(sym)
      curr_count = sum([len(s) for s in self.follows.values()])
      if prev_count == curr_count: # nothing to add, so finish
        return self.follows

  def follow(self, sym):
    '''Compute the follow set for a particular symbol sym.'''
    for rule_body in self.rules[sym]:
      tokens = rule_body.split()
      k = 0
      n = len(tokens)
      while k < n:
        # for productions sym -> curr
        curr_sym = tokens[k]
        if curr_sym in self.nonterminals:
          if k == n-1: # this means that first(X_i+1...) is epsilon
            # so add follows(sym) to follow(curr)
            self.follows[curr_sym].update(self.follows[sym])
          else:
            # find first(X_i+1...)
            sentence = ' '.join(tokens[k+1:])
            f = self.first_sent(sentence)
            if self.EPSILON in f: # if epsilon in the first set, add follow(sym) to follow(curr)
              self.follows[curr_sym].update(self.follows[sym])
              f.remove(self.EPSILON)
            self.follows[curr_sym].update(f)
        k += 1
    return self.follows[sym]

  def get_follows(self, sym=''):
    '''Get the follow set of this grammar, or a particular symbol.'''
    if self.follows:
      if sym: # if the sets have been computed and this symbol exists
        return self.follows[sym]
      return self.follows
    self.__compute_follows() # otherwise, compute the follow sets of this grammar
    if sym:
      return self.follows[sym]
    return self.follows

  def get_rulenum(self, rule):
    '''Get the index number of the given rule string.'''
    if rule in self.rule_order:
      return self.rule_order[rule]
    return -1

  def get_rule(self, num):
    '''Get the rule at a particular index number.'''
    if num in self.rule_index:
      return self.rule_index[num]
    return ''

  def get_rules(self):
    '''Get all rules of this grammar.'''
    return self.rules

  def get_startsym(self):
    '''Get the start symbol of this grammar.'''
    return self.start_sym

  def get_nonterminals(self):
    '''Get the set of nonterminals in this grammar.'''
    return self.nonterminals

class Parser(object):
  def __init__(self, grammar):
    '''Create a new Parser object by supplying a valid grammar object.'''
    self.grammar = grammar
    self.__create_table() # create the parse table

  def __create_table(self): # follows the algorithm in the assignment spec
    from collections import defaultdict
    self.table = defaultdict(dict)
    rules = self.grammar.get_rules()
    for rule_head in rules: # for each rule
      for rule_body in rules[rule_head]:
        r = (' %s ' % self.grammar.DERIVE_SYM).join([rule_head, rule_body])
        ruleno = self.grammar.get_rulenum(r) # get the rule index of this rule
        first = self.grammar.first_sent(rule_body) # compute its first set
        for sym in first:
          if sym != self.grammar.EPSILON:
            v = self.table[rule_head].get(sym)
            if v and v != ruleno: # if there's already something there
              raise IncorrectGrammar('Grammar is not LL(1)!')
            self.table[rule_head][sym] = ruleno
        if self.grammar.EPSILON in first:
          follow = self.grammar.get_follows(rule_head)
          for sym in follow:
            v = self.table[rule_head].get(sym)
            if v and v != ruleno: # if there's already something there
              raise IncorrectGrammar('Grammar is not LL(1)!')
            self.table[rule_head][sym] = ruleno
          if self.grammar.INPUT_END in follow:
            v = self.table[rule_head].get(self.grammar.INPUT_END)
            if v and v != ruleno: # if there's already something there
              raise IncorrectGrammar('Grammar is not LL(1)!')
            self.table[rule_head][self.grammar.INPUT_END] = ruleno

  def get_table(self):
    '''Get the parse table.'''
    return self.table

  def get_rule(self, nonterm, term):
    '''Get the parse rule with a particular nonterminal and terminal.'''
    ruleno = self.table[nonterm].get(term)
    if ruleno is not None: # if ruleno is None, then there is no rule here
      return self.grammar.get_rule(ruleno)

  def parse(self, string): # follows the algorithm given in the assignment spec
    from collections import deque
    stack = deque()
    stack.appendleft(self.grammar.get_startsym())
    in_stream = iter(string+self.grammar.INPUT_END)
    curr = in_stream.next()
    while stack:
      top = stack[0]
      if top in self.grammar.get_nonterminals():
        rule = self.get_rule(top, curr)
        if rule:
          stack.popleft()
          sym, body = rule.split(self.grammar.DERIVE_SYM)
          body_syms = body.strip().split()
          body_syms.reverse()
          stack.extendleft(body_syms)
        else:
          return False
      elif top == curr:
        if top != self.grammar.INPUT_END:
          stack.popleft()
          curr = in_stream.next()
      # if we hit an epsilon, consume it without matching any input
      elif top == self.grammar.EPSILON:
        stack.popleft()
      else:
        return False
    if curr != self.grammar.INPUT_END:
      return False
    return True

class IncorrectGrammar(Exception):
  pass
