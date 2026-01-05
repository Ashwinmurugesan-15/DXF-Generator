import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function useGenerator() {
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
        setLoading(true);
        const response = await axios.post(`${API_BASE_URL}/parse/dxf`, formData, {
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
      e.target.value = '';
    }
  };

  const handleGenerateDXF = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

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
        const response = await axios.post(`${API_BASE_URL}${endpoint}`, { items }, {
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
          
          const response = await axios.post(`${API_BASE_URL}${endpoint}`, data, {
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
    } finally {
      setLoading(false);
    }
  };

  return {
    activeTab, setActiveTab,
    isBatchMode, setIsBatchMode,
    beamSingle, columnSingle,
    beamBatch, columnBatch,
    loading, error, success,
    handleAddItem, handleRemoveItem, handleInputChange,
    handleFileUpload, handleGenerateDXF
  };
}
