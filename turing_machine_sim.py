https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
#
# tm-sim.py
#
# author: bjr
# date: 21 mar 2020
# last update: 22 mar 2020
#    16 mar 2021, updated 
#     3 apr 2021, return conventions for accept/reject
#                 verbose_levels reimplemented
#                 character # is not allowed as a tape symbol
#                 for magical reasons, then " is also not allowed
#                 added class method help()
#    15 apr 2021, made multi-tape
#    19 apr 2021, documentation updated
#    15 mar 2022, updated for session 222 
#    27 mar 2022, add get_tape method
#
# copyright 2023 (c) All Rights Reserved.
#



grammar = """
    M-> (Stanza [emptyline])*
    Stanza-> StartStanza | AcceptStanza | RejectStanza | StateStanza | TapeStanza
    StartStanza-> "start" ":" Ident
    AcceptStanza-> "accept" ":" Ident ([newline] [indent] Ident])*
    RejectStanza-> "reject" ":" Ident ([newline] [indent] Ident])*
    TapeStanza-> "tapes:" number
    StateStanze-> "state" ":" Ident ([newline] [indent] StateTransition)+
    StateTransition-> (Symbol|Special){k} (Symbol|Special){k} (Action){k} Ident
    Action-> l|r|n|L|R|N
    Symbol-> \w | [!$-/]     # a tape symbols are alphanumeric and punctuation ! and $ through /
    Special-> [:_]           # the special wildcard and blank metacharacters
    Ident-> \w+              # name of a state
    """


# The : in a transition rule,
#    - In the read section: wildcard match on that tape
#    - In the write section: the current read symbol on that tape
#    For k tapes, there can only be 0, 1, k-1 or k ':' in the read section
#    and they are matched in that preference order.
#

# The # is reserved as the start of a comment (not part of the BNF)
# Comments begin with a hash # and continue to the end of the line

# A missing transition halts with reject in the non-name reject state.


import string
import sys
import os
import argparse
import re



