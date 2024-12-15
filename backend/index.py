# index.py
import sympy
from sympy import simplify, Symbol, Add, Mul
from sympy.parsing.latex import parse_latex
from sympy.core.relational import Relational

def replace_symbols_with_assumptions(expr, assumptions):
    if not assumptions:
        return expr
    replacements = {}
    for s in expr.free_symbols:
        if s.name in assumptions:
            new_name = f"{s.name}_assume"
            new_s = Symbol(new_name, **assumptions[s.name])
            replacements[s] = new_s
    return expr.subs(replacements)

def canonicalize_equation(expr):
    if isinstance(expr, Relational):
        expr = expr.lhs - expr.rhs
    return expr

def find_all_occurrences(string, substring):
    occurrences = []
    start = 0
    while True:
        idx = string.find(substring, start)
        if idx == -1:
            break
        occurrences.append((idx, len(substring)))
        start = idx + 1
    return occurrences

def expr_size(expr):
    count = 1
    for arg in expr.args:
        count += expr_size(arg)
    return count

def canonical_form(expr):
    """
    Приводит выражение к канонической форме:
    - Раскрываем выражение (expand)
    - Для сложений (Add) и умножений (Mul) сортируем аргументы по srepr()
    """
    expr = sympy.expand(expr)
    if expr.is_Atom:
        return expr
    # Применяем рекурсивно канонизацию к аргументам
    new_args = [canonical_form(a) for a in expr.args]
    if isinstance(expr, Add) or isinstance(expr, Mul):
        # Сортируем аргументы
        new_args.sort(key=lambda x: sympy.srepr(x))
        if isinstance(expr, Add):
            return Add(*new_args, evaluate=False)
        else:
            return Mul(*new_args, evaluate=False)
    else:
        # Другие типы (Pow, Function etc.) просто пересобираем с канонизированными аргументами
        return type(expr)(*new_args)

def subexpressions(expr):
    subs = set()
    for sub in sympy.preorder_traversal(expr):
        subs.add(sub)
    return subs

def can_match_with_renaming(sub1, sub2):
    var_map = {}
    def match(e1, e2):
        if e1.is_Atom and e2.is_Atom:
            if e1.is_Symbol and e2.is_Symbol:
                if e1 in var_map:
                    return var_map[e1] == e2
                else:
                    var_map[e1] = e2
                    return True
            else:
                return e1.equals(e2)
        if type(e1) != type(e2):
            return False
        if len(e1.args) != len(e2.args):
            return False
        return all(match(a1, a2) for a1, a2 in zip(e1.args, e2.args))
    return match(sub1, sub2)

def largest_common_subexpression(expr1, expr2):
    subs1 = list(subexpressions(expr1))
    subs2 = list(subexpressions(expr2))
    # Сортируем по размеру по убыванию
    subs1.sort(key=expr_size, reverse=True)
    best_size = 0
    for s1 in subs1:
        size_s1 = expr_size(s1)
        if size_s1 <= best_size:
            break
        for s2 in subs2:
            if expr_size(s2) < best_size:
                continue
            if can_match_with_renaming(s1, s2):
                if size_s1 > best_size:
                    best_size = size_s1
                break
    return best_size

def get_subexpressions_with_index(expr):
    subexpr_set = set()
    subexpr_dict = {}
    index_map = {}
    def _traverse(x, idx=0):
        r = sympy.srepr(x)
        subexpr_set.add(r)
        if r not in subexpr_dict:
            subexpr_dict[r] = x
        if r not in index_map:
            index_map[r] = []
        index_map[r].append(idx)
        cur_idx = idx + 1
        for a in x.args:
            cur_idx = _traverse(a, cur_idx)
        return cur_idx

    _traverse(expr, 0)
    return subexpr_set, subexpr_dict, index_map

def canonicalize_variables(expr1, expr2):
    vars1 = sorted(expr1.free_symbols, key=lambda x: x.name)
    vars2 = sorted(expr2.free_symbols, key=lambda x: x.name)
    if len(vars1) == len(vars2):
        new_vars = [Symbol(f"x_{i}") for i in range(1, len(vars1)+1)]
        mapping1 = {v1: nv for v1, nv in zip(vars1, new_vars)}
        mapping2 = {v2: nv for v2, nv in zip(vars2, new_vars)}
        new_expr1 = simplify(expr1.subs(mapping1))
        new_expr2 = simplify(expr2.subs(mapping2))
        return new_expr1, new_expr2, True
    else:
        # Различное количество переменных. Просто вернём как есть.
        return expr1, expr2, False

def compare_formulas_sympy(formula1: str, formula2: str, assumptions=None):
    """
    Сравнивает две формулы, используя:
    - Канонизацию имён переменных
    - Приведение к канонической форме (сортировка аргументов в Add/Mul)
    - Поиск наибольшего общего подвыражения (НОП)
    """
    try:
        expr1 = parse_latex(formula1)
        expr2 = parse_latex(formula2)
    except Exception as e:
        raise ValueError(f"Ошибка при парсинге формул: {e}")

    expr1 = canonicalize_equation(expr1)
    expr2 = canonicalize_equation(expr2)

    expr1 = replace_symbols_with_assumptions(expr1, assumptions)
    expr2 = replace_symbols_with_assumptions(expr2, assumptions)

    # Упрощаем
    expr1_simpl = simplify(expr1)
    expr2_simpl = simplify(expr2)

    # Канонизация переменных
    expr1_canon, expr2_canon, can_compare = canonicalize_variables(expr1_simpl, expr2_simpl)

    # Приводим к канонической форме (упорядочиваем слагаемые и множители)
    expr1_canon = canonical_form(expr1_canon)
    expr2_canon = canonical_form(expr2_canon)

    if can_compare and expr1_canon.equals(expr2_canon):
        equivalent = True
        similarity = 100.0
        simplified1 = expr1_canon
        simplified2 = expr2_canon
    else:
        equivalent = False
        simplified1 = expr1_canon
        simplified2 = expr2_canon
        size1 = expr_size(simplified1)
        size2 = expr_size(simplified2)
        if (size1 + size2) == 0:
            similarity = 0.0
        else:
            L = largest_common_subexpression(simplified1, simplified2)
            similarity = (2*L/(size1+size2))*100

    subexprs1, subexprs_dict1, index_map1 = get_subexpressions_with_index(simplified1)
    subexprs2, subexprs_dict2, index_map2 = get_subexpressions_with_index(simplified2)
    intersection = subexprs1.intersection(subexprs2)
    latex_simplified2 = sympy.latex(simplified2)

    common_subexpressions = []
    common_indices_in_expr2 = {}
    substring_occurrences_in_simplified2 = {}

    for s in intersection:
        sub_expr = subexprs_dict1[s]
        l_sub = sympy.latex(sub_expr)
        common_subexpressions.append(l_sub)
        indices = index_map2[s]
        common_indices_in_expr2[l_sub] = indices
        occ = find_all_occurrences(latex_simplified2, l_sub)
        substring_occurrences_in_simplified2[l_sub] = occ

    return (equivalent,
            similarity,
            common_subexpressions,
            common_indices_in_expr2,
            substring_occurrences_in_simplified2,
            simplified1,
            simplified2)
