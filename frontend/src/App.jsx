import { Routes, Route, Navigate } from 'react-router-dom'
import { Protected, GuestOnly } from './components/Shell'
import Landing from './pages/Landing'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import Results from './pages/Results'
import History from './pages/History'
import Profile from './pages/Profile'
export default function App() {
  return <Routes>
    <Route path="/" element={<Landing />} />
    <Route path="/login" element={<GuestOnly><Auth mode="login" /></GuestOnly>} />
    <Route path="/signup" element={<GuestOnly><Auth mode="signup" /></GuestOnly>} />
    <Route element={<Protected />}><Route path="/dashboard" element={<Dashboard />} /><Route path="/analyze" element={<Analyze />} />
      <Route path="/results/:id" element={<Results />} /><Route path="/history" element={<History />} /><Route path="/profile" element={<Profile />} /></Route>
    <Route path="*" element={<Navigate to="/" replace />} /></Routes>
}
