import { useState } from 'react';
import { Search, Box, Network, Users, Clock, Plus, Edit, CheckCircle } from 'lucide-react';
import { createFileRoute } from '@tanstack/react-router';
import { useHeaderSlot } from '@/components/layout/Header';
import { Input } from '@/components/ui/input';

function CustomHeaderOptions() {
    const [searchQuery, setSearchQuery] = useState('');
    return (
        <div className="relative">
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            <Input
                type="text"
                placeholder="Search"
                className="pl-10 pr-4 py-2 w-64"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
        </div>
    )
}

function Dashboard() {
    useHeaderSlot(CustomHeaderOptions)
    return (
        <main className="p-6">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-sm p-6 flex items-center space-x-4">
                    <div className="p-3 bg-gray-100 rounded-lg">
                        <Box size={24} className="text-gray-800" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Total Applications</p>
                        <h2 className="text-2xl font-semibold">24</h2>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 flex items-center space-x-4">
                    <div className="p-3 bg-gray-100 rounded-lg">
                        <Network size={24} className="text-gray-800" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Active Environments</p>
                        <h2 className="text-2xl font-semibold">72</h2>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 flex items-center space-x-4">
                    <div className="p-3 bg-gray-100 rounded-lg">
                        <Users size={24} className="text-gray-800" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-gray-500">Team Members</p>
                        <h2 className="text-2xl font-semibold">16</h2>
                    </div>
                </div>
            </div>

            {/* Recent Applications */}
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">Recent Applications</h2>
                    <button className="flex items-center px-4 py-2 bg-black text-white rounded-md text-sm">
                        <Plus size={16} className="mr-2" />
                        New Application
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-semibold">Frontend Dashboard</h3>
                            <p className="text-sm text-gray-500">Customer-facing web application</p>
                        </div>
                        <div className="flex justify-between items-center">
                            <div className="flex items-center space-x-1 text-sm text-gray-500">
                                <Clock size={16} />
                                <span>Updated 2 hours ago</span>
                            </div>
                            <div className="flex items-center">
                                <span className="px-3 py-1 bg-green-100 text-green-800 text-xs rounded-full">Production</span>
                                <div className="ml-2 flex items-center space-x-1 text-sm text-gray-500">
                                    <Network size={16} />
                                    <span>3 environments</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="mb-4">
                            <h3 className="text-lg font-semibold">Backend API</h3>
                            <p className="text-sm text-gray-500">Core services and microservices</p>
                        </div>
                        <div className="flex justify-between items-center">
                            <div className="flex items-center space-x-1 text-sm text-gray-500">
                                <Clock size={16} />
                                <span>Updated 5 hours ago</span>
                            </div>
                            <div className="flex items-center">
                                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Staging</span>
                                <div className="ml-2 flex items-center space-x-1 text-sm text-gray-500">
                                    <Network size={16} />
                                    <span>4 environments</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div>
                <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>

                <div className="bg-white rounded-lg shadow-sm p-6">
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center">
                                    <Plus size={16} className="text-white" />
                                </div>
                                <div>
                                    <p className="text-sm">
                                        New variable <span className="font-semibold">API_KEY</span> added to Frontend Dashboard
                                    </p>
                                </div>
                            </div>
                            <span className="text-sm text-gray-500">1h ago</span>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                    <Edit size={16} className="text-white" />
                                </div>
                                <div>
                                    <p className="text-sm">
                                        Updated <span className="font-semibold">DATABASE_URL</span> in Backend API staging
                                    </p>
                                </div>
                            </div>
                            <span className="text-sm text-gray-500">3h ago</span>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <CheckCircle size={16} className="text-white" />
                                </div>
                                <div>
                                    <p className="text-sm">
                                        Deployed changes to <span className="font-semibold">Frontend Dashboard</span> production
                                    </p>
                                </div>
                            </div>
                            <span className="text-sm text-gray-500">6h ago</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

export const Route = createFileRoute('/env')({
    component: Dashboard,
})
