import React, { useState } from 'react';
import axios from 'axios';

function Generator({ onLogout }) {
  const [activeTab, setActiveTab] = useState('beam'); // 'beam' or 'column'
  const [isBatchMode, setIsBatchMode] = useState(false);
  
  // Separate states for Single Mode
  const [beamSingle, setBeamSingle] = useState({ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' });
  const [columnSingle, setColumnSingle] = useState({ width: '', height: '' });
  
  // Separate states for Batch Mode
  const [beamBatch, setBeamBatch] = useState([
    { total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' }
  ]);
  const [columnBatch, setColumnBatch] = useState([
    { width: '', height: '' }
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleAddItem = () => {
    if (activeTab === 'beam') {
      if (beamBatch.length >= 5) return;
      setBeamBatch([...beamBatch, { total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' }]);
    } else {
      if (columnBatch.length >= 5) return;
      setColumnBatch([...columnBatch, { width: '', height: '' }]);
    }
  };

  const handleRemoveItem = (index) => {
    if (activeTab === 'beam') {
      const newItems = beamBatch.filter((_, i) => i !== index);
      setBeamBatch(newItems.length > 0 ? newItems : [{ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' }]);
    } else {
      const newItems = columnBatch.filter((_, i) => i !== index);
      setColumnBatch(newItems.length > 0 ? newItems : [{ width: '', height: '' }]);
    }
  };

  const handleInputChange = (index, field, value) => {
    if (isBatchMode) {
      if (activeTab === 'beam') {
        const newItems = [...beamBatch];
        newItems[index][field] = value;
        setBeamBatch(newItems);
      } else {
        const newItems = [...columnBatch];
        newItems[index][field] = value;
        setColumnBatch(newItems);
      }
    } else {
      if (activeTab === 'beam') {
        setBeamSingle({ ...beamSingle, [field]: value });
      } else {
        setColumnSingle({ ...columnSingle, [field]: value });
      }
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/parse/dxf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { type, data } = response.data;
      
      if (type === 'ibeam') {
        setActiveTab('beam');
        setBeamSingle({
          total_depth: data.total_depth.toString(),
          flange_width: data.flange_width.toString(),
          web_thickness: data.web_thickness.toString(),
          flange_thickness: data.flange_thickness.toString()
        });
        setSuccess(`Successfully parsed Beam dimensions from ${file.name}`);
      } else if (type === 'column') {
        setActiveTab('column');
        setColumnSingle({
          width: data.width.toString(),
          height: data.height.toString()
        });
        setSuccess(`Successfully parsed Column dimensions from ${file.name}`);
      }
      
      setIsBatchMode(false);
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const message = err.response?.data?.detail || err.message;
      setError(`Failed to parse DXF: ${message}`);
      setTimeout(() => setError(null), 10000);
    } finally {
      setLoading(false);
      // Reset input value to allow uploading the same file again
      e.target.value = '';
    }
  };

  const handleGenerateDXF = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Basic Validation
    if (isBatchMode) {
      const currentItems = activeTab === 'beam' ? beamBatch : columnBatch;
      for (let i = 0; i < currentItems.length; i++) {
        const item = currentItems[i];
        for (const [key, value] of Object.entries(item)) {
          if (!value || value <= 0) {
            setError(`Please enter a valid positive number for all fields in Row ${i + 1}`);
            setLoading(false);
            setTimeout(() => setError(null), 10000);
            return;
          }
        }
      }
    } else {
      const currentItem = activeTab === 'beam' ? beamSingle : columnSingle;
      for (const [key, value] of Object.entries(currentItem)) {
        if (!value || value <= 0) {
          setError(`Please enter a valid positive number for ${key.replace('_', ' ')}`);
          setLoading(false);
          setTimeout(() => setError(null), 10000);
          return;
        }
      }
    }

    try {
      if (isBatchMode) {
        const items = activeTab === 'beam' 
          ? beamBatch.map(item => ({
              total_depth: parseFloat(item.total_depth),
              flange_width: parseFloat(item.flange_width),
              web_thickness: parseFloat(item.web_thickness),
              flange_thickness: parseFloat(item.flange_thickness)
            }))
          : columnBatch.map(item => ({
              width: parseFloat(item.width),
              height: parseFloat(item.height)
            }));

        const endpoint = activeTab === 'beam' ? '/generate/ibeam/batch' : '/generate/column/batch';
        const response = await axios.post(`http://localhost:8000${endpoint}`, { items }, {
          responseType: 'blob',
        });

        const blob = new Blob([response.data], { type: 'application/zip' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${activeTab}s_batch.zip`);
        document.body.appendChild(link);
        link.click();
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);

        setSuccess("DXF generated successfully");
        setTimeout(() => setSuccess(null), 5000);

        // Reset inputs
        if (activeTab === 'beam') {
          setBeamSingle({ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' });
          setBeamBatch([{ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' }]);
        } else {
          setColumnSingle({ width: '', height: '' });
          setColumnBatch([{ width: '', height: '' }]);
        }

      } else {
        const item = activeTab === 'beam' ? beamSingle : columnSingle;
        const endpoint = activeTab === 'beam' ? '/generate/ibeam' : '/generate/column';
        const data = activeTab === 'beam' 
          ? {
              total_depth: parseFloat(item.total_depth),
              flange_width: parseFloat(item.flange_width),
              web_thickness: parseFloat(item.web_thickness),
              flange_thickness: parseFloat(item.flange_thickness)
            }
          : {
              width: parseFloat(item.width),
              height: parseFloat(item.height)
            };
        
        const response = await axios.post(`http://localhost:8000${endpoint}`, data, {
          responseType: 'blob',
        });
        
        const blob = new Blob([response.data], { type: 'application/dxf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const fileName = activeTab === 'beam' 
          ? `Beam_${data.total_depth}x${data.flange_width}.dxf`
          : `Column_${data.width}x${data.height}.dxf`;
          
        link.setAttribute('download', fileName);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);

        setSuccess("DXF generated successfully");
        setTimeout(() => setSuccess(null), 5000);

        // Reset inputs
        if (activeTab === 'beam') {
          setBeamSingle({ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' });
          setBeamBatch([{ total_depth: '', flange_width: '', web_thickness: '', flange_thickness: '' }]);
        } else {
          setColumnSingle({ width: '', height: '' });
          setColumnBatch([{ width: '', height: '' }]);
        }
      }
    } catch (err) {
      let message = err.message;
      
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const errorData = JSON.parse(text);
          message = errorData.detail || message;
        } catch (e) {
          console.error("Failed to parse error blob:", e);
        }
      } else if (err.response?.data?.detail) {
        message = err.response.data.detail;
      }

      setError(`Failed to generate ${activeTab === 'beam' ? 'Beam' : 'Column'} DXF: ${message}`);
      setTimeout(() => setError(null), 10000);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const itemsCount = activeTab === 'beam' ? beamBatch.length : columnBatch.length;

  return (
    <>
      <button className="top-logout-btn" onClick={onLogout}>
        Logout
      </button>
      <div className="main-card">
        <header className="header">
          <h1>DXF Generator</h1>
        </header>

      <div className="tab-switcher">
        <button 
          className={`tab-btn ${activeTab === 'beam' ? 'active' : ''}`}
          onClick={() => setActiveTab('beam')}
        >
          Beam
        </button>
        <button 
          className={`tab-btn ${activeTab === 'column' ? 'active' : ''}`}
          onClick={() => setActiveTab('column')}
        >
          Column
        </button>
      </div>

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

      {!isBatchMode && (
        <div className="upload-zone">
          <input
            type="file"
            accept=".dxf"
            onChange={handleFileUpload}
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
      )}

      <form onSubmit={handleGenerateDXF} className="input-form">
        {!isBatchMode ? (
          <div className="standard-inputs">
            {activeTab === 'beam' ? (
              <>
                <div className="input-field">
                  <label>Total Depth (H)</label>
                  <input 
                    type="number" 
                    placeholder="H"
                    value={beamSingle.total_depth}
                    onChange={(e) => handleInputChange(0, 'total_depth', e.target.value)}
                  />
                </div>
                <div className="input-field">
                  <label>Flange Width (B)</label>
                  <input 
                    type="number" 
                    placeholder="B"
                    value={beamSingle.flange_width}
                    onChange={(e) => handleInputChange(0, 'flange_width', e.target.value)}
                  />
                </div>
                <div className="input-field">
                  <label>Web Thickness (tw)</label>
                  <input 
                    type="number" 
                    placeholder="tw"
                    value={beamSingle.web_thickness}
                    onChange={(e) => handleInputChange(0, 'web_thickness', e.target.value)}
                  />
                </div>
                <div className="input-field">
                  <label>Flange Thickness (tf)</label>
                  <input 
                    type="number" 
                    placeholder="tf"
                    value={beamSingle.flange_thickness}
                    onChange={(e) => handleInputChange(0, 'flange_thickness', e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="input-field">
                  <label>Width (W)</label>
                  <input 
                    type="number" 
                    placeholder="W"
                    value={columnSingle.width}
                    onChange={(e) => handleInputChange(0, 'width', e.target.value)}
                  />
                </div>
                <div className="input-field">
                  <label>Height (H)</label>
                  <input 
                    type="number" 
                    placeholder="H"
                    value={columnSingle.height}
                    onChange={(e) => handleInputChange(0, 'height', e.target.value)}
                  />
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="items-container">
            {activeTab === 'beam' ? (
              <>
                <div className="grid-header">
                  <span>Total Depth (H)</span>
                  <span>Flange Width (B)</span>
                  <span>Web Thk (tw)</span>
                  <span>Flange Thk (tf)</span>
                  <span className="spacer"></span>
                </div>
                {beamBatch.map((item, index) => (
                  <div key={index} className="grid-row">
                    <input 
                      type="number" 
                      placeholder="H"
                      value={item.total_depth}
                      onChange={(e) => handleInputChange(index, 'total_depth', e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="B"
                      value={item.flange_width}
                      onChange={(e) => handleInputChange(index, 'flange_width', e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="tw"
                      value={item.web_thickness}
                      onChange={(e) => handleInputChange(index, 'web_thickness', e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="tf"
                      value={item.flange_thickness}
                      onChange={(e) => handleInputChange(index, 'flange_thickness', e.target.value)}
                    />
                    <button 
                      type="button" 
                      className="remove-btn"
                      onClick={() => handleRemoveItem(index)}
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </>
            ) : (
              <>
                <div className="grid-header column-grid">
                  <span>Width (W)</span>
                  <span>Height (H)</span>
                  <span className="spacer"></span>
                </div>
                {columnBatch.map((item, index) => (
                  <div key={index} className="grid-row column-grid">
                    <input 
                      type="number" 
                      placeholder="W"
                      value={item.width}
                      onChange={(e) => handleInputChange(index, 'width', e.target.value)}
                    />
                    <input 
                      type="number" 
                      placeholder="H"
                      value={item.height}
                      onChange={(e) => handleInputChange(index, 'height', e.target.value)}
                    />
                    <button 
                      type="button" 
                      className="remove-btn"
                      onClick={() => handleRemoveItem(index)}
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </>
            )}
            <button 
              type="button" 
              className="add-item-btn"
              onClick={handleAddItem}
            >
              + Add Item
            </button>
          </div>
        )}

        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="generate-btn" disabled={loading}>
          {loading ? 'Generating...' : isBatchMode ? `Generate ${itemsCount} Files` : 'Generate DXF'}
        </button>

        {success && <div className="success-msg">{success}</div>}
      </form>
    </div>
    </>
  );
}

export default Generator;
