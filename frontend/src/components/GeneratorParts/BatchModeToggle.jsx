import React from 'react';

function BatchModeToggle({ isBatchMode, setIsBatchMode }) {
  return (
    <div className="batch-mode">
      <label className="checkbox-container">
        <input 
          type="checkbox" 
          checked={isBatchMode} 
          onChange={(e) => setIsBatchMode(e.target.checked)} 
        />
        <span className="checkmark"></span>
        Batch Generation Mode (Multi-Value)
      </label>
    </div>
  );
}

export default BatchModeToggle;
