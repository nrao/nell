"""CNF  maps a parse tree of a proposition into its conjunctive-normal form.

   INPUT FORMAT: a parse tree (nested list) of this format:

   L ::=  [ op, L, L ]  |  [ "-", L ]  |  "p"
          where op is any of  "&", "v", "->"
                p  is a string of letters

  Here are examples:
      ["&", ["v", "p", "q"], "r"]
      ["-", ["->", "p", ["-", "s"]]]
      ["-", ["-", "p"]]
      ["->", "a", "b"]
      "p"

   If the input nested list does _not_ match the above format, 
   the program will crash!

   OUTPUT FORMAT: a nested listed representation of the tree's cnf:

     C ::=  [ D1, D2, ... Dn ]
     D ::=  [ F1, F2, ... Fm ]
     F ::=  "p"  |  "-p"
            where  p  is a string of letters

   Example: the cnf,   (p v q v -r) & (s) & (-p v s),  is presented as the
   nested list,        [["p", "q", "-r"], ["s"], ["-p", "s"]]


   The conversion of a tree into CNF uses the algorithm in the lecture notes,
   Chapter 5.
"""

# operators:
IMPLIES = "->"
NOT = "-"
OR = "v"
AND  = "&"


def main():
    """main lets you test the algorithm with interactive input"""
    import Parse
    text = raw_input("Type a proposition: ")
    print
    prop0 = Parse.parse(Parse.scan(text))
    print "parse tree: "
    print prop0
    print
    prop1 = removeImplications(prop0)
    print "-> removed:"
    print prop1
    print
    prop2 = moveNegations(prop1)
    print "- shifted inwards:"
    print prop2
    print
    prop3 = makeIntoCNF(prop2)
    print "cnf:"
    print  prop3
    print
    prop4 = flattenCNF(prop3)
    print "flattened cnf:"
    print  prop4
    print
    prop5 = removeDuplicates(prop4)
    prop6 = removeTautologies(prop5)
    print "simplified cnf:", prop6

def goSequent() :
    """goSequent helps a user interactively type a sequent to be proved,
       formats it in cnf (where the goal prop is negated),
       and writes it as a string to a textfile.

       The string has the format,   D1 D2 ... Dn,
       where     D ::=  [F1, F2, ... Fm]
                 F ::=  "p"  |  "-p"
                         where  p  is a string of letters
       Example: the input,    p->r, q->r |- (p v q) -> r,
       is mapped to the cnf form,
               [['-p', 'r'], ['-q', 'r'], ['p', 'q'], ['-r']]
       and the string,
               [-p,r][-q,r][p,q][-r]
       is written to the output file that the user requests.
    """
    import Parse
    premises = True
    answer = []
    while premises:
        text = raw_input("Type premise (or |-): ").strip()
        if text == "|-" :
            premises = False
        else :
            prop = cnf( Parse.parse(Parse.scan(text)) )
            answer = answer + prop
    text = raw_input("Type goal prop: ")
    not_text = "-(" + text + ")"
    not_goal =  cnf( Parse.parse(Parse.scan(not_text)) )
    answer = answer + not_goal

    print "clauses are:", answer
    print
    filename = raw_input("Type name of destination file: ")
    output = open(filename, "w")
    textline = ""
    for clause in answer :
        textline = textline + "["
        items = ""
        for literal in clause :
            items = items + "," + literal
        if items != "" :
            items = items[1:]   # forget leading comma
        textline = textline + items + "]"
    print "wrote to", filename + ":", textline
    output.write(textline)
    output.close

      

def cnf(parsetree) :
    """cnf maps  parsetree  into a flattened, simplified cnf list

       pre:  parsetree  is a nested-list parse tree of a proposition
       post: answer is the equivalent, flattened, simplified cnf of parsetree
    """
    cnf1 = makeIntoCNF( moveNegations( removeImplications(parsetree) ) )
    answer =  removeTautologies( removeDuplicates( flattenCNF( cnf1 ) ) )
    return answer
   

