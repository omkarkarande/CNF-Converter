#***************************************************************************************************************************#
#*********************************************************IMPORTS***********************************************************#
#***************************************************************************************************************************#
import sys, argparse
from itertools import islice
import collections

#***************************************************************************************************************************#
#*********************************************************GLOBALS***********************************************************#
#***************************************************************************************************************************#

#FILE
inputfilename = ""
outputfilename = "sentences_CNF.txt"

#CONTENTS OF THE FILE
number_of_sentences = 0

#***************************************************************************************************************************#
#*********************************************************VALIDATORS********************************************************#
#***************************************************************************************************************************#

#-----------------------------------------------#
#Checks if the logic is implication on 2 items
#-----------------------------------------------#
def isImplicationCandidate(logic):
    if logic[0] == 'implies' and len(logic) == 3:
        return True
    else:
        return False

#-----------------------------------------------#
#Checks if the logic is a double implication 
#-----------------------------------------------#
def isIFFCandidate(logic):
    if logic[0] == 'iff' and len(logic) == 3:
        return True
    else:
        return False
    
    
#-----------------------------------------------#
#Checks if the logic is a negation 
#-----------------------------------------------#
def isNPCandidate(logic):
    if logic[0] == 'not' and len(logic) == 2 and len(logic[1]) != 1:
        return True
    else:
        return False

#-----------------------------------------------#
#Checks if the logic is a candidate for distribution 
#Checks for ORs of one or more ANDs
#-----------------------------------------------#
def isDistributionCandidate(logic):
    
    if logic[0] == 'or':
        for i in range(1, len(logic)):
            if len(logic[i]) > 1:
                if logic[i][0] == 'and':
                    return True
    return False

#***************************************************************************************************************************#
#******************************************************HELPER METHODS*******************************************************#
#***************************************************************************************************************************#

#------------------------------------------------------#
#Cleans Up the logic by removing any duplicates, and 
#un-nesting unecessary nested lists
#[or, [or a b], [or c d]] becomes [or a b c d]
#------------------------------------------------------#
def cleanUp(logic):
    
    result = []
    
    #Treat negation lists as unique literals.
    #No operations to perform on nots
    if logic[0] == 'not':
        return logic
    
    #append the operator 
    result.append(logic[0])
    outer_op = logic[0]
    
    #Loop through the literals
    for i in range(1, len(logic)):
        #if the operator matches to the outer operator
        if logic[i][0] == outer_op:
            #Loop through the literals of this list
            for j in range(1, len(logic[i])):
                result.append(logic[i][j])
        else:
            #append the logic as is
            result.append(logic[i])
            
    return result

#------------------------------------------------------#
#Convert into a form where all operators have only 2 
#literals
#Used to simplify the distribution process
#or(a b c d) = or(or(or(a b) c) d)
#------------------------------------------------------#
def getSimplified(operator, literals, current):
    
    result = []
    result.append(operator)
    
    #If the literal length is 1 append the literal else recursively call for simplification
    if len(literals) == 1:
        result.append(literals[0])
    else:
        result.append(getSimplified(operator, literals[0:len(literals)-1], literals[len(literals)-1]))
        
    #append the current 
    result.append(current)
    
    #return simplified logic
    return result

    
#------------------------------------------------------#
#Simplifies the given logic and all sub-logics
#------------------------------------------------------#
def simplify(logic):
    
    #Only simplify when the literals to an operator are more than 2
    if len(logic) > 3:
        #need to simplify
        logic = getSimplified(logic[0], logic[1:len(logic)-1], logic[len(logic) - 1])
        
    #Repeat recursively for all sub logics
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = simplify(logic[i])
        
    #Only simplify when the literals to an operator are more than 2
    if len(logic) > 3:
        #need to simplify
        logic = getSimplified(logic[0], logic[1:len(logic)-1], logic[len(logic) - 1])
        
    return logic

    
#------------------------------------------------------#
#Checks if the given two clauses are logically equal
#------------------------------------------------------#
def isEqual(logic1, logic2):
    #If the lengths dont match, they aren't equal
    if len(logic1) != len(logic2):
        return False
    else:
        #if both are Variables
        if len(logic1) == len(logic2) == 1:
            if logic1 == logic2:
                return True
            else:
                return False
        else:
            #If both are clauses
            #make a temporary list to check with the first
            temp = list(logic2)
            for element in logic1:
                try:
                    #Try to remove the element if it exisits in the second list
                    temp.remove(element)
                except ValueError:
                    return False
                
            #return if test is empty or no
            #If it is empty, the two lists are equal
            return not temp

#------------------------------------------------------#
#Checks if the given logic is in the first list 
#------------------------------------------------------#
def inResult(result, logic):
    
    for i in range(1, len(result)):
        #Check if the logic is equivalent to any one of the logics in result
        if isEqual(result[i], logic):
            return True
    
    return False
    

    
