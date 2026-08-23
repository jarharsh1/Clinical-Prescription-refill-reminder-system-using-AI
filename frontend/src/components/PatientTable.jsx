import { useMemo, useState } from 'react';

function filterStatus(patient) {
  if (patient.risk.status === 'overdue') return 'overdue';
  if (patient.ops_issue !== 'None') return 'issue';
  if (patient.risk.status === 'due_soon') return 'due_soon';
  return 'ok';
}

function StatusCell({ patient, role }) {
  if (role === 'clinician') {
    const d = patient.risk.days_until_due;
    if (d < 0) return <div className="font-semibold text-red-600">Overdue by {Math.abs(d)} days</div>;
    if (d <= 7) return <div className="font-semibold text-yellow-600">Due in {d} days</div>;
    return <div className="font-semibold text-green-600">On Track</div>;
  }
  if (patient.ops_issue !== 'None') {
    const color = patient.ops_issue === 'Manual Call Required' ? 'red' : 'yellow';
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${color}-100 text-${color}-800`}>
        {patient.ops_issue}
      </span>
    );
  }
  return (
    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
      No Issues
    </span>
  );
}

export default function PatientTable({ patients, role, onSelect }) {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [clinicianFilter, setClinicianFilter] = useState('all');
  const [conditionFilter, setConditionFilter] = useState('all');
  const isAdmin = role === 'admin';

  const clinicians = useMemo(() => [...new Set(patients.map((p) => p.doctor))], [patients]);
  const conditions = useMemo(() => [...new Set(patients.map((p) => p.condition))], [patients]);

  const filtered = useMemo(() => {
    const term = search.toLowerCase();
    return patients.filter((p) => {
      const matchesSearch =
        p.name.toLowerCase().includes(term) ||
        p.id.toLowerCase().includes(term) ||
        p.medication.toLowerCase().includes(term);
      if (!matchesSearch) return false;
      if (isAdmin) {
        const matchesClinician = clinicianFilter === 'all' || p.doctor === clinicianFilter;
        const matchesCondition = conditionFilter === 'all' || p.condition === conditionFilter;
        return matchesClinician && matchesCondition;
      }
      return statusFilter === 'all' || filterStatus(p) === statusFilter;
    });
  }, [patients, search, statusFilter, clinicianFilter, conditionFilter, isAdmin]);

  const actionText = role === 'ops' ? 'Resolve' : 'View Details';

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="lg:col-span-2">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700">
            Search Patients
          </label>
          <input
            id="search"
            type="text"
            placeholder="Search by name, ID, or medication..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm border px-3 py-2"
          />
        </div>
        {isAdmin ? (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">Filter by Clinician</label>
              <select
                value={clinicianFilter}
                onChange={(e) => setClinicianFilter(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md border"
              >
                <option value="all">All Clinicians</option>
                {clinicians.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Filter by Condition</label>
              <select
                value={conditionFilter}
                onChange={(e) => setConditionFilter(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md border"
              >
                <option value="all">All Conditions</option>
                {conditions.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700">Filter by Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md border"
            >
              <option value="all">All Statuses</option>
              <option value="overdue">Overdue</option>
              <option value="due_soon">Due Soon</option>
              <option value="issue">Operational Issue</option>
              <option value="ok">On Track</option>
            </select>
          </div>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Medication</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Doctor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-500">
                  No patients found.
                </td>
              </tr>
            ) : (
              filtered.map((patient) => (
                <tr key={patient.id}>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{patient.name}</div>
                    <div className="text-sm text-gray-500">{patient.id}</div>
                  </td>
                  <td className="px-6 py-4 text-sm">{patient.medication}</td>
                  <td className="px-6 py-4 text-sm">{patient.doctor}</td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        patient.risk.level === 'High'
                          ? 'bg-red-100 text-red-800'
                          : patient.risk.level === 'Medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {patient.risk.level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <StatusCell patient={patient} role={role} />
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <button
                      onClick={() => onSelect(patient)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      {actionText}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
