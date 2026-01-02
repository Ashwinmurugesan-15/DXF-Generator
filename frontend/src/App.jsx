import { useState } from 'react'
import './App.css'
import Login from './components/Login'
import Generator from './components/Generator'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const handleLogin = () => {
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
  }

  return (
    <div className={`app-container ${isLoggedIn ? 'logged-in' : ''}`}>
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <Generator onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
