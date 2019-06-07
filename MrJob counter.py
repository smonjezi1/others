from __future__ import unicode_literals
import unittest
import mwparserfromhell
from mwparserfromhell import parser
from mwparserfromhell.compat import range
from mwparserfromhell.nodes import Tag, Template, Text, Wikilink
from mwparserfromhell.nodes.extras import Parameter

#from ._test_tree_equality import TreeEqualityTestCase, wrap, wraptext
#def mapper(self, _, line):
#    bigString = ''.join(re.findall(r'(<text xml:space="preserve">.*</text>)',line))
#    root = etree.fromstring(bigString.decode('utf-8'))
#    if not(bigString == ''):
#        bigString = etree.tostring(root,method='text', encoding = "UTF-8")    
#        wikicode = mwparserfromhell.parse(bigString)
#        bigString = wikicode.strip_code()
#        yield bigString, None

#def reducer(self, key, values):
#    yield key, None

#def steps(self):
#    return [
#        MRStep(mapper=self.mapper, reducer=self.reducer)
#    ]
        
from mrjob.job import MRJob
from mrjob.step import MRStep
import re
from lxml import etree


WORD_RE = re.compile(r"\w+")

class MRWordCount(MRJob):
   # each value is a line in input file
   def mapper(self, key, value):
       for word in WORD_RE.findall(value):
           yield word.lower(), 1

   def combiner(self, word, counts):
       yield word, sum(counts)

   def reducer(self, key, values):
       yield key, sum(values)

if __name__ == '__main__':
   MRWordCount.run()