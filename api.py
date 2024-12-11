# main.py
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Импортируем функции и модели из converter.py и analysis.py
from converter import ast2latex, ASTNode
from index import compare_formulas_sympy

# Импортируем функции и модели из db.py
from db import (
    create_formula,
    update_formula,
    delete_formula,
    get_all_formulas,
    get_db
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title="LaTeX AST Converter API",
    description="API для преобразования LaTeX формул в AST и обратно, управления формулами и поиска похожих формул",
    version="1.0.0"
)

# Pydantic модели

class LatexFormula(BaseModel):
    formula: str
    userid: int
    action: str  # 'create', 'update', 'delete'
    formula_id: Optional[int] = None  # Необходимо для update и delete
    legend: Optional[str] = None  # Необходимо для create и update
    description: Optional[str] = None  # Необходимо для create и update

class AnalysisResult(BaseModel):
    result: str

class FormulaResponse(BaseModel):
    id: int
    latex_formula: str
    author_id: int
    legend: Optional[str] = None
    description: Optional[str] = None
    creation_date: Optional[str] = None
    update_date: Optional[str] = None

class SimilarFormulaResponse(BaseModel):
    formula: FormulaResponse
    similarity: float

class FindSimilarRequest(BaseModel):
    formula: str

class ASTToLatexRequest(BaseModel):
    ast: List[Dict[str, Any]]  # Изменено: теперь ast является списком словарей

class LatexResponse(BaseModel):
    latex: str

class ASTResponse(BaseModel):
    ast: List[Dict[str, Any]]  # Изменено при необходимости

# Эндпоинты

@app.post("/convert_ast_to_latex", response_model=LatexResponse)
def convert_ast_to_latex_endpoint(request: ASTToLatexRequest):
    """
    Принимает AST формулу в формате JSON, преобразует её в LaTeX и возвращает.
    Ожидаемый формат:
    {
        "ast": [
            {"type": "node_type_1", "value": "value1", ...},
            {"type": "node_type_2", "value": "value2", ...},
            ...
        ]
    }
    """
    try:
        ast_nodes = request.ast  # Получаем список словарей
        latex_str = ast2latex(ast_nodes)  # Передаем список словарей в ast2latex
        return {"latex": latex_str}
    except Exception as e:
        logger.error(f"Ошибка при конвертации AST в LaTeX: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при конвертации AST в LaTeX: {e}")

@app.post("/manage_formula")
def manage_formula(latex_formula: LatexFormula, db: Session = Depends(get_db)):
    """
    Сохраняет, обновляет или удаляет LaTeX формулу в базе данных.
    """
    formula = latex_formula.formula
    userid = latex_formula.userid
    action = latex_formula.action.lower()
    formula_id = latex_formula.formula_id
    legend = latex_formula.legend
    description = latex_formula.description

    if action == "create":
        # При создании формулы formula_id игнорируется
        if not legend or not description:
            raise HTTPException(status_code=400, detail="legend и description обязательны для создания формулы.")
        try:
            new_formula = create_formula(
                db=db,
                latex_formula=formula,
                author_id=userid,
                legend=legend,
                description=description
            )
            return {"status": "success", "message": "Формула создана.", "formula_id": new_formula.id}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании формулы: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при создании формулы: {e}")

    elif action == "update":
        # Для обновления формулы formula_id обязателен
        if not formula_id:
            raise HTTPException(status_code=400, detail="formula_id обязателен для обновления.")
        try:
            update_data = {"latex_formula": formula}
            if legend is not None:
                update_data["legend"] = legend
            if description is not None:
                update_data["description"] = description
            updated_formula = update_formula(db, formula_id, **update_data)
            if not updated_formula:
                raise HTTPException(status_code=404, detail="Формула не найдена.")
            return {"status": "success", "message": f"Формула с ID {formula_id} обновлена."}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении формулы: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при обновлении формулы: {e}")

    elif action == "delete":
        # Для удаления формулы formula_id обязателен
        if not formula_id:
            raise HTTPException(status_code=400, detail="formula_id обязателен для удаления.")
        try:
            deleted = delete_formula(db, formula_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Формула не найдена.")
            return {"status": "success", "message": f"Формула с ID {formula_id} удалена."}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении формулы: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении формулы: {e}")

    else:
        raise HTTPException(status_code=400, detail="Неверное действие. Допустимые действия: create, update, delete.")


@app.get("/formulas", response_model=List[FormulaResponse])
def get_all_formulas_endpoint(db: Session = Depends(get_db)):
    """
    Получает все формулы из базы данных.
    """
    try:
        all_formulas = get_all_formulas(db)
        if not all_formulas:
            return []
        all_formulas_response = [
            FormulaResponse(
                id=formula.id,
                latex_formula=formula.latex_formula,
                author_id=formula.author_id,
                legend=formula.legend,
                description=formula.description,
                creation_date=formula.creation_date.strftime("%Y-%m-%d %H:%M:%S") if formula.creation_date else None,
                update_date=formula.update_date.strftime("%Y-%m-%d %H:%M:%S") if formula.update_date else None
            )
            for formula in all_formulas
        ]
        return all_formulas_response
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении формул: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении формул: {e}")

@app.post("/find_similar", response_model=List[SimilarFormulaResponse])
def find_similar_formulas(request: FindSimilarRequest, db: Session = Depends(get_db)):
    """
    Принимает LaTeX формулу, сравнивает её со всеми формулами в базе данных и возвращает топ-10 похожих формул.
    """
    input_formula = request.formula
    assumptions = None  # Убираем передачу предположений

    try:
        # Получаем все формулы из базы данных
        all_formulas = get_all_formulas(db)
        if not all_formulas:
            return []

        similarities = []

        for formula in all_formulas:
            try:
                # Сравниваем только поля формулы
                equivalent, similarity = compare_formulas_sympy(
                    formula1=input_formula,
                    formula2=formula.latex_formula,
                    assumptions=assumptions  # Передаём None
                )
                similarities.append({
                    "formula": FormulaResponse(
                        id=formula.id,
                        latex_formula=formula.latex_formula,
                        author_id=formula.author_id,
                        legend=formula.legend,
                        description=formula.description,
                        creation_date=formula.creation_date.strftime("%Y-%m-%d %H:%M:%S") if formula.creation_date else None,
                        update_date=formula.update_date.strftime("%Y-%m-%d %H:%M:%S") if formula.update_date else None
                    ),
                    "similarity": similarity
                })
            except Exception as e:
                # Логируем ошибку и продолжаем с другими формулами
                logger.error(f"Ошибка при сравнении формул ID {formula.id}: {e}")
                continue

        # Сортируем по убыванию сходства и выбираем топ-10
        top_similar = sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:10]

        return top_similar
    except Exception as e:
        logger.error(f"Ошибка при поиске похожих формул: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске похожих формул: {e}")

# Пример запуска приложения (если вы запускаете этот скрипт напрямую)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
