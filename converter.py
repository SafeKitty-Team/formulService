from __future__ import annotations
import logging
from typing import List, Union, Optional, Dict
from pydantic import BaseModel

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASTNode(BaseModel):
    type: str
    name: Optional[str] = None
    value: Optional[Union[int, float]] = None
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None
    argument: Optional[ASTNode] = None
    elements: Optional[List[ASTNode]] = None  # Для обработки векторов и списков
    # Добавьте другие необходимые поля

    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'


def ast_to_latex(ast_node: Union[ASTNode, List[ASTNode]]) -> str:
    """
    Преобразует AST в LaTeX строку.
    :param ast_node: Корневой узел AST или список узлов
    :return: LaTeX строка
    """
    if ast_node is None:
        return ''
    if isinstance(ast_node, list):
        # Обрабатываем список узлов
        return ' '.join([ast_to_latex(node) for node in ast_node])
    if not isinstance(ast_node, ASTNode):
        logger.error(f"Получен некорректный узел: {ast_node}")
        return ''
    if ast_node.type == 'number':
        return str(ast_node.value)
    elif ast_node.type == 'variable':
        return ast_node.name
    elif ast_node.type == 'vector':
        elements = ', '.join([ast_to_latex(elem) for elem in ast_node.elements])
        return r'\begin{pmatrix}' + elements + r'\end{pmatrix}'
    elif ast_node.type == 'operator':
        left = ast_to_latex(ast_node.left)
        right = ast_to_latex(ast_node.right)
        if ast_node.name == '+':
            return f"{left} + {right}"
        elif ast_node.name == '-':
            return f"{left} - {right}"
        elif ast_node.name == '*':
            return f"{left} \\cdot {right}"
        elif ast_node.name == '/':
            return r"\frac{" + left + "}{" + right + "}"
        elif ast_node.name == '^':
            return f"{left}^{{{right}}}"
        elif ast_node.name == '=':
            return f"{left} = {right}"
        elif ast_node.name == 'dot':
            return f"{left} \\cdot {right}"
        elif ast_node.name == 'cross':
            return f"{left} \\times {right}"
        else:
            return f"{left} {ast_node.name} {right}"
    elif ast_node.type == 'function':
        arg = ast_to_latex(ast_node.argument)
        return f"\\{ast_node.name}{{{arg}}}"
    elif ast_node.type == 'expression_list':
        return ' '.join([ast_to_latex(node) for node in ast_node.elements])
    else:
        logger.warning(f"Необработанный тип узла: {ast_node.type}")
        return ''


def build_ast_from_list(nodes: List[ASTNode]) -> Union[ASTNode, List[ASTNode]]:
    """
    Строит дерево выражений из списка узлов AST.
    :param nodes: Список узлов AST
    :return: Корневой узел AST или список узлов
    """
    tokens = nodes
    position = 0

    def parse_expression(precedence=0):
        nonlocal position
        left = parse_term()
        while position < len(tokens):
            token = tokens[position]
            if token.type == 'operator' and token.name in {'+', '-', '*', '/', '^', '=', 'dot', 'cross'}:
                op = token.name
                op_precedence = get_precedence(op)
                if op_precedence < precedence:
                    break
                position += 1
                right = parse_expression(op_precedence + 1)
                left = ASTNode(type='operator', name=op, left=left, right=right)
            else:
                break
        return left

    def parse_term():
        nonlocal position
        if position >= len(tokens):
            return None
        token = tokens[position]
        if token.type in {'number', 'variable'}:
            position += 1
            return token
        elif token.type == 'vector':
            position += 1
            elements = token.elements
            if elements:
                elements = [parse_term() for _ in elements]
            token.elements = elements
            return token
        elif token.type == 'operator' and token.name == '(':
            position += 1  # Пропускаем '('
            node = parse_expression()
            if position < len(tokens) and tokens[position].type == 'operator' and tokens[position].name == ')':
                position += 1  # Пропускаем ')'
                return node
            else:
                raise ValueError("Пропущена закрывающая скобка")
        elif token.type == 'operator' and token.name in {'-', '+'}:
            op = token.name
            position += 1
            operand = parse_term()
            zero_node = ASTNode(type='number', value=0)
            return ASTNode(type='operator', name=op, left=zero_node, right=operand)
        elif token.type == 'function':
            func_token = token
            position += 1
            if position < len(tokens) and tokens[position].type == 'operator' and tokens[position].name == '(':
                position += 1  # Пропускаем '('
                arg = parse_expression()
                if position < len(tokens) and tokens[position].type == 'operator' and tokens[position].name == ')':
                    position += 1  # Пропускаем ')'
                    func_token.argument = arg
                    return func_token
                else:
                    raise ValueError("Пропущена закрывающая скобка после функции")
            else:
                raise ValueError("Пропущена открывающая скобка после функции")
        else:
            raise ValueError(f"Неожиданный токен: {token}")

    def get_precedence(op):
        precedences = {'=': 1, '+': 2, '-': 2, 'dot': 3, 'cross': 3, '*': 4, '/': 4, '^': 5}
        return precedences.get(op, 0)

    ast_nodes = []
    while position < len(tokens):
        node = parse_expression()
        if node is not None:
            ast_nodes.append(node)
        else:
            position += 1  # Пропускаем неопознанные токены

    if len(ast_nodes) == 1:
        return ast_nodes[0]
    else:
        # Если несколько корневых узлов, возвращаем список
        return ASTNode(type='expression_list', elements=ast_nodes)


def ast2latex(ast_input: List[Dict]):
    """
    Тестирует конвертацию AST в LaTeX.
    :param ast_input: Список узлов AST в формате словаря
    """
    try:
        # Преобразуем словари в ASTNode
        ast_nodes = [ASTNode(**node_dict) for node_dict in ast_input]
        # Строим дерево AST из списка узлов
        ast_tree = build_ast_from_list(ast_nodes)
        if ast_tree is None:
            raise ValueError("AST дерево пустое")
        # Преобразуем AST в LaTeX
        latex_output = ast_to_latex(ast_tree)
        return latex_output
    except Exception as e:
        logger.error(f"Ошибка при конвертации AST в LaTeX: {e}")
        print(f"Ошибка при конвертации AST в LaTeX: {e}")


if __name__ == "__main__":
    # Пример AST для квадратного уравнения
    ast_input = [
        {"type": "variable", "name": "x"},
        {"type": "operator", "name": "="},
        {"type": "operator", "name": "("},
        {"type": "operator", "name": "-"},
        {"type": "variable", "name": "b"},
        {"type": "operator", "name": "+"},
        {"type": "function", "name": "sqrt"},
        {"type": "operator", "name": "("},
        {"type": "variable", "name": "b"},
        {"type": "operator", "name": "^"},
        {"type": "number", "value": 2},
        {"type": "operator", "name": "-"},
        {"type": "number", "value": 4},
        {"type": "operator", "name": "*"},
        {"type": "variable", "name": "a"},
        {"type": "operator", "name": "*"},
        {"type": "variable", "name": "c"},
        {"type": "operator", "name": ")"},
        {"type": "operator", "name": ")"},
        {"type": "operator", "name": "/"},
        {"type": "number", "value": 2},
        {"type": "operator", "name": "*"},
        {"type": "variable", "name": "a"},
    ]
    print(ast2latex(ast_input))