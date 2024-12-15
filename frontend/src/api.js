import axios from 'axios';

// Базовый URL теперь относительный
const apiClient = axios.create({
  baseURL: '',  // Пустая строка для относительных путей
  headers: {
    'Content-Type': 'application/json'
  }
});

export const getAllFormulas = async () => {
  const resp = await apiClient.get('/formulas');
  return resp.data;
};

export const createFormula = async (formula, userid, legend, description) => {
  const resp = await apiClient.post('/manage_formula', {
    formula,
    userid,
    action: "create",
    legend,
    description
  });
  return resp.data;
};

export const updateFormula = async (formula_id, formula, userid, legend, description) => {
  const resp = await apiClient.post('/manage_formula', {
    formula,
    userid,
    action: "update",
    formula_id,
    legend,
    description
  });
  return resp.data;
};

export const deleteFormula = async (formula_id, userid) => {
  const resp = await apiClient.post('/manage_formula', {
    formula: "",
    userid,
    action: "delete",
    formula_id
  });
  return resp.data;
};

export const findSimilar = async (formula) => {
  const resp = await apiClient.post('/find_similar', { formula });
  return resp.data;
};

export const convertAstToLatex = async (ast) => {
  const resp = await apiClient.post('/convert_ast_to_latex', { ast });
  return resp.data;
};

export const convertToDocx = async (formulas) => {
  const resp = await apiClient.post('/convert_to_docx', formulas);
  return resp.data;
};