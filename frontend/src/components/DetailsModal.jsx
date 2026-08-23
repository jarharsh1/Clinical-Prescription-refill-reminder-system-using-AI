import { useState } from 'react';
import { api } from '../api/client';

function RiskPanel({ risk }) {
  const color =
    risk.level === 'High' ? 'text-red-600' : risk.level === 'Medium' ? 'text-yellow-600' : 'text-green-600';
  return (
    <div className="mt-4 border rounded-md p-3 bg-gray-50">
      <p className="text-sm">
        <strong>Adherence Risk:</strong> <span className={`font-bold ${color}`}>{risk.level}</span>{' '}
        <span className="text-gray-500">({risk.score}/100)</span>
      </p>
      <ul className="mt-2 text-xs text-gray-600 list-disc list-inside space-y-0.5">
        {risk.reasons.map((r, i) => (
          <li key={i}>{r}</li>
        ))}
      </ul>
    </div>
  );
}

export default function DetailsModal({ patient, role, onClose, onResolved }) {
  const [resolving, setResolving] = useState(false);
  const [sending, setSending] = useState(false);
  const [channel, setChannel] = useState('SMS');
  const [reminderResult, setReminderResult] = useState(null);
  const [error, setError] = useState(null);

  if (!patient) return null;
  const canAct = role === 'ops' || role === 'admin';

  async function handleResolve() {
    setResolving(true);
    setError(null);
    try {
      await api.resolvePatient(patient.id);
      onResolved?.(patient.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setResolving(false);
    }
  }

  async function handleSendReminder() {
    setSending(true);
    setError(null);
    try {
      const result = await api.sendReminder(patient.id, channel);
      setReminderResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  let content;
  if (role === 'clinician') {
    content = (
      <>
        <h3 className="text-lg font-medium text-gray-900">{patient.name} - Clinical</h3>
        <div className="mt-4 space-y-2 text-sm">
          <p><strong>Medication:</strong> {patient.medication}</p>
          <p><strong>Condition:</strong> {patient.condition}</p>
          <p><strong>Last Refill:</strong> {patient.last_refill}</p>
          <p><strong>Due Date:</strong> {patient.due_date}</p>
        </div>
      </>
    );
  } else if (role === 'ops') {
    content = (
      <>
        <h3 className="text-lg font-medium text-gray-900">{patient.name} - Operational</h3>
        <div className="mt-4 space-y-2 text-sm">
          <p><strong>Issue:</strong> <span className="font-bold text-red-600">{patient.ops_issue}</span></p>
          <p><strong>Insurance:</strong> {patient.insurance}</p>
          <p><strong>Contact:</strong> {patient.contact}</p>
        </div>
      </>
    );
  } else {
    content = (
      <>
        <h3 className="text-lg font-medium text-gray-900">{patient.name} - Full Overview</h3>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-semibold">Clinical Info</h4>
            <p><strong>Medication:</strong> {patient.medication}</p>
            <p><strong>Condition:</strong> {patient.condition}</p>
            <p><strong>Last Refill:</strong> {patient.last_refill}</p>
          </div>
          <div>
            <h4 className="font-semibold">Operational Info</h4>
            <p><strong>Issue:</strong> {patient.ops_issue}</p>
            <p><strong>Insurance:</strong> {patient.insurance}</p>
            <p><strong>Contact:</strong> {patient.contact}</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className="fixed z-20 inset-0 overflow-y-auto" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform sm:my-8 sm:align-middle sm:max-w-lg sm:w-full relative">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            {content}
            <RiskPanel risk={patient.risk} />

            {canAct && (
              <div className="mt-4 border-t pt-4 space-y-3">
                {patient.ops_issue !== 'None' && (
                  <button
                    onClick={handleResolve}
                    disabled={resolving}
                    className="w-full inline-flex justify-center rounded-md border border-transparent px-4 py-2 bg-green-600 text-white text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                  >
                    {resolving ? 'Resolving…' : 'Mark Ops Issue Resolved'}
                  </button>
                )}
                <div className="flex gap-2">
                  <select
                    value={channel}
                    onChange={(e) => setChannel(e.target.value)}
                    className="border-gray-300 rounded-md text-sm border px-2"
                  >
                    <option value="SMS">SMS</option>
                    <option value="Email">Email</option>
                  </select>
                  <button
                    onClick={handleSendReminder}
                    disabled={sending}
                    className="flex-1 inline-flex justify-center rounded-md border border-transparent px-4 py-2 bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {sending ? 'Generating…' : 'Send AI Reminder'}
                  </button>
                </div>
                {reminderResult && (
                  <div className="text-xs bg-indigo-50 border border-indigo-100 rounded-md p-3 text-left">
                    <p className="font-semibold text-indigo-700">
                      Simulated {reminderResult.log.channel} sent (generated by {reminderResult.log.generated_by})
                    </p>
                    <p className="mt-1 text-gray-700 whitespace-pre-wrap">{reminderResult.log.message}</p>
                  </div>
                )}
              </div>
            )}
            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
          </div>
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              onClick={onClose}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
