import React from 'react';

function UploadZone({ onFileUpload, loading }) {
  return (
    <div className="upload-zone">
      <input
        type="file"
        accept=".dxf"
        onChange={onFileUpload}
        style={{ display: 'none' }}
        id="dxf-upload-input"
      />
      <button 
        className="upload-btn"
        onClick={() => document.getElementById('dxf-upload-input').click()}
        disabled={loading}
      >
        <span className="upload-icon">↑</span> Upload DXF to Edit
      </button>
      <p className="upload-hint">Upload an existing DXF to auto-fill these values</p>
    </div>
  );
}

export default UploadZone;