def removeImplications(prop) :  # textbook, p.63, calls it, IMPL_FREE
    """removeImplications replaces every implication in  prop  via this 
       equivalence:  P -> Q  -||-  -P v Q

       pre: prop is a nested-list parsetree
       post: answer is equivalent to prop, where every occurrence of
             [IMPLIES, A, B]  is replaced by  [OR, [NOT, A], B]
    """
    if isinstance(prop, str) :
        """{ assert:  prop  is a primitive proposition }"""
        answer = prop
    else :  # isinstance(prop,list) 
        """{ assert: prop  is a compound proposition }"""
        op = prop[0]
        if op == NOT :
            tree = removeImplications(prop[1])
            """{ assert: tree has all implications removed }"""
            answer = [NOT, tree]
        else : # op  is a binary operator
            tree1 = removeImplications(prop[1])
            tree2 = removeImplications(prop[2])
            """{ assert: tree1 and tree2 have all implications removed }"""
            if op == IMPLIES :
                answer = [OR, [NOT, tree1], tree2]
            else :  # op is  AND  or  OR
                answer = [op, tree1, tree2]

    """{ assert: in all cases above, the postcondition is achieved }"""
    return answer


def moveNegations(prop) :  # textbook, p. 62, calls it, NNF 
    """moveNegations moves all negations inwards until they rest against
       primitive propositions.  These equivalences are used:
        -(-P)  -||-  P
        -(P op Q)  -||-  -P dualop -Q, 
                         where  dualAND is OR; dualOR is AND

       pre: prop is a nested-list parsetree whose operators are AND, OR, NOT
       post: answer is the equivalent nested list where all
            NOTs have been attached to primitive proposition letters.
            (The text calls this _negation normal form_.)
    """
    if isinstance(prop, str) :
        """{ assert: prop  is a primitive proposition }"""
        answer = prop
    else :  # isinstance(prop,list) 
        """{ assert: prop  is a compound proposition }"""
        op = prop[0]
        if op == NOT :
            """{ assert:  prop = [NOT, arg] }"""
            # descend one more level of structure to see what to do with NOT:
            arg = prop[1]
            if isinstance(arg, str) :
                """{ assert:  prop = [NOT, P] }"""
                answer = "-" + arg    # negation is attached to primitive prop
            else :  # isinstance(prop,list) 
                """{ assert: prop = [NOT, [inner_op, ...]] }"""
                inner_op = arg[0]
                if inner_op == NOT :
                    """{ assert: prop = [NOT, [NOT, rest]] }"""
                    # the two negations cancel, so...
                    answer = moveNegations(arg[1])
                else : # inner_op is AND or OR
                    """{ assert: prop = [NOT, [op, arg1, arg2]] }"""
                    tree1 = moveNegations([NOT, arg[1]])
                    tree2 = moveNegations([NOT, arg[2]])
                    """{ assert:  tree1 and tree2 are the values of arg1 and
                           arg2  where all negations are moved inwards }"""
                    # finally, flip  AND to OR,  OR to AND:
                    dual = {AND: OR,  OR: AND}  # a python dictionary 
                    answer = [dual[inner_op], tree1, tree2] 
        else : # op is AND or OR
            """{ assert: prop = [op, prop1, prop2] }"""
            tree1 = moveNegations(prop[1])
            tree2 = moveNegations(prop[2])
            """{ assert:  tree1 and tree2 are the values of arg1 and arg2
                   where all negations are moved inwards }"""
            answer = [op, tree1, tree2]

    """{ assert: in all cases, postcondition is satisfied }"""
    return answer


def makeIntoCNF(prop) :  # textbook, p. 60, calls this  CNF
    """makeIntoCNF moves the ORs within the AND clauses.

       pre: prop is a nested-list parsetree in ``negation normal form'' ---
            it has only AND and OR operators and negations are attached to
            primitive propositions.
       post: answer is equivalent to prop and is in cnf.
    """
    if isinstance(prop, str) :  # prop has form "P" or "-P"
        answer = prop
    else :  # prop  has form  [op, prop1, prop2]
        op = prop[0]
        tree1 =  makeIntoCNF(prop[1])
        tree2 =  makeIntoCNF(prop[2])
        """{ assert: tree1 and tree2  are in  cnf }"""
        if op == AND :
            answer = [AND, tree1, tree2]
        else : # op == OR
            answer = distribute_Or(tree1, tree2)
    return answer


