from sympy.parsing.latex import parse_latex
from sympy import (
    latex, sympify, Symbol, Integer, Float, Rational,
    Pow, Add, Mul, sqrt, log, sin, cos, tan,
    Integral, Derivative, Limit, Sum, Function, S, symbols
)
from sympy.core.relational import Relational
from sympy.functions.elementary.trigonometric import TrigonometricFunction
from sympy.functions.elementary.hyperbolic import HyperbolicFunction
from sympy.functions.elementary.exponential import exp

def ast_to_latex(ast):
    """
    Функция для преобразования AST (Abstract Syntax Tree) в строку LaTeX.
    Рекурсивно обрабатывает каждый узел AST.

    :param ast: Словарь, представляющий AST.
    :return: Строка LaTeX.
    """
    node_type = ast.get('type')

    if node_type == 'fraction':
        # Обработка дроби
        numerator = ast_to_latex(ast['numerator'])
        denominator = ast_to_latex(ast['denominator'])
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    elif node_type == 'addition':
        # Обработка сложения
        operands = [ast_to_latex(op) for op in ast['operands']]
        return ' + '.join(operands)
    elif node_type == 'subtraction':
        # Обработка вычитания
        minuend = ast_to_latex(ast['minuend'])
        subtrahend = ast_to_latex(ast['subtrahend'])
        return f"{minuend} - {subtrahend}"
    elif node_type == 'multiplication':
        # Обработка умножения
        operands = [ast_to_latex(op) for op in ast['operands']]
        return ' \\cdot '.join(operands)
    elif node_type == 'division':
        # Обработка деления
        dividend = ast_to_latex(ast['dividend'])
        divisor = ast_to_latex(ast['divisor'])
        return f"\\dfrac{{{dividend}}}{{{divisor}}}"
    elif node_type == 'power':
        # Обработка возведения в степень
        base = ast_to_latex(ast['base'])
        exponent = ast_to_latex(ast['exponent'])
        return f"{base}^{{{exponent}}}"
    elif node_type == 'sqrt':
        # Обработка квадратного корня
        radicand = ast_to_latex(ast['radicand'])
        return f"\\sqrt{{{radicand}}}"
    elif node_type == 'nth_root':
        # Обработка корня n-й степени
        radicand = ast_to_latex(ast['radicand'])
        index = ast_to_latex(ast['index'])
        return f"\\sqrt[{index}]{{{radicand}}}"
    elif node_type == 'function':
        # Обработка функций (тригонометрических, логарифмических и т.д.)
        func_name = ast['name']
        arguments = ast.get('arguments', [])
        if arguments:
            args_latex = ', '.join([ast_to_latex(arg) for arg in arguments])
            return f"\\{func_name}({args_latex})"
        else:
            argument = ast_to_latex(ast['argument'])
            return f"\\{func_name}{{{argument}}}"
    elif node_type == 'negative':
        # Обработка отрицательных чисел или выражений
        operand = ast_to_latex(ast['operand'])
        return f"-{operand}"
    elif node_type == 'number':
        # Обработка целых чисел
        return str(ast['value'])
    elif node_type == 'float':
        # Обработка чисел с плавающей точкой
        return str(ast['value'])
    elif node_type == 'variable':
        # Обработка переменных
        return ast['name']
    elif node_type == 'parentheses':
        # Обработка выражений в скобках
        expression = ast_to_latex(ast['expression'])
        return f"\\left({expression}\\right)"
    elif node_type == 'log':
        # Обработка логарифмов
        argument = ast_to_latex(ast['argument'])
        base = ast_to_latex(ast['base']) if 'base' in ast else ''
        if base:
            return f"\\log_{{{base}}}{{{argument}}}"
        else:
            return f"\\ln{{{argument}}}"
    elif node_type == 'integral':
        # Обработка интегралов
        integrand = ast_to_latex(ast['integrand'])
        variable = ast_to_latex(ast['variable'])
        limits = ast.get('limits')
        if limits:
            lower_limit = ast_to_latex(limits['lower'])
            upper_limit = ast_to_latex(limits['upper'])
            return f"\\int_{{{lower_limit}}}^{{{upper_limit}}} {integrand} \\, d{variable}"
        else:
            return f"\\int {integrand} \\, d{variable}"
    elif node_type == 'derivative':
        # Обработка производных
        function = ast_to_latex(ast['function'])
        variable = ast_to_latex(ast['variable'])
        order = ast.get('order', 1)
        if order == 1:
            return f"\\frac{{d}}{{d{variable}}}{function}"
        else:
            return f"\\frac{{d^{order}}}{{d{variable}^{order}}}{function}"
    elif node_type == 'limit':
        # Обработка пределов
        expression = ast_to_latex(ast['expression'])
        variable = ast_to_latex(ast['variable'])
        value = ast_to_latex(ast['value'])
        direction = ast.get('direction', '')
        if direction == '+':
            return f"\\lim_{{{variable} \\to {value}^+}} {expression}"
        elif direction == '-':
            return f"\\lim_{{{variable} \\to {value}^-}} {expression}"
        else:
            return f"\\lim_{{{variable} \\to {value}}} {expression}"
    elif node_type == 'sum':
        # Обработка сумм
        expression = ast_to_latex(ast['expression'])
        variable = ast_to_latex(ast['variable'])
        lower_limit = ast_to_latex(ast['lower_limit'])
        upper_limit = ast_to_latex(ast['upper_limit'])
        return f"\\sum_{{{variable}={lower_limit}}}^{{{upper_limit}}} {expression}"
    elif node_type == 'equation':
        # Обработка уравнений
        lhs = ast_to_latex(ast['lhs'])
        rhs = ast_to_latex(ast['rhs'])
        operator = ast.get('operator', '=')
        return f"{lhs} {operator} {rhs}"
    else:
        # Если тип узла неизвестен
        raise ValueError(f"Неизвестный тип узла AST: {node_type}")