class TuringMachine:
    
    # class properties
    verbose_levels = {'none':0,'explain':1,'verbose':2, 'debug':3}
    result_reasons = ['ok', 'transition missing', 'time limit']
    all_actions = ["r","l","n"]

    def __init__(self):
        self.start_state = "" # is an state identifier
        self.accept_states = set() # is a set of state identifiers
        self.reject_states = set() # is a set of state identifiers    
        self.transitions = {} # (state,symbol-tuple):(state,symbol-tuple,action-tuple)
        self.current_state = ""
        self.k = 1           # number of tapes
        self.tapes = [ ['_'] for i in range(self.k)]  
        self.positions = [ 0 for i in range(self.k)]
        self.verbose = 0
        self.result = 0
        self.step_count = 0

    def set_start_state(self,state):
        self.start_state = state
        
    def set_k(self,k):
        self.k = k
        self.positions = [ 0 for i in range(self.k)]
        self.tapes = [ ['_'] for i in range(self.k)]

    def set_tape(self,tape_string,k):
        assert k>=0 and k<self.k
        tape_string += '_'
        self.tapes[k] =  ['_' if symbol==':' or symbol==' ' else symbol for symbol in tape_string]

    def add_accept_state(self,state):
        self.accept_states.add(state)

    def add_reject_state(self,state):
        self.reject_states.add(state)
    
    def get_current_state(self):
        return self.curent_state

    def add_transition(self,state_from,read_symbols,write_symbols,actions,state_to):
        assert len(read_symbols)==self.k and len(write_symbols)==self.k and len(actions)==self.k
        
        for action in actions:
            if action.lower() not in self.all_actions:
                # return something instead, nobody likes a chatty program
                return "WARNING: unrecognized action." 
        x = (state_from,read_symbols)
        if x in self.transitions:
            # return something instead, nobody likes a chatty program
            return "WARNING: multiple outgoing states not allowed for DFA's."
        self.transitions[x] = (state_to,write_symbols,actions)
        return None


    def step_transition(self):
        
        c_s = self.current_state
        reads = tuple(self.tapes[i][self.positions[i]] for i in range(self.k))
        
        wild = False
        while True:
            if (c_s,reads) in self.transitions:
                (new_state, symbols, actions ) = self.transitions[(c_s,reads)]
                break

            # exactly one : is allowed
            for i in range(self.k-1,-1,-1):
                x = tuple(reads[j] if i!=j else ':' for j in range(self.k))
                if (c_s,x) in self.transitions:
                    (new_state, symbols, actions ) = self.transitions[(c_s,x)]
                    wild = True
                    break      
            if wild:
                break
            
            # exactly one non : is allowed
            for i in range(self.k-1,-1,-1):
                x = tuple(':' if i!=j else reads[j] for j in range(self.k))
                if (c_s,x) in self.transitions:
                    (new_state, symbols, actions ) = self.transitions[(c_s,x)]
                    wild = True
                    break     
            if wild:
                break
                
            # all : is allowed
            wild_card = tuple(':' for i in range(self.k))
            if (c_s,wild_card) in self.transitions:
                (new_state, symbols, actions ) = self.transitions[(c_s,wild_card)]
                break 

            # here we implement a rejection of convenience, if there is
            # no transition, action is n, and the state does not advance.
            if self.verbose>1:
                reads_p = reads
                if self.k==1:
                    reads_p = reads[0]
                print(f'warning: transition not found: ({c_s},{reads_p})')
            self.result = 1  # transition not found
            return False
        
        # wildcard code
        symbols = tuple(symbols[i] if symbols[i]!=':' else reads[i] for i in range(self.k))

        shout = False
        self.current_state = new_state
        for i in range(self.k):
            self.tapes[i][self.positions[i]] = symbols[i]
            
            if actions[i].lower() != actions[i]:
                shout = True

            if actions[i].lower() == 'l' and self.positions[i]>0:
                self.positions[i] -= 1
            if actions[i].lower() == 'r':
                self.positions[i] += 1
                if self.positions[i]==len(self.tapes[i]):
                    self.tapes[i][self.positions[i]:] = '_'
            if actions[i].lower() == 'n':
                pass
   
        if shout or self.verbose>0:
            self.print_tapes()
        return True

    def compute_init(self):
        self.current_state = self.start_state
        self.result = 0
        self.step_count = 0
        for i in range(self.k):
            self.positions[i] = 0
            self.set_tape('_',i)

    def compute_tm(self,tape_string,step_limit=100,verbose='explain'):
        
        if isinstance(verbose,int):
            self.verbose = verbose
        elif verbose in TuringMachine.verbose_levels:
            self.verbose = TuringMachine.verbose_levels[verbose]
        
        self.compute_init()
        if type(tape_string)==type(''):  # could be an array of strings
            self.set_tape(tape_string,0)

        stop_states = self.accept_states.union(self.reject_states)
        
        if self.verbose > 0:
            self.print_tapes()
        
        self.result = 0  # ok
        res = True
        while self.current_state not in stop_states:
            self.step_count += 1
            res = self.step_transition()
            
            if self.step_count > step_limit:
                self.result = 2  # out of time
                res = False
                break 
            if not res:
                break

        if not res:
            result = False
        else:
            result = self.current_state in self.accept_states
            
        if self.verbose > 0:
            s = 'accept' if result else 'reject'
            print(f'{s} ({self.result_reasons[self.result]})')

        return result

    def is_exception(self):
        return self.result>1
 
    def get_tape(self):
        return ''.join(self.tapes[0])
   
    def get_tapes(self):
        tapes = []
        for t in range(self.k):
            t = self.tapes[t][:]
            # remove trailing blanks; if entirely blank leave one blank
            for i in range(len(t)-1,0,-1):
                if t[i]=='_':
                    del t[i]
                else:
                    break 
            s = ''.join(t)
            tapes.append(s)
        return tapes
        
    def print_tapes(self):
        if self.k==1:
            print(f'{self.step_count} [{self.current_state}]',end='')
        else:
            print(f'{self.step_count} [{self.current_state}]')
        for i in range(self.k):
            t, p = self.tapes[i], self.positions[i]
            s = ''.join(t[:p] + ['['] + [t[p]] + [']'] + t[p+1:])
            print(f'\t{s}')
    
    def print_tm(self):
        print("\nstart state:\n\t",self.start_state)
        print("accept states:\n\t",self.accept_states)
        print("reject states:\n\t",self.reject_states)
        print("transitions:")
        for t in self.transitions:
            print("\t",t,"->",self.transitions[t])
    
    @classmethod
    def help(cls):
        print('The verbose levels are:')
        for level in cls.verbose_levels:
            print(f'\t{cls.verbose_levels[level]}: {level}')
        print()
        print('The grammar for the Turing Machine description is:')
        print(grammar)
        
        
