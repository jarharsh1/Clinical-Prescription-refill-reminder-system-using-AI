import '../chartSetup';
import { Bar, Doughnut, Pie } from 'react-chartjs-2';

const CHART_COMPONENTS = { bar: Bar, doughnut: Doughnut, pie: Pie };

const baseOptions = { responsive: true, maintainAspectRatio: false };

export default function ChartCard({ title, type, data, options, indexAxis }) {
  const ChartComponent = CHART_COMPONENTS[type];
  const mergedOptions = {
    ...baseOptions,
    ...(indexAxis ? { indexAxis } : {}),
    ...options,
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="relative h-[250px] w-full">
        <ChartComponent data={data} options={mergedOptions} />
      </div>
    </div>
  );
}
