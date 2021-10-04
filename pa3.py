# Name: pa3.py
# Author(s): Justin Cavalli, Shaydon Bodemar
# Date: 10/28/2020
# Description: Reads in a regular expression and simulates it as a DFA

from collections import defaultdict


class InvalidExpression(Exception):
	pass


class SyntaxTreeNode:
	def __init__(self, LeftNode=None, RightNode=None, val=''):
		"""
		Initializes a SyntaxTreeNode object which has two children that are
		also SyntaxTreeNodes (default value None) and an associated value
		representing the stored operator/operand.
		"""
		self.LeftNode = LeftNode
		self.RightNode = RightNode
		self.val = val


class RegEx:
	def __init__(self, filename):
		""" 
		Initializes a RegEx object from the specifications
		in the file whose name is filename.
		"""
		self.operators = {'|', '*'}
		self.alphabet = {'e': 'e'}
		file1 = open(filename, 'r')
		temp = file1.readline()[:-1]
		for char in temp:
			self.alphabet[char] = char
		self.regex = file1.readline()[:-1]
		self.SyntaxTree = None
		self.check_regex()

		# convert regex to NFA
		self.create_syntax_tree()
		self.num_states = 0
		self.nfa_transition_table = defaultdict(list)
		NFA = self.to_nfa()
		# convert NFA to DFA
		self.DFA = NFA.toDFA()


	def to_nfa(self):
		"""
		Transition the stored regex string to an NFA by manually setting
		each data structure for an NFA appropiately and returning the
		resulting object.
		"""
		ans_NFA = NFA()
		ans_NFA.start_state = '1'
		self.num_states += 1
		ans_NFA.accept_states.append(str(2))
		self.num_states += 1
		# handle case of empty set (no value in SyntaxTree and no children)
		if self.SyntaxTree.val == '':
			ans_NFA.transition_table[ans_NFA.start_state + '\'e\''] = 2
		self.add_transition(self.SyntaxTree, 1, 2)
		ans_NFA.transition_table = self.nfa_transition_table
		self.alphabet.pop('e', None)
		for key in self.alphabet:
			ans_NFA.alphabet = ans_NFA.alphabet + key
		ans_NFA.num_states = self.num_states
		return ans_NFA


	def add_transition(self, root, left_state, right_state):
		"""
		Recursively implement a depth first traversal of the SyntaxTree.
		For each root, states are added to the NFA transition table corresponding to the operator.
		"""
		if root.val == '|':
			self.num_states += 4
			temp = self.num_states
			self.nfa_transition_table[str(left_state) + '\'e\''].append(str(self.num_states - 3))
			self.nfa_transition_table[str(left_state) + '\'e\''].append(str(self.num_states - 1))
			self.nfa_transition_table[str(self.num_states-2) + '\'e\''].append(str(right_state))
			self.nfa_transition_table[str(self.num_states) + '\'e\''].append(str(right_state))
			self.add_transition(root.LeftNode, temp-3, temp-2)
			self.add_transition(root.RightNode, temp-1, temp)
		elif root.val == ' ':
			self.num_states += 1
			temp = self.num_states
			self.add_transition(root.LeftNode, left_state, temp)
			self.add_transition(root.RightNode, temp, right_state)
		elif root.val == '*':
			self.num_states += 2
			self.nfa_transition_table[str(left_state) + '\'e\''].append(str(self.num_states - 1))
			self.nfa_transition_table[str(self.num_states) + '\'e\''].append(str(self.num_states - 1))
			self.nfa_transition_table[str(left_state) + '\'e\''].append(str(right_state))
			self.nfa_transition_table[str(self.num_states) + '\'e\''].append(str(right_state))
			self.add_transition(root.LeftNode, self.num_states - 1, self.num_states)
		else:
			self.nfa_transition_table[str(left_state) + '\'' + root.val + '\''].append(str(right_state))
			return

	
	def create_syntax_tree(self):
		"""
		Changes string regex into an Abstract Syntax Tree.
		"""
		prev_char = None
		operands = []
		operators = []

		for char in self.regex:
			if self.implied_concatenation(prev_char, char):
				while len(operators) > 0 and (operators[len(operators)-1].val == '*' or operators[len(operators)-1].val == ' '):
					# pop all operators of greater or equal precendence
					if operators[len(operators)-1].val == '*':
						operators[len(operators)-1].LeftNode = operands.pop()
						operands.append(operators.pop())
					elif operators[len(operators)-1].val == ' ':
						operators[len(operators)-1].RightNode = operands.pop()
						operators[len(operators)-1].LeftNode = operands.pop()
						operands.append(operators.pop())
				operators.append(SyntaxTreeNode(val=' '))
				if char == '(':
					operators.append(SyntaxTreeNode(val=char))
				else:
					operands.append(SyntaxTreeNode(val=char))
			else:
				if char in self.alphabet:
					operands.append(SyntaxTreeNode(val=char))
				elif char == '(':
					operators.append(SyntaxTreeNode(val=char))
				elif char == '*':
					if len(operators) > 0 and operators[len(operators)-1].val == '*':
						# pop any other star operators present
						operators[len(operators)-1].LeftNode = operands.pop()
						operands.append(operators.pop())
						operators.append(SyntaxTreeNode(val=char))
					else:
						temp = SyntaxTreeNode(val=char,LeftNode=operands.pop())
						operands.append(temp)
				elif char == '|':
					while len(operators) > 0:
						# pop back all operands since all are greater or equal precendence to '|'
						if operators[len(operators)-1].val == '*':
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
						elif operators[len(operators)-1].val == ' ':
							operators[len(operators)-1].RightNode = operands.pop()
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
						elif operators[len(operators)-1].val == '|':
							operators[len(operators)-1].RightNode = operands.pop()
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
						else:
							break
					operators.append(SyntaxTreeNode(val=char))
				elif char == ')':
					# pop stuff all the way back to open paren
					while operators[len(operators)-1].val != '(':
						if operators[len(operators)-1].val == '*':
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
						elif operators[len(operators)-1].val == ' ':
							operators[len(operators)-1].RightNode = operands.pop()
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
						elif operators[len(operators)-1].val == '|':
							operators[len(operators)-1].RightNode = operands.pop()
							operators[len(operators)-1].LeftNode = operands.pop()
							operands.append(operators.pop())
					operators.pop()
			prev_char = char
		if len(operators) > 0 and operators[len(operators)-1].val == '*':
			operators[len(operators)-1].LeftNode = operands.pop()
			operands.append(operators.pop())
		else:
			while len(operators) > 0:
				operators[len(operators)-1].RightNode = operands.pop()
				operators[len(operators)-1].LeftNode = operands.pop()
				operands.append(operators.pop())
		self.SyntaxTree = operands.pop()


	def simulate(self, str):
		"""
		Returns True if the string str is in the language of
		the 'self' regular expression.
		"""
		return self.DFA.simulate(str)


	def implied_concatenation(self, prev, cur):
		"""
		Returns True if the combination of characters represents
		implied concatenation.
		"""
		if prev in self.alphabet or prev == '*' or prev == ')':
			if cur in self.alphabet or cur == '(':
				return True
		return False


	#TODO: fix false negatives for check_regex. Look at how prev is handled
	def check_regex(self):
		#regex 7... are incorrectly invalidated
		self.regex = self.regex.replace(' ', '')
		if self.regex == 'N':
			return
		if self.regex[0] in self.operators:
			raise InvalidExpression('Regex cannot start with an operator')
		prev = ''
		paren = []
		for char in self.regex:
			# e must be included in the alphabet
			if char not in self.alphabet and char not in self.operators and char != '(' and char != ')':
				raise InvalidExpression('Invalid character within expression')
			if char == '(':
				paren.append('(')
			if char == ')':
				if len(paren) == 0:
					raise InvalidExpression('Invalid order/number of parentheses')
				paren.pop()
			if prev == '|':
				if char == '*' or char == '|':
					raise InvalidExpression('Invalid sequence of operators')
			if prev == '*':
				if char == '*':
					raise InvalidExpression('Invalid sequence of operators')
			prev = char
			# e could be handeled but is not technically invalid
		if(prev == '|'):
			raise InvalidExpression('Invalid sequence of operators')
		if len(paren) > 0:
			raise InvalidExpression('Invalid number of parentheses')