def latex_to_ast(latex_str):
    """
    Функция для преобразования строки LaTeX в AST.
    Парсит LaTeX-строку и строит AST.

    :param latex_str: Строка LaTeX.
    :return: Словарь, представляющий AST.
    """
    try:
        parsed_expr = parse_latex(latex_str)
        return sympy_expr_to_ast(parsed_expr)
    except Exception as e:
        return {"error": str(e)}

def sympy_expr_to_ast(expr):
    """
    Рекурсивная функция для преобразования выражения SymPy в AST.

    :param expr: Выражение SymPy.
    :return: Словарь, представляющий AST.
    """
    if isinstance(expr, Integer):
        # Обработка целых чисел
        if expr < 0:
            return {
                "type": "negative",
                "operand": {"type": "number", "value": -int(expr)}
            }
        else:
            return {"type": "number", "value": int(expr)}
    elif isinstance(expr, Float):
        # Обработка чисел с плавающей точкой
        if expr < 0:
            return {
                "type": "negative",
                "operand": {"type": "float", "value": -float(expr)}
            }
        else:
            return {"type": "float", "value": float(expr)}
    elif isinstance(expr, Symbol):
        # Обработка переменных
        return {"type": "variable", "name": str(expr)}
    elif isinstance(expr, Add):
        # Обработка сложения и вычитания
        operands = []
        for term in expr.args:
            if term.is_negative:
                operands.append({
                    "type": "negative",
                    "operand": sympy_expr_to_ast(-term)
                })
            else:
                operands.append(sympy_expr_to_ast(term))
        return {"type": "addition", "operands": operands}
    elif isinstance(expr, Mul):
        # Обработка умножения
        coeff, factors = expr.as_coeff_mul()
        operands = []
        if coeff != 1:
            operands.append(sympy_expr_to_ast(coeff))
        operands += [sympy_expr_to_ast(factor) for factor in factors]
        return {"type": "multiplication", "operands": operands}
    elif isinstance(expr, Pow):
        # Обработка возведения в степень
        base, exponent = expr.args
        return {
            "type": "power",
            "base": sympy_expr_to_ast(base),
            "exponent": sympy_expr_to_ast(exponent)
        }
    elif isinstance(expr, Rational):
        # Обработка рациональных чисел (дробей)
        numerator = sympy_expr_to_ast(expr.p)
        denominator = sympy_expr_to_ast(expr.q)
        return {
            "type": "fraction",
            "numerator": numerator,
            "denominator": denominator
        }
    elif isinstance(expr, TrigonometricFunction):
        # Обработка тригонометрических функций
        func_name = expr.func.__name__.lower()
        argument = sympy_expr_to_ast(expr.args[0])
        return {
            "type": "function",
            "name": func_name,
            "argument": argument
        }
    elif isinstance(expr, HyperbolicFunction):
        # Обработка гиперболических функций
        func_name = expr.func.__name__.lower()
        argument = sympy_expr_to_ast(expr.args[0])
        return {
            "type": "function",
            "name": func_name,
            "argument": argument
        }
    elif isinstance(expr, log):
        # Обработка логарифмов
        args = expr.args
        if len(args) == 1:
            argument = sympy_expr_to_ast(args[0])
            return {
                "type": "log",
                "argument": argument
            }
        else:
            argument = sympy_expr_to_ast(args[0])
            base = sympy_expr_to_ast(args[1])
            return {
                "type": "log",
                "argument": argument,
                "base": base
            }
    elif expr.func == sqrt:
        # Обработка квадратного корня
        radicand = sympy_expr_to_ast(expr.args[0])
        return {
            "type": "sqrt",
            "radicand": radicand
        }
    elif isinstance(expr, Integral):
        # Обработка интегралов
        integrand = sympy_expr_to_ast(expr.args[0])
        variables = expr.variables
        variable = sympy_expr_to_ast(variables[0])
        if expr.limits:
            limits = expr.limits[0]
            lower = sympy_expr_to_ast(limits[1])
            upper = sympy_expr_to_ast(limits[2])
            return {
                "type": "integral",
                "integrand": integrand,
                "variable": variable,
                "limits": {
                    "lower": lower,
                    "upper": upper
                }
            }
        else:
            return {
                "type": "integral",
                "integrand": integrand,
                "variable": variable
            }
    elif isinstance(expr, Derivative):
        # Обработка производных
        function = sympy_expr_to_ast(expr.expr)
        variables = expr.variables
        variable = sympy_expr_to_ast(variables[0][0]) if isinstance(variables[0], tuple) else sympy_expr_to_ast(variables[0])
        order = variables[0][1] if isinstance(variables[0], tuple) else 1
        return {
            "type": "derivative",
            "function": function,
            "variable": variable,
            "order": order
        }
    elif isinstance(expr, Limit):
        # Обработка пределов
        expression = sympy_expr_to_ast(expr.args[0])
        variable = sympy_expr_to_ast(expr.args[1])
        value = sympy_expr_to_ast(expr.args[2])
        direction = expr.direction
        return {
            "type": "limit",
            "expression": expression,
            "variable": variable,
            "value": value,
            "direction": direction
        }
    elif isinstance(expr, Sum):
        # Обработка сумм
        expression = sympy_expr_to_ast(expr.function)
        variable = sympy_expr_to_ast(expr.variables[0])
        lower_limit = sympy_expr_to_ast(expr.limits[0][1])
        upper_limit = sympy_expr_to_ast(expr.limits[0][2])
        return {
            "type": "sum",
            "expression": expression,
            "variable": variable,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit
        }
    elif isinstance(expr, Relational):
        # Обработка уравнений и неравенств
        lhs = sympy_expr_to_ast(expr.lhs)
        rhs = sympy_expr_to_ast(expr.rhs)
        operator = expr.rel_op
        return {
            "type": "equation",
            "lhs": lhs,
            "rhs": rhs,
            "operator": operator
        }
    elif expr.func == exp:
        # Обработка экспоненциальной функции
        exponent = sympy_expr_to_ast(expr.args[0])
        return {
            "type": "function",
            "name": "exp",
            "argument": exponent
        }
    elif isinstance(expr, Function):
        # Обработка пользовательских функций
        func_name = expr.func.__name__
        arguments = [sympy_expr_to_ast(arg) for arg in expr.args]
        return {
            "type": "function",
            "name": func_name,
            "arguments": arguments
        }
    else:
        # Если тип выражения неизвестен
        return {"type": "unknown", "value": str(expr)}
