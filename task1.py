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
  firsts = g.get_firsts()
  print 'First:'
  for sym in firsts:
    print '  %s -> %s' % (sym, ' '.join(firsts[sym]))
  follows = g.get_follows()
  print 'Follows:'
  for sym in follows:
    print '  %s -> %s' % (sym, ' '.join(follows[sym]))
