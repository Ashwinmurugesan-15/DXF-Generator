import BeamInputs from './BeamInputs';
import ColumnInputs from './ColumnInputs';

function BatchList({ 
  activeTab, 
  items, 
  handleInputChange, 
  handleRemoveItem, 
  handleAddItem 
}) {
  return (
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
          {items.map((item, index) => (
            <BeamInputs 
              key={index} 
              data={item} 
              onChange={handleInputChange} 
              isBatch={true} 
              onRemove={handleRemoveItem} 
              index={index} 
            />
          ))}
        </>
      ) : (
        <>
          <div className="grid-header column-grid">
            <span>Width (W)</span>
            <span>Height (H)</span>
            <span className="spacer"></span>
          </div>
          {items.map((item, index) => (
            <ColumnInputs 
              key={index} 
              data={item} 
              onChange={handleInputChange} 
              isBatch={true} 
              onRemove={handleRemoveItem} 
              index={index} 
            />
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
  );
}

export default BatchList;
