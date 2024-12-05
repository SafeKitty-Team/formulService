# Импорт необходимых модулей
from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexCharsNode, LatexGroupNode, LatexMathNode
from pylatexenc.latex2text import LatexNodes2Text

# Функция для преобразования LaTeX-строки в AST
def latex_to_ast(latex_str):
    try:
        # Создаём объект LatexWalker
        walker = LatexWalker(latex_str)
        # Получаем список узлов
        nodes, pos, len_ = walker.get_latex_nodes()
        # Обрабатываем узлы и строим AST
        ast = process_nodes(nodes)
        return ast
    except Exception as e:
        return {"error": str(e)}

# Рекурсивная функция для обработки узлов и построения AST
def process_nodes(nodes):
    ast_nodes = []
    for node in nodes:
        if isinstance(node, LatexCharsNode):
            # Обработка текстовых символов
            content = node.chars.strip()
            if content:
                ast_nodes.append({"type": "variable", "name": content})
        elif isinstance(node, LatexMacroNode):
            # Обработка макросов LaTeX
            macro_name = node.macroname
            if macro_name == 'vec':
                # Обработка векторного обозначения
                argument = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({"type": "vector", "content": argument})
            elif macro_name == 'boldsymbol':
                # Обработка жирных символов
                argument = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({"type": "boldsymbol", "content": argument})
            elif macro_name == 'frac':
                # Обработка дробей
                numerator = process_nodes([node.nodeargd.argnlist[0]])
                denominator = process_nodes([node.nodeargd.argnlist[1]])
                ast_nodes.append({
                    "type": "fraction",
                    "numerator": numerator,
                    "denominator": denominator
                })
            elif macro_name == 'sqrt':
                # Обработка квадратного корня
                argument = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({
                    "type": "sqrt",
                    "content": argument
                })
            elif macro_name in ['sin', 'cos', 'tan', 'ln', 'log', 'exp']:
                # Обработка математических функций
                argument = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({
                    "type": "function",
                    "name": macro_name,
                    "argument": argument
                })
            elif macro_name == 'hat':
                # Обработка символа 'hat' (крышечка над символом)
                argument = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({
                    "type": "hat",
                    "content": argument
                })
            else:
                # Обработка других макросов
                arguments = []
                if node.nodeargd:
                    arguments = process_nodes(node.nodeargd.argnlist)
                ast_nodes.append({
                    "type": "macro",
                    "name": macro_name,
                    "arguments": arguments
                })
        elif isinstance(node, LatexGroupNode):
            # Обработка групп (скобки и аргументы макросов)
            content = process_nodes(node.nodelist)
            ast_nodes.extend(content)
        elif isinstance(node, LatexEnvironmentNode):
            # Обработка окружений (не часто встречаются в формулах)
            env_name = node.environmentname
            content = process_nodes(node.nodelist)
            ast_nodes.append({
                "type": "environment",
                "name": env_name,
                "content": content
            })
        elif isinstance(node, LatexMathNode):
            # Обработка математических выражений
            content = process_nodes(node.nodelist)
            ast_nodes.extend(content)
        else:
            # Обработка других типов узлов при необходимости
            pass
    return ast_nodes

# Функция для преобразования AST обратно в LaTeX-строку
def ast_to_latex(ast_nodes):
    latex_str = ''
    for node in ast_nodes:
        if isinstance(node, str):
            # Если узел является строкой, просто добавляем его
            latex_str += node
            continue
        node_type = node.get('type')
        if node_type == 'variable':
            latex_str += node['name']
        elif node_type == 'vector':
            content = ast_to_latex(node['content'])
            latex_str += f"\\vec{{{content}}}"
        elif node_type == 'boldsymbol':
            content = ast_to_latex(node['content'])
            latex_str += f"\\boldsymbol{{{content}}}"
        elif node_type == 'fraction':
            numerator = ast_to_latex(node['numerator'])
            denominator = ast_to_latex(node['denominator'])
            latex_str += f"\\frac{{{numerator}}}{{{denominator}}}"
        elif node_type == 'sqrt':
            content = ast_to_latex(node['content'])
            latex_str += f"\\sqrt{{{content}}}"
        elif node_type == 'function':
            name = node['name']
            argument = ast_to_latex(node['argument'])
            latex_str += f"\\{name}{{{argument}}}"
        elif node_type == 'hat':
            content = ast_to_latex(node['content'])
            latex_str += f"\\hat{{{content}}}"
        elif node_type == 'macro':
            name = node['name']
            arguments = ''.join([f"{{{ast_to_latex([arg])}}}" for arg in node['arguments']])
            latex_str += f"\\{name}{arguments}"
        elif node_type == 'environment':
            name = node['name']
            content = ast_to_latex(node['content'])
            latex_str += f"\\begin{{{name}}}{content}\\end{{{name}}}"
        else:
            # Обработка других типов узлов
            pass
    return latex_str

# Функция для тестирования
def test_conversion(latex_input):
    print(f"Тестируем LaTeX ввод: {latex_input}")
    ast = latex_to_ast(latex_input)
    if 'error' in ast:
        print(f"Ошибка при парсинге LaTeX: {ast['error']}")
        print("-" * 50)
        return
    print("AST:")
    print(ast)
    latex_output = ast_to_latex(ast)
    print(f"Преобразованный обратно LaTeX: {latex_output}")
    print("-" * 50)

if __name__ == "__main__":
    # Список тестовых случаев
    test_cases = [
        r'a + b - c',
        r'\vec{A} + \vec{B} = \vec{C}',
        r'\boldsymbol{F} = m \boldsymbol{a}',
        r'E = mc^2',
        r'\vec{F} = G \frac{m_1 m_2}{r^2} \hat{r}',
        r'\nabla \cdot \vec{E} = \frac{\rho}{\varepsilon_0}',
        r'\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \varepsilon_0 \frac{\partial \vec{E}}{\partial t}',
        r'W = \vec{F} \cdot \vec{s}',
        r'\vec{p} = m \vec{v}',
        r'\vec{L} = \vec{r} \times \vec{p}',
        r'V = IR',
        r'\varepsilon = -\frac{d\Phi}{dt}',
        r'E = \frac{1}{4\pi\varepsilon_0} \frac{q}{r^2}',
        r'\Phi = \int \vec{E} \cdot d\vec{A}',
        r'\Delta x \Delta p \geq \frac{\hbar}{2}',
        r'S = \int L \, dt',
        r'\lambda = \frac{h}{p}'
    ]

    # Выполняем тестирование
    for latex_input in test_cases:
        test_conversion(latex_input)
