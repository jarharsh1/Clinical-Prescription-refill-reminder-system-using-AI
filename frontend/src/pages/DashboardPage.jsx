import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { usePatients } from '../hooks/usePatients';
import Header from '../components/Header';
import PatientTable from '../components/PatientTable';
import DetailsModal from '../components/DetailsModal';
import ClinicianDashboard from '../dashboards/ClinicianDashboard';
import OpsDashboard from '../dashboards/OpsDashboard';
import AdminDashboard from '../dashboards/AdminDashboard';

const TITLES = {
  clinician: 'Clinician Dashboard',
  ops: 'Operations Dashboard',
  admin: 'Admin Dashboard',
};

export default function DashboardPage() {
  const { user } = useAuth();
  const { patients, loading, error, refresh } = usePatients();
  const [selected, setSelected] = useState(null);

  const role = user.role;

  function handleResolved(patientId) {
    refresh();
    setSelected((prev) => (prev && prev.id === patientId ? { ...prev, ops_issue: 'None' } : prev));
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title={TITLES[role]} />
      <main className="py-8 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 text-center p-4 text-red-600 bg-red-50 rounded-md">{error}</div>
        )}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading patient data…</div>
        ) : (
          <>
            {role === 'clinician' && <ClinicianDashboard patients={patients} />}
            {role === 'ops' && <OpsDashboard patients={patients} />}
            {role === 'admin' && <AdminDashboard patients={patients} />}
            <PatientTable patients={patients} role={role} onSelect={setSelected} />
          </>
        )}
      </main>
      {selected && (
        <DetailsModal
          patient={selected}
          role={role}
          onClose={() => setSelected(null)}
          onResolved={handleResolved}
        />
      )}
    </div>
  );
}