def distribute_Or(p1, p2):  # textbook, p.61, calls this  DISTR
    """distribute_Or  converts a proposition of form,   p1 v p2,
       where  p1  and  p2  are already in cnf,  into an answer in cnf  via:
          (P11 & P12) v P2  -||-  (P11 v P2) & (P12 v P2)

       pre: p1 and p2 are nested-list parsetrees in cnf
       post: answer is equivalent to  p1 v p2  but is in cnf
    """
    if isinstance(p1, list) and p1[0] == AND :
        """{ assert:  p1 = P11 & P12 }"""
        answer = [AND, distribute_Or(p1[1],p2), distribute_Or(p1[2],p2)]
    elif  isinstance(p2, list) and p2[0] == AND :
        """{ assert:  p2 = P21 & P22 }"""
        answer = [AND, distribute_Or(p1,p2[1]), distribute_Or(p1,p2[2])]
    else :
        """{ assert: since  p1 and p2 are both in cnf, then both are
             disjunctive clauses, which can be appended }"""
        answer = [OR, p1, p2]
    return answer


def flattenCNF(prop) :
    """makes a list of conjuncts of lists of disjuncts;
       returns a list of lists of props

       pre: prop is a nested-list parsetree in cnf
       post: answer is  prop  reformatted as
             [ [d11, d21, ...], [d21, d22, ...], ..., [dn1, dn2, ...]]
             where the OR operators are implicit in the nested lists,
             and the AND operators are implicit in the top-level list.
    """
    # this is a helper function for the use of  flattenCNF  only:
    def flattenDisjuncts(prop) :
        """makes a list of primitive props from  prop, a nested disjunction.

           pre: prop is a nested list where are embedded operators are OR
           post: ans  is a list of all the "P", "-P" arguments of the ORs
        """
        if isinstance(prop, str) :
            ans = [prop]
        else :  # prop  has form  [OR, p1, p2]
            ans = flattenDisjuncts(prop[1]) + flattenDisjuncts(prop[2])
        return ans


    if isinstance(prop, str) :  # prop is "P" or "-P"
        answer = [ [prop] ]
    else :  # prop  has form  [op, p1, p2]
        op = prop[0]
        if op == OR :
            answer = [ flattenDisjuncts(prop[1]) + flattenDisjuncts(prop[2]) ]
        else : # op == AND
            answer = flattenCNF(prop[1]) + flattenCNF(prop[2])
    return answer


def removeDuplicates(prop):
    """removeDuplicates  removes from each disjunctive clause duplicate
       occurrences of any "P" or "-P",  that is,
                [ ... [p,...,p,...] ...]  ==>  [ ... [...,p,...] ...].

       pre: prop  is in flattened cnf
       post:  answer is an equivalent proposition with duplicates removed
    """
    answer = []
    for disjunct in prop :
        answer = answer + [ removeDuplicate(disjunct) ]
    return answer


def removeDuplicate(d) :
    """removes all duplicate strings from list  d"""
    if d == [] :
        ans = d
    else :
        p = d[0]
        rest = removeDuplicate(d[1:])
        if p in rest :
            ans = rest
        else :
            ans = [p] + rest
    return ans


def removeTautologies(prop):
    """removeTautologies  removes all disjunctive clauses of form,
         [ ..., P, ..., -P,... ],  because they are equivalent to True.

       pre:  prop  is a flattened cnf
       post: answer is equivalent to  prop  with  tautology clauses removed
    """
    answer = []
    for disjunct in prop :
        if not isTautology(disjunct) :
            answer = answer + [disjunct]
    return answer


def isTautology(d):
    """examines disjunctive clause (list) d to see if it is
       a tautology, that is, it contains both "P" and "-P" for some P"""
    for prim in d :
       c = prim[0]
       if c == NOT :
           opposite = prim[1:]
       else :
           opposite = NOT + prim
       if opposite in d :
           return True
    return False

