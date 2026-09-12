import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppProvider, useApp } from './context/AppContext'
import AuthPage from './pages/AuthPage'
import Layout from './components/layout/Layout'
import { Analytics, Categories, Dashboard, Profile, Transactions, Accounts } from './pages/FinancePages'

function Protected() {
  const { authStatus } = useApp()
  if (authStatus === 'loading') return <div className="app-loading" aria-live="polite">Loading your workspace...</div>
  return authStatus === 'authenticated' ? <Layout /> : <Navigate to="/login" replace />
}

function App() { return <BrowserRouter><Routes>
  <Route path="/login" element={<AuthPage />} /><Route path="/register" element={<AuthPage initialStep="signup" />} />
  <Route element={<Protected />}><Route path="/" element={<Dashboard />} /><Route path="/transactions" element={<Transactions />} /><Route path="/accounts" element={<Accounts />} /><Route path="/categories" element={<Categories />} /><Route path="/analytics" element={<Analytics />} /><Route path="/profile" element={<Profile />} /><Route path="*" element={<Navigate to="/" replace />} /></Route>
</Routes></BrowserRouter> }

export default function Root() { return <AppProvider><App /></AppProvider> }
