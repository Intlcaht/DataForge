
import { AlertTriangle, CheckCircle, Database } from 'lucide-react';
import { useState } from 'react';

import { StatCard } from '@/components/derived/StatCard';
import { createFileRoute } from '@tanstack/react-router';
// import { useFetchMany } from '@/contexts/RestClientContext';

export const Route = createFileRoute('/databases')({
    component: DatabaseManagementDashboard,
})

function DatabaseManagementDashboard() {

    // const { fetchAll, loading, error } = useFetchMany("databases")

    const [databases] = useState([
        { name: 'postgres.production-db-1', status: 'Healthy', type: 'PostgreSQL', size: '250GB' },
        { name: 'mariadb.staging-db-1', status: 'Warning', type: 'MySQL', size: '100GB' },
    ]);

    return (
        <main className="p-6">
            {/* Database Stats */}
            <div className="grid grid-cols-3 gap-6 mb-6">
                <StatCard
                    icon={<Database className="text-gray-600" size={24} />}
                    title="Active Databases"
                    value="12"
                    color="bg-white"
                />
                <StatCard
                    icon={<CheckCircle className="text-green-500" size={24} />}
                    title="Healthy"
                    value="10"
                    color="bg-white"
                />
                <StatCard
                    icon={<AlertTriangle className="text-amber-500" size={24} />}
                    title="Warnings"
                    value="2"
                    color="bg-white"
                />
            </div>

            {/* Database Instances */}
            <div className="bg-white rounded-md shadow mb-6">
                <div className="p-4 border-b border-gray-200">
                    <h2 className="text-lg font-medium">Database Instances</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-sm text-gray-500">
                                <th className="px-4 py-3 font-normal">Name</th>
                                <th className="px-4 py-3 font-normal">Status</th>
                                <th className="px-4 py-3 font-normal">Type</th>
                                <th className="px-4 py-3 font-normal">Size</th>
                                <th className="px-4 py-3 font-normal">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {databases.map((db) => (
                                <tr key={db.name} className="border-t border-gray-100">
                                    <td className="px-4 py-3 text-sm">{db.name}</td>
                                    <td className="px-4 py-3">
                                        <span className={`inline-block px-2 py-1 text-xs rounded-full ${db.status === 'Healthy'
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-amber-100 text-amber-800'
                                            }`}>
                                            {db.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm">{db.type}</td>
                                    <td className="px-4 py-3 text-sm">{db.size}</td>
                                    <td className="px-4 py-3 text-sm">
                                        <div className="flex gap-2">
                                            <button className="text-blue-600 hover:text-blue-800">Manage</button>
                                            <button className="text-red-600 hover:text-red-800">Delete</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

        </main>
    );
}

