import './App.css'
import { HashRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './components/auth/page'
import DashboardPage from './components/dashboard/page'

function App() {

  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/d" element={<DashboardPage />} />
      </Routes>
    </HashRouter>
  )
}

export default App
