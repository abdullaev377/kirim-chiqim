import { createContext, useContext, useEffect, useState } from 'react'
import { accountsApi, categoriesApi, currenciesApi, statsApi, transactionsApi } from '../api/resources'
import { clearTokens, getApiError } from '../api/client'
import { getProfile } from '../api/auth'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [data, setData] = useState({ accounts: [], categories: [], currencies: [], transactions: [], stats: { income: 0, expense: 0, balance: 0 } })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [authStatus, setAuthStatus] = useState('loading')

  const refresh = async (params) => {
    setLoading(true); setError('')
    try {
      const [accounts, categories, currencies, transactions, stats] = await Promise.all([
        accountsApi.list(), categoriesApi.list(), currenciesApi.list(), transactionsApi.list(params), statsApi(),
      ])
      setData({ accounts, categories, currencies, transactions, stats })
      return { accounts, categories, currencies, transactions, stats }
    } catch (requestError) { setError(getApiError(requestError)); throw requestError } finally { setLoading(false) }
  }

  useEffect(() => {
    let active = true
    const bootstrap = async () => {
      if (!localStorage.getItem('access')) { setAuthStatus('unauthenticated'); setLoading(false); return }
      try {
        const profile = await getProfile()
        if (!active) return
        localStorage.setItem('ledgerly_profile', JSON.stringify(profile))
        setAuthStatus('authenticated')
        await refresh()
      } catch {
        if (!active) return
        clearTokens()
        setAuthStatus('unauthenticated')
        setLoading(false)
      }
    }
    bootstrap()
    return () => { active = false }
  }, [])
  return <AppContext.Provider value={{ data, loading, error, refresh, setError, authStatus }}>{children}</AppContext.Provider>
}

export const useApp = () => useContext(AppContext)