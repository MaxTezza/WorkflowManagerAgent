from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import uuid
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import json
import time
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent Manager Platform")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.ai_agent_manager

# Collections
workflows_collection = db.workflows
trends_collection = db.trends
products_collection = db.products
agent_logs_collection = db.agent_logs
settings_collection = db.settings

# Helper function to convert MongoDB documents
def convert_mongo_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [convert_mongo_doc(item) for item in doc]
    if isinstance(doc, dict):
        # Remove MongoDB _id field and convert any remaining ObjectId fields
        result = {}
        for key, value in doc.items():
            if key == '_id':
                continue  # Skip MongoDB _id
            elif hasattr(value, '__dict__'):
                # Skip complex objects that can't be serialized
                continue
            else:
                result[key] = convert_mongo_doc(value)
        return result
    return doc

# Pydantic models
class WorkflowCreate(BaseModel):
    name: str
    description: str
    type: str  # content_creation, product_development, marketing_automation
    steps: List[Dict[str, Any]]
    priority: int = 1
    target_profitability: float = 0.0

class Workflow(BaseModel):
    id: str
    name: str
    description: str
    type: str
    steps: List[Dict[str, Any]]
    status: str  # pending, running, completed, failed, paused
    priority: int
    target_profitability: float
    actual_profitability: float = 0.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    current_step: int = 0
    results: Dict[str, Any] = {}

class TrendData(BaseModel):
    id: str
    keyword: str
    source: str
    trend_score: float
    volume: int
    profitability_potential: float
    detected_at: datetime
    product_opportunities: List[str]

class AgentStatus(BaseModel):
    status: str  # active, idle, thinking, executing
    current_task: Optional[str]
    active_workflows: int
    completed_today: int
    total_profit_today: float
    decisions_made: int
    last_activity: datetime

class Product(BaseModel):
    id: str
    name: str
    type: str
    workflow_id: str
    created_at: datetime
    cost: float
    revenue: float
    profit: float
    status: str  # created, published, selling, archived

# Global agent state
agent_state = {
    "status": "idle",
    "current_task": None,
    "active_workflows": 0,
    "completed_today": 0,
    "total_profit_today": 0.0,
    "decisions_made": 0,
    "last_activity": datetime.now()
}

# Trend detection functions
# Revenue Generation Functions
async def analyze_template_opportunities():
    """Analyze trending topics for profitable template opportunities"""
    try:
        # Get recent trends
        recent_trends = await trends_collection.find().sort("detected_at", -1).limit(20).to_list(20)
        
        template_opportunities = []
        for trend in recent_trends:
            keyword = trend.get('keyword', '').lower()
            
            # High-value template categories
            template_types = []
            if any(word in keyword for word in ['business', 'startup', 'entrepreneur', 'plan']):
                template_types.extend(['Business Plan Template', 'Pitch Deck Template', 'Financial Tracker'])
            if any(word in keyword for word in ['social media', 'instagram', 'content', 'marketing']):
                template_types.extend(['Social Media Templates', 'Content Calendar', 'Instagram Story Templates'])
            if any(word in keyword for word in ['productivity', 'planner', 'organize', 'schedule']):
                template_types.extend(['Productivity Planner', 'Goal Tracker', 'Daily Schedule Template'])
            if any(word in keyword for word in ['resume', 'cv', 'job', 'career']):
                template_types.extend(['Resume Template', 'Cover Letter Template', 'Portfolio Template'])
            if any(word in keyword for word in ['wedding', 'event', 'party', 'celebration']):
                template_types.extend(['Wedding Planner', 'Event Timeline', 'Invitation Template'])
            
            if template_types:
                for template_type in template_types:
                    opportunity = {
                        "id": str(uuid.uuid4()),
                        "template_type": template_type,
                        "trending_keyword": trend.get('keyword', ''),
                        "market_demand": trend.get('trend_score', 0),
                        "estimated_price": calculate_template_price(template_type),
                        "difficulty": "Easy" if any(word in template_type.lower() for word in ['planner', 'tracker', 'calendar']) else "Medium",
                        "time_to_create": "2-4 hours",
                        "platforms": ["Etsy", "Gumroad", "Creative Market"],
                        "profit_potential": trend.get('profitability_potential', 0) * calculate_template_price(template_type),
                        "created_at": datetime.now(),
                        "status": "opportunity_identified"
                    }
                    template_opportunities.append(opportunity)
        
        # Save to database
        if template_opportunities:
            await db.template_opportunities.insert_many(template_opportunities)
            
        return template_opportunities[:10]  # Return top 10 opportunities
        
    except Exception as e:
        logger.error(f"Error analyzing template opportunities: {e}")
        return []

