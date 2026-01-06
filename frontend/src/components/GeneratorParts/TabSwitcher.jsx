function TabSwitcher({ activeTab, setActiveTab }) {
  return (
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
  );
}

export default TabSwitcher;
