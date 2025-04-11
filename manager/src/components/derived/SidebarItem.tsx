// Component for sidebar items
export function SidebarItem({ icon, label, active = false }) {
  return (
    <div className={`flex items-center px-3 py-2 my-1 text-sm rounded-md ${active ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
      <div className="mr-3">{icon}</div>
      <span className="font-medium">{label}</span>
    </div>
  );
}
