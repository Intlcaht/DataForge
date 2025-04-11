// Component for stat cards
export function StatCard({ icon, title, value, color }) {
  return (
    <div className={`${color} rounded-md shadow p-6`}>
      <div className="flex justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-semibold mt-2">{value}</p>
        </div>
        <div className="flex items-center justify-center">
          {icon}
        </div>
      </div>
    </div>
  );
}
