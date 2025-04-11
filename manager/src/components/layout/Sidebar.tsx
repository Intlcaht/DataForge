import { Link } from '@tanstack/react-router'
import { SidebarItem } from '../derived/SidebarItem'
import { Activity, Database, Home, Settings, Shield, Variable } from 'lucide-react'

function Sidebar() {

  // const router = useRouter();

  return (
    <div className="w-60 bg-white border-r border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center">
          <div className="bg-indigo-600 text-white p-1 rounded">
            <span className="font-bold">LOGO</span>
          </div>
        </div>
      </div>

      <nav className="mt-2 px-2">
        <Link to='/'>
          <SidebarItem icon={<Home size={20} />} label="Dashboard" active />
        </Link>
        <Link to='/databases'>
          <SidebarItem icon={<Database size={20} />} label="Databases" />
        </Link>
        <Link to='/env'>
          <SidebarItem icon={<Variable size={20} />} label="Env Vars" />
        </Link>
        <SidebarItem icon={<Settings size={20} />} label="Configuration" />
        <SidebarItem icon={<Shield size={20} />} label="Security" />
        <SidebarItem icon={<Activity size={20} />} label="Monitoring" />
      </nav>
    </div>
  )
}

export default Sidebar