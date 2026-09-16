import time
import inspect
from functools import wraps

def record_node_timing(node_key: str):
    """
    Decorator that calculates execution time and safely appends it 
    to the LangGraph state without breaking existing partial returns.
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(state, *args, **kwargs):
                start = time.perf_counter()
                result = await func(state, *args, **kwargs)
                duration = round(time.perf_counter() - start, 3)
                
                if isinstance(result, dict):
                    # 1. Grab all previous timings from the incoming state
                    timings = dict(state.get("timing_metrics", {}) or {})
                    # 2. Add the current node's time
                    timings[node_key] = duration
                    # 3. Inject the accumulated dictionary back into the node's output
                    result["timing_metrics"] = timings
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(state, *args, **kwargs):
                start = time.perf_counter()
                result = func(state, *args, **kwargs)
                duration = round(time.perf_counter() - start, 3)
                
                if isinstance(result, dict):
                    timings = dict(state.get("timing_metrics", {}) or {})
                    timings[node_key] = duration
                    result["timing_metrics"] = timings
                return result
            return sync_wrapper
    return decorator