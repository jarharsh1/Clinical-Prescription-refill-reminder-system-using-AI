const COLORS = {
  indigo: 'text-indigo-600',
  red: 'text-red-600',
  yellow: 'text-yellow-500',
};

export default function KpiCard({ label, value, color = 'indigo' }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md text-center">
      <h3 className="text-lg font-medium text-gray-500">{label}</h3>
      <p className={`mt-1 text-4xl font-bold ${COLORS[color] || COLORS.indigo}`}>{value}</p>
    </div>
  );
}
