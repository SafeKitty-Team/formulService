import React, { useEffect, useState } from 'react';
import { getAllFormulas, findSimilar } from '../api';
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ScrollArea } from "../components/ui/scroll-area";
import { List, Plus, Search } from "lucide-react";
import { BlockMath } from 'react-katex';
import MathInput from 'react-math-keyboard';
import 'katex/dist/katex.min.css';
import '../styles/mathinput.css';

function cleanLatex(latex) {
  return latex.replace(/\\text\{([a-zA-Z0-9])\}/g, '$1');
}

function SimilarFormulas() {
  const [formulas, setFormulas] = useState([]);
  const [compareMode, setCompareMode] = useState('existing');
  const [selectedFormulaId, setSelectedFormulaId] = useState(null);
  const [newLatex, setNewLatex] = useState('');
  const [results, setResults] = useState([]);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [searchFormula, setSearchFormula] = useState('');

  const loadFormulas = async () => {
    const data = await getAllFormulas();
    setFormulas(data);
  };

  useEffect(() => {
    loadFormulas();
  }, []);

  const handleChangeNewLatex = (value) => {
    setNewLatex(cleanLatex(value));
  };

  const handleSearch = async () => {
    let formulaToSend = '';
    if (compareMode === 'existing') {
      const f = formulas.find(f => f.id === Number(selectedFormulaId));
      if(!f) {
        alert('Выберите формулу!');
        return;
      }
      formulaToSend = f.latex_formula;
    } else {
      if(!newLatex.trim()) {
        alert('Введите формулу!');
        return;
      }
      formulaToSend = newLatex;
    }
    
    try {
      const data = await findSimilar(formulaToSend);
      setResults(data);
      setSearchFormula(formulaToSend);
      setSearchPerformed(true);
    } catch (e) {
      alert("Ошибка при поиске похожих формул");
    }
  };

  return (
    <div className="space-y-6">
      {!searchPerformed ? (
        <>
          <header>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              Найти похожие формулы
            </h2>
          </header>

          <Tabs 
            defaultValue="existing" 
            className="w-full"
            onValueChange={(value) => {
              setCompareMode(value);
              setSelectedFormulaId(null);
              setNewLatex('');
            }}
          >
            <TabsList className="mb-6">
              <TabsTrigger value="existing" className="flex items-center">
                <List className="w-4 h-4 mr-2" />
                Из существующих
              </TabsTrigger>
              <TabsTrigger value="new" className="flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Другая формула
              </TabsTrigger>
            </TabsList>

            <TabsContent value="existing">
              <ScrollArea className="h-[400px] rounded-md border border-slate-200 dark:border-slate-700 p-4">
                {formulas.length === 0 ? (
                  <p className="text-slate-600 dark:text-slate-300 p-4">Нет формул</p>
                ) : (
                  formulas.map(f => (
                    <Card
                      key={f.id}
                      className={`mb-4 cursor-pointer transition-all ${
                        selectedFormulaId === f.id
                          ? 'ring-2 ring-blue-500'
                          : 'hover:shadow-md'
                      }`}
                      onClick={() => setSelectedFormulaId(f.id)}
                    >
                      <CardContent className="p-4">
                        {f.legend && (
                          <h3 className="text-lg font-semibold mb-2 text-slate-900 dark:text-white">
                            {f.legend}
                          </h3>
                        )}
                        <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                          <BlockMath>{f.latex_formula}</BlockMath>
                        </div>
                        {selectedFormulaId === f.id && (
                          <p className="text-sm text-green-500 mt-2">Выбрано</p>
                        )}
                      </CardContent>
                    </Card>
                  ))
                )}
              </ScrollArea>
            </TabsContent>

            <TabsContent value="new">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
                      Введите Формулу:
                    </label>
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                      <MathInput
                        setValue={handleChangeNewLatex}
                        value={newLatex}
                        divisionFormat="obelus"
                      />
                    </div>
                    {newLatex && (
                      <div className="mt-4">
                        <h3 className="text-lg font-semibold mb-2">Предпросмотр</h3>
                        <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                          <BlockMath>{newLatex}</BlockMath>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end">
            <Button
              onClick={handleSearch}
              className="flex items-center"
            >
              <Search className="w-4 h-4 mr-2" />
              Найти
            </Button>
          </div>
        </>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Результаты поиска
            </h2>
            <Button
              onClick={() => {
                setSearchPerformed(false);
                setResults([]);
              }}
              className="flex items-center"
            >
              <Search className="w-4 h-4 mr-2" />
              Новый поиск
            </Button>
          </div>

          <div className="flex items-center space-x-2">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
              Найденные формулы
            </h3>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              ({results.length})
            </span>
          </div>

          <div className="space-y-6">
            {results.map((result, idx) => (
              <Card 
                key={idx} 
                className="overflow-hidden bg-white dark:bg-slate-900 shadow-lg hover:shadow-xl transition-shadow duration-200"
              >
                <CardContent className="p-6">
                  <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                    {result.formula.legend}
                  </h3>

                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                        Исходная формула
                      </h4>
                      <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4 border-2 border-blue-500">
                        <BlockMath>{searchFormula}</BlockMath>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                        Найденная формула
                      </h4>
                      <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                        <BlockMath>{result.formula.latex_formula}</BlockMath>
                      </div>
                    </div>
                  </div>

                  {result.formula.description && (
                    <p className="text-slate-600 dark:text-slate-300 mb-6">
                      {result.formula.description}
                    </p>
                  )}

                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
                        Эквивалентность
                      </h4>
                      <p className={`text-lg font-semibold ${
                        result.equivalent 
                          ? 'text-green-600 dark:text-green-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {result.equivalent ? 'Да' : 'Нет'}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
                        Сходство
                      </h4>
                      <p className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                        {result.similarity}%
                      </p>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                        Упрощенная форма 1
                      </h4>
                      <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                        <BlockMath>{result.simplified1}</BlockMath>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
                        Упрощенная форма 2
                      </h4>
                      <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                        <BlockMath>{result.simplified2}</BlockMath>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimilarFormulas;