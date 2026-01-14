import os
import subprocess
import sys
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()

class TestCase(BaseModel):
    name: str
    path: str
    suite: str

class TestRunResult(BaseModel):
    status: str
    output: str
    exit_code: int

@router.get("/testcases", response_model=List[TestCase])
async def get_testcases():
    test_dir = os.path.join(os.getcwd(), "tests")
    test_cases = []
    
    if not os.path.exists(test_dir):
        return []

    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                suite = "unit" if "unit" in root else "integration" if "integration" in root else "other"
                test_cases.append(TestCase(
                    name=file,
                    path=os.path.relpath(os.path.join(root, file), os.getcwd()),
                    suite=suite
                ))
    
    return test_cases

@router.get("/testcases/run/all", response_model=TestRunResult)
async def run_all_tests():
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        
        process = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "-v"],
            capture_output=True,
            text=True,
            env=env
        )
        
        return TestRunResult(
            status="passed" if process.returncode == 0 else "failed",
            output=process.stdout + process.stderr,
            exit_code=process.returncode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
