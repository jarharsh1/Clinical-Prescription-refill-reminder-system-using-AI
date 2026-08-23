import { useEffect, useState } from 'react';
import ChartCard from '../components/ChartCard';
import KpiCard from '../components/KpiCard';
import { api } from '../api/client';
import { clinicianChart, conditionChart, medicationChart } from '../utils/chartData';

export default function AdminDashboard({ patients }) {
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    api.getKpis().then(setKpis).catch(() => setKpis(null));
  }, [patients]);

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KpiCard label="Total Patients" value={kpis?.total_patients ?? '—'} color="indigo" />
        <KpiCard label="Overdue Refills" value={kpis?.overdue_refills ?? '—'} color="red" />
        <KpiCard label="Open Ops Issues" value={kpis?.open_ops_issues ?? '—'} color="yellow" />
        <KpiCard label="High-Risk Patients" value={kpis?.high_risk_patients ?? '—'} color="red" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <ChartCard title="Patients by Clinician" type="bar" data={clinicianChart(patients)} indexAxis="y" />
        <ChartCard title="Top 5 Medications" type="bar" data={medicationChart(patients)} />
        <ChartCard title="Patients by Condition" type="pie" data={conditionChart(patients)} />
      </div>
    </>
  );
}
