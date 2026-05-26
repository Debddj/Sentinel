import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Models from './pages/Models'
import ModelDetail from './pages/ModelDetail'
import Alerts from './pages/Alerts'
import Calibration from './pages/Calibration'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/models" element={<Models />} />
        <Route path="/models/:id" element={<ModelDetail />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/calibration" element={<Calibration />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}