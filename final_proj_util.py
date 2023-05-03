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
# definition of class CnfFormula
# for csc427 semester 232 (jan 2023-may 2023)
# last-update:
#      20 April 2023 -bjr: copied from proj8
#
# copyright (c) 2020-2023 burton rosenberg All rights reserved.
#

# A cnf is represented as a list of clauses;
#    each clause a list of literals;
#    each literal a pair of a string and a boolean:
#       the string is the variable name, 
#       the boolean is True for plain variables and False or negated variables.

# A truth assignment is a dictionary from the variable name to a boolean value

class Booleans:
   
    def __init__(self,n):
        assert n>0, 'n must be a postitive integer'
        self.n = n
        self.seq = [True for i in range(n)]
    
    def enum(self):
        for i in range(2**self.n):
            k = 1
            for j in range(self.n):
                self.seq[j] = (i & k)==0
                k <<= 1
            yield self.seq

class CnfFormula: 

    def __init__(self,cnf,verbose=False):
        self.cnf = cnf
        self.var = []
        for clause in self.cnf:
            for variable in clause:
                if variable[0] not in self.var:
                    self.var.append(variable[0])
        self.verbose = verbose
                    
    # respond to a print with a string representation of the formula
    def __repr__(self):
        def p_aux(c,s):
            f = False
            s += '('
            for v in c:
                if f: s += ' OR '
                f = True
                if v[1]: s += f'{v[0]}'
                else: s += f'~{v[0]}'
            s += ')'
            return s    
        s, f = '', False
        for clause in self.cnf:
            if f: s += ' AND '
            f, s = True, p_aux(clause,s)
        return s
    
    def make_assignment(self,bools):
        d, i = {}, 0
        for l in self.var:
            d[l] = bools[i]
            i +=1
        if self.verbose: print(f'assignment: {d}')
        return d

    ## write code here

    def is_3cnf(self):
        for clause in self.cnf:
            if len(clause)!=3:
                return False
        return True

    # write code here

    def evaluate(self, assignment):
        
        def evaluate_aux(disjunct,assignment):
            for v in disjunct:
                assert v[0] in assignment, "missing variable in assignment"
                if assignment[v[0]] == v[1]:
                    return True
            return False

        for disjunct in self.cnf:
            if not evaluate_aux(disjunct,assignment):
                return False
        return True
    
    def is_sat(self):
        bools = Booleans(len(self.var))
        for trial in bools.enum():
            a = self.make_assignment(trial)
            if self.evaluate(a): True
        return False

    def count_sat(self):
        a_l = []
        bools = Booleans(len(self.var))
        for trial in bools.enum():
            a = self.make_assignment(trial)
            if self.evaluate(a): a_l.append(a.copy())
        return a_l

class CYK:
    
    # https://github.com/lagmoellertim/pyCYK.git
    # MIT License Copyright (c) 2019 Tim-Luca Lagmöller
    
    """
    startstate = "S"

    grammar = {
        startstate:["VaE","VbF"],
        "G":["GG","a","b","VaVb"],
        "E":["GVa","a"],
        "F":["GVb","b"],
        "Va":["a"],
        "Vb":["b"]
    }

    word = "abacba"
    
    cyk = CYK(grammar, startstate)
    cyk.checkWord(word) #Returns True or False
    
    """
    
    def __init__(self, grammar, startstate):
        self.grammar = grammar
        self.startstate = startstate

    def __getValidCombinations(self, left_collection_set, right_collection_set):
        valid_combinations = []
        for num_collection, left_collection in enumerate(left_collection_set):
            right_collection = right_collection_set[num_collection]
            for left_item in left_collection:
                for right_item in right_collection:
                    combination = left_item + right_item
                    for key, value in self.grammar.items():
                        if combination in value:
                            if not key in valid_combinations:
                                valid_combinations.append(key)
        return valid_combinations

    def __getCollectionSets(self, full_table, x_position, x_offset):
        table_segment = []
        y_position = 0
        while x_offset >= 2:
            item_set = full_table[y_position][x_position:x_position+x_offset]
            if x_offset > len(item_set):
                return None
            table_segment.append(item_set)
            x_offset -= 1
            y_position += 1
        vertical_combinations = []
        horizontal_combinations = []
        for item in table_segment:
            vertical_combinations.append(item[0])
            horizontal_combinations.append(item[-1])
        return vertical_combinations[::-1], horizontal_combinations
        
    def __generateTable(self, word):
        table = [[]]
        for letter in word:
            valid_states = []
            for key, value in self.grammar.items():
                if letter in value:
                    valid_states.append(key)
            table[0].append(valid_states)
        for x_offset in range(2,len(word)+1):
            table.append([])
            for x_position in range(len(word)):
                collection_sets = self.__getCollectionSets(table, x_position, x_offset)
                if collection_sets:
                    table[-1].append(self.__getValidCombinations(*collection_sets))
        
        return table
        
    def checkWord(self, word):
        return self.startstate in self.__generateTable(word)[-1][-1]

            
            
        