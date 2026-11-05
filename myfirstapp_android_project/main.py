"""
My First App - a polished Kivy calculator.
Python 3 + Kivy. No network permissions or external services required.
"""
import ast
import operator
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex


Window.clearcolor = get_color_from_hex("#07111F")

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    """Evaluate arithmetic only; never execute arbitrary Python."""
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    expression = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", expression)
    if not expression or len(expression) > 120:
        raise ValueError("Enter a calculation")

    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = float(node.value)
            if abs(value) > 1e100:
                raise ValueError("Number too large")
            return value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("Exponent too large")
            result = OPS[type(node.op)](left, right)
            if abs(result) > 1e100:
                raise ValueError("Result too large")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](visit(node.operand))
        raise ValueError("Invalid expression")

    result = visit(tree)
    if not math_is_finite(result):
        raise ValueError("Invalid result")
    return result


def math_is_finite(value):
    return value == value and value not in (float("inf"), float("-inf"))


def pretty_number(value):
    if abs(value) < 1e-12:
        value = 0
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.10f}".rstrip("0").rstrip(".")


class RoundedButton(Button):
    def __init__(self, fill="#17243A", **kwargs):
        super().__init__(**kwargs)
        self.fill = get_color_from_hex(fill)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = get_color_from_hex("#F4F7FF")
        self.font_size = sp(23)
        self.bold = True
        with self.canvas.before:
            self.canvas_color = Color(*self.fill)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(17)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CalculatorUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(18), dp(16), dp(18), dp(18)],
                         spacing=dp(12), **kwargs)
        self.expression = ""
        self.history = []
        self.just_calculated = False

        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        header.add_widget(Image(source="icon.png", size_hint=(None, 1), width=dp(44)))
        title_box = BoxLayout(orientation="vertical", spacing=0)
        title_box.add_widget(Label(text="[b]My First App[/b]", markup=True,
                                   font_size=sp(19), halign="left", valign="middle",
                                   color=get_color_from_hex("#F5F7FF")))
        title_box.add_widget(Label(text="SMART CALCULATOR", font_size=sp(9),
                                   halign="left", valign="middle",
                                   color=get_color_from_hex("#6D91B9")))
        header.add_widget(title_box)
        history_btn = RoundedButton(text="↶", fill="#243752", size_hint=(None, 1), width=dp(48))
        history_btn.font_size = sp(25)
        history_btn.bind(on_release=self.show_history)
        header.add_widget(history_btn)
        self.add_widget(header)

        display = BoxLayout(orientation="vertical", padding=[dp(16), dp(12)],
                            spacing=dp(8), size_hint_y=0.29)
        with display.canvas.before:
            Color(*get_color_from_hex("#101D31"))
            self.display_rect = RoundedRectangle(pos=display.pos, size=display.size, radius=[dp(24)])
        display.bind(pos=lambda w, p: setattr(self.display_rect, "pos", p),
                     size=lambda w, s: setattr(self.display_rect, "size", s))
        self.expression_label = Label(text="", font_size=sp(18), color=get_color_from_hex("#8EA7C7"),
                                      halign="right", valign="middle", size_hint_y=0.40)
        self.expression_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.result_label = Label(text="0", font_size=sp(43), bold=True,
                                  color=get_color_from_hex("#FFFFFF"),
                                  halign="right", valign="middle", size_hint_y=0.60)
        self.result_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        display.add_widget(self.expression_label)
        display.add_widget(self.result_label)
        self.add_widget(display)

        keys = [
            ("C", "DEL", "%", "÷"),
            ("7", "8", "9", "×"),
            ("4", "5", "6", "−"),
            ("1", "2", "3", "+"),
            ("±", "0", ".", "="),
        ]
        grid = GridLayout(cols=4, rows=5, spacing=dp(10), size_hint_y=0.71)
        for row in keys:
            for key in row:
                if key in ("C", "DEL"):
                    fill = "#74334B" if key == "C" else "#263A58"
                    color = "#FFFFFF"
                elif key in ("%", "÷", "×", "−", "+"):
                    fill, color = "#123E78", "#65C8FF"
                elif key == "=":
                    fill, color = "#087FE8", "#FFFFFF"
                elif key == "±":
                    fill, color = "#263A58", "#BBD2F2"
                else:
                    fill, color = "#17263D", "#F5F7FF"
                btn = RoundedButton(text=key, fill=fill)
                btn.color = get_color_from_hex(color)
                btn.bind(on_release=lambda instance, value=key: self.press(value))
                grid.add_widget(btn)
        self.add_widget(grid)

        footer = Label(text="DESIGNED FOR EVERYDAY MATH", font_size=sp(9),
                       color=get_color_from_hex("#49617E"), size_hint_y=None, height=dp(18))
        self.add_widget(footer)

    def update_display(self):
        self.expression_label.text = self.expression
        if self.expression:
            try:
                result = safe_calculate(self.expression)
                self.result_label.text = pretty_number(result)
            except Exception:
                self.result_label.text = " "
        else:
            self.result_label.text = "0"

    def press(self, key):
        if key == "C":
            self.expression = ""
            self.just_calculated = False
            self.update_display()
            return
        if key == "DEL":
            self.expression = self.expression[:-1]
            self.just_calculated = False
            self.update_display()
            return
        if key == "=":
            if not self.expression:
                return
            try:
                answer = safe_calculate(self.expression)
                old = self.expression
                shown = pretty_number(answer)
                self.history.insert(0, f"{old} = {shown}")
                self.history = self.history[:30]
                self.expression = str(answer)
                self.result_label.text = shown
                self.expression_label.text = old + " ="
                self.just_calculated = True
            except ZeroDivisionError:
                self.result_label.text = "Cannot divide by 0"
            except Exception:
                self.result_label.text = "Invalid expression"
            return
        if key == "±":
            match = re.search(r"(-?\d+(?:\.\d+)?)$", self.expression)
            if match:
                number = match.group(1)
                replacement = number[1:] if number.startswith("-") else "-" + number
                self.expression = self.expression[:match.start()] + replacement
            elif not self.expression:
                self.expression = "-"
            self.just_calculated = False
            self.update_display()
            return

        if self.just_calculated and key not in ("+", "−", "×", "÷", "%"):
            self.expression = ""
        self.just_calculated = False

        if key == ".":
            match = re.search(r"(\d*\.?\d*)$", self.expression)
            if match and "." in match.group(1):
                return
            if not self.expression or self.expression[-1] in "+−×÷%(":
                self.expression += "0"
        if key in ("+", "−", "×", "÷") and (not self.expression or self.expression[-1] in "+−×÷"):
            if key == "−" and (not self.expression or self.expression[-1] in "+−×÷("):
                self.expression += key
            elif self.expression:
                self.expression = self.expression[:-1] + key
            self.update_display()
            return

        self.expression += key
        self.update_display()

    def show_history(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        if self.history:
            for item in self.history:
                content.add_widget(Label(text=item, color=get_color_from_hex("#EAF2FF"),
                                         size_hint_y=None, height=dp(34), font_size=sp(16)))
        else:
            content.add_widget(Label(text="Your calculations will appear here.",
                                     color=get_color_from_hex("#A9BCD5")))
        close = RoundedButton(text="Close", fill="#087FE8", size_hint_y=None, height=dp(48))
        content.add_widget(close)
        popup = Popup(title="Calculation history", content=content,
                      size_hint=(0.88, 0.65), separator_color=get_color_from_hex("#087FE8"))
        close.bind(on_release=popup.dismiss)
        popup.open()


class MyFirstApp(App):
    title = "My First App"

    def build(self):
        self.icon = "icon.png"
        return CalculatorUI()


if __name__ == "__main__":
    MyFirstApp().run()
