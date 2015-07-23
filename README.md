# CNF-Converter
Python code to convert First Order Logic statements to Conjunctive Normal Form
<br><br>
Input file is in the form of a count followed by that many FOL sentences on each line
<br><br>
Example: <br>
5<br>
statement 1<br>
statement 2<br>
statement 3<br>
statement 4<br>
statement 5<br>

<br><br>
Each FOL statement is represented as a python list in the form of operation followed by literals.<br><br>
Example A v B v C ^ !D would be written as:<br>
['or', 'A', 'B', ['and', 'C', ['not', 'D']]]

<br><br>
Output generated is in the same format.
