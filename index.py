
from difflib import SequenceMatcher
from converter import latex_to_ast


def normalize_ast(ast_nodes, symbol_table=None, counter=0):
    if symbol_table is None:
        symbol_table = {}

    normalized_nodes = []
    for node in ast_nodes:
        node_type = node.get('type')
        if node_type == 'variable':
            name = node['name']
            if name not in symbol_table:
                symbol_table[name] = f'v{counter}'
                counter += 1
            normalized_name = symbol_table[name]
            normalized_nodes.append({'type': 'variable', 'name': normalized_name})
        else:
            # Рекурсивно нормализуем дочерние узлы
            normalized_node = {'type': node_type}
            for key, value in node.items():
                if key not in ['type', 'name']:
                    if isinstance(value, list):
                        normalized_value, counter = normalize_ast(value, symbol_table, counter)
                        normalized_node[key] = normalized_value
                    else:
                        normalized_node[key] = value
                elif key == 'name':
                    # Если это не переменная, сохраняем имя макроса или функции
                    normalized_node['name'] = value
            normalized_nodes.append(normalized_node)
    return normalized_nodes, counter

# Функция для генерации канонического представления AST
def ast_to_canonical(ast_nodes):
    canonical_str = ''
    for node in ast_nodes:
        node_type = node.get('type')
        if node_type == 'variable':
            canonical_str += f"var({node['name']})"
        elif node_type in ['fraction', 'sqrt', 'function', 'hat', 'boldsymbol', 'vector']:
            canonical_str += node_type + '('
            for key in node:
                if key not in ['type', 'name']:
                    value = node[key]
                    if isinstance(value, list):
                        canonical_str += ast_to_canonical(value)
                    else:
                        canonical_str += str(value)
            canonical_str += ')'
        elif node_type == 'macro':
            macro_name = node.get('name', 'unknown')
            canonical_str += f"macro({macro_name})"
            if 'arguments' in node:
                canonical_str += '(' + ast_to_canonical(node['arguments']) + ')'
        else:
            # Обработка других типов узлов
            pass
    return canonical_str

# Функция для вычисления степени сходства
def compute_similarity(s1, s2):
    matcher = SequenceMatcher(None, s1, s2)
    return matcher.ratio()

# Инициализация "базы данных"
formula_database = []

# Функция для сохранения формулы в базу данных
def store_formula(latex_str):
    ast = latex_to_ast(latex_str)
    if 'error' in ast:
        print(f"Ошибка при парсинге LaTeX: {ast['error']}")
        return
    normalized_ast, _ = normalize_ast(ast)
    canonical = ast_to_canonical(normalized_ast)
    formula_entry = {
        'latex': latex_str,
        'ast': ast,
        'normalized_ast': normalized_ast,
        'canonical': canonical
    }
    formula_database.append(formula_entry)

# Функция для сравнения новой формулы с базой данных
def compare_formula(latex_str, threshold=0.8):
    ast = latex_to_ast(latex_str)
    if 'error' in ast:
        print(f"Ошибка при парсинге LaTeX: {ast['error']}")
        return []
    normalized_ast, _ = normalize_ast(ast)
    canonical = ast_to_canonical(normalized_ast)

    matches = []
    for entry in formula_database:
        existing_canonical = entry['canonical']
        similarity = compute_similarity(canonical, existing_canonical)
        if similarity >= threshold:
            matches.append({
                'entry': entry,
                'similarity': similarity
            })

    # Сортируем совпадения по убыванию степени сходства
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches

# Основная функция для тестирования
def main():
    # Формулы для добавления в базу данных
    formulas = [
        r'\frac{a + b}{c^2}',
        r'\sqrt{a^2 + b^2}',
        r'\int_{a}^{b} x \, dx',
    ]

    # Добавляем формулы в базу данных
    for formula in formulas:
        store_formula(formula)

    # Новая формула для сравнения
    new_formula = r'\frac{x + y}{z^2}'

    print(f"Сравнение формулы: {new_formula}")
    matches = compare_formula(new_formula)

    if matches:
        print("Найдены совпадения:")
        for match in matches:
            entry = match['entry']
            similarity = match['similarity']
            print(f"Формула: {entry['latex']}, Сходство: {similarity:.2f}")
    else:
        print("Совпадений не найдено.")

if __name__ == "__main__":
    main()