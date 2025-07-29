#!/usr/bin/env python3
"""
AI Agent Manager Platform - Revenue Generation Testing
Tests the enhanced revenue-focused features and APIs
"""

import requests
import sys
import json
import time
from datetime import datetime

class RevenueAPITester:
    def __init__(self, base_url="https://3ee80574-49a2-4e62-a787-b3906e46306d.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.revenue_data = {}
        self.workflow_id = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED")
        
        if details:
            print(f"   Details: {details}")
        print()

    def run_api_test(self, name, method, endpoint, expected_status=200, data=None, timeout=10):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            
            success = response.status_code == expected_status
            response_data = {}
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_data = response.json()
                except:
                    response_data = {}
            
            details = f"Status: {response.status_code}"
            if response_data and isinstance(response_data, dict):
                if 'message' in response_data:
                    details += f", Message: {response_data['message']}"
                elif len(response_data) > 0:
                    details += f", Data keys: {list(response_data.keys())[:5]}"
            
            self.log_test(name, success, details)
            return success, response_data
            
        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_revenue_apis(self):
        """Test all revenue-focused APIs"""
        print("🔍 TESTING REVENUE GENERATION APIs")
        print("=" * 50)
        
        # Test revenue stats
        success, stats = self.run_api_test(
            "Revenue Stats API",
            "GET", 
            "api/revenue/stats"
        )
        if success:
            self.revenue_data['stats'] = stats
            print(f"   📊 Total Revenue Target: ${stats.get('total_revenue_target', 0)}")
            print(f"   📈 Active Revenue Workflows: {stats.get('active_revenue_workflows', 0)}")
            print(f"   ✅ Completed Revenue Workflows: {stats.get('revenue_workflows_completed', 0)}")
            print(f"   💡 Opportunities Today: {stats.get('opportunities_today', 0)}")
        
        # Test revenue opportunities
        success, opportunities = self.run_api_test(
            "Revenue Opportunities API",
            "GET",
            "api/revenue/opportunities"
        )
        if success:
            self.revenue_data['opportunities'] = opportunities
            print(f"   🎯 Found {len(opportunities)} revenue opportunities")
            if opportunities:
                for i, opp in enumerate(opportunities[:3]):
                    print(f"      {i+1}. {opp.get('template_type', 'Unknown')} - ${opp.get('estimated_price', 0)}")
        
        # Test next revenue actions
        success, actions = self.run_api_test(
            "Revenue Next Actions API",
            "GET",
            "api/revenue/next-actions"
        )
        if success:
            self.revenue_data['next_actions'] = actions
            print(f"   🚨 Found {len(actions)} pending revenue actions")
            if actions:
                for i, action in enumerate(actions[:3]):
                    print(f"      {i+1}. {action.get('next_step', 'Unknown')} - ${action.get('revenue_target', 0)}")

    def test_core_apis(self):
        """Test core platform APIs"""
        print("\n🔍 TESTING CORE PLATFORM APIs")
        print("=" * 50)
        
        # Test agent status
        success, agent_status = self.run_api_test(
            "Agent Status API",
            "GET",
            "api/agent/status"
        )
        if success:
            print(f"   🤖 Agent Status: {agent_status.get('status', 'unknown')}")
            print(f"   📋 Current Task: {agent_status.get('current_task', 'None')}")
            print(f"   ⚡ Active Workflows: {agent_status.get('active_workflows', 0)}")
        
        # Test workflows
        success, workflows = self.run_api_test(
            "Workflows API",
            "GET",
            "api/workflows"
        )
        if success:
            print(f"   📝 Total Workflows: {len(workflows)}")
            revenue_workflows = [w for w in workflows if w.get('category') == 'digital_templates']
            print(f"   💰 Revenue Workflows: {len(revenue_workflows)}")
            
            # Check for high priority revenue workflows
            high_priority_revenue = [w for w in revenue_workflows if w.get('priority', 0) >= 4]
            print(f"   🔥 High Priority Revenue Workflows: {len(high_priority_revenue)}")
        
        # Test dashboard stats
        success, dashboard = self.run_api_test(
            "Dashboard Stats API",
            "GET",
            "api/dashboard/stats"
        )
        if success:
            print(f"   📊 Total Workflows: {dashboard.get('total_workflows', 0)}")
            print(f"   🏃 Active Workflows: {dashboard.get('active_workflows', 0)}")
            print(f"   ✅ Completed Workflows: {dashboard.get('completed_workflows', 0)}")
            print(f"   💰 Revenue Potential: ${dashboard.get('revenue_potential', 0)}")
        
        # Test trends
        success, trends = self.run_api_test(
            "Trends API",
            "GET",
            "api/trends"
        )
        if success:
            print(f"   📈 Market Trends: {len(trends)}")
        
        # Test agent logs
        success, logs = self.run_api_test(
            "Agent Logs API",
            "GET",
            "api/agent/logs"
        )
        if success:
            print(f"   📋 Agent Log Entries: {len(logs)}")
            revenue_logs = [log for log in logs if 'revenue' in log.get('action', '').lower()]
            print(f"   💰 Revenue-focused Log Entries: {len(revenue_logs)}")

    def test_workflow_creation(self):
        """Test creating a revenue-focused workflow"""
        print("\n🔍 TESTING WORKFLOW CREATION")
        print("=" * 50)
        
        # Create a revenue generation workflow
        workflow_data = {
            "name": "Test Revenue Template - Business Plan",
            "description": "Create a profitable business plan template for digital marketplace",
            "type": "revenue_generation",
            "priority": 4,
            "target_profitability": 22.5,  # 90% of $25 price
            "steps": [
                {
                    "type": "market_research",
                    "name": "Research business plan template market",
                    "description": "Analyze competitor pricing and features",
                    "estimated_time": 30,
                    "status": "pending"
                },
                {
                    "type": "template_creation",
                    "name": "Create business plan template",
                    "description": "Design and build the template",
                    "estimated_time": 180,
                    "status": "pending"
                }
            ]
        }
        
        success, response = self.run_api_test(
            "Create Revenue Workflow",
            "POST",
            "api/workflows",
            200,
            workflow_data
        )
        
        if success:
            workflow_id = response.get('id')
            print(f"   ✅ Created workflow with ID: {workflow_id}")
            self.workflow_id = workflow_id
            
            # Test retrieving the created workflow
            if workflow_id:
                success, workflow = self.run_api_test(
                    "Get Created Workflow",
                    "GET",
                    f"api/workflows/{workflow_id}"
                )
                if success:
                    print(f"   📋 Workflow Type: {workflow.get('type')}")
                    print(f"   🎯 Category: {workflow.get('category')}")
                    print(f"   ⭐ Priority: {workflow.get('priority')}")
                    print(f"   💰 Estimated Revenue: ${workflow.get('estimated_revenue', 0)}")

    def test_revenue_workflow_features(self):
        """Test specific revenue workflow features"""
        print("\n🔍 TESTING REVENUE WORKFLOW FEATURES")
        print("=" * 50)
        
        # Check if workflows have proper revenue metadata
        success, workflows = self.run_api_test(
            "Verify Revenue Workflow Metadata",
            "GET",
            "api/workflows"
        )
        
        if success:
            revenue_workflows = [w for w in workflows if w.get('category') == 'digital_templates']
            
            if revenue_workflows:
                print(f"   ✅ Found {len(revenue_workflows)} revenue workflows")
                
                total_revenue_target = sum(w.get('estimated_revenue', 0) for w in revenue_workflows)
                completed_revenue = [w for w in revenue_workflows if w.get('status') == 'completed']
                
                print(f"   💰 Total Revenue Target: ${total_revenue_target}")
                print(f"   ✅ Completed Revenue Workflows: {len(completed_revenue)}")
                
                # Check for expected $60 target
                if total_revenue_target >= 60:
                    self.log_test("Revenue Target >= $60", True, f"Found ${total_revenue_target}")
                else:
                    self.log_test("Revenue Target >= $60", False, f"Only ${total_revenue_target} found")
                
                # Check priority levels
                high_priority = [w for w in revenue_workflows if w.get('priority', 0) >= 4]
                self.log_test("High Priority Revenue Workflows", len(high_priority) > 0, 
                            f"Found {len(high_priority)} high priority workflows")
            else:
                self.log_test("Revenue Workflows Found", False, "No digital_templates workflows found")

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 AI AGENT MANAGER - REVENUE GENERATION TESTING")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all test suites
        self.test_revenue_apis()
        self.test_core_apis()
        self.test_workflow_creation()
        self.test_revenue_workflow_features()
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.revenue_data.get('stats'):
            stats = self.revenue_data['stats']
            print(f"\n💰 REVENUE SUMMARY:")
            print(f"   Total Revenue Target: ${stats.get('total_revenue_target', 0)}")
            print(f"   Active Revenue Workflows: {stats.get('active_revenue_workflows', 0)}")
            print(f"   Completed Templates: {stats.get('revenue_workflows_completed', 0)}")
            print(f"   Today's Opportunities: {stats.get('opportunities_today', 0)}")
        
        print(f"\n🎯 BUSINESS IMPACT:")
        print(f"   Revenue-focused features: {'✅ Working' if self.tests_passed > self.tests_run * 0.8 else '❌ Issues detected'}")
        print(f"   Ready for money generation: {'✅ Yes' if self.tests_passed > self.tests_run * 0.8 else '❌ Needs fixes'}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = RevenueAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())