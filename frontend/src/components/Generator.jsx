import TabSwitcher from './GeneratorParts/TabSwitcher';
import BatchModeToggle from './GeneratorParts/BatchModeToggle';
import UploadZone from './GeneratorParts/UploadZone';
import BatchList from './GeneratorParts/BatchList';
import BeamInputs from './GeneratorParts/BeamInputs';
import ColumnInputs from './GeneratorParts/ColumnInputs';
import { useGenerator } from '../hooks/useGenerator';

function Generator({ onLogout }) {
  const {
    activeTab, setActiveTab,
    isBatchMode, setIsBatchMode,
    beamSingle, columnSingle,
    beamBatch, columnBatch,
    loading, error, success,
    handleAddItem, handleRemoveItem, handleInputChange,
    handleFileUpload, handleGenerateDXF
  } = useGenerator();

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

        <TabSwitcher activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <BatchModeToggle isBatchMode={isBatchMode} setIsBatchMode={setIsBatchMode} />

        {!isBatchMode && (
          <UploadZone onFileUpload={handleFileUpload} loading={loading} />
        )}

        <form onSubmit={handleGenerateDXF} className="input-form">
          {!isBatchMode ? (
            <div className="standard-inputs">
              {activeTab === 'beam' ? (
                <BeamInputs data={beamSingle} onChange={handleInputChange} isBatch={false} />
              ) : (
                <ColumnInputs data={columnSingle} onChange={handleInputChange} isBatch={false} />
              )}
            </div>
          ) : (
            <BatchList 
              activeTab={activeTab}
              items={activeTab === 'beam' ? beamBatch : columnBatch}
              handleInputChange={handleInputChange}
              handleRemoveItem={handleRemoveItem}
              handleAddItem={handleAddItem}
            />
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