def calculate_template_price(template_type):
    """Calculate estimated selling price for template types"""
    pricing_map = {
        'Business Plan Template': 25,
        'Pitch Deck Template': 35,
        'Financial Tracker': 15,
        'Social Media Templates': 20,
        'Content Calendar': 18,
        'Instagram Story Templates': 12,
        'Productivity Planner': 22,
        'Goal Tracker': 16,
        'Daily Schedule Template': 14,
        'Resume Template': 8,
        'Cover Letter Template': 6,
        'Portfolio Template': 28,
        'Wedding Planner': 45,
        'Event Timeline': 25,
        'Invitation Template': 15
    }
    return pricing_map.get(template_type, 20)

async def create_template_workflow(opportunity):
    """Create a workflow to produce a digital template"""
    workflow_steps = [
        {
            "type": "market_research",
            "name": f"Research {opportunity['template_type']} market",
            "description": f"Analyze competitor pricing and features for {opportunity['template_type']}",
            "tools": ["Etsy search", "Google Trends", "Pinterest research"],
            "estimated_time": 30,
            "status": "pending"
        },
        {
            "type": "design_planning", 
            "name": "Plan template design",
            "description": f"Create design brief and layout plan for {opportunity['template_type']}",
            "tools": ["Canva (free)", "GIMP", "Paper sketching"],
            "estimated_time": 45,
            "status": "pending"
        },
        {
            "type": "template_creation",
            "name": "Create template",
            "description": f"Design and build the {opportunity['template_type']} using free tools",
            "tools": ["Canva", "Google Docs/Sheets", "GIMP"],
            "estimated_time": 180,  # 3 hours
            "status": "pending"
        },
        {
            "type": "quality_check",
            "name": "Review and refine",
            "description": "Check template quality, usability, and market fit",
            "tools": ["Manual review", "Test with sample data"],
            "estimated_time": 30,
            "status": "pending"
        },
        {
            "type": "listing_creation",
            "name": "Create marketplace listings",
            "description": f"Write descriptions, create previews, set pricing for {opportunity['template_type']}",
            "tools": ["Etsy", "Gumroad", "Creative Market"],
            "estimated_time": 60,
            "status": "pending"
        },
        {
            "type": "revenue_tracking",
            "name": "Monitor sales performance",
            "description": "Track sales, customer feedback, and optimize pricing",
            "tools": ["Platform analytics", "Revenue tracking"],
            "estimated_time": 15,
            "status": "pending"
        }
    ]
    
    workflow_data = {
        "id": str(uuid.uuid4()),
        "name": f"Create {opportunity['template_type']} - Revenue Target: ${opportunity['estimated_price']}",
        "description": f"Complete workflow to create and sell {opportunity['template_type']} based on trending keyword: {opportunity['trending_keyword']}",
        "type": "revenue_generation",
        "category": "digital_templates",
        "steps": workflow_steps,
        "status": "pending",
        "priority": 4,  # High priority for revenue generation
        "target_profitability": opportunity['estimated_price'] * 0.9,  # 90% profit margin
        "actual_profitability": 0.0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "current_step": 0,
        "results": {},
        "opportunity_id": opportunity['id'],
        "estimated_revenue": opportunity['estimated_price'],
        "time_investment": sum(step['estimated_time'] for step in workflow_steps),
        "roi_per_hour": opportunity['estimated_price'] * 0.9 / (sum(step['estimated_time'] for step in workflow_steps) / 60)
    }
    
    await workflows_collection.insert_one(workflow_data)
    return workflow_data

