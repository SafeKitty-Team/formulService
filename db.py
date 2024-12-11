# db.py

from sqlalchemy import create_engine, Column, Integer, Text, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, sessionmaker, validates, Session
from sqlalchemy.exc import SQLAlchemyError
import os

# Настройки подключения к базе данных
DB_USERNAME = 'admin'
DB_PASSWORD = 'pinpinpin'  # Рекомендуется использовать переменные окружения для хранения пароля
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'formula_db'

DATABASE_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Создание движка и сессии
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Formula(Base):
    __tablename__ = 'formulas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    latex_formula = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)
    legend = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    creation_date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_date = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Геттеры
    def get_id(self):
        return self.id

    def get_latex_formula(self):
        return self.latex_formula

    def get_author_id(self):
        return self.author_id

    def get_legend(self):
        return self.legend

    def get_description(self):
        return self.description

    def get_creation_date(self):
        return self.creation_date

    def get_update_date(self):
        return self.update_date

    # Сеттеры
    def set_latex_formula(self, latex_formula):
        self.latex_formula = latex_formula

    def set_author_id(self, author_id):
        self.author_id = author_id

    def set_legend(self, legend):
        self.legend = legend

    def set_description(self, description):
        self.description = description

    # Валидация данных (опционально)
    @validates('author_id')
    def validate_author_id(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("author_id должен быть положительным целым числом.")
        return value

# Создание таблицы (если она не существует)
Base.metadata.create_all(engine)

def get_db():
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_formula(db: Session, latex_formula, author_id, legend=None, description=None):
    """Создает новую запись формулы в базе данных."""
    try:
        new_formula = Formula(
            latex_formula=latex_formula,
            author_id=author_id,
            legend=legend,
            description=description
        )
        db.add(new_formula)
        db.commit()
        db.refresh(new_formula)
        print(f"Формула с ID {new_formula.id} создана.")
        return new_formula
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Ошибка при создании формулы: {e}")
        raise

def update_formula(db: Session, formula_id, **kwargs):
    """
    Обновляет поля формулы по заданному ID.
    Пример использования: update_formula(db, 1, latex_formula="a^2 + b^2 = c^2")
    """
    try:
        formula = db.query(Formula).filter_by(id=formula_id).first()
        if not formula:
            print(f"Формула с ID {formula_id} не найдена.")
            return None

        for key, value in kwargs.items():
            if hasattr(formula, key) and value is not None:
                setattr(formula, key, value)
            else:
                print(f"Поле '{key}' не существует в модели Formula или значение None.")
        db.commit()
        db.refresh(formula)
        print(f"Формула с ID {formula_id} обновлена.")
        return formula
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Ошибка при обновлении формулы: {e}")
        raise

def delete_formula(db: Session, formula_id):
    """Удаляет запись формулы по ID."""
    try:
        formula = db.query(Formula).filter_by(id=formula_id).first()
        if formula:
            db.delete(formula)
            db.commit()
            print(f"Формула с ID {formula_id} удалена.")
            return True
        else:
            print(f"Формула с ID {formula_id} не найдена.")
            return False
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Ошибка при удалении формулы: {e}")
        raise

def get_all_formulas(db: Session):
    """
    Возвращает все формулы в виде списка объектов Formula.
    """
    try:
        formulas = db.query(Formula).all()
        return formulas
    except SQLAlchemyError as e:
        print(f"Ошибка при получении формул: {e}")
        return []