# you can add other classes here, including DFA and NFA (modified to suit
# the needs of this project).
class NFA:
	""" Simulates an NFA """

	# TODO: modify to accept input from memory rather than from file
	def __init__(self):
		"""
		Initializes NFA from the file whose name is
		nfa_filename.  (So you should create an internal representation
		of the nfa.)
		"""
		self.alphabet = ''
		self.num_states = 0
		self.transition_table = {}
		self.start_state = ''
		self.accept_states = []


	def toDFA(self):
		"""
		Converts the 'self' NFA into an equivalent DFA
		and writes it to the file whose name is dfa_filename.
		The format of the DFA file must have the same format
		as described in the first programming assignment (pa1).
		This file must be able to be opened and simulated by your
		pa1 program.

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""
		# create sorted list of start states for the dfa start state
		start_states = [self.start_state]
		start_states = self.epsilon_transitions(start_states)
		start_states = list(dict.fromkeys(start_states))
		start_states.sort(key=int)
		dfastart_state = ','.join(start_states)

		dfatransition_table = {}

		# create queue of values for new states encountered
		state_queue = []
		state_queue.append(str(0))
		state_queue.append(dfastart_state)

		# enqueue all standalone nfa states
		for i in range(1, self.num_states+1):
			state_queue.append(str(i))

		# create list of accept states and determine if start state is accepted
		dfaaccept_states = []
		for nfa_state in start_states:
			if nfa_state in self.accept_states:
				dfaaccept_states.append(dfastart_state)
				break

		# loop as long as queue contains any unhandled states created
		while(len(state_queue) > 0):
			dfa_state = state_queue.pop(0)
			# know which states from the nfa are present in this dfa state
			nfa_states = dfa_state.split(',')
			# find destination state for every alphabet item
			for item in self.alphabet:

				dfa_entry = dfa_state + '\'' + item + '\''
				if dfa_entry in dfatransition_table:
					continue
				temp = []
				# add destinations to running list for every nfa state present in the dfa state
				for state in nfa_states:
					if state + '\'' + item + '\'' in self.transition_table:
						temp.extend(self.transition_table[state + '\'' + item + '\''])
					else:
						temp.append(str(0))
				# ensure list has only unique, sorted values
				temp = list(dict.fromkeys(temp))
				temp.sort(key=int)
				temp = self.epsilon_transitions(temp)
				temp = list(dict.fromkeys(temp))
				temp.sort(key=int)
				if len(temp) > 1 and temp[0] == '0':
					temp.pop(0)
				# add output state to accept states if one of nfa states is accepted
				accept = False
				for nfa_state in temp:
					if nfa_state in self.accept_states:
						accept = True
						break
				output_dfa_state = ','.join(temp)
				if accept and output_dfa_state not in dfaaccept_states:
					dfaaccept_states.append(output_dfa_state)
				# add this state to the transition table
				dfatransition_table[dfa_entry] = output_dfa_state
				# if created output state is not in the transition table, enqueue to be handled
				if output_dfa_state + '\'' + item + '\'' not in dfatransition_table and output_dfa_state + '\'' + item + '\'' not in state_queue:
					state_queue.append(output_dfa_state)

		out_DFA = DFA()
		out_DFA.start_state = dfastart_state
		out_DFA.accept_states = dfaaccept_states
		out_DFA.transition_table = dfatransition_table
		return out_DFA


	def epsilon_transitions(self, states):
		"""
		Checks if each element in the list 'states' has an epsilon transition. 
		In the case that it does, add this state to the list and continue checking recursively.
		Otherwise, return the new list of states, now accounting for epsilon transitions.
		"""
		for state in states:
			if state + '\'e\'' in self.transition_table:
				states.extend(self.transition_table[state + '\'e\''])
		return states

## Present and necessary to determine the presence of a string in the language once a DFA has been created
class DFA:
	""" Simulates a DFA """
	
	# TODO: modify constructor to take direct inputs rather than file IO
	def __init__(self):
		"""
		Initializes DFA
		"""
		self.transition_table = {}
		self.start_state = 1
		self.accept_states = []

	def simulate(self, string):
		""" 
		Simulates the DFA on input str.  Returns
		True if str is in the language of the DFA,
		and False if not.
		"""
		cur_state = self.start_state
		for i in range (len(string)):
			cur_state = self.transition_table[str(cur_state) + '\'' + string[i] + '\'']
		return cur_state in self.accept_states