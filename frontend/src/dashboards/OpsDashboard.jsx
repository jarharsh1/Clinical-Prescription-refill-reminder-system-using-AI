import ChartCard from '../components/ChartCard';
import { exceptionChart, pipelineChart } from '../utils/chartData';

export default function OpsDashboard({ patients }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <ChartCard title="Refill Pipeline" type="doughnut" data={pipelineChart(patients)} />
      <ChartCard title="Manual Exception Types" type="bar" data={exceptionChart(patients)} />
    </div>
  );
}
