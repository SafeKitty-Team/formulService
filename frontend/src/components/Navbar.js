import React from 'react';
import { Button } from "../components/ui/button";
import { List, Plus, Search, FileDown } from "lucide-react";

function Navbar({ setView, currentView }) {
  return (
    <nav className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
              Formula Manager
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button 
              variant={currentView === 'list' ? "default" : "ghost"}
              onClick={() => setView('list')}
              className="flex items-center"
            >
              <List className="w-4 h-4 mr-2" />
              Формулы
            </Button>
            <Button
              variant={currentView === 'add' ? "default" : "ghost"}
              onClick={() => setView('add')}
              className="flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Добавить
            </Button>
            <Button
              variant={currentView === 'similar' ? "default" : "ghost"}
              onClick={() => setView('similar')}
              className="flex items-center"
            >
              <Search className="w-4 h-4 mr-2" />
              Поиск формул или похожих
            </Button>
            <Button
              variant={currentView === 'export' ? "default" : "ghost"}
              onClick={() => setView('export')}
              className="flex items-center"
            >
              <FileDown className="w-4 h-4 mr-2" />
              Экспорт в docx
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;