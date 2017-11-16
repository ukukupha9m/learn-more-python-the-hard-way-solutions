import re
from basic.scanner import Scanner
from basic.parser import Parser
from basic.analyzer import BasicAnalyzer
from basic import productions as prod
import sys

TOKENS = [
(re.compile(r"^LET"),    "LET"),
(re.compile(r"^PRINT"),  "PRINT"),
(re.compile(r"^[A-Z_][A-Z0-9_]*"), "NAME"),
(re.compile(r"^[0-9]+"), "INTEGER"),
(re.compile(r"^\="),     "EQUAL"),
(re.compile(r"^\+"),     "PLUS"),
(re.compile(r"^\-"),     "MINUS"),
(re.compile(r"^\*"),     "MULT"),
(re.compile(r"^/"),      "DIV"),
(re.compile(r"^\s+"),    "SPACE"),
]

class BasicParser(Parser):

    def root(self):
        """root = *(expression)"""
        line_no = prod.IntExpr(self.match('INTEGER')).integer
        return line_no, self.expression()

    def expression(self):
        """expression = name / assign / infix / integer / print"""
        start = self.peek()

        if start == 'NAME':
            nameexpr = self.name()
            op = self.peek()

            if op in ['PLUS', 'MINUS', 'DIV', 'MULT']:
                return self.infix(nameexpr, op)
            else:
                return nameexpr
        elif start == 'LET':
            return self.assign()
        elif start == 'PRINT':
            return self.print()
        elif start == 'INTEGER':
            numexpr = self.integer()
            op = self.peek()

            if op in ['PLUS', 'MINUS', 'DIV', 'MULT']:
                return self.infix(numexpr, op)
            else:
                return numexpr
        else:
            assert False, f"Syntax error {self.scanner.error()}"

    def name(self):
        name = self.match('NAME')
        return prod.NameExpr(name)

    def integer(self):
        number = self.match('INTEGER')
        return prod.IntExpr(number)

    def assign(self):
        self.skip('LET')
        nameexpr = self.name()
        self.skip('EQUAL')
        right = self.expression()
        return prod.AssignExpr(nameexpr, right)

    def infix(self, left, op):
        """plus = expression PLUS expression"""
        self.match(op)
        right = self.expression()
        return prod.InfixExpr(left, op, right)

    def print(self):
        self.match('PRINT')
        expr = self.expression()
        return prod.PrintExpr(expr)

class BasicWorld(object):

    def __init__(self, variables):
        self.variables = variables
        self.functions = {}

    def code(self, code):
        self.code = code
        self.ip = 0

    def exec(self):
        line = self.code[self.ip]


    def clone(self):
        """Sort of a lame way to implement scope."""
        temp = BasicWorld(self.variables.copy())
        temp.code = self.code
        temp.functions = self.functions
        return temp


def run(script):
    scanner = Scanner(TOKENS, script)
    parser = BasicParser(scanner)
    parse_tree = parser.parse()
    world = BasicWorld({})
    analyzer = BasicAnalyzer(parse_tree, world)
    world.prods = analyzer.analyze()

    for line_no, prod in world.prods:
        prod.interpret(world)

if __name__ == "__main__":
    _, script = sys.argv

    run(open(script).readlines())
