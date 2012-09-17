#!/usr/bin/python

if __name__ == '__main__':
  import sys
  import common
  try:
    grammar_def = sys.argv[1]
  except IndexError, e:
    print 'No grammar file supplied'
    sys.exit(-1)
  g = common.Grammar(grammar_def)
  rules = g.grammar_to_bnf()
  for head in rules:
    for body in rules[head]:
      print '%s ::= %s' % (head, body)
