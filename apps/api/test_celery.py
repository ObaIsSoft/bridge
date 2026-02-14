"""
Simple test to verify Celery task can be queued
"""
import sys
sys.path.insert(0, '/Users/obafemi/bridge/apps/api')

from app.core.celery import celery_app
from app.services.tasks import run_extraction_task

# Test if task can be queued
try:
    result = run_extraction_task.delay('test-bridge-id', 'test-user-id')
    print(f"✅ SUCCESS: Task queued with ID: {result.id}")
    print(f"Task status: {result.status}")
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
