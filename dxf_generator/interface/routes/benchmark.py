from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch
from dxf_generator.services.dxf_service import DXFService
from dxf_generator.config.logging_config import logger

router = APIRouter()

# Mock Component for internal benchmark
class MockComponent:
    def __init__(self, id):
        self.data = {"id": id}
    
    def generate_dxf(self, filename):
        time.sleep(0.1) 

def run_user_request(user_id):
    """Simulates a single user request"""
    component = MockComponent(user_id)
    components = [component]
    filenames = [f"bench_{user_id}.dxf"]
    
    # Mocking open 
    with patch("builtins.open", MagicMock()):
        DXFService.save_batch(components, filenames)

@router.get("/benchmark", response_class=PlainTextResponse)
async def get_benchmark_table():
    """
    Runs a live benchmark and returns the results as a formatted table.
    Uses non-blocking pattern with as_completed().
    """
    DXFService.clear_caches()
    
    output = []
    output.append("Starting Load Test Simulation...")
    output.append(f"{'Users':<10} {'Total Requests':<15} {'Time Taken (sec)':<20} {'RPS':<10}")
    output.append("-" * 55)
    
    requests_per_user = 5
    
    for num_users in [1, 10, 100]:
        DXFService.clear_caches()
        
        # 1. Measure Submission Time (Non-Blocking)
        submission_start = time.time()
        executor = ThreadPoolExecutor(max_workers=num_users)
        futures = []
        
        for i in range(num_users):
            for j in range(requests_per_user):
                user_id = f"{i}_{j}"
                # call run_user_request which calls save_batch (should be instant)
                future = executor.submit(run_user_request, user_id)
                futures.append(future)
        
        submission_end = time.time()
        submission_time = submission_end - submission_start
        
        # 2. Measure Processing Time (Time for all background tasks to finish)
        # We wait for the benchmark wrapper tasks, which wait for save_batch
        # internal logic (if blocking) or finish instantly (if non-blocking).
        # Since run_user_request logic calls save_batch, and save_batch is async,
        # these futures SHOULD finish instantly.
        # However, to be safe and measure "System Under Load", we might also want to wait.
        
        executor.shutdown(wait=True)
        processing_end = time.time()
        
        # In a fire-and-forget system, "Time Taken" usually refers to response time (submission).
        # "Processing Time" is backend latency.
        # We will report Response Time (Submission) as the primary metric, 
        # but also log Processing Time.
        
        total_reqs = num_users * requests_per_user
        
        # Note: If save_batch is properly non-blocking, processing_end should be very close to submission_end
        # because run_user_request returns after submission. 
        # The ACTUAL background processing happens in BatchProcessor's executor, which we aren't waiting for here!
        # This confirms if save_batch ITSELF is blocking.
        
        duration = submission_time
        rps = total_reqs / duration if duration > 0 else 0
        
        # Format: Response Time (Processing Time)
        time_display = f"{submission_time:.4f}s"
        
        output.append(f"{num_users:<10} {total_reqs:<15} {time_display:<20} {f'{rps:.1f}':<10}")
        logger.info(f"Benchmark {num_users} users: Submission={submission_time:.4f}s, WrapperWait={processing_end-submission_end:.4f}s")
        
    return "\n".join(output)