async def scrape_reddit_trends():
    """Scrape trending topics from Reddit"""
    try:
        headers = {'User-Agent': 'AI-Agent-Manager/1.0'}
        url = 'https://www.reddit.com/r/Entrepreneur/hot.json?limit=10'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            trends = []
            
            for post in data['data']['children']:
                post_data = post['data']
                trend = {
                    "id": str(uuid.uuid4()),
                    "keyword": post_data['title'][:100],
                    "source": "reddit_entrepreneur",
                    "trend_score": post_data['score'] / 100.0,
                    "volume": post_data['num_comments'],
                    "profitability_potential": min(post_data['score'] / 1000.0, 1.0),
                    "detected_at": datetime.now(),
                    "product_opportunities": analyze_product_opportunities(post_data['title'])
                }
                trends.append(trend)
            
            # Save to database
            if trends:
                await trends_collection.insert_many(trends)
            
            return trends
    except Exception as e:
        logger.error(f"Error scraping Reddit trends: {e}")
        return []

def analyze_product_opportunities(title):
    """Basic product opportunity analysis"""
    opportunities = []
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['course', 'learn', 'tutorial', 'guide']):
        opportunities.append('Online Course')
    if any(word in title_lower for word in ['template', 'design', 'mockup']):
        opportunities.append('Digital Template')
    if any(word in title_lower for word in ['tool', 'app', 'software', 'automation']):
        opportunities.append('SaaS Tool')
    if any(word in title_lower for word in ['ebook', 'book', 'guide', 'manual']):
        opportunities.append('Digital Guide')
    if any(word in title_lower for word in ['checklist', 'worksheet', 'planner']):
        opportunities.append('Productivity Tool')
    
    return opportunities if opportunities else ['General Digital Product']

# Workflow execution engine
async def execute_workflow_step(workflow_id: str, step_index: int):
    """Execute a single workflow step"""
    try:
        workflow = await workflows_collection.find_one({"id": workflow_id})
        if not workflow or step_index >= len(workflow['steps']):
            return False
        
        step = workflow['steps'][step_index]
        step_type = step.get('type')
        
        # Log the step execution
        await agent_logs_collection.insert_one({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "action": f"Executing step: {step.get('name', 'Unknown')}",
            "workflow_id": workflow_id,
            "step_index": step_index,
            "details": step
        })
        
        # Simulate different step types
        if step_type == 'trend_research':
            await asyncio.sleep(2)  # Simulate research time
            result = {"trends_found": 5, "top_keyword": "AI automation"}
        elif step_type == 'content_creation':
            await asyncio.sleep(3)  # Simulate content creation
            result = {"content_created": True, "word_count": 1500}
        elif step_type == 'market_analysis':
            await asyncio.sleep(1)
            result = {"market_size": "Large", "competition": "Medium", "profit_potential": 0.8}
        elif step_type == 'product_publish':
            await asyncio.sleep(1)
            result = {"published": True, "platform": "digital_marketplace"}
        else:
            result = {"executed": True, "step_type": step_type}
        
        # Update workflow progress
        progress = int(((step_index + 1) / len(workflow['steps'])) * 100)
        await workflows_collection.update_one(
            {"id": workflow_id},
            {
                "$set": {
                    "current_step": step_index + 1,
                    "progress": progress,
                    f"results.step_{step_index}": result
                }
            }
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error executing workflow step: {e}")
        return False

async def agent_decision_engine():
    """AI Agent decision making engine"""
    while True:
        try:
            agent_state["status"] = "thinking"
            agent_state["last_activity"] = datetime.now()
            
            # Check for pending workflows
            pending_workflows = await workflows_collection.find({"status": "pending"}).sort("priority", -1).to_list(None)
            
            # Check for running workflows that need next step
            running_workflows = await workflows_collection.find({"status": "running"}).to_list(None)
            
            for workflow in running_workflows:
                if workflow['current_step'] < len(workflow['steps']):
                    agent_state["status"] = "executing"
                    agent_state["current_task"] = f"Executing {workflow['name']}"
                    
                    success = await execute_workflow_step(workflow['id'], workflow['current_step'])
                    if success:
                        agent_state["decisions_made"] += 1
                        
                        # Check if workflow is complete
                        if workflow['current_step'] + 1 >= len(workflow['steps']):
                            await workflows_collection.update_one(
                                {"id": workflow['id']},
                                {
                                    "$set": {
                                        "status": "completed",
                                        "completed_at": datetime.now(),
                                        "progress": 100
                                    }
                                }
                            )
                            agent_state["completed_today"] += 1
            
            # Start new workflows if capacity allows
            if len(running_workflows) < 3 and pending_workflows:  # Max 3 concurrent workflows
                workflow = pending_workflows[0]
                await workflows_collection.update_one(
                    {"id": workflow['id']},
                    {
                        "$set": {
                            "status": "running",
                            "started_at": datetime.now()
                        }
                    }
                )
                agent_state["active_workflows"] += 1
                
                # Log decision
                await agent_logs_collection.insert_one({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now(),
                    "action": f"Started workflow: {workflow['name']}",
                    "reasoning": f"High priority ({workflow['priority']}) and capacity available",
                    "workflow_id": workflow['id']
                })
            
            agent_state["status"] = "idle"
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            logger.error(f"Agent decision engine error: {e}")
            await asyncio.sleep(10)

# Background tasks
background_tasks_started = False

async def start_background_tasks():
    global background_tasks_started
    if not background_tasks_started:
        background_tasks_started = True
        # Start agent decision engine
        asyncio.create_task(agent_decision_engine())
        # Start trend detection
        asyncio.create_task(periodic_trend_detection())

async def periodic_trend_detection():
    """Periodic trend detection"""
    while True:
        try:
            await scrape_reddit_trends()
            await asyncio.sleep(300)  # Every 5 minutes
        except Exception as e:
            logger.error(f"Trend detection error: {e}")
            await asyncio.sleep(600)  # Wait 10 minutes on error

# API Endpoints
@app.on_event("startup")
async def startup_event():
    await start_background_tasks()

@app.get("/api/agent/status")
async def get_agent_status():
    return AgentStatus(**agent_state)

@app.get("/api/workflows")
async def get_workflows():
    workflows = await workflows_collection.find().sort("created_at", -1).to_list(100)
    return convert_mongo_doc(workflows)

@app.post("/api/workflows")
async def create_workflow(workflow: WorkflowCreate):
    workflow_data = {
        "id": str(uuid.uuid4()),
        "name": workflow.name,
        "description": workflow.description,
        "type": workflow.type,
        "steps": workflow.steps,
        "status": "pending",
        "priority": workflow.priority,
        "target_profitability": workflow.target_profitability,
        "actual_profitability": 0.0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "current_step": 0,
        "results": {}
    }
    
    await workflows_collection.insert_one(workflow_data)
    return {"message": "Workflow created", "id": workflow_data["id"]}

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    workflow = await workflows_collection.find_one({"id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return convert_mongo_doc(workflow)

@app.put("/api/workflows/{workflow_id}/status")
async def update_workflow_status(workflow_id: str, status: str):
    result = await workflows_collection.update_one(
        {"id": workflow_id},
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Status updated"}

@app.get("/api/trends")
async def get_trends():
    trends = await trends_collection.find().sort("detected_at", -1).limit(50).to_list(50)
    return convert_mongo_doc(trends)

@app.get("/api/trends/refresh")
async def refresh_trends():
    try:
        trends = await scrape_reddit_trends()
        if trends is None:
            trends = []
        return {"message": f"Found {len(trends)} new trends", "trends": convert_mongo_doc(trends)}
    except Exception as e:
        logger.error(f"Error refreshing trends: {e}")
        return {"message": "Error refreshing trends", "error": str(e), "trends": []}

@app.get("/api/products")
async def get_products():
    products = await products_collection.find().sort("created_at", -1).to_list(100)
    return convert_mongo_doc(products)

@app.get("/api/agent/logs")
async def get_agent_logs():
    logs = await agent_logs_collection.find().sort("timestamp", -1).limit(100).to_list(100)
    return convert_mongo_doc(logs)

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    total_workflows = await workflows_collection.count_documents({})
    active_workflows = await workflows_collection.count_documents({"status": "running"})
    completed_workflows = await workflows_collection.count_documents({"status": "completed"})
    total_trends = await trends_collection.count_documents({})
    total_products = await products_collection.count_documents({})
    
    # Calculate profitability
    pipeline = [
        {"$group": {"_id": None, "total_profit": {"$sum": "$actual_profitability"}}}
    ]
    profit_result = await workflows_collection.aggregate(pipeline).to_list(1)
    total_profit = profit_result[0]["total_profit"] if profit_result else 0.0
    
    return {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "completed_workflows": completed_workflows,
        "total_trends": total_trends,
        "total_products": total_products,
        "total_profit": total_profit,
        "agent_status": agent_state["status"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)