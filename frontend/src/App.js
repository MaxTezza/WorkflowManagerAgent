import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [agentStatus, setAgentStatus] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [trends, setTrends] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);
  const [revenueStats, setRevenueStats] = useState(null);
  const [revenueOpportunities, setRevenueOpportunities] = useState([]);
  const [nextActions, setNextActions] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showCreateWorkflow, setShowCreateWorkflow] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch data functions
  const fetchAgentStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent/status`);
      const data = await response.json();
      setAgentStatus(data);
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/workflows`);
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trends`);
      const data = await response.json();
      setTrends(data);
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
      const data = await response.json();
      setDashboardStats(data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  const fetchAgentLogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent/logs`);
      const data = await response.json();
      setAgentLogs(data);
    } catch (error) {
      console.error('Error fetching agent logs:', error);
    }
  };

  const fetchRevenueStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/revenue/stats`);
      const data = await response.json();
      setRevenueStats(data);
    } catch (error) {
      console.error('Error fetching revenue stats:', error);
    }
  };

  const fetchRevenueOpportunities = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/revenue/opportunities`);
      const data = await response.json();
      setRevenueOpportunities(data);
    } catch (error) {
      console.error('Error fetching revenue opportunities:', error);
    }
  };

  const fetchNextActions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/revenue/next-actions`);
      const data = await response.json();
      setNextActions(data);
    } catch (error) {
      console.error('Error fetching next actions:', error);
    }
  };

  const refreshTrends = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/trends/refresh`);
      await fetchTrends();
    } catch (error) {
      console.error('Error refreshing trends:', error);
    }
  };

  // Initialize data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchAgentStatus(),
        fetchWorkflows(),
        fetchTrends(),
        fetchDashboardStats(),
        fetchAgentLogs(),
        fetchRevenueStats(),
        fetchRevenueOpportunities(),
        fetchNextActions()
      ]);
      setLoading(false);
    };
    
    loadData();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchAgentStatus();
      fetchWorkflows();
      fetchDashboardStats();
      fetchAgentLogs();
      fetchRevenueStats();
      fetchNextActions();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const AgentStatusIndicator = () => (
    <div className="flex items-center space-x-2">
      <div className={`w-3 h-3 rounded-full ${
        agentStatus?.status === 'active' ? 'bg-green-500 animate-pulse' :
        agentStatus?.status === 'executing' ? 'bg-blue-500 animate-pulse' :
        agentStatus?.status === 'thinking' ? 'bg-yellow-500 animate-pulse' :
        'bg-gray-400'
      }`}></div>
      <span className="font-medium capitalize">{agentStatus?.status || 'Unknown'}</span>
      {agentStatus?.current_task && (
        <span className="text-sm text-gray-600">- {agentStatus.current_task}</span>
      )}
    </div>
  );

  const WorkflowCard = ({ workflow }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-l-blue-500">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{workflow.name}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
          workflow.status === 'running' ? 'bg-blue-100 text-blue-800' :
          workflow.status === 'failed' ? 'bg-red-100 text-red-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {workflow.status}
        </span>
      </div>
      <p className="text-gray-600 text-sm mb-3">{workflow.description}</p>
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm text-gray-500">Progress</span>
        <span className="text-sm font-medium">{workflow.progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${workflow.progress}%` }}
        ></div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Type:</span>
          <p className="font-medium capitalize">{workflow.type?.replace('_', ' ')}</p>
        </div>
        <div>
          <span className="text-gray-500">Priority:</span>
          <p className="font-medium">{workflow.priority}</p>
        </div>
      </div>
    </div>
  );

  const RevenueOpportunityCard = ({ opportunity }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-l-green-500">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{opportunity.template_type}</h3>
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
          ${opportunity.estimated_price}
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3">Based on trending: {opportunity.trending_keyword}</p>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-gray-500">Difficulty:</span>
          <span className="ml-2 font-medium">{opportunity.difficulty}</span>
        </div>
        <div>
          <span className="text-gray-500">Time:</span>
          <span className="ml-2 font-medium">{opportunity.time_to_create}</span>
        </div>
      </div>
      <div className="mt-3">
        <span className="text-gray-500 text-sm">Platforms:</span>
        <div className="flex flex-wrap gap-1 mt-1">
          {opportunity.platforms?.map((platform, idx) => (
            <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
              {platform}
            </span>
          ))}
        </div>
      </div>
      <div className="mt-3 pt-3 border-t">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">Profit Potential:</span>
          <span className="font-bold text-green-600">${opportunity.profit_potential?.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );

  const NextActionCard = ({ action }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-l-yellow-500">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{action.next_step}</h3>
        <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
          {action.estimated_time} min
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-3">{action.description}</p>
      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm text-gray-500">Progress</span>
          <span className="text-sm font-medium">{action.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-yellow-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${action.progress}%` }}
          ></div>
        </div>
      </div>
      <div className="text-sm">
        <span className="text-gray-500">Revenue Target:</span>
        <span className="ml-2 font-bold text-green-600">${action.revenue_target}</span>
      </div>
      {action.tools && action.tools.length > 0 && (
        <div className="mt-3">
          <span className="text-gray-500 text-sm">Tools needed:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {action.tools.map((tool, idx) => (
              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const CreateWorkflowModal = () => {
    const [newWorkflow, setNewWorkflow] = useState({
      name: '',
      description: '',
      type: 'content_creation',
      steps: [],
      priority: 1
    });

    const workflowTemplates = {
      content_creation: [
        { type: 'trend_research', name: 'Research trending topics', duration: 2 },
        { type: 'content_creation', name: 'Create content', duration: 5 },
        { type: 'market_analysis', name: 'Analyze market potential', duration: 1 },
        { type: 'product_publish', name: 'Publish product', duration: 1 }
      ],
      product_development: [
        { type: 'market_analysis', name: 'Market research', duration: 3 },
        { type: 'trend_research', name: 'Trend validation', duration: 2 },
        { type: 'content_creation', name: 'Product development', duration: 8 },
        { type: 'product_publish', name: 'Launch product', duration: 2 }
      ],
      marketing_automation: [
        { type: 'trend_research', name: 'Audience research', duration: 2 },
        { type: 'content_creation', name: 'Create marketing materials', duration: 4 },
        { type: 'market_analysis', name: 'Campaign optimization', duration: 2 },
        { type: 'product_publish', name: 'Deploy campaign', duration: 1 }
      ]
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        const workflowData = {
          ...newWorkflow,
          steps: workflowTemplates[newWorkflow.type] || []
        };
        
        const response = await fetch(`${API_BASE_URL}/api/workflows`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(workflowData)
        });
        
        if (response.ok) {
          setShowCreateWorkflow(false);
          fetchWorkflows();
          setNewWorkflow({ name: '', description: '', type: 'content_creation', steps: [], priority: 1 });
        }
      } catch (error) {
        console.error('Error creating workflow:', error);
      }
    };

    if (!showCreateWorkflow) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold mb-4">Create New Workflow</h3>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={newWorkflow.name}
                onChange={(e) => setNewWorkflow({...newWorkflow, name: e.target.value})}
                className="w-full p-2 border rounded-lg"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={newWorkflow.description}
                onChange={(e) => setNewWorkflow({...newWorkflow, description: e.target.value})}
                className="w-full p-2 border rounded-lg h-20"
                required
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Type</label>
              <select
                value={newWorkflow.type}
                onChange={(e) => setNewWorkflow({...newWorkflow, type: e.target.value})}
                className="w-full p-2 border rounded-lg"
              >
                <option value="content_creation">Content Creation</option>
                <option value="product_development">Product Development</option>
                <option value="marketing_automation">Marketing Automation</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Priority</label>
              <select
                value={newWorkflow.priority}
                onChange={(e) => setNewWorkflow({...newWorkflow, priority: parseInt(e.target.value)})}
                className="w-full p-2 border rounded-lg"
              >
                <option value={1}>Low</option>
                <option value={2}>Medium</option>
                <option value={3}>High</option>
                <option value={4}>Critical</option>
              </select>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
              >
                Create Workflow
              </button>
              <button
                type="button"
                onClick={() => setShowCreateWorkflow(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading AI Agent Manager...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Agent Manager</h1>
              <p className="text-gray-600">Intelligent Workflow Automation Platform</p>
            </div>
            <div className="flex items-center space-x-4">
              <AgentStatusIndicator />
              <button
                onClick={() => setShowCreateWorkflow(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                New Workflow
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            {['dashboard', 'workflows', 'revenue', 'trends', 'logs'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-3 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab === 'revenue' ? '💰 Revenue' : tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 rounded-full bg-blue-100">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Workflows</p>
                    <p className="text-2xl font-semibold text-gray-900">{dashboardStats?.total_workflows || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 rounded-full bg-green-100">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Active Workflows</p>
                    <p className="text-2xl font-semibold text-gray-900">{dashboardStats?.active_workflows || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 rounded-full bg-purple-100">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Trends Detected</p>
                    <p className="text-2xl font-semibold text-gray-900">{dashboardStats?.total_trends || 0}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 rounded-full bg-yellow-100">
                    <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Revenue Potential</p>
                    <p className="text-2xl font-semibold text-green-600">${dashboardStats?.revenue_potential?.toFixed(2) || '0.00'}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-3 rounded-full bg-red-100">
                    <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Next Actions</p>
                    <p className="text-2xl font-semibold text-red-600">{nextActions?.length || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Revenue Section */}
            {revenueStats && (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">💰 Revenue Generation Status</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">${revenueStats.total_revenue_target?.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">Target Revenue</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">{revenueStats.active_revenue_workflows}</p>
                    <p className="text-sm text-gray-600">Active Revenue Workflows</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">{revenueStats.opportunities_today}</p>
                    <p className="text-sm text-gray-600">Opportunities Today</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-yellow-600">${revenueStats.average_template_price?.toFixed(2)}</p>
                    <p className="text-sm text-gray-600">Avg Template Price</p>
                  </div>
                </div>
              </div>
            )}

            {/* Next Actions Section */}
            {nextActions && nextActions.length > 0 && (
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                  <h3 className="text-lg font-semibold text-red-600">🚨 Action Required - Revenue Workflows</h3>
                  <p className="text-sm text-gray-600 mt-1">Complete these steps to generate revenue</p>
                </div>
                <div className="p-6 space-y-4">
                  {nextActions.slice(0, 3).map((action, idx) => (
                    <NextActionCard key={idx} action={action} />
                  ))}
                </div>
              </div>
            )}

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                  <h3 className="text-lg font-semibold">Recent Workflows</h3>
                </div>
                <div className="p-6 space-y-4">
                  {workflows.slice(0, 3).map((workflow, idx) => (
                    <WorkflowCard key={idx} workflow={workflow} />
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                  <h3 className="text-lg font-semibold">Revenue Opportunities</h3>
                </div>
                <div className="p-6 space-y-4">
                  {revenueOpportunities.slice(0, 3).map((opportunity, idx) => (
                    <RevenueOpportunityCard key={idx} opportunity={opportunity} />
                  ))}
                  {revenueOpportunities.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Agent is analyzing trends for revenue opportunities...</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'workflows' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">All Workflows</h2>
              <button
                onClick={() => setShowCreateWorkflow(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Create Workflow
              </button>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {workflows.map((workflow, idx) => (
                <WorkflowCard key={idx} workflow={workflow} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'revenue' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold">💰 Revenue Generation Center</h2>
                <p className="text-gray-600">AI-powered digital product creation for maximum profitability</p>
              </div>
            </div>

            {/* Revenue Stats */}
            {revenueStats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-green-400 to-green-600 rounded-lg p-6 text-white">
                  <h3 className="text-lg font-semibold mb-2">Total Revenue Target</h3>
                  <p className="text-3xl font-bold">${revenueStats.total_revenue_target?.toFixed(2)}</p>
                </div>
                <div className="bg-gradient-to-r from-blue-400 to-blue-600 rounded-lg p-6 text-white">
                  <h3 className="text-lg font-semibold mb-2">Active Revenue Workflows</h3>
                  <p className="text-3xl font-bold">{revenueStats.active_revenue_workflows}</p>
                </div>
                <div className="bg-gradient-to-r from-purple-400 to-purple-600 rounded-lg p-6 text-white">
                  <h3 className="text-lg font-semibold mb-2">Completed Templates</h3>
                  <p className="text-3xl font-bold">{revenueStats.revenue_workflows_completed}</p>
                </div>
                <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg p-6 text-white">
                  <h3 className="text-lg font-semibold mb-2">Avg Template Price</h3>
                  <p className="text-3xl font-bold">${revenueStats.average_template_price?.toFixed(2)}</p>
                </div>
              </div>
            )}

            {/* Next Actions */}
            {nextActions && nextActions.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-red-700 mb-4">🚨 Immediate Actions Required</h3>
                <p className="text-red-600 mb-4">Complete these steps to start earning revenue:</p>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {nextActions.map((action, idx) => (
                    <NextActionCard key={idx} action={action} />
                  ))}
                </div>
              </div>
            )}

            {/* Revenue Opportunities */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b">
                <h3 className="text-lg font-semibold">🎯 Identified Revenue Opportunities</h3>
                <p className="text-sm text-gray-600 mt-1">Templates the AI agent found based on trending topics</p>
              </div>
              <div className="p-6">
                {revenueOpportunities.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {revenueOpportunities.map((opportunity, idx) => (
                      <RevenueOpportunityCard key={idx} opportunity={opportunity} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">AI agent is analyzing market trends to identify profitable template opportunities...</p>
                    <p className="text-sm text-gray-500 mt-2">Check back in a few minutes for new opportunities</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Market Trends</h2>
              <button
                onClick={refreshTrends}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                Refresh Trends
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trends.map((trend, idx) => (
                <div key={idx} className="bg-white rounded-lg shadow-md p-4 border-l-4 border-l-green-500">
                  <h4 className="font-semibold text-gray-800 mb-2">{trend.keyword}</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500">Score:</span>
                      <span className="ml-2 font-medium">{trend.trend_score?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Volume:</span>
                      <span className="ml-2 font-medium">{trend.volume}</span>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span className="text-gray-500 text-sm">Opportunities:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {trend.product_opportunities?.map((opp, idx) => (
                        <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          {opp}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Agent Activity Logs</h2>
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="space-y-4">
                  {agentLogs.map((log, idx) => (
                    <div key={idx} className="border-l-4 border-l-blue-500 pl-4 py-2">
                      <div className="flex justify-between items-start">
                        <p className="font-medium">{log.action}</p>
                        <span className="text-sm text-gray-500">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      {log.reasoning && (
                        <p className="text-sm text-gray-600 mt-1">{log.reasoning}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <CreateWorkflowModal />
    </div>
  );
}

export default App;