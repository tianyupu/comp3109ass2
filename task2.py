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
  try:
    p = common.Parser(g)
    parsetable = p.get_table()
    for nonterm in parsetable:
      for term in parsetable[nonterm]:
        print 'R[%s, %s] = %s' % (nonterm, term, parsetable[nonterm][term])
  except common.IncorrectGrammar, e:
    print e
