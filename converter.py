from sympy.parsing.latex import parse_latex
from sympy import latex

def ast_to_latex(ast):
    """
    Функция для преобразования AST (Abstract Syntax Tree) в строку LaTeX.
    Рекурсивно обрабатывает каждый узел AST.

    :param ast: Словарь, представляющий AST.
    :return: Строка LaTeX.
    """
    if ast['type'] == 'fraction':
        # Если узел представляет дробь, рекурсивно обрабатываем числитель и знаменатель.
        numerator = ast_to_latex(ast['numerator'])
        denominator = ast_to_latex(ast['denominator'])
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    elif ast['type'] == 'addition':
        # Если узел представляет сложение, обрабатываем каждый операнд.
        operands = [ast_to_latex(op) for op in ast['operands']]
        return ' + '.join(operands)
    elif ast['type'] == 'power':
        # Если узел представляет возведение в степень, обрабатываем основание и показатель.
        base = ast_to_latex(ast['base'])
        exponent = ast_to_latex(ast['exponent'])
        return f"{base}^{{{exponent}}}"
    elif ast['type'] == 'variable':
        # Если узел представляет переменную, возвращаем её имя.
        return ast['name']
    elif ast['type'] == 'number':
        # Если узел представляет число, возвращаем его значение как строку.
        return str(ast['value'])
    else:
        # Если узел неизвестного типа, выбрасываем ошибку.
        raise ValueError("Unknown AST node type")


def latex_to_ast(latex):
    """
    Функция для преобразования строки LaTeX в AST.
    Использует библиотеку для парсинга LaTeX и строит дерево AST.

    :param latex: Строка LaTeX.
    :return: Словарь, представляющий AST.
    """
    try:
        # Парсим LaTeX-строку в выражение SymPy
        parsed_expr = parse_latex(latex)
        # Преобразуем SymPy-выражение в AST.
        return sympy_to_ast(parsed_expr)
    except Exception as e:
        # Если произошла ошибка, возвращаем описание ошибки.
        return {"error": str(e)}

def sympy_to_ast(expr):
    """
    Рекурсивная функция для преобразования выражений SymPy в AST.

    :param expr: Выражение SymPy.
    :return: Словарь, представляющий AST.
    """
    from sympy import Add, Pow, Mul, Symbol, Integer
    if isinstance(expr, Add):
        # Если выражение представляет сложение, обрабатываем его аргументы.
        return {
            "type": "addition",
            "operands": [sympy_to_ast(arg) for arg in expr.args]
        }
    elif isinstance(expr, Pow):
        # Если выражение представляет возведение в степень, обрабатываем основание и показатель.
        return {
            "type": "power",
            "base": sympy_to_ast(expr.args[0]),
            "exponent": sympy_to_ast(expr.args[1])
        }
    elif isinstance(expr, Mul):
        # Если выражение представляет умножение (или дробь), выделяем числитель и знаменатель.
        num, denom = expr.as_numer_denom()
        return {
            "type": "fraction",
            "numerator": sympy_to_ast(num),
            "denominator": sympy_to_ast(denom)
        }
    elif isinstance(expr, Symbol):
        # Если выражение представляет переменную, возвращаем её имя.
        return {"type": "variable", "name": str(expr)}
    elif isinstance(expr, Integer):
        # Если выражение представляет число, возвращаем его значение.
        return {"type": "number", "value": int(expr)}
    else:
        # Если выражение неизвестного типа, выбрасываем ошибку.
        raise ValueError("Unsupported expression type")
