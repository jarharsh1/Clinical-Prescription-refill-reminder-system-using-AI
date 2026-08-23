import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';

export function usePatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listPatients();
      setPatients(data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Could not load patient data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { patients, loading, error, refresh };
}
