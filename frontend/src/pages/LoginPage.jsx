import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DEMO_ACCOUNTS = [
  { role: 'Clinician', username: 'clinician', password: 'clinician123' },
  { role: 'Operations', username: 'ops', password: 'ops123' },
  { role: 'Admin', username: 'admin', password: 'admin123' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(username, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-2xl shadow-2xl">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">AI Refill Dashboard</h2>
          <p className="mt-2 text-center text-sm text-gray-600">Sign in with your credentials</p>
        </div>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2 border focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2 border focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              autoComplete="current-password"
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full flex justify-center py-2 px-4 rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            {submitting ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <div className="border-t pt-4">
          <p className="text-xs text-gray-500 mb-2">Demo accounts (seeded automatically):</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {DEMO_ACCOUNTS.map((acc) => (
              <li key={acc.username}>
                <span className="font-medium">{acc.role}:</span> {acc.username} / {acc.password}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
