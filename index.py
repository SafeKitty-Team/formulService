import sympy
from sympy import simplify, Symbol, Eq
from sympy.parsing.latex import parse_latex
from sympy.core.relational import Relational

def replace_symbols_with_assumptions(expr, assumptions, shared_symbols):
    """
    Заменяет символы в выражении на новые символы с заданными предположениями.
    """
    if not assumptions:
        return expr

    replacements = {}
    for s in expr.free_symbols:
        if s.name in assumptions:
            if s.name not in shared_symbols:
                # Создаём новый символ с уникальным именем и предположениями
                new_name = f"{s.name}_assume"
                new_s = Symbol(new_name, **assumptions[s.name])
                shared_symbols[s.name] = new_s
            else:
                new_s = shared_symbols[s.name]
            replacements[s] = new_s
    # Заменяем все символы с помощью subs
    expr = expr.subs(replacements)
    return expr

def compare_formulas_sympy(formula1: str, formula2: str, assumptions=None) -> (bool, float):
    """
    Сравнивает две формулы, представленные в виде строк LaTeX, используя SymPy.
    Возвращает:
    - Эквивалентны ли они
    - Процент сходства на основе коэффициента Жаккара
    """
    try:
        # Парсим формулы
        expr1 = parse_latex(formula1)
        expr2 = parse_latex(formula2)
    except Exception as e:
        raise ValueError(f"Ошибка при парсинге формул: {e}")

    # Преобразуем равенства в выражения (приводим к виду expr = 0)
    if isinstance(expr1, Relational):
        expr1 = expr1.lhs - expr1.rhs
    if isinstance(expr2, Relational):
        expr2 = expr2.lhs - expr2.rhs

    # Создаём общий словарь для символов с предположениями
    shared_symbols = {}

    # Заменяем символы на новые с предположениями, если они заданы
    expr1 = replace_symbols_with_assumptions(expr1, assumptions, shared_symbols)
    expr2 = replace_symbols_with_assumptions(expr2, assumptions, shared_symbols)

    # Упрощаем выражения несколько раз для улучшения результата
    simplified1 = simplify(expr1)
    simplified1 = simplify(simplified1)
    simplified2 = simplify(expr2)
    simplified2 = simplify(simplified2)

    # Для отладки: выводим упрощённые выражения
    # Проверяем эквивалентность
    equivalent = simplified1.equals(simplified2)

    if equivalent:
        similarity = 100.0
    else:
        # Извлекаем подвыражения
        subexprs1 = get_subexpressions(simplified1)
        subexprs2 = get_subexpressions(simplified2)

        # Вычисляем коэффициент Жаккара
        intersection = subexprs1.intersection(subexprs2)
        union = subexprs1.union(subexprs2)

        if not union:
            similarity = 0.0
        else:
            similarity = (len(intersection) / len(union)) * 100

    return equivalent, similarity

def get_subexpressions(expr: sympy.Expr) -> set:
    """
    Получает все подвыражения из выражения SymPy.
    """
    subexprs = set()
    for sub in sympy.preorder_traversal(expr):
        if isinstance(sub, Relational):
            # Пропускаем реляционные выражения (например, неравенства)
            continue
        subexprs.add(sympy.srepr(sub))  # Используем srepr для хешируемого представления
    return subexprs

# Пример использования
if __name__ == "__main__":
    formula1 = "a \\left( -b + \\sqrt{ -4 a c + b^{2} } \\right) / 2"
    formula2 = "x = a \\left( -b + \\sqrt{ -4 a c + b^{2} } \\right) / 2"

    # Предположения, если необходимы
    assumptions = {
        'a': {'real': True},
        'b': {'real': True},
        'c': {'real': True},
        'x': {'real': True}
    }

    try:
        equivalent, similarity = compare_formulas_sympy(formula1, formula2, assumptions)
        print(f"Эквивалентны: {equivalent}, Сходство: {similarity:.2f}%")
    except ValueError as e:
        print(f"Ошибка при сравнении формул ID 6: {e}")