#***************************************************************************************************************************#
#*********************************************************RULES*************************************************************#
#***************************************************************************************************************************#


#------------------------------------------------------#
#Eliminate implication for a given logic
#A => B becomes ~A V B
#imples can take only two variables eg. A => B
#------------------------------------------------------#
def eliminateImplication(logic):
    
    result = []
    result.append('or')
    result.append(['not', logic[1]])
    result.append(logic[2])
    
    return result
    
#------------------------------------------------------#
#Eliminate iff for a given logic
#A <=> B becomes (A=>B)^(B=>A)
#iff can take only two variables eg. A<=>B
#------------------------------------------------------#
def eliminateIFF(logic):
    
    result = []
    result.append('and')
    result.append(eliminateImplication(['implies', logic[1], logic[2]]))
    result.append(eliminateImplication(['implies', logic[2], logic[1]]))
    
    return result

#------------------------------------------------------#
#Propogate NOT inwards
#~(A V B) = ~A ^ ~B
#~(A ^ B) = ~A V ~B
#format must take not followed by a list
#recursively propogates not inwards
#------------------------------------------------------#
def propogateNOT(logic):
    
    result = []
    
    #Checking if the inward logic is OR then append AND
    if(logic[1][0] == 'or'):
        result.append('and')
    #Chicking if inward logic is AND then append OR
    elif(logic[1][0] == 'and'):
        result.append('or')
    #Checking if inward logic is NOT then return the logic alone
    elif(logic[1][0] == 'not'):
        return logic[1][1]
        
    #For all arguments of the inner list
    for i in range(1, len(logic[1])):
        #check if the first argument is another list
        if len(logic[1][i]) != 1:
            #recursively call to propogate not further inwards
            result.append(propogateNOT(['not', logic[1][i]]))
        else:
            #else append the negation of the single element
            result.append(['not', logic[1][i]])
     
    return result


#------------------------------------------------------#
#Distribute ORs over ANDs in the given logic
#P v (Q ^ R) = (P v Q) ^ (P ^ R)
#------------------------------------------------------#
def distributeOR(logic):
    
    result = []
    #AND will propogate outwards
    result.append('and')
    
    #Check if both the lists are ands
    if logic[1][0] == 'and' and logic[2][0] == 'and':
        #Distribute the literals 
        result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
        result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
        result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
        result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
        
    else:
        #Either one is and and
        if logic[1][0] == 'and':
            
            #Check if the second argument is a list
            if len(logic[2]) > 2:
                #check if its a candidate for distribution
                if isDistributionCandidate(logic[2]):
                    logic[2] = parseDistribution(logic[2])
                    
                    #Distribute the literals 
                    result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
                
                else:
                    #Keep the second as it is
                    result.append(parseDistribution(['or', logic[1][1], logic[2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2]]))
                    
            else:
                #Keep the second as it is
                result.append(parseDistribution(['or', logic[1][1], logic[2]]))
                result.append(parseDistribution(['or', logic[1][2], logic[2]]))
        else:
            
            #Check if the second argument is a list
            if len(logic[1]) > 2:
                #check if its a candidate for distribution
                if isDistributionCandidate(logic[1]):
                    logic[1] = parseDistribution(logic[1])
                    
                    #Distribute the literals 
                    result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
                else:
                    #Keep the second as it is
                    result.append(parseDistribution(['or', logic[1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1], logic[2][2]]))
            else:
                #Keep the second as it is
                result.append(parseDistribution(['or', logic[1], logic[2][1]]))
                result.append(parseDistribution(['or', logic[1], logic[2][2]]))
            
                
    return simplify(result)

#------------------------------------------------------#
#Removes any duplicate entries from the cleanedup CNF
#[and [or A B] [or B A]] => [or A B]
#------------------------------------------------------#
def removeDuplicates(logic):
    
    #Check if the logic is not a literal or a not
    if len(logic) > 2:
        result = []
        result.append(logic[0])
        result.append(logic[1])
        
        for i in range(2, len(logic)):
            #Only add the logic to the list if its equivalent is not already present
            if not inResult(result, logic[i]):
                result.append(logic[i])
        
        #check if the cleaned clause is just of size 2 
        #Case of the comment above
        if len(result) == 2:
            result = result[1]
    
        return result
    else:
        #return the logic if its a literal or a not
        return logic
    

#***************************************************************************************************************************#
#******************************************************PARSER METHODS*******************************************************#
#***************************************************************************************************************************#

#------------------------------------------------------#
#Clean up the logic. 
#Merges consecutive similar statements into one 
#coherent statement.
#------------------------------------------------------#
def parseCleanUp(logic):
  
    #Clean the logic
    logic = cleanUp(logic)
   
    
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseCleanUp(logic[i])
    
 
    #Clean the logic again
    logic = cleanUp(logic)
  
    #return the final clean logic
    return logic


