import React from 'react';
import MathInput from 'react-math-keyboard';
import { BlockMath } from 'react-katex';
import '../styles/math-keyboard.css';

function CustomMathInput({ 
  value, 
  setValue, 
  defaultValue, 
  initialLatex,
  showPreview = true 
}) {
  return (
    <div className="w-full space-y-4">
      <div className="relative bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 p-4">
        <MathInput
          setValue={setValue}
          value={value}
          defaultValue={defaultValue}
          initialLatex={initialLatex}
          divisionFormat="obelus"
          style={{
            width: '100%',
            minHeight: '45px',
            padding: '8px',
            backgroundColor: 'transparent'
          }}
        />
      </div>
      {showPreview && value && (
        <div className="formula-preview">
          <span className="block text-sm font-medium text-slate-500 dark:text-slate-400 mb-2">
            Предпросмотр:
          </span>
          <div className="overflow-x-auto whitespace-pre-wrap break-words">
            <BlockMath breakLine={true}>{value}</BlockMath>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomMathInput;