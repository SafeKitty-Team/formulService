# main.py
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import FileResponse
import logging
import sympy
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from jscon2pdf import json_to_docx
import os

os.makedirs("output_docs", exist_ok=True)

# Импортируем функции и модели
from converter import ast2latex
from index import compare_formulas_sympy  # Предполагается, что compare_formulas_sympy возвращает расширенные данные
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

app = FastAPI(
    title="LaTeX AST Converter API",
    description="API для преобразования LaTeX формул в AST и обратно, управления формулами и поиска похожих формул",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LatexFormula(BaseModel):
    formula: str
    userid: int
    action: str  # 'create', 'update', 'delete'
    formula_id: Optional[int] = None  # Необходимо для update и delete
    legend: Optional[str] = None      # Необходимо для create и update
    description: Optional[str] = None # Необходимо для create и update

class FormulaData(BaseModel):
    id: int
    latex_formula: str
    author_id: int
    legend: Optional[str]
    description: Optional[str]
    creation_date: Optional[str]
    update_date: Optional[str]


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


class FindSimilarRequest(BaseModel):
    formula: str


class ASTToLatexRequest(BaseModel):
    ast: List[Dict[str, Any]]


class LatexResponse(BaseModel):
    latex: str


class ASTResponse(BaseModel):
    ast: List[Dict[str, Any]]


class CommonSubexpressionInfo(BaseModel):
    subexpression: str
    indices_in_expr2: List[int]
    occurrences_in_simplified2: List[Tuple[int, int]]


class DetailedSimilarityInfo(BaseModel):
    formula: FormulaResponse
    equivalent: bool
    similarity: float
    simplified1: str
    simplified2: str
    common_subexpressions: List[CommonSubexpressionInfo]



@app.post("/convert_ast_to_latex", response_model=LatexResponse)
def convert_ast_to_latex_endpoint(request: ASTToLatexRequest):
    try:
        ast_nodes = request.ast
        latex_str = ast2latex(ast_nodes)
        return {"latex": latex_str}
    except Exception as e:
        logger.error(f"Ошибка при конвертации AST в LaTeX: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при конвертации AST в LaTeX: {e}")

OUTPUT_DIRECTORY = "output_docs"

app.mount("/output_docs", StaticFiles(directory=OUTPUT_DIRECTORY), name="output_docs")


@app.post("/convert_to_docx")
def convert_to_docx_endpoint(data: List[FormulaData]):
    """
    Конвертирует JSON в DOCX и возвращает ссылку на файл.
    """
    try:
        # Преобразование Pydantic-моделей в список словарей
        data_dict = [item.dict() for item in data]
        
        # Вызов функции для создания DOCX
        file_path = json_to_docx(data_dict, OUTPUT_DIRECTORY)
        
        # Формирование ссылки для скачивания
        file_name = os.path.basename(file_path)
        file_url = f"http://localhost:8000/output_docs/{file_name}"
        logger.info(f"Файл успешно создан: {file_url}")
        return {"status": "success", "file_url": file_url}
    except Exception as e:
        logger.error(f"Ошибка при создании DOCX: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/manage_formula")
def manage_formula(latex_formula: LatexFormula, db: Session = Depends(get_db)):
    formula = latex_formula.formula
    userid = latex_formula.userid
    action = latex_formula.action.lower()
    formula_id = latex_formula.formula_id
    legend = latex_formula.legend
    description = latex_formula.description

    if action == "create":
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
            print(new_formula)
            return {"status": "success", "message": "Формула создана.", "formula_id": new_formula.id}
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при создании формулы: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка при создании формулы: {e}")

    elif action == "update":
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
    try:
        all_formulas = get_all_formulas(db)
        if not all_formulas:
            return []
        return [
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
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении формул: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении формул: {e}")


@app.post("/find_similar", response_model=List[DetailedSimilarityInfo])
def find_similar_formulas(request: FindSimilarRequest, db: Session = Depends(get_db)):
    input_formula = request.formula
    print(input_formula)
    assumptions = None

    try:
        all_formulas = get_all_formulas(db)
        if not all_formulas:
            return []

        results = []
        for formula in all_formulas:
            try:
                (equivalent,
                 similarity,
                 common_subexpressions,
                 common_indices_in_expr2,
                 substring_occurrences_in_simplified2,
                 simplified1,
                 simplified2) = compare_formulas_sympy(
                    formula1=input_formula,
                    formula2=formula.latex_formula,
                    assumptions=assumptions
                )

                # Формируем список CommonSubexpressionInfo
                common_info_list = []
                for subexpr in common_subexpressions:
                    common_info_list.append(CommonSubexpressionInfo(
                        subexpression=subexpr,
                        indices_in_expr2=common_indices_in_expr2[subexpr],
                        occurrences_in_simplified2=substring_occurrences_in_simplified2[subexpr]
                    ))

                results.append(
                    DetailedSimilarityInfo(
                        formula=FormulaResponse(
                            id=formula.id,
                            latex_formula=formula.latex_formula,
                            author_id=formula.author_id,
                            legend=formula.legend,
                            description=formula.description,
                            creation_date=formula.creation_date.strftime("%Y-%m-%d %H:%M:%S") if formula.creation_date else None,
                            update_date=formula.update_date.strftime("%Y-%m-%d %H:%M:%S") if formula.update_date else None
                        ),
                        equivalent=equivalent,
                        similarity=similarity,
                        simplified1=sympy.latex(simplified1),
                        simplified2=sympy.latex(simplified2),
                        common_subexpressions=common_info_list
                    )
                )
            except Exception as e:
                logger.error(f"Ошибка при сравнении формул ID {formula.id}: {e}")
                continue

        # Сортируем по сходству
        results = sorted(results, key=lambda x: x.similarity, reverse=True)[:10]
        return results

    except Exception as e:
        logger.error(f"Ошибка при поиске похожих формул: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске похожих формул: {e}")

# Используется в релиз версии

# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# @app.get("/{full_path:path}")
# async def serve_react(full_path: str):
#     # Для API эндпоинтов
#     if full_path.startswith("api/"):
#         return {"message": "This is API endpoint"}
#     return FileResponse('index.html')
