import ChartCard from '../components/ChartCard';
import { riskLevelChart, statusChart } from '../utils/chartData';

export default function ClinicianDashboard({ patients }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <ChartCard title="Adherence Risk Distribution" type="doughnut" data={riskLevelChart(patients)} />
      <ChartCard title="Patients by Refill Status" type="bar" data={statusChart(patients)} />
    </div>
  );
}
