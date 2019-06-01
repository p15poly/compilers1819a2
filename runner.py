
"""
GRAMMAR
-------
Stmt_list   -> Stmt Stmt_list | .
Stmt        -> id equals Expr | print Expr
Expr        -> Term Term_tail.
Term_tail   -> xor Term Term_tail | .
Term        -> Factor Factor_tail.
Factor_tail -> or Factor Factor_tail | .
Factor      -> Atom Atom_tail.
Atom_tail   -> and Atom Atom_tail | .
Atom        -> leftPar Expr rightPar | id | number
FIRST sets
----------
Stmt_list:		id print
Stmt:			id print
Term_tail:		xor
Term:			leftPar id number
Factor_tail:	or
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
		binary = plex.Rep1(binary)
		name = letter + plex.Rep(letter|decimal)
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
			(binary, 'BIN_N'),
			(andOp, plex.TEXT),
			(orOp, plex.TEXT),
			(xorOp, plex.TEXT),
			(name, 'id')				
			])

		self.list = {}	# list of variables
		
		# create and store the scanner object
		self.scanner = plex.Scanner(self.lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		
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
		if self.la=='id' or self.la=='print':
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
			return		
		else if self.la =='print':	
			self.match('print')
			self.expr()
			return
			
		else:
			raise ParseError('in stmt: "id" or "print" expected')
	
	
	def expr(self):
		if self.la == '(' or self.la=='id' or self.la == 'BIN_N':
			term1 = self.term()
			
			while self.la == 'xor':
				self.match('xor')
				term2 = self.term()
				term1 = term1^term2		
			if self.la ==')' or self.la=='id' or self.la == 'print' or self.la == None:
				return term1
			else:
				raise ParseError('in expr: "xor" expected')
		else:
			raise ParseError('in expr: "(", "id" or "BIN_N" expected')

		
	def term(self):
		if self.la =='(' or self.la =='id' or self.la == 'BIN_N':
			factor1 = self.factor()
			while self.la == 'or':
				self.match('or')
				factor2 = self.factor()
				factor1 = factor1|factor2
			if self.la ==')' or self.la =='xor' or self.la =='id' or self.la =='print' or self.la == None:
				return factor1
			else:
				raise ParseError('in term: "or" expected')

		else:
			raise ParseError('in term: "(", "id" or "BIN_N" expected')


	def factor(self):
		if self.la =='(' or self.la =='id' or self.la =='BIN_N':
			atom1 = self.atom()
			while self.la == 'and':
				self.match('and')
				atom2 = self.factor()
				atom1 = atom1&atom2
			if self.la ==')' or self.la =='or' or self.la =='xor' or self.la=='id' or self.la =='print' or self.la == None:
				return atom1
			else:
				raise ParseError('in factor: "and" expected')
		else:
			raise ParseError('in factor: "(", "id" or "BIN_N" expected')

	def atom(self):
		if self.la == '(':
            self.match('(')
            self.expr()
            self.match(')')
            return
        else if self.la =='id':
            self.match('id')
            return
        else if self.la =='BIN_N':
            self.match('BIN_N')
            return
        else:
            raise ParseError('in atom: "(", "id" or "BIN_N" expected')


		
# the main part of program
parser = MyParser()
with open("parsing.txt","r") as fp:
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
