import React, { useState } from 'react';
import Navbar from './components/Navbar';
import FormulaList from './components/FormulaList';
import FormulaEditor from './components/FormulaEditor';
import SimilarFormulas from './components/SimilarFormulas';
import FormulaExport from './components/FormulaExport';

function App() {
  const [view, setView] = useState('list'); // 'list', 'add', 'similar', 'export'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <Navbar setView={setView} currentView={view} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {view === 'list' && <FormulaList setView={setView} />}
        {view === 'add' && <FormulaEditor setView={setView} />}
        {view === 'similar' && <SimilarFormulas />}
        {view === 'export' && <FormulaExport />}
      </main>
    </div>
  );
}

export default App;