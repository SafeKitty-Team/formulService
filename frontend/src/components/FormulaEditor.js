import React, { useState } from 'react';
import { createFormula } from '../api';
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Save, X } from "lucide-react";
import { BlockMath } from 'react-katex';
import CustomMathInput from './CustomMathInput';
import 'katex/dist/katex.min.css';

function cleanLatex(latex) {
  return latex.replace(/\\text\{([a-zA-Z0-9])\}/g, '$1');
}

function FormulaEditor({ setView }) {
  const [legend, setLegend] = useState('');
  const [description, setDescription] = useState('');
  const [userid, setUserId] = useState(1);
  const [latex, setLatex] = useState('');

  const handleChangeLatex = (value) => {
    setLatex(cleanLatex(value));
  };

  const handleSubmit = async () => {
    if(!latex.trim() || !legend.trim() || !description.trim()){
      alert("Заполните все поля!");
      return;
    }
    try {
      await createFormula(latex, userid, legend, description);
      setLegend('');
      setDescription('');
      setLatex('');
      alert('Формула успешно добавлена!');
      setView('list')
    } catch(e) {
      alert("Ошибка при добавлении формулы");
    }
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          Добавить Формулу
        </h2>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Легенда
          </label>
          <Input
            placeholder="Здесь можно написать легенду (ex. Знаменитая формула Энштейна)"
            value={legend}
            onChange={(e) => setLegend(e.target.value)}
            className="w-full bg-white dark:bg-slate-900"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Формула
          </label>
          <div className="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 p-4">
          <CustomMathInput
            setValue={handleChangeLatex}
            value={latex}
            showPreview={true}
          />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Описание
          </label>
          <Textarea
            placeholder="Введите описание"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full bg-white dark:bg-slate-900"
          />
        </div>

        {/* Блок предпросмотра */}
        {(latex || legend || description) && (
          <Card className="bg-slate-50 dark:bg-slate-800 mt-6">
            <CardHeader className="pb-3">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                Предпросмотр
              </h3>
            </CardHeader>
            <CardContent className="space-y-4">
              {legend && (
                <h4 className="text-xl font-semibold text-slate-900 dark:text-white">
                  {legend}
                </h4>
              )}
              {latex && (
                <div className="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg p-4">
                  <div className="whitespace-pre-wrap break-words">
                    <BlockMath breakLine={true}>{latex}</BlockMath>
                  </div>
                </div>
              )}
              {description && (
                <p className="text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
                  {description}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        <div className="flex justify-end space-x-4 pt-4">
          <Button
            variant="outline"
            onClick={() => setView('list')}
            className="flex items-center"
          >
            <X className="w-4 h-4 mr-2" />
            Отмена
          </Button>
          <Button
            onClick={handleSubmit}
            className="flex items-center"
          >
            <Save className="w-4 h-4 mr-2" />
            Добавить формулу
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default FormulaEditor;