#!/usr/bin/env python3

import requests
import sys
import json
import time
from datetime import datetime

class AIAgentManagerTester:
    def __init__(self, base_url="https://3ee80574-49a2-4e62-a787-b3906e46306d.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.workflow_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=10):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
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
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_agent_status(self):
        """Test agent status endpoint"""
        success, response = self.run_test(
            "Agent Status",
            "GET",
            "api/agent/status",
            200
        )
        if success:
            required_fields = ['status', 'active_workflows', 'completed_today', 'total_profit_today', 'decisions_made', 'last_activity']
            for field in required_fields:
                if field not in response:
                    print(f"⚠️  Warning: Missing field '{field}' in agent status")
        return success

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "api/dashboard/stats",
            200
        )
        if success:
            required_fields = ['total_workflows', 'active_workflows', 'completed_workflows', 'total_trends', 'total_products', 'total_profit', 'agent_status']
            for field in required_fields:
                if field not in response:
                    print(f"⚠️  Warning: Missing field '{field}' in dashboard stats")
        return success

    def test_get_workflows(self):
        """Test get workflows endpoint"""
        success, response = self.run_test(
            "Get Workflows",
            "GET",
            "api/workflows",
            200
        )
        return success

    def test_create_workflow(self):
        """Test create workflow endpoint"""
        workflow_data = {
            "name": f"Test Workflow {datetime.now().strftime('%H%M%S')}",
            "description": "Automated test workflow for content creation",
            "type": "content_creation",
            "steps": [
                {"type": "trend_research", "name": "Research trending topics", "duration": 2},
                {"type": "content_creation", "name": "Create content", "duration": 5},
                {"type": "market_analysis", "name": "Analyze market potential", "duration": 1},
                {"type": "product_publish", "name": "Publish product", "duration": 1}
            ],
            "priority": 2,
            "target_profitability": 100.0
        }
        
        success, response = self.run_test(
            "Create Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'id' in response:
            self.workflow_id = response['id']
            print(f"   Created workflow with ID: {self.workflow_id}")
        
        return success

    def test_get_single_workflow(self):
        """Test get single workflow endpoint"""
        if not self.workflow_id:
            print("⚠️  Skipping single workflow test - no workflow ID available")
            return True
            
        success, response = self.run_test(
            "Get Single Workflow",
            "GET",
            f"api/workflows/{self.workflow_id}",
            200
        )
        return success

    def test_get_trends(self):
        """Test get trends endpoint"""
        success, response = self.run_test(
            "Get Trends",
            "GET",
            "api/trends",
            200
        )
        return success

    def test_refresh_trends(self):
        """Test refresh trends endpoint"""
        success, response = self.run_test(
            "Refresh Trends",
            "GET",
            "api/trends/refresh",
            200,
            timeout=30  # Longer timeout for Reddit scraping
        )
        return success

    def test_get_products(self):
        """Test get products endpoint"""
        success, response = self.run_test(
            "Get Products",
            "GET",
            "api/products",
            200
        )
        return success

    def test_get_agent_logs(self):
        """Test get agent logs endpoint"""
        success, response = self.run_test(
            "Get Agent Logs",
            "GET",
            "api/agent/logs",
            200
        )
        return success

    def test_workflow_execution_monitoring(self):
        """Monitor workflow execution for a short period"""
        if not self.workflow_id:
            print("⚠️  Skipping workflow monitoring - no workflow ID available")
            return True
            
        print(f"\n🔍 Monitoring workflow execution for 30 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            success, workflow = self.run_test(
                "Monitor Workflow Progress",
                "GET",
                f"api/workflows/{self.workflow_id}",
                200
            )
            
            if success:
                status = workflow.get('status', 'unknown')
                progress = workflow.get('progress', 0)
                current_step = workflow.get('current_step', 0)
                print(f"   Status: {status}, Progress: {progress}%, Step: {current_step}")
                
                if status == 'completed':
                    print("✅ Workflow completed successfully!")
                    return True
                elif status == 'failed':
                    print("❌ Workflow failed!")
                    return False
            
            time.sleep(5)
        
        print("⚠️  Workflow monitoring timeout - workflow may still be running")
        return True

def main():
    print("🚀 Starting AI Agent Manager Backend API Tests")
    print("=" * 60)
    
    tester = AIAgentManagerTester()
    
    # Test all endpoints
    tests = [
        tester.test_agent_status,
        tester.test_dashboard_stats,
        tester.test_get_workflows,
        tester.test_create_workflow,
        tester.test_get_single_workflow,
        tester.test_get_trends,
        tester.test_refresh_trends,
        tester.test_get_products,
        tester.test_get_agent_logs,
        tester.test_workflow_execution_monitoring
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
        
        # Small delay between tests
        time.sleep(1)
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())