#------------------------------------------------------#
#Checks if the given logic statement is an IFF or an 
#IMPLICATION. 
#Recursively goes deeper and removes all instances of 
#implication and IFFs
#------------------------------------------------------#
def parseImplications(logic):
    
    
    #If it is an iff statement, replace logic with the one we get by eliminating iffs
    if isIFFCandidate(logic):
        logic = eliminateIFF(logic)
    #If it is an implies statement, replace logic with the one we get by eliminating implies
    elif isImplicationCandidate(logic):
        logic = eliminateImplication(logic)
    
    
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseImplications(logic[i])
    

    #If it is an iff statement, replace logic with the one we get by eliminating iffs
    if isIFFCandidate(logic):
        logic = eliminateIFF(logic)
    #If it is an implies statement, replace logic with the one we get by eliminating implies
    elif isImplicationCandidate(logic):
        logic = eliminateImplication(logic)
       
    #return the final logic statement devoid of all implications and iffs
    return logic


#----------------------------------------------------------#
#Checks if the logic is a NOT of another logic.
#If so recursively goes deeper to propogate the NOT inwards.
#De-Morgans Law
#----------------------------------------------------------#
def parseNOTs(logic):
    
    #If it is a NOT statement, replace logic with the one we get by propogating not inwards
    if isNPCandidate(logic):
        logic = propogateNOT(logic)
    
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseNOTs(logic[i])
            
            
    #If it is a NOT statement, replace logic with the one we get by propogating not inwards
    if isNPCandidate(logic):
        logic = propogateNOT(logic)
    
    #return the final logic statement with NOT propogated inwards
    return logic
    

#----------------------------------------------------------#
#Checks if the given logic is a candidate for 
#distribution of OR over AND
#Recursively goes deeper and distributes all such instances.
#----------------------------------------------------------#
def parseDistribution(logic):
      
    #Check if the logic is a candidate for distribution of OR over ANDs
    if isDistributionCandidate(logic):
        logic = distributeOR(logic)
        
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseDistribution(logic[i])
            
    #Check if the logic is a candidate for distribution of OR over ANDs
    
    if isDistributionCandidate(logic):
        logic = distributeOR(logic)
    
    #return distributed logic
    return simplify(logic)

#----------------------------------------------------------#
#Recursively removes any duplicates in the logic
#Duplicates include clauses like [A v A] which are converted 
#to A
#Also removes logically similar clauses
#[A v B] = [B v A]
#----------------------------------------------------------#
def parseDuplicates(logic):
    
    #remove duplicate logics
    logic = removeDuplicates(logic)
    
    #For all sub logics remove duplicates from each
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseDuplicates(logic[i])
     
    #Final parse to remove duplicates due to the sub logics
    logic = removeDuplicates(logic)
    
    return logic


#***************************************************************************************************************************#
#******************************************************PARSER METHODS*******************************************************#
#***************************************************************************************************************************#

#----------------------------------------------------------#
#Parses the given logic and convers it into CNF
#----------------------------------------------------------#
def parseLogic(logic):
    
    #For Empty logic
    if len(logic) == 0:
        return logic
    #For logic with one Literal
    if len(logic) == 1:
        return logic[0]
    
    result = parseImplications(logic)
    result = parseNOTs(result)
    result = simplify(result)
    result = parseDistribution(result)
    result = parseCleanUp(result)
    result = parseDuplicates(result)
    
    return result



#***************************************************************************************************************************#
#*****************************************************FILE HANDLING*********************************************************#
#***************************************************************************************************************************#

#----------------------------------------------------------#
#Using the argparse module to look for options
#argparse only in python 2.7 and later
#----------------------------------------------------------#
parser = argparse.ArgumentParser(description="CNF Converter.")
parser.add_argument('-i', '--input', help='Input file name', required=True)
parser.add_argument('-o', '--output', help='Optional output file name', required=False)
args = parser.parse_args()

#Get the filename from the argument.
inputfilename = args.input
#Check if a custom output filename is given.
if args.output is not None:
    outputfilename = args.output

    
    
#----------------------------------------------------------#
#Read the statements from the file
#----------------------------------------------------------#
#with statement to handle opening files
with open(inputfilename) as f:
    
    #open the file to write on
    output_file = open(outputfilename, "w")
    #Get the number of sentences to read from the file
    number_of_sentences = int(f.readline().strip())
    #read that many sentences
    for line in islice(f, 0, number_of_sentences):
        cnf = str(parseLogic(eval(line.strip()))).replace("'", "\"")
        
        if len(cnf) == 1:
            cnf = "\"" + cnf + "\""
            
        output_file.write(cnf+"\n")
    
    output_file.close()


#****************************************************************END*************************************************************#