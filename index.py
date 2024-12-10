import sympy
from sympy import simplify, Symbol, log, exp, pi
from sympy.parsing.latex import parse_latex
from sympy.core.relational import Relational

def replace_symbols_with_assumptions(expr, assumptions, shared_symbols):
    """
    Заменяет символы в выражении на новые символы с заданными предположениями.

    Параметры:
    - expr: Выражение SymPy.
    - assumptions: Словарь предположений для переменных (например, {'x': {'positive': True}}).
    - shared_symbols: Словарь для хранения общих символов.

    Возвращает:
    - Новое выражение SymPy с заменёнными символами.
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
                print(f"Создание нового символа: {new_name} с предположениями {assumptions[s.name]}")
            else:
                new_s = shared_symbols[s.name]
            replacements[s] = new_s
            print(f"Замена символа: {s} на {new_s}")

    # Заменяем все символы с помощью subs
    expr = expr.subs(replacements)
    return expr

def compare_formulas_sympy(formula1: str, formula2: str, assumptions=None) -> (bool, float):
    """
    Сравнивает две формулы, представленные в виде строк LaTeX, используя SymPy.
    Возвращает:
    - Эквивалентны ли они
    - Процент сходства на основе коэффициента Жаккара

    Параметры:
    - formula1: Первая формула в LaTeX.
    - formula2: Вторая формула в LaTeX.
    - assumptions: Словарь предположений для переменных (например, {'x': {'positive': True}}).
    """
    try:
        # Парсим формулы без предположений
        expr1 = parse_latex(formula1)
        expr2 = parse_latex(formula2)
    except Exception as e:
        raise ValueError(f"Ошибка при парсинге формул: {e}")

    # Создаём общий словарь для символов с предположениями
    shared_symbols = {}

    # Заменяем символы на новые с предположениями
    expr1 = replace_symbols_with_assumptions(expr1, assumptions, shared_symbols)
    expr2 = replace_symbols_with_assumptions(expr2, assumptions, shared_symbols)

    # Упрощаем выражения несколько раз для улучшения результата
    simplified1 = simplify(expr1)
    simplified1 = simplify(simplified1)
    simplified2 = simplify(expr2)
    simplified2 = simplify(simplified2)

    # Для отладки: выводим упрощённые выражения
    print(f"Упрощённая Формула 1: {simplified1}")
    print(f"Упрощённая Формула 2: {simplified2}")

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

    Параметры:
    - expr: Выражение SymPy.

    Возвращает:
    - Множество строковых представлений подвыражений.
    """
    subexprs = set()
    for sub in sympy.preorder_traversal(expr):
        if isinstance(sub, Relational):
            # Пропускаем реляционные выражения (например, неравенства)
            continue
        subexprs.add(sympy.srepr(sub))  # Используем srepr для хешируемого представления
    return subexprs

def run_tests_sympy():
    test_cases = [
        # Тест 7
        {
            "formula1": r"\sqrt{x^2}",
            "formula2": r"|x|",
            "assumptions": {"x": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 8
        {
            "formula1": r"\tan(\theta)",
            "formula2": r"\frac{\sin(\theta)}{\cos(\theta)}",
            "assumptions": {"theta": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 9
        {
            "formula1": r"(a + b)^2",
            "formula2": r"a^2 + 2ab + b^2",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 10
        {
            "formula1": r"\sin^2(x) + \cos^2(x)",
            "formula2": "1",
            "assumptions": {"x": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 11
        {
            "formula1": r"1 + \tan^2(x)",
            "formula2": r"\sec^2(x)",
            "assumptions": {"x": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 12
        {
            "formula1": r"\frac{\sin(x)}{\cos(x)}",
            "formula2": r"\tan(x)",
            "assumptions": {"x": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 13
        {
            "formula1": "a + b",
            "formula2": "a - b",
            "assumptions": {},
            "expected_eq": False,
            "expected_sim": 0.0
        },
        # Тест 14
        {
            "formula1": r"\ln(x)",
            "formula2": "e^x",
            "assumptions": {},
            "expected_eq": False,
            "expected_sim": 33
        },
        # Тест 15
        {
            "formula1": r"\sqrt{x}",
            "formula2": "x^{2}",
            "assumptions": {"x": {"real": True}},
            "expected_eq": False,
            "expected_sim": 0.0
        },
        # Тест 16
        {
            "formula1": "a*b + c",
            "formula2": "a*b + d",
            "assumptions": {},
            "expected_eq": False,
            "expected_sim": 33.33  # Общий подвыражение a*b
        },
        # Тест 17
        {
            "formula1": "x^2 + y^2",
            "formula2": "x^2 + z^2",
            "assumptions": {},
            "expected_eq": False,
            "expected_sim": 33.33  # Общий термин x^2
        },
        # Тест 18
        {
            "formula1": "e^{x} + e^{y}",
            "formula2": "e^{x} + e^{z}",
            "assumptions": {},
            "expected_eq": False,
            "expected_sim": 66.67  # Общий подвыражение e^x
        },
        # Тест 19
        {
            "formula1": r"\frac{a \cdot b}{c}",
            "formula2": r"a \cdot \frac{b}{c}",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 20
        {
            "formula1": r"(a \cdot b) \cdot c",
            "formula2": "a \cdot (b \cdot c)",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 21
        {
            "formula1": r"\frac{\frac{a}{b}}{c}",
            "formula2": r"\frac{a}{b \cdot c}",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 22
        {
            "formula1": r"\frac{a + b}{c}",
            "formula2": r"\frac{a}{c} + \frac{b}{c}",
            "assumptions": {"c": {"nonzero": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 23
        {
            "formula1": r"\frac{1}{a} + \frac{1}{b}",
            "formula2": r"\frac{a + b}{a \cdot b}",
            "assumptions": {"a": {"positive": True}, "b": {"positive": True, "neq": 1}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 24
        {
            "formula1": r"(a + b)^3",
            "formula2": r"a^3 + 3a^2b + 3ab^2 + b^3",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 25
        {
            "formula1": r"\arcsin(\sin(x))",
            "formula2": "x",
            "assumptions": {"x": {"real": True}},  # Без конкретного диапазона
            "expected_eq": False,  # SymPy не учитывает диапазон автоматически
            "expected_sim": 33.33  # Общие подвыражения (например, sin(x), arcsin(sin(x)))
        },
        # Тест 26
        {
            "formula1": r"x^{a} \cdot x^{b}",
            "formula2": r"x^{a + b}",
            "assumptions": {"x": {"nonzero": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 27
        {
            "formula1": r"\log_b(a)",
            "formula2": r"\frac{\ln(a)}{\ln(b)}",
            "assumptions": {"a": {"positive": True}, "b": {"positive": True, "neq": 1}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 28
        {
            "formula1": r"(a - b)*(a + b)",
            "formula2": r"a^2 - b^2",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 30
        {
            "formula1": r"\frac{d}{dx}(x^3)",
            "formula2": "3x^2",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 31
        {
            "formula1": r"\int 3x^2 \, dx",
            "formula2": "x^3",
            "assumptions": {},
            "expected_eq": True,  # Игнорируем постоянную C
            "expected_sim": 100.0
        },
        # Тест 33
        {
            "formula1": r"\log_b(a)",
            "formula2": r"\frac{\ln(a)}{\ln(b)}",
            "assumptions": {"a": {"positive": True}, "b": {"positive": True, "neq": 1}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 34
        {
            "formula1": r"a \cdot (b \cdot c)",
            "formula2": r"(a \cdot b) \cdot c",
            "assumptions": {},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 35
        {
            "formula1": r"\cos(-x)",
            "formula2": r"\cos(x)",
            "assumptions": {"x": {"real": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
        # Тест 36
        {
            "formula1": r"x^{a} \cdot x^{b}",
            "formula2": r"x^{a + b}",
            "assumptions": {"x": {"nonzero": True}},
            "expected_eq": True,
            "expected_sim": 100.0
        },
    ]

    for idx, test in enumerate(test_cases, start=6):
        f1 = test["formula1"]
        f2 = test["formula2"]
        assumptions = test.get("assumptions", {})
        expected_eq = test["expected_eq"]
        expected_sim = test["expected_sim"]
        try:
            equal, similarity = compare_formulas_sympy(f1, f2, assumptions=assumptions)
            result_eq = "✅" if equal == expected_eq else "❌"
            # Округляем similarity до двух знаков
            similarity_rounded = round(similarity, 2)
            # Определяем результат сходства
            if equal:
                # Если эквивалентны, должен быть 100%
                if similarity_rounded == 100.0:
                    result_sim = "✅"
                else:
                    result_sim = f"❌ (ожидалось 100.00%)"
            else:
                # Если не эквивалентны, проверяем, соответствует ли similarity ожидаемому
                if abs(similarity_rounded - expected_sim) < 0.01:
                    result_sim = "✅"
                else:
                    result_sim = f"❌ (ожидалось {expected_sim:.2f}%)"
            print(f"Тест {idx}:")
            print(f"Формулы '{f1}' и '{f2}' эквивалентны: {equal}, Процент сходства: {similarity_rounded:.2f}% {result_eq}{result_sim}\n")
        except ValueError as ve:
            print(f"Тест {idx}: Ошибка: {ve}\n")

def main():
    run_tests_sympy()

if __name__ == "__main__":
    main()
