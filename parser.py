
"""
Grammar
-------
Stmt_list   -> Stmt Stmt_list | .
Stmt        -> id assign Expr | print Expr.
Expr        -> Term Term_tail.
Term_tail   -> xor Term Term_tail | .
Term        -> Factor Factor_tail.
Factor_tail -> or Factor Factor_tail | .
Factor      -> Atom Atom_tail.
Atom_tail   -> and Atom Atom_tail | .
Atom        -> leftPar Expr rightPar | id | number.
FIRST sets
----------
Stmt_list:		id print
Stmt:			id print
Term_tail:		xor
Term:			leftPar id number
Factor_tail:	        or
Factor:			leftPar id number
Atom_tail:		and
Atom:			leftPar id number
Expr:			leftPar id number
FOLLOW sets
-----------
Stmt_list:		∅
Stmt:			id print
Term_tail:		rightPar id print
Term:			rightPar xor id print
Factor_tail:	        rightPar xor id print
Factor:			rightPar or xor id print
Atom_tail:		rightPar or xor id print
Atom:			rightPar and or xor id print
Expr:			rightPar id print
"""


import plex



class ParseError(Exception):
	pass



class MyParser:
	
	def create_scanner(self,fp):

		# define some pattern constructs
		decimal = plex.Range('09')
		binary = plex.Range('01')
		letter = plex.Range('azAZ')
		
		equals = plex.Str('=')
		lPar = plex.Str('(')
		rPar = plex.Str(')')
		space = plex.Any(' \n\t')
		binary = plex.Rep1(binaryDigit)
		name = letter + plex.Rep(letter|decimalDigit)
		printOp = plex.Str('print')
		andOp = plex.Str('and')			
		orOp = plex.Str('or')
		xorOp = plex.Str('xor')

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		self.lexicon = plex.Lexicon([
			(space,plex.IGNORE),
			(lPar, plex.TEXT),
			(rPar, plex.TEXT),
			(equals, plex.TEXT),
			(printOp, plex.TEXT),
			(binary, 'BINARY_NUM'),
			(andOp, plex.TEXT),
			(orOp, plex.TEXT),
			(xorOp, plex.TEXT),
			(name, 'id')				
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(self.lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.stmt_list()
	
			
	def stmt_list(self):
		if self.la=='id' or self.la =='print':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError('stmt_list: "id" or "print" expected')
			 	
	
	def stmt(self):
		if self.la =='id':
			self.match('id')
			self.match('=')
			self.expr()
		elif self.la=='print':	
			self.match('print')
			self.expr()
		else:
			raise ParseError('in stmt: "id" or "print" expected')
	
	
	def expr(self):
		if self.la =='(' or self.la =='id' or self.la =='BIN_N':
			self.term()
			self.term_tail
		else:
			raise ParseError('in expr: "(", "id" or "BIN_N" expected')

	def term_tail(self):
		if self.la =='xor':
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la ==')' or self.la =='id' or self.la =='print' or self.la == None:
			return
		else:
			raise ParseError('in term_tail: "xor", ")", '+ '"id" or "print" expected')

	def term(self):
		if self.la =='(' or self.la =='id' or self.la =='BIN_N':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError('in term: "(, "id" or "BIN_N" expected')
		
	def factor_tail(self):
		if self.la =='or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la ==')' or self.la =='xor' or self.la=='id' or self.la=='print' or self.la == None:
			return
		else:
			raise ParseError('in factor_tail: "or", ")", "xor", '+ '" id" or "print" expected')

	def factor(self):
		if self.la =='(' or self.la == 'id' or self.la == 'BIN_N':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError('in factor: "(", "id" or "BIN_N" expected')

	def atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la ==')' or self.la == 'or' or self.la == 'xor' or self.la =='id' or self.la == 'print' or self.la == None:
			return
		else:
			raise ParseError('in atom_tail: "and", ")", "or", "xor", "id" or "print" expected')

	def atom(self):
		if self.la =='(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la=='id':
			self.match('id')
		elif self.la=='BIN_N':
			self.match('BIN_N')
		else:
			raise ParseError('in atom: "(", "id" or "BIN_N" expected')



		
# the main part of program

# create the parser object
parser = MyParser()

with open("recursive-descent-parsing.txt","r") as fp:
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
