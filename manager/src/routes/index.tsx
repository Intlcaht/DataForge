
import { AlertTriangle, CheckCircle, Database, RefreshCw, Settings, Shield } from 'lucide-react';
import { useState } from 'react';

import { StatCard } from '@/components/derived/StatCard';
import { createFileRoute } from '@tanstack/react-router';
// import { useFetchMany } from '@/contexts/RestClientContext';

export const Route = createFileRoute('/')({
    component: DatabaseManagementDashboard,
})

function DatabaseManagementDashboard() {

    // const { fetchAll, loading, error } = useFetchMany("databases")

    const [databases] = useState([
        { name: 'postgres.production-db-1', status: 'Healthy', type: 'PostgreSQL', size: '250GB' },
        { name: 'mariadb.staging-db-1', status: 'Warning', type: 'MySQL', size: '100GB' },
        { name: 'neo4j.pipe-db-1', status: 'Warning', type: 'Neo4j', size: '10GB' },
        { name: 'redis.job-db-1', status: 'Healthy', type: 'Redis', size: '32GB' },
    ]);

    const recentActivities = [
        { type: 'backup', db: 'production-db-1', time: '5 minutes ago' },
        { type: 'schema', db: 'staging-db-1', time: '30 minutes ago' },
    ];

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

            {/* Two-column layout for Activities and Actions */}
            <div className="grid grid-cols-2 gap-6">
                {/* Recent Activity */}
                <div className="bg-white rounded-md shadow">
                    <div className="p-4 border-b border-gray-200">
                        <h2 className="text-lg font-medium">Recent Activity</h2>
                    </div>
                    <div className="p-4">
                        <div className="space-y-4">
                            {recentActivities.map((activity, index) => (
                                <div key={index} className="flex items-start">
                                    <div className={`p-2 rounded-full ${activity.type === 'backup' ? 'bg-green-100' : 'bg-blue-100'
                                        } mr-4`}>
                                        {activity.type === 'backup' ? (
                                            <CheckCircle size={20} className="text-green-600" />
                                        ) : (
                                            <RefreshCw size={20} className="text-blue-600" />
                                        )}
                                    </div>
                                    <div>
                                        <p className="text-sm">
                                            {activity.type === 'backup' ? 'Backup completed for ' : 'Schema update applied to '}
                                            <span className="font-medium">{activity.db}</span>
                                        </p>
                                        <p className="text-xs text-gray-500">{activity.time}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Management Actions */}
                <div className="bg-white rounded-md shadow">
                    <div className="p-4 border-b border-gray-200">
                        <h2 className="text-lg font-medium">Management Actions</h2>
                    </div>
                    <div className="p-4">
                        <div className="space-y-4">
                            <button className="w-full py-3 flex items-center justify-center bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                <Settings size={20} className="mr-2" />
                                <span>Manage Instances</span>
                            </button>
                            <button className="w-full py-3 flex items-center justify-center bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                                <Shield size={20} className="mr-2" />
                                <span>Security Settings</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

