
"""Parse implements the functions for parsing a propositional logic
   proposition.

   Input syntax of propositions:
     an input proposition is a string structured according to these
     grammar rules:

   E ::=  T op T  |  T
   T ::=  -F  |  F
   F ::=  p  |  ( E )
          where  op  is any of  &, |, ->
                 p   is an alphabetic letter (or string of letters)

   All compound propositions must be bracketed with parens.
   Examples:   (p | q) & r 
               -( p -> -s )
               - ( - p )
               ((a -> (b)) )
               p
   
   These examples are incorrect because they lack adequate parens:
       p | q | r
       - -p

   Format of parsed propsition: a nested listed of this form:

   L ::=  [ op, L, L ]  |  [ "-", L ]  |  "p"
          where op is any of  "&", "|", "->"
                p  is a lower-case letter

  The nested list is a simple-minded representation of a parse tree.
  Here are the parsed nested lists corresponding to the above examples:
      ["&", ["|", "p", "q"], "r"]
      ["-", ["->", "p", ["-", "s"]]]
      ["-", ["-", "p"]]
      ["->", "a", "b"]
      "p"
"""

#Global data structures for parsing:

tokens =  []   # holds the list of symbols in the input proposition
symbol = ""    # holds the next symbol to be placed into the parse tree

# Operators used to parse:
EOF = "$"
AND = "&"
ALTAND = "^"
OR = "|"
ALTOR = "v"
NOT = "-"
IMPLIES = "->"
LEFTPAREN = "("
RIGHTPAREN = ")"
SPACE = " "
NEWLINE = "\\n"
BINARYOPS = (AND, OR, NOT, IMPLIES)
SEPARATORS = (AND, OR, NOT, LEFTPAREN, RIGHTPAREN, SPACE, NEWLINE)




def scan(text) :
    """scan splits apart the symbols in  text  into a list.

       pre:  text is a string holding a proposition
       post: answer is a list of the words and symbols within text
             (spaces and newlines are removed)"""
    next = ""  # the next symbol/word to be added to the answer list
    answer = []
    for letter in text:
        """{ invariant:  answer + next + letter  equals all the words/symbols
              read so far from  text  with spaces/newlines  removed }"""
        # Convert ALTAND to AND  
        if letter == ALTAND:
            #print "WARNING: Replacing ^ with &"
            letter = AND
        # Convert ALTOR to OR  
        if letter == ALTOR:
            #print "WARNING: Replacing v with |"
            letter = OR
        # see if word in  next  is complete and should be appended to answer:
        if letter in SEPARATORS and next != "" :
            answer.append(next)
            next = ""
        elif next in SEPARATORS :
            if letter == ">" :
                answer.append(IMPLIES)
                letter = ""   # ouch --- not a nice thing to do...
            else :
                answer.append(next)
            next = ""
        else :
            pass  # word in  next  not completed yet
        """{ assert: next  holds "" or an incomplete word }"""
        if letter != SPACE and letter != NEWLINE :
            next = next + letter

    """{ assert: all of text is read, so  answer + next  equals  text }"""
    if next != "" :
        answer.append(next)
    return answer
            


def parse(wordlist) :
    """parse returns the nested list that represents  wordlist's  parse tree.
       pre:  wordlist is a list of symbols that spell out a well-formed
             proposition
       post: answer is  wordlist's parse tree, in the format described earlier"""
    global tokens, symbol
    tokens = wordlist
    getNext()
    answer = parseE()
    if symbol != EOF :  # consumed all the symbols ?
        raise SyntaxError, "extra symbols: %s, %s" % (symbol, tokens)
        #print "error: extra symbols:", symbol, tokens
    return answer


def getNext() :
    """getNext removes the next symbol from the  tokens  list and copies it
       into  symbol.  If tokens is [], then  symbol = EOF"""
    global tokens, symbol
    if len(tokens) == 0 :
        symbol = EOF
    else :
        symbol = tokens[0]
        tokens = tokens[1:]


def parseE():
    """builds a tree (nested list) that matches this grammar rule:
       E ::=  T op T  |  T """
    tree1 = parseT()
    if symbol in BINARYOPS :  # T op T
        op = symbol
        getNext();
        tree2 = parseT()
        answer = [op, tree1, tree2]
    else :  # T
        answer = tree1
    return answer
        


def parseT():
    """builds a tree (nested list) that matches this grammar rule:
       T ::=  - F  |  F"""
    if symbol == NOT :  # - F
        getNext()
        tree = parseF()
        answer = [NOT, tree]
    else :  # F
        answer = parseF()
    return answer
        


def parseF():
    """builds a tree (nested list) that matches this grammar rule:
       F ::=  p  |  ( E )"""
    if symbol.isalnum() : # p
        answer = symbol
        getNext()
    elif symbol == "(" :  # ( E ) 
        getNext()
        answer = parseE()
        if symbol == ")" :
            getNext()
        else :
            raise SyntaxError, "F1: missing right paren"
            #print "error F1: missing right paren"
    else :
        answer = []
        raise SyntaxError, "F2: illegal symbol"
        #print "error F2: illegal symbol"
    return answer

if __name__ == '__main__':
#def main() :
    """main lets you interactively type a proposition and parse it.
       Input: a proposition according to the above grammar
       Output: the parse tree"""
    text = raw_input("Type proposition: ")
    tree = parse(scan(text))
    print "parse:", tree

