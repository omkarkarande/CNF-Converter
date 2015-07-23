# CNF-Converter
Python code to convert First Order Logic statements to Conjunctive Normal Form

Input file is in the form of a count followed by that many FOL sentences on each line
<br>
Example: 
5
statement 1
statement 2
statement 3
statement 4
statement 5


Each FOL statement is represented as a python list in the form of operation followed by literals.
Example A v B v C ^ !D would be written as:
['or', 'A', 'B', ['and', 'C', ['not', 'D']]]


Output generated is in the same format.
