import client from './client'

const resource = path => ({
  list: params => client.get(`/api/${path}/`, { params }).then(({ data }) => data),
  create: body => client.post(`/api/${path}/`, body).then(({ data }) => data),
  update: (id, body) => client.patch(`/api/${path}/${id}/`, body).then(({ data }) => data),
  remove: id => client.delete(`/api/${path}/${id}/`),
})

export const accountsApi = resource('accounts')
export const categoriesApi = resource('categories')
export const transactionsApi = resource('transactions')
export const currenciesApi = resource('currencies')
export const statsApi = () => client.get('/api/transactions/stats/').then(({ data }) => data)