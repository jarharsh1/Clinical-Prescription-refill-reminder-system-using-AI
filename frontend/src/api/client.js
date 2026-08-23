const TOKEN_KEY = 'refill_dashboard_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed with status ${status}`);
    this.status = status;
  }
}

async function request(path, { method = 'GET', body, headers = {}, form = false } = {}) {
  const token = getToken();
  const finalHeaders = { ...headers };
  if (token) finalHeaders.Authorization = `Bearer ${token}`;
  if (body && !form) finalHeaders['Content-Type'] = 'application/json';

  const res = await fetch(`/api${path}`, {
    method,
    headers: finalHeaders,
    body: form ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    if (res.status === 401) setToken(null);
    throw new ApiError(res.status, isJson ? data.detail : data);
  }
  return data;
}

export const api = {
  login: (username, password) => {
    const form = new URLSearchParams({ username, password });
    return request('/auth/login', { method: 'POST', body: form, form: true });
  },
  me: () => request('/auth/me'),
  listPatients: () => request('/patients'),
  getPatient: (id) => request(`/patients/${id}`),
  getPatientHistory: (id) => request(`/patients/${id}/history`),
  resolvePatient: (id) => request(`/patients/${id}/resolve`, { method: 'PATCH', body: {} }),
  updatePatient: (id, data) => request(`/patients/${id}`, { method: 'PATCH', body: data }),
  createPatient: (data) => request('/patients', { method: 'POST', body: data }),
  sendReminder: (id, channel) =>
    request(`/patients/${id}/remind`, { method: 'POST', body: { channel } }),
  getContactLogs: (id) => request(`/patients/${id}/contact-logs`),
  getKpis: () => request('/dashboard/kpis'),
};

export { ApiError };
