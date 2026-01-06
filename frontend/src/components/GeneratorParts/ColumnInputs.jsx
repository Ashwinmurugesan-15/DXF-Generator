function ColumnInputs({ data, onChange, isBatch, onRemove, index }) {
  if (isBatch) {
    return (
      <div className="grid-row column-grid">
        <input type="number" placeholder="W" value={data.width} onChange={(e) => onChange(index, 'width', e.target.value)} />
        <input type="number" placeholder="H" value={data.height} onChange={(e) => onChange(index, 'height', e.target.value)} />
        <button type="button" className="remove-btn" onClick={() => onRemove(index)}>🗑️</button>
      </div>
    );
  }

  return (
    <>
      <div className="input-field">
        <label>Width (W)</label>
        <input type="number" placeholder="W" value={data.width} onChange={(e) => onChange(0, 'width', e.target.value)} />
      </div>
      <div className="input-field">
        <label>Height (H)</label>
        <input type="number" placeholder="H" value={data.height} onChange={(e) => onChange(0, 'height', e.target.value)} />
      </div>
    </>
  );
}

export default ColumnInputs;
