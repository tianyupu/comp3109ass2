if __name__ == '__main__':
  import sys
  import common
  try:
    grammar_def = sys.argv[1]
    sentence_file = sys.argv[2]
  except IndexError, e:
    print e
    sys.exit(-1)
  g = common.Grammar(grammar_def)
  sentences = open(sentence_file, 'rU').readlines()
  try:
    p = common.Parser(g)
    for s in sentences:
      if p.parse(s.strip()):
        print 'accept'
      else:
        print 'reject'
  except common.IncorrectGrammar, e:
    print e
