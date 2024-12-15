import React, { useEffect, useState } from 'react';
import { getAllFormulas, updateFormula, deleteFormula } from '../api';
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Edit2, Trash2, Save, X, Search } from "lucide-react";
import { BlockMath } from 'react-katex';
import CustomMathInput from './CustomMathInput';
import 'katex/dist/katex.min.css';
import '../styles/mathinput.css';

function cleanLatex(latex) {
  if (!latex) return '';
  return latex.replace(/\\text\{([a-zA-Z0-9])\}/g, '$1');
}

function FormulaList() {
  const [formulas, setFormulas] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editedLatex, setEditedLatex] = useState('');
  const [editedLegend, setEditedLegend] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [userid] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentFormula, setCurrentFormula] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadFormulas = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getAllFormulas();
      
      if (Array.isArray(data)) {
        const validData = data.filter(item => 
          item && 
          typeof item === 'object' && 
          'id' in item && 
          'latex_formula' in item
        );
        setFormulas(validData);
      } else {
        console.error('Received invalid data format:', data);
        setFormulas([]);
      }
    } catch (err) {
      console.error('Error loading formulas:', err);
      setError('Ошибка загрузки формул');
      setFormulas([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFormulas();
  }, []);

  const handleEdit = (f) => {
    if (!f || typeof f !== 'object') return;
    
    setEditingId(f.id);
    setEditedLatex(f.latex_formula || '');
    setEditedLegend(f.legend || '');
    setEditedDescription(f.description || '');
    setCurrentFormula(f);
  };

  const handleChangeLatex = (value) => {
    setEditedLatex(cleanLatex(value || ''));
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditedLatex('');
    setEditedLegend('');
    setEditedDescription('');
    setCurrentFormula(null);
  };

  const handleSave = async (id) => {
    if (!id) return;
    
    if (!editedLatex.trim() || !editedLegend.trim() || !editedDescription.trim()) {
      alert("Заполните все поля!");
      return;
    }

    try {
      await updateFormula(id, editedLatex, userid, editedLegend, editedDescription);
      handleCancelEdit();
      await loadFormulas();
    } catch (err) {
      console.error('Error saving formula:', err);
      alert("Ошибка при сохранении формулы");
    }
  };

  const handleDelete = async (id) => {
    if (!id) return;
    
    if (!window.confirm("Вы уверены, что хотите удалить формулу?")) return;
    
    try {
      await deleteFormula(id, userid);
      await loadFormulas();
    } catch (err) {
      console.error('Error deleting formula:', err);
      alert("Ошибка при удалении формулы");
    }
  };

  const filteredFormulas = formulas.filter(formula => {
    if (!formula) return false;
    
    const searchLower = (searchQuery || '').toLowerCase();
    const legend = (formula.legend || '').toLowerCase();
    const description = (formula.description || '').toLowerCase();
    
    return legend.includes(searchLower) || description.includes(searchLower);
  });

  if (isLoading) {
    return <div className="text-center py-4">Загрузка...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          Список Формул
        </h2>
      </header>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-slate-400" />
        </div>
        <Input
          type="text"
          placeholder="Поиск по легенде или описанию..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid gap-6">
        {filteredFormulas.length === 0 ? (
          <p className="text-slate-600 dark:text-slate-300 text-center py-4">
            {searchQuery ? "Формулы не найдены" : "Нет формул"}
          </p>
        ) : (
          filteredFormulas.map((f) => (
            <Card key={f.id} className="transition-shadow hover:shadow-lg">
              <CardContent className="p-6">
                {editingId === f.id ? (
                  <div className="space-y-4">
                    <Input
                      placeholder="Легенда"
                      value={editedLegend}
                      onChange={(e) => setEditedLegend(e.target.value)}
                      className="w-full"
                    />
                    <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 p-4">
                      <CustomMathInput
                        setValue={handleChangeLatex}
                        value={editedLatex}
                        defaultValue={currentFormula?.latex_formula}
                        initialLatex={currentFormula?.latex_formula}
                      />
                      {editedLatex && (
                        <div className="mt-4">
                          <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                            Предпросмотр:
                          </h4>
                          <div className="overflow-x-auto whitespace-pre-wrap break-words">
                            <BlockMath breakLine={true}>{editedLatex}</BlockMath>
                          </div>
                        </div>
                      )}
                    </div>
                    <Textarea
                      placeholder="Описание"
                      value={editedDescription}
                      onChange={(e) => setEditedDescription(e.target.value)}
                      rows={4}
                      className="w-full"
                    />
                    <div className="flex justify-end space-x-2">
                      <Button
                        variant="outline"
                        onClick={handleCancelEdit}
                        className="flex items-center"
                      >
                        <X className="w-4 h-4 mr-2" />
                        Отмена
                      </Button>
                      <Button
                        onClick={() => handleSave(f.id)}
                        className="flex items-center"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Сохранить
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    {f.legend && (
                      <h3 className="text-xl font-semibold mb-4 text-slate-900 dark:text-white">
                        {f.legend}
                      </h3>
                    )}
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 mb-4">
                      <div className="overflow-x-auto whitespace-pre-wrap break-words">
                        <BlockMath breakLine={true}>{f.latex_formula}</BlockMath>
                      </div>
                    </div>
                    {f.description && (
                      <div className="text-slate-600 dark:text-slate-300 mb-4 whitespace-pre-line">
                        {f.description}
                      </div>
                    )}
                    <div className="flex justify-end space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(f)}
                        className="flex items-center"
                      >
                        <Edit2 className="w-4 h-4 mr-2" />
                        Изменить
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(f.id)}
                        className="flex items-center"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Удалить
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

export default FormulaList;