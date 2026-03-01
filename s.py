""" my own language! (EASY .epp credit from https://www.youtube.com/@WeeklyHow/videos)
Features:
- Variables and math (+, -, *, /, %)
- say (print)
- if / otherwise conditions
- Natural language comparisons: "if 2 is bigger than 1 then:"
- repeat loops
- while loops
- ask for input
- and / or / not operators
- GUI: window, button, label, textbox, slider, checkbox, display
- color property on label and button
- multi-statement button actions separated by semicolons: button "x": a = 1 ; b = 2

Usage:
- Run a .epp file:  python s.py my_program.epp
- If no file is given, runs a built-in demo.
"""

import sys
import tkinter as tk
from dataclasses import dataclass, field
from typing import Any, List, Optional


# =========================
# Tokenizer (Lexer)
# =========================

class Token:
    def __init__(self, type_: str, value: Any = None, line: int = 0, col: int = 0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.col})"


KEYWORDS = {
    "say": "SAY",
    "if": "IF",
    "then": "THEN",
    "otherwise": "OTHERWISE",
    "repeat": "REPEAT",
    "while": "WHILE",
    "ask": "ASK",
    "window": "WINDOW",
    "button": "BUTTON",
    "label": "LABEL",
    "textbox": "TEXTBOX",
    "slider": "SLIDER",
    "checkbox": "CHECKBOX",
    "to": "TO",
    "true": "TRUE",
    "false": "FALSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "color": "COLOR",
    "display": "DISPLAY",
    "do": "DO",
    "end": "END",
    "compute": "COMPUTE",
    # Natural language comparison words
    "is": "IS",
    "bigger": "BIGGER",
    "smaller": "SMALLER",
    "than": "THAN",
    "equals": "EQUALS",
}


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(text)

    def peek(self) -> str:
        if self.pos >= self.length:
            return "\0"
        return self.text[self.pos]

    def advance(self) -> str:
        ch = self.peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def skip_whitespace(self):
        while True:
            ch = self.peek()
            if ch in (" ", "\t"):
                self.advance()
            else:
                break

    def string(self) -> Token:
        start_line, start_col = self.line, self.col
        self.advance()  # skip opening "
        result = []
        while True:
            ch = self.peek()
            if ch == "\0":
                raise SyntaxError(f"Unterminated string at line {start_line}")
            if ch == '"':
                self.advance()
                break
            if ch == "\\":
                self.advance()
                esc = self.peek()
                if esc == "n":
                    result.append("\n")
                elif esc == "t":
                    result.append("\t")
                elif esc == '"':
                    result.append('"')
                else:
                    result.append(esc)
                self.advance()
            else:
                result.append(self.advance())
        return Token("STRING", "".join(result), start_line, start_col)

    def number(self) -> Token:
        start_line, start_col = self.line, self.col
        digits = []
        while self.peek().isdigit():
            digits.append(self.advance())
        if self.peek() == "." and self.text[self.pos + 1:self.pos + 2].isdigit():
            digits.append(self.advance())  # consume '.'
            while self.peek().isdigit():
                digits.append(self.advance())
            return Token("NUMBER", float("".join(digits)), start_line, start_col)
        return Token("NUMBER", int("".join(digits)), start_line, start_col)

    def identifier(self) -> Token:
        start_line, start_col = self.line, self.col
        chars = []
        while True:
            ch = self.peek()
            if ch.isalnum() or ch == "_":
                chars.append(self.advance())
            else:
                break
        text = "".join(chars)
        lower = text.lower()
        if lower in KEYWORDS:
            return Token(KEYWORDS[lower], text, start_line, start_col)
        return Token("IDENT", text, start_line, start_col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < self.length:
            ch = self.peek()
            if ch in (" ", "\t"):
                self.skip_whitespace()
                continue
            if ch == "#":
                # skip comment until end of line
                while self.peek() not in ("\n", "\r", "\0"):
                    self.advance()
                continue
            if ch in ("\n", "\r"):
                self.advance()
                tokens.append(Token("NEWLINE", None, self.line, self.col))
                continue
            if ch == '"':
                tokens.append(self.string())
                continue
            if ch.isdigit():
                tokens.append(self.number())
                continue
            if ch.isalpha() or ch == "_":
                tokens.append(self.identifier())
                continue

            # Operators and punctuation
            start_line, start_col = self.line, self.col
            if ch == "=":
                self.advance()
                if self.match("="):
                    tokens.append(Token("EQEQ", "==", start_line, start_col))
                else:
                    tokens.append(Token("ASSIGN", "=", start_line, start_col))
            elif ch == "!":
                self.advance()
                if self.match("="):
                    tokens.append(Token("NEQ", "!=", start_line, start_col))
                else:
                    raise SyntaxError(f"Unexpected character '!' at line {self.line}")
            elif ch == ">":
                self.advance()
                if self.match("="):
                    tokens.append(Token("GTE", ">=", start_line, start_col))
                else:
                    tokens.append(Token("GT", ">", start_line, start_col))
            elif ch == "<":
                self.advance()
                if self.match("="):
                    tokens.append(Token("LTE", "<=", start_line, start_col))
                else:
                    tokens.append(Token("LT", "<", start_line, start_col))
            elif ch == "+":
                self.advance()
                tokens.append(Token("PLUS", "+", start_line, start_col))
            elif ch == "-":
                self.advance()
                if self.match(">"):
                    tokens.append(Token("ARROW", "->", start_line, start_col))
                else:
                    tokens.append(Token("MINUS", "-", start_line, start_col))
            elif ch == "*":
                self.advance()
                tokens.append(Token("STAR", "*", start_line, start_col))
            elif ch == "/":
                self.advance()
                tokens.append(Token("SLASH", "/", start_line, start_col))
            elif ch == ":":
                self.advance()
                tokens.append(Token("COLON", ":", start_line, start_col))
            elif ch == "%":
                self.advance()
                tokens.append(Token("PERCENT", "%", start_line, start_col))
            elif ch == ";":
                self.advance()
                tokens.append(Token("SEMI", ";", start_line, start_col))
            elif ch == "(":
                self.advance()
                tokens.append(Token("LPAREN", "(", start_line, start_col))
            elif ch == ")":
                self.advance()
                tokens.append(Token("RPAREN", ")", start_line, start_col))
            else:
                raise SyntaxError(f"Unexpected character '{ch}' at line {self.line}, col {self.col}")

        tokens.append(Token("EOF", None, self.line, self.col))
        return tokens


# =========================
# AST Nodes
# =========================

class Expr:
    pass


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Var(Expr):
    name: str


@dataclass
class Unary(Expr):
    op: str
    right: Expr


@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


class Stmt:
    pass


@dataclass
class Say(Stmt):
    expr: Expr


@dataclass
class Assign(Stmt):
    name: str
    expr: Expr


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    otherwise_branch: Optional[Stmt] = None


@dataclass
class Repeat(Stmt):
    count_expr: Expr
    body: Stmt


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass
class Ask(Stmt):
    prompt_expr: Expr
    name: str


@dataclass
class WindowStmt(Stmt):
    title: str


@dataclass
class LabelStmt(Stmt):
    text: str
    color: Optional[str] = None


@dataclass
class TextBoxStmt(Stmt):
    name: str


@dataclass
class SliderStmt(Stmt):
    min_expr: Expr
    max_expr: Expr
    name: str


@dataclass
class CheckboxStmt(Stmt):
    label: str
    name: str


@dataclass
class ButtonStmt(Stmt):
    label: str
    action: Stmt
    color: Optional[str] = None


@dataclass
class Block(Stmt):
    stmts: List[Stmt]


@dataclass
class DisplayStmt(Stmt):
    name: str


@dataclass
class ComputeStmt(Stmt):
    """Evaluate the string value of src_var as a math expression, store in dst_var."""
    src_var: str
    dst_var: str


# =========================
# Parser
# =========================

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def at_end(self) -> bool:
        return self.peek().type == "EOF"

    def advance(self) -> Token:
        if not self.at_end():
            self.current += 1
        return self.previous()

    def check(self, type_: str) -> bool:
        if self.at_end():
            return False
        return self.peek().type == type_

    def match(self, *types: str) -> bool:
        if self.check_any(types):
            self.advance()
            return True
        return False

    def check_any(self, types: tuple) -> bool:
        if self.at_end():
            return False
        return self.peek().type in types

    def consume(self, type_: str, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        token = self.peek()
        raise ParseError(f"{message} at line {token.line}, col {token.col}")

    def parse(self) -> List[Stmt]:
        statements: List[Stmt] = []
        while not self.at_end():
            while self.match("NEWLINE"):
                pass
            if self.at_end():
                break
            statements.append(self.statement())
            while self.match("NEWLINE"):
                pass
        return statements

    def statement(self) -> Stmt:
        if self.match("SAY"):
            return self.say_statement()
        if self.match("IF"):
            return self.if_statement()
        if self.match("WHILE"):
            return self.while_statement()
        if self.match("REPEAT"):
            return self.repeat_statement()
        if self.match("ASK"):
            return self.ask_statement()
        if self.match("WINDOW"):
            return self.window_statement()
        if self.match("BUTTON"):
            return self.button_statement()
        if self.match("LABEL"):
            return self.label_statement()
        if self.match("TEXTBOX"):
            return self.textbox_statement()
        if self.match("SLIDER"):
            return self.slider_statement()
        if self.match("CHECKBOX"):
            return self.checkbox_statement()
        if self.match("DISPLAY"):
            return self.display_statement()
        if self.match("COMPUTE"):
            return self.compute_statement()
        if self.check("IDENT"):
            return self.assign_statement()
        token = self.peek()
        raise ParseError(f"Unexpected token '{token.type}' at line {token.line}, col {token.col}")

    def say_statement(self) -> Stmt:
        expr = self.expression()
        return Say(expr)

    def assign_statement(self) -> Stmt:
        name = self.advance().value
        self.consume("ASSIGN", "Expected '=' after variable name")
        expr = self.expression()
        return Assign(name, expr)

    def if_statement(self) -> Stmt:
        condition = self.expression()
        # Accept both "if x > 3:" and "if x > 3 then:"
        self.match("THEN")
        self.consume("COLON", "Expected ':' after if condition")
        then_stmt = self.inline_statement()
        # Look for 'otherwise' on the next line
        otherwise_stmt = None
        saved = self.current
        # skip newlines
        while self.match("NEWLINE"):
            pass
        if self.match("OTHERWISE"):
            self.consume("COLON", "Expected ':' after 'otherwise'")
            otherwise_stmt = self.inline_statement()
        else:
            self.current = saved  # rewind if no otherwise
        return If(condition, then_stmt, otherwise_stmt)

    def while_statement(self) -> Stmt:
        condition = self.expression()
        self.consume("COLON", "Expected ':' after while condition")
        body = self.inline_statement()
        return While(condition, body)

    def repeat_statement(self) -> Stmt:
        count_expr = self.expression()
        self.consume("COLON", "Expected ':' after repeat count")
        body = self.inline_statement()
        return Repeat(count_expr, body)

    def ask_statement(self) -> Stmt:
        prompt_expr = self.expression()
        self.consume("ARROW", "Expected '->' after ask prompt")
        name_tok = self.consume("IDENT", "Expected variable name after '->'")
        return Ask(prompt_expr, name_tok.value)

    def window_statement(self) -> Stmt:
        title_tok = self.consume("STRING", "Expected window title in quotes")
        return WindowStmt(title_tok.value)

    def label_statement(self) -> Stmt:
        text_tok = self.consume("STRING", "Expected label text in quotes")
        color = None
        if self.match("COLOR"):
            color_tok = self.consume("STRING", "Expected color name in quotes after 'color'")
            color = color_tok.value
        return LabelStmt(text_tok.value, color)

    def textbox_statement(self) -> Stmt:
        self.consume("ARROW", "Expected '->' after textbox")
        name_tok = self.consume("IDENT", "Expected variable name after '->'")
        return TextBoxStmt(name_tok.value)

    def slider_statement(self) -> Stmt:
        min_expr = self.expression()
        self.consume("TO", "Expected 'to' in slider")
        max_expr = self.expression()
        self.consume("ARROW", "Expected '->' after slider range")
        name_tok = self.consume("IDENT", "Expected variable name after '->'")
        return SliderStmt(min_expr, max_expr, name_tok.value)

    def checkbox_statement(self) -> Stmt:
        label_tok = self.consume("STRING", "Expected checkbox label in quotes")
        self.consume("ARROW", "Expected '->' after checkbox label")
        name_tok = self.consume("IDENT", "Expected variable name after '->'")
        return CheckboxStmt(label_tok.value, name_tok.value)

    def button_statement(self) -> Stmt:
        label_tok = self.consume("STRING", "Expected button label in quotes")
        color = None
        if self.match("COLOR"):
            color_tok = self.consume("STRING", "Expected color name in quotes after 'color'")
            color = color_tok.value
        self.consume("COLON", "Expected ':' after button label")
        # Support multi-line do..end block
        while self.match("NEWLINE"):
            pass
        if self.match("DO"):
            action = self.block_statement()
        else:
            action = self.inline_statement()
        return ButtonStmt(label_tok.value, action, color)

    def block_statement(self) -> Stmt:
        """Parse statements until END keyword."""
        stmts = []
        while self.match("NEWLINE"):
            pass
        while not self.at_end() and not self.check("END"):
            while self.match("NEWLINE"):
                pass
            if self.check("END"):
                break
            stmts.append(self.statement())
            while self.match("NEWLINE"):
                pass
        self.consume("END", "Expected 'end' to close 'do' block")
        return Block(stmts)

    def display_statement(self) -> Stmt:
        self.consume("ARROW", "Expected '->' after display")
        name_tok = self.consume("IDENT", "Expected variable name after '->'")
        return DisplayStmt(name_tok.value)

    def compute_statement(self) -> Stmt:
        src_tok = self.consume("IDENT", "Expected variable name after 'compute'")
        self.consume("ARROW", "Expected '->' after compute variable")
        dst_tok = self.consume("IDENT", "Expected result variable after '->'")
        return ComputeStmt(src_tok.value, dst_tok.value)

    def inline_statement(self) -> Stmt:
        start = self.current
        end = start
        while end < len(self.tokens) and self.tokens[end].type not in ("NEWLINE", "EOF"):
            end += 1

        if start == end:
            token = self.peek()
            raise ParseError(f"Expected statement after ':' at line {token.line}, col {token.col}")

        sub_tokens = self.tokens[start:end] + [Token("EOF", None)]
        sub_parser = Parser(sub_tokens)
        # Parse multiple semicolon-separated statements
        stmts = [sub_parser.statement()]
        while sub_parser.match("SEMI"):
            if not sub_parser.at_end():
                stmts.append(sub_parser.statement())
        self.current = end
        if len(stmts) == 1:
            return stmts[0]
        return Block(stmts)

    # Expression parsing with precedence:
    # or > and > not > equality > comparison > term > factor > unary > primary

    def expression(self) -> Expr:
        return self.or_expr()

    def or_expr(self) -> Expr:
        expr = self.and_expr()
        while self.match("OR"):
            right = self.and_expr()
            expr = Binary(expr, "OR", right)
        return expr

    def and_expr(self) -> Expr:
        expr = self.not_expr()
        while self.match("AND"):
            right = self.not_expr()
            expr = Binary(expr, "AND", right)
        return expr

    def not_expr(self) -> Expr:
        if self.match("NOT"):
            right = self.not_expr()
            return Unary("NOT", right)
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match("EQEQ", "NEQ"):
            op = self.previous().type
            right = self.comparison()
            expr = Binary(expr, op, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        # Standard symbolic comparisons
        while self.match("GT", "LT", "GTE", "LTE"):
            op = self.previous().type
            right = self.term()
            expr = Binary(expr, op, right)
            return expr
        # Natural language: "is bigger than", "is smaller than", "is equals"
        if self.match("IS"):
            if self.match("BIGGER"):
                self.match("THAN")  # optional "than"
                right = self.term()
                return Binary(expr, "GT", right)
            if self.match("SMALLER"):
                self.match("THAN")
                right = self.term()
                return Binary(expr, "LT", right)
            if self.match("EQUALS"):
                right = self.term()
                return Binary(expr, "EQEQ", right)
            # bare "is" means ==
            right = self.term()
            return Binary(expr, "EQEQ", right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match("PLUS", "MINUS"):
            op = self.previous().type
            right = self.factor()
            expr = Binary(expr, op, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match("STAR", "SLASH", "PERCENT"):
            op = self.previous().type
            right = self.unary()
            expr = Binary(expr, op, right)
        return expr

    def unary(self) -> Expr:
        if self.match("MINUS"):
            op = self.previous().type
            right = self.unary()
            return Unary(op, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match("NUMBER"):
            return Literal(self.previous().value)
        if self.match("STRING"):
            return Literal(self.previous().value)
        if self.match("TRUE"):
            return Literal(True)
        if self.match("FALSE"):
            return Literal(False)
        if self.match("IDENT"):
            return Var(self.previous().value)
        if self.match("LPAREN"):
            expr = self.expression()
            self.consume("RPAREN", "Expected ')' after expression")
            return expr
        token = self.peek()
        raise ParseError(f"Expected value or variable at line {token.line}, col {token.col}")


# =========================
# GUI Runtime Helpers
# =========================

class TkVarWrapper:
    def __init__(self, tk_var, kind: str):
        self.tk_var = tk_var
        self.kind = kind  # "string", "int", "bool"

    def get(self):
        val = self.tk_var.get()
        if self.kind == "int":
            return int(val)
        if self.kind == "bool":
            return bool(val)
        return str(val)

    def set(self, value):
        if self.kind == "int":
            try:
                self.tk_var.set(int(value))
            except Exception:
                self.tk_var.set(0)
        elif self.kind == "bool":
            self.tk_var.set(bool(value))
        else:
            self.tk_var.set(str(value))


class GuiRuntime:
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.row = 0
        self.btn_col = 0
        self.var_bindings = {}  # name -> TkVarWrapper

    def ensure_root(self, title: str):
        if self.root is None:
            self.root = tk.Tk()
        self.root.title(title)

    def add_label(self, text: str, color: Optional[str] = None):
        kwargs = {"text": text, "anchor": "w"}
        if color:
            kwargs["fg"] = color
        lbl = tk.Label(self.root, **kwargs)
        lbl.grid(row=self.row, column=0, columnspan=4, sticky="w", padx=5, pady=2)
        self.btn_col = 0
        self.row += 1

    def add_textbox(self, name: str):
        lbl = tk.Label(self.root, text=name + ":", anchor="w")
        lbl.grid(row=self.row, column=0, sticky="w", padx=5, pady=2)
        var = tk.StringVar()
        entry = tk.Entry(self.root, textvariable=var, width=30)
        entry.grid(row=self.row, column=1, sticky="we", padx=5, pady=2)
        self.var_bindings[name] = TkVarWrapper(var, "string")
        self.row += 1

    def add_slider(self, name: str, min_val: int, max_val: int):
        lbl = tk.Label(self.root, text=name + ":", anchor="w")
        lbl.grid(row=self.row, column=0, sticky="w", padx=5, pady=2)
        var = tk.IntVar(value=min_val)
        scale = tk.Scale(self.root, from_=min_val, to=max_val, orient="horizontal", variable=var)
        scale.grid(row=self.row, column=1, sticky="we", padx=5, pady=2)
        self.var_bindings[name] = TkVarWrapper(var, "int")
        self.row += 1

    def add_checkbox(self, label: str, name: str):
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(self.root, text=label, variable=var)
        cb.grid(row=self.row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.var_bindings[name] = TkVarWrapper(var, "bool")
        self.row += 1

    def add_button(self, label: str, command, color: Optional[str] = None, width: int = 4):
        kwargs = {"text": label, "command": command, "width": width, "font": ("Arial", 14)}
        if color:
            kwargs["bg"] = color
        btn = tk.Button(self.root, **kwargs)
        # use keypad column layout: 4 buttons per row
        col = self.btn_col
        btn.grid(row=self.row, column=col, pady=2, padx=2, sticky="we")
        self.btn_col += 1
        if self.btn_col >= 4:
            self.btn_col = 0
            self.row += 1

    def add_display(self, name: str):
        var = tk.StringVar(value="")
        lbl = tk.Label(self.root, textvariable=var, font=("Courier", 24, "bold"),
                       anchor="e", bg="#222", fg="#00ff99", relief="sunken",
                       padx=10, pady=8, width=16)
        lbl.grid(row=self.row, column=0, columnspan=4, sticky="we", padx=5, pady=4)
        self.var_bindings[name] = TkVarWrapper(var, "string")
        self.display_names = getattr(self, "display_names", [])
        self.display_names.append(name)
        self.row += 1

    def refresh_displays(self, env: dict):
        for name in getattr(self, "display_names", []):
            if name in env and name in self.var_bindings:
                self.var_bindings[name].set(str(env[name]))

    def mainloop(self):
        if self.root is not None:
            for i in range(4):
                self.root.columnconfigure(i, weight=1)
            self.root.mainloop()


# =========================
# Interpreter
# =========================

class EasyRuntimeError(Exception):
    pass


class Interpreter:
    def __init__(self):
        self.env = {}  # variable name -> value or TkVarWrapper
        self.gui: Optional[GuiRuntime] = None

    def run(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.execute(stmt)
            if self.gui is not None:
                self.gui.mainloop()
        except EasyRuntimeError as e:
            print("EASY runtime error:", e)
        except ParseError as e:
            print("EASY parse error:", e)

    def execute(self, stmt: Stmt):
        if isinstance(stmt, Say):
            value = self.evaluate(stmt.expr)
            print(value)
        elif isinstance(stmt, Assign):
            value = self.evaluate(stmt.expr)
            self.set_var(stmt.name, value)
        elif isinstance(stmt, If):
            cond = self.evaluate(stmt.condition)
            if self.is_truthy(cond):
                self.execute(stmt.then_branch)
            elif stmt.otherwise_branch is not None:
                self.execute(stmt.otherwise_branch)
        elif isinstance(stmt, While):
            limit = 100_000  # safety guard
            count = 0
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
                count += 1
                if count >= limit:
                    raise EasyRuntimeError("while loop ran too many times (infinite loop?)")
        elif isinstance(stmt, Repeat):
            count_val = self.evaluate(stmt.count_expr)
            try:
                n = int(count_val)
            except ValueError:
                raise EasyRuntimeError("repeat count must be a number")
            for _ in range(n):
                self.execute(stmt.body)
        elif isinstance(stmt, Ask):
            prompt = self.evaluate(stmt.prompt_expr)
            user_input = input(str(prompt) + " ")
            self.set_var(stmt.name, user_input)
        elif isinstance(stmt, WindowStmt):
            self.ensure_gui()
            self.gui.ensure_root(stmt.title)
        elif isinstance(stmt, LabelStmt):
            self.ensure_gui()
            self.gui.add_label(stmt.text, stmt.color)
        elif isinstance(stmt, TextBoxStmt):
            self.ensure_gui()
            self.gui.add_textbox(stmt.name)
        elif isinstance(stmt, SliderStmt):
            self.ensure_gui()
            min_val = self.evaluate(stmt.min_expr)
            max_val = self.evaluate(stmt.max_expr)
            try:
                min_i = int(min_val)
                max_i = int(max_val)
            except ValueError:
                raise EasyRuntimeError("slider range must be numbers")
            self.gui.add_slider(stmt.name, min_i, max_i)
        elif isinstance(stmt, CheckboxStmt):
            self.ensure_gui()
            self.gui.add_checkbox(stmt.label, stmt.name)
        elif isinstance(stmt, ButtonStmt):
            self.ensure_gui()
            def on_click(stmt=stmt):
                try:
                    self.execute(stmt.action)
                    # refresh all display widgets after any button action
                    if self.gui:
                        self.gui.refresh_displays(self.env)
                except EasyRuntimeError as e:
                    print("EASY runtime error in button:", e)
                except ParseError as e:
                    print("EASY parse error in button:", e)
            self.gui.add_button(stmt.label, on_click, stmt.color)
        elif isinstance(stmt, Block):
            for s in stmt.stmts:
                self.execute(s)
        elif isinstance(stmt, DisplayStmt):
            self.ensure_gui()
            self.gui.add_display(stmt.name)
        elif isinstance(stmt, ComputeStmt):
            expr_str = str(self.get_var(stmt.src_var))
            try:
                # Safe eval: only allow numbers and math operators
                import re
                if re.fullmatch(r"[\d\.\+\-\*\/\(\)\s]+", expr_str):
                    result = eval(expr_str)
                    if isinstance(result, float) and result == int(result):
                        result = int(result)
                    self.set_var(stmt.dst_var, result)
                else:
                    self.set_var(stmt.dst_var, "Error")
            except Exception:
                self.set_var(stmt.dst_var, "Error")
        else:
            raise EasyRuntimeError(f"Unknown statement type: {type(stmt)}")

    def ensure_gui(self):
        if self.gui is None:
            self.gui = GuiRuntime()

    def evaluate(self, expr: Expr):
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Var):
            return self.get_var(expr.name)
        if isinstance(expr, Unary):
            if expr.op == "MINUS":
                right = self.evaluate(expr.right)
                try:
                    return -float(right) if isinstance(right, float) else -int(right)
                except Exception:
                    raise EasyRuntimeError("Unary '-' needs a number")
            if expr.op == "NOT":
                return not self.is_truthy(self.evaluate(expr.right))
        if isinstance(expr, Binary):
            op = expr.op
            # Short-circuit for and/or
            if op == "AND":
                left = self.evaluate(expr.left)
                return left if not self.is_truthy(left) else self.evaluate(expr.right)
            if op == "OR":
                left = self.evaluate(expr.left)
                return left if self.is_truthy(left) else self.evaluate(expr.right)

            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            if op == "PLUS":
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if op == "MINUS":
                return left - right
            if op == "STAR":
                return left * right
            if op == "SLASH":
                if right == 0:
                    raise EasyRuntimeError("Division by zero")
                return left / right
            if op == "PERCENT":
                if right == 0:
                    raise EasyRuntimeError("Modulo by zero")
                return left % right
            if op == "GT":
                return left > right
            if op == "LT":
                return left < right
            if op == "GTE":
                return left >= right
            if op == "LTE":
                return left <= right
            if op == "EQEQ":
                return left == right
            if op == "NEQ":
                return left != right
        raise EasyRuntimeError(f"Unknown expression type: {type(expr)}")

    def get_var(self, name: str):
        if name in self.env:
            val = self.env[name]
            if isinstance(val, TkVarWrapper):
                return val.get()
            return val
        if self.gui is not None and name in self.gui.var_bindings:
            return self.gui.var_bindings[name].get()
        return 0

    def set_var(self, name: str, value: Any):
        if self.gui is not None and name in self.gui.var_bindings:
            self.gui.var_bindings[name].set(value)
            return
        if name in self.env and isinstance(self.env[name], TkVarWrapper):
            self.env[name].set(value)
        else:
            self.env[name] = value
        # update any display widget bound to this name
        if self.gui is not None:
            self.gui.refresh_displays(self.env)

    @staticmethod
    def is_truthy(val: Any) -> bool:
        return bool(val)


# =========================
# Demo EASY Program
# =========================

DEMO_CODE = """
# Welcome message
say "Welcome to EASY!"

# Basic math
x = 5 + 3
say "x = 5 + 3 = " + x

y = 10 * 2 - 4
say "y = 10 * 2 - 4 = " + y

z = 100 / 4
say "z = 100 / 4 = " + z

# Natural language comparison
if x is bigger than 3 then: say "x is bigger than 3"

if y is smaller than 5 then: say "y is small"
otherwise: say "y is not small"

# and / or / not
a = true
b = false
if a and not b: say "a is true and b is false"
if a or b: say "at least one is true"

# while loop
count = 0
while count < 3: count = count + 1
say "counted to: " + count

# repeat loop
repeat 3: say "loop!"

# GUI demo
window "EASY Demo App"
label "=== EASY GUI Demo ===" color "blue"
label "Enter your name:"
textbox -> userName

slider 0 to 100 -> volume
checkbox "Loud mode" -> isLoud

button "Say Hi" color "green": say "Hi, " + userName
button "Show Volume": say "Volume is " + volume
button "Check Loud" color "red": if isLoud == true: say "LOUD MODE ON!"
"""


def run_easy(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    statements = parser.parse()
    interpreter = Interpreter()
    interpreter.run(statements)


def main():
    if len(sys.argv) >= 2:
        path = sys.argv[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except OSError as e:
            print(f"Could not read file '{path}': {e}")
            return
        run_easy(code)
    else:
        print("No .epp file provided; running built-in EASY demo.\n")
        run_easy(DEMO_CODE)


if __name__ == "__main__":
    main()