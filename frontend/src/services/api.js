import axios from 'axios'
const api = axios.create({ baseURL: 'http://127.0.0.1:5000/api' })
api.interceptors.request.use(c => { const t = localStorage.getItem('token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c })
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401 && !e.config.url.includes('/auth/login')) { localStorage.removeItem('token'); if (location.pathname !== '/login') location.href = '/login' }
  e.userMessage = e.response?.data?.message || (e.request ? 'Cannot reach the server. Check your connection.' : 'Something went wrong.')
  return Promise.reject(e)
})
const d = p => p.then(r => r.data.data)
export const Api = {
  register: b => d(api.post('/auth/register', b)), login: b => d(api.post('/auth/login', b)), me: () => d(api.get('/auth/me')),
  stats: () => d(api.get('/dashboard/stats')),
  analyze: text => d(api.post('/analyze', { job_description: text })),
  upload: file => { const f = new FormData(); f.append('file', file); return d(api.post('/analyze/upload', f)) },
  list: params => d(api.get('/analyses', { params })), get: id => d(api.get(`/analyses/${id}`)), remove: id => d(api.delete(`/analyses/${id}`)),
  profile: () => d(api.get('/profile')), updateProfile: b => d(api.put('/profile', b)), mlInfo: () => d(api.get('/ml/info')),
}
