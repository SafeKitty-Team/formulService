import React, { useState, useEffect } from 'react';
import { getAllFormulas, convertToDocx } from '../api';
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Search, FileDown } from "lucide-react";
import { BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

export default function FormulaExport() {
  const [formulas, setFormulas] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFormulas, setSelectedFormulas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadFormulas();
  }, []);

  const loadFormulas = async () => {
    const data = await getAllFormulas();
    setFormulas(data);
  };

  const handleSelect = (formula) => {
    setSelectedFormulas(prev => {
      if (prev.find(f => f.id === formula.id)) {
        return prev.filter(f => f.id !== formula.id);
      } else {
        return [...prev, formula];
      }
    });
  };

  const handleExport = async () => {
    try {
      setIsLoading(true);
      const response = await convertToDocx(selectedFormulas);
      if (response.status === 'success' && response.file_url) {
        const link = document.createElement('a');
        link.href = response.file_url;
        link.download = 'formulas.docx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      alert('Ошибка при экспорте формул');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredFormulas = formulas.filter(formula => {
    const searchLower = searchQuery.toLowerCase();
    return (
      formula.legend?.toLowerCase().includes(searchLower) ||
      formula.description?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="space-y-6">
      <div className="w-full flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Экспорт формул в DOCX
          </h2>
          <div className="flex items-center gap-4">
            <p className="text-slate-600 dark:text-slate-300">
              Выберите формулы для конвертации в DOCX формат
            </p>
            <span className="inline-flex items-center justify-center px-3 py-1 text-sm font-medium rounded-md bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-700/10 dark:bg-blue-900/20 dark:text-blue-400">
              Выбрано: {selectedFormulas.length}
            </span>
          </div>
        </div>
        <Button
          onClick={handleExport}
          disabled={selectedFormulas.length === 0 || isLoading}
          className="h-10"
        >
          <FileDown className="w-4 h-4 mr-2" />
          {isLoading ? 'Генерация...' : 'Сгенерировать'}
        </Button>
      </div>

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

      <div className="grid gap-4">
        {filteredFormulas.length === 0 ? (
          <p className="text-slate-600 dark:text-slate-300 text-center py-4">
            {searchQuery ? "Формулы не найдены" : "Нет формул"}
          </p>
        ) : (
          filteredFormulas.map((formula) => (
            <Card 
              key={formula.id}
              className={`cursor-pointer transition-all ${
                selectedFormulas.find(f => f.id === formula.id)
                  ? 'ring-2 ring-blue-500'
                  : 'hover:shadow-md'
              }`}
              onClick={() => handleSelect(formula)}
            >
              <CardContent className="p-6">
                {formula.legend && (
                  <h3 className="text-xl font-semibold mb-4 text-slate-900 dark:text-white">
                    {formula.legend}
                  </h3>
                )}
                <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 mb-4">
                  <BlockMath>{formula.latex_formula}</BlockMath>
                </div>
                {formula.description && (
                  <p className="text-slate-600 dark:text-slate-300">
                    {formula.description}
                  </p>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}