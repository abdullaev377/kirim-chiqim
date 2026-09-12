import client, { saveTokens } from './client'

export const login = async payload => { const { data } = await client.post('/auth/login', payload); saveTokens(data); return data }
export const signup = async payload => { const { data } = await client.post('/auth/signup', payload); saveTokens(data); return data }
export const verifyCode = async code => { const { data } = await client.post('/auth/code-verify', { code }); saveTokens(data); return data }
export const requestNewCode = () => client.get('/auth/new-code').then(({ data }) => data)
export const changeInfo = async payload => { const body = { ...payload }; if (!body.password && !body.conf_password) { delete body.password; delete body.conf_password } const { data } = await client.patch('/auth/change-info', body); saveTokens(data); return data }
export const changePhoto = async file => { const body = new FormData(); body.append('photo', file); const { data } = await client.patch('/auth/change-photo', body); saveTokens(data); return data }
export const getProfile = () => client.get('/auth/profile').then(({ data }) => data)
export const logout = refresh => client.post('/auth/logout/', { refresh })