function BeamInputs({ data, onChange, isBatch, onRemove, index }) {
  if (isBatch) {
    return (
      <div className="grid-row">
        <input type="number" placeholder="H" value={data.total_depth} onChange={(e) => onChange(index, 'total_depth', e.target.value)} />
        <input type="number" placeholder="B" value={data.flange_width} onChange={(e) => onChange(index, 'flange_width', e.target.value)} />
        <input type="number" placeholder="tw" value={data.web_thickness} onChange={(e) => onChange(index, 'web_thickness', e.target.value)} />
        <input type="number" placeholder="tf" value={data.flange_thickness} onChange={(e) => onChange(index, 'flange_thickness', e.target.value)} />
        <button type="button" className="remove-btn" onClick={() => onRemove(index)}>🗑️</button>
      </div>
    );
  }

  return (
    <>
      <div className="input-field">
        <label>Total Depth (H)</label>
        <input type="number" placeholder="H" value={data.total_depth} onChange={(e) => onChange(0, 'total_depth', e.target.value)} />
      </div>
      <div className="input-field">
        <label>Flange Width (B)</label>
        <input type="number" placeholder="B" value={data.flange_width} onChange={(e) => onChange(0, 'flange_width', e.target.value)} />
      </div>
      <div className="input-field">
        <label>Web Thickness (tw)</label>
        <input type="number" placeholder="tw" value={data.web_thickness} onChange={(e) => onChange(0, 'web_thickness', e.target.value)} />
      </div>
      <div className="input-field">
        <label>Flange Thickness (tf)</label>
        <input type="number" placeholder="tf" value={data.flange_thickness} onChange={(e) => onChange(0, 'flange_thickness', e.target.value)} />
      </div>
    </>
  );
}

export default BeamInputs;