### end class TuringMachine


class MachineParser:

    @staticmethod
    def parse(tm_obj, fa_string):
        """
        Code to parse a Turing Machine description into the Turing Machine object.
        """
        
        fa_array = fa_string.splitlines()
        line_no = 0 
        current_state = ""
        in_state_read = False
        in_accept_read = False
        in_reject_read = False
        state_line_re = '\s+(\w|[!$-/:_])\s+(\w|[!$-/:_])\s+(\w)\s+(\w+)'
        k = 1
        not_seen_a_state_line = True

        for line in fa_array:
            while True:

                # comment lines are fully ignored
                if re.search('^\s*#',line):
                    break

                if re.search('^\s+',line):

                    if in_state_read:
                        m = re.search(state_line_re,line)
                        if m:
                            reads = tuple(m.group(i) for i in range(1,1+k))
                            writes = tuple(m.group(i) for i in range(1+k,1+2*k))
                            actions = tuple(m.group(i) for i in range(1+2*k,1+3*k))
                            to_state = m.group(1+3*k)
                            
                            res = tm_obj.add_transition(current_state,reads,writes,actions,to_state)
                            if res: 
                                print(res, f'{line_no}: {line}')
                                return False
                            break

                    if in_accept_read:
                        m = re.search('\s+(\w+)',line)
                        if m:
                            tm_obj.add_accept_state(m.group(1))
                            break

                    if in_reject_read:
                        m = re.search('\s+(\w+)',line)
                        if m:
                            tm_obj.add_reject_state(m.group(1))
                            break

                in_state_read = False
                in_accept_read = False
                in_reject_read = False

                # blank lines do end multiline input
                if re.search('^\s*$',line):
                    break ;

                m = re.search('^start:\s*(\w+)',line)
                if m:
                    tm_obj.set_start_state(m.group(1))
                    break

                m = re.search('^accept:\s*(\w+)',line)
                if m:
                    tm_obj.add_accept_state(m.group(1))
                    in_accept_read = True
                    break

                m = re.search('^reject:\s*(\w+)',line)
                if m:
                    tm_obj.add_reject_state(m.group(1))
                    in_reject_read = True
                    break

                m = re.search('^tapes:\s*(\d+)',line)
                if m:
                    assert not_seen_a_state_line
                    k = int(m.group(1))
                    tm_obj.set_k(k)
                    state_line_re = '\s+'
                    for i in range(k):
                        state_line_re += '(\w|[!$-/:_])\s+'
                    for i in range(k):
                        state_line_re += '(\w|[!$-/:_])\s+'
                    for i in range(k):
                        state_line_re += '(\w)\s+'
                    state_line_re += '(\w+)'
                    break

                m = re.search('^state:\s*(\w+)',line)
                if m:
                    not_seen_a_state_line = False
                    in_state_read = True
                    current_state = m.group(1)
                    break

                print(f"unparsable line, dropping {line_no}: {line}")
                return False
                break

            line_no += 1
        return True
    
    @staticmethod
    def create_from_description(description):
        tm = TuringMachine()
        MachineParser.parse(tm,description)
        return tm

### end class MachineParser

# note: thought to migrate this into a utility file, but that would create
# a backward incompatibility with versions of this file, within a semester. -28 mar 2022

def create_and_test_turing_machine(label, tm_description, test_cases,verbose='explain'):
    """
    label: a string nameing the test or Turing Machine
    tm_decription: a string with the TM description
    test_cases: a pair of lists, the first being strings in the language, the second being strings not in the language
    """

    print(f'\nTesting {label}')
    tm = MachineParser.create_from_description(tm_description)
    correct = 0
    incorrect = 0
    exception = 0
    side = True
    for test_side in test_cases:
        for s in test_side:
            # assume complexity is some quadratic
            res = tm.compute_tm(s,step_limit=10*(len(s)+5)**2,verbose=verbose)
            if tm.is_exception():
                print(f'exception:\t|{s}|')
                exception += 1
                continue
            if res==True:
                print(f'accept:\t|{s}|')
            else:
                print(f'reject:\t|{s}|')
            if res==side:
                correct += 1
            else:
                incorrect += 1
        side = not side
    print(f'correct: {correct}, incorrect: {incorrect}, exceptions: {exception}')
    return incorrect == 0 and exception == 0


### end def's


