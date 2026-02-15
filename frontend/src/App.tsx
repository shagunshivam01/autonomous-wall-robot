import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import PlanningPage from './pages/PlanningPage'
import VisualizationPage from './pages/VisualizationPage'
import HistoryPage from './pages/HistoryPage'

function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Plan Path</Link>
        <Link to="/history">History</Link>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<PlanningPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/visualize/:trajectoryId" element={<VisualizationPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App
