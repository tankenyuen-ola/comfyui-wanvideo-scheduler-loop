"""
ComfyUI-WanVideo-Scheduler-Loop
A custom node for looping through WanVideo schedulers in ComfyUI
"""

import random
import sys
import os

# WanVideo scheduler list from ComfyUI-WanVideoWrapper
# This is the exact list from wanvideo/schedulers/__init__.py
WANVIDEO_SCHEDULERS = [
    "unipc", "unipc/beta",
    "dpm++", "dpm++/beta",
    "dpm++_sde", "dpm++_sde/beta",
    "euler", "euler/beta",
    # "euler/accvideo",  # Commented out in original
    "deis",
    "lcm", "lcm/beta",
    "res_multistep",
    "flowmatch_causvid",
    "flowmatch_distill",
    "flowmatch_pusa",
    "multitalk"
]

# Try to import WanVideo schedulers to verify they're available
try:
    # This assumes ComfyUI-WanVideoWrapper is installed
    # We can try to import from the actual module to verify it's available
    import sys
    import os
    
    # Try to find the WanVideoWrapper in custom_nodes
    custom_nodes_path = None
    for path in sys.path:
        if "custom_nodes" in path:
            custom_nodes_path = path
            break
    
    if custom_nodes_path:
        wanvideo_path = os.path.join(custom_nodes_path, "ComfyUI-WanVideoWrapper")
        if os.path.exists(wanvideo_path):
            print("ComfyUI-WanVideoWrapper found. Using WanVideo schedulers.")
        else:
            print("Warning: ComfyUI-WanVideoWrapper not found in custom_nodes.")
            print("Please ensure ComfyUI-WanVideoWrapper is properly installed.")
    
except Exception as e:
    print(f"Note: Could not verify WanVideoWrapper installation: {e}")
    print("Schedulers will still work if WanVideoWrapper is properly installed.")

class WanVideoSchedulerSelector:
    """
    A node that allows looping through WanVideo schedulers with different modes:
    - select: manually select a scheduler
    - seed: use a seed to randomly select a scheduler
    - index: use an index to cycle through schedulers
    """
    
    RETURN_TYPES = (WANVIDEO_SCHEDULERS, "STRING",)
    RETURN_NAMES = ("scheduler", "scheduler_name",)
    FUNCTION = "get_scheduler"
    CATEGORY = "WanVideo/Schedulers"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scheduler": (WANVIDEO_SCHEDULERS,),
                "mode": (["select", "seed", "index"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "index": ("INT", {"default": 0, "min": 0, "max": len(WANVIDEO_SCHEDULERS)-1}),
            }
        }

    def get_scheduler(self, scheduler, mode, seed, index):
        """
        Get scheduler based on the selected mode
        Returns the scheduler name as a string for WanVideo nodes
        """
        if mode == "select":
            # Return the manually selected scheduler
            return (scheduler, scheduler)
        
        elif mode == "seed":
            # Use seed to randomly select a scheduler
            random.seed(seed)
            selected_scheduler = random.choice(WANVIDEO_SCHEDULERS)
            return (selected_scheduler, selected_scheduler)
        
        elif mode == "index":
            # Use index to cycle through schedulers
            selected_scheduler = WANVIDEO_SCHEDULERS[index % len(WANVIDEO_SCHEDULERS)]
            return (selected_scheduler, selected_scheduler)
        
        # Fallback
        return (scheduler, scheduler)


class WanVideoSchedulerLoop:
    """
    A more advanced node that provides additional looping functionality
    with step control and batch processing
    """
    
    RETURN_TYPES = (WANVIDEO_SCHEDULERS, "STRING", "INT",)
    RETURN_NAMES = ("scheduler", "scheduler_name", "current_index",)
    FUNCTION = "loop_scheduler"
    CATEGORY = "WanVideo/Schedulers"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["sequential", "random", "ping_pong"],),
                "step": ("INT", {"default": 0, "min": 0, "max": 1000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "reset": ("BOOLEAN", {"default": False}),
                "skip_schedulers": ("STRING", {"default": "", "multiline": False}),
            }
        }

    def loop_scheduler(self, mode, step, seed, reset=False, skip_schedulers=""):
        """
        Advanced scheduler looping with different patterns
        """
        # Parse skip list
        skip_list = []
        if skip_schedulers.strip():
            skip_list = [s.strip() for s in skip_schedulers.split(",")]
        
        # Filter schedulers
        available_schedulers = [s for s in WANVIDEO_SCHEDULERS if s not in skip_list]
        
        if not available_schedulers:
            available_schedulers = WANVIDEO_SCHEDULERS
        
        if mode == "sequential":
            # Sequential loop through schedulers
            index = step % len(available_schedulers)
            selected_scheduler = available_schedulers[index]
            
        elif mode == "random":
            # Random selection with seed
            random.seed(seed + step)  # Different random for each step
            selected_scheduler = random.choice(available_schedulers)
            index = available_schedulers.index(selected_scheduler)
            
        elif mode == "ping_pong":
            # Ping pong pattern: forward then backward
            cycle_length = len(available_schedulers) * 2 - 2
            if cycle_length <= 0:
                cycle_length = 1
            
            pos = step % cycle_length
            if pos < len(available_schedulers):
                index = pos
            else:
                index = len(available_schedulers) - 2 - (pos - len(available_schedulers))
            
            index = max(0, min(index, len(available_schedulers) - 1))
            selected_scheduler = available_schedulers[index]
        
        else:
            # Fallback
            index = 0
            selected_scheduler = available_schedulers[0]
        
        return (selected_scheduler, selected_scheduler, index)


class WanVideoSchedulerInfo:
    """
    A utility node to get information about available WanVideo schedulers
    """
    
    RETURN_TYPES = ("STRING", "INT",)
    RETURN_NAMES = ("scheduler_list", "total_count",)
    FUNCTION = "get_info"
    CATEGORY = "WanVideo/Schedulers"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "format": (["list", "comma_separated", "numbered"], {"default": "list"}),
            }
        }

    def get_info(self, format="list"):
        """
        Get information about available schedulers
        """
        total_count = len(WANVIDEO_SCHEDULERS)
        
        if format == "comma_separated":
            scheduler_info = ", ".join(WANVIDEO_SCHEDULERS)
        elif format == "numbered":
            scheduler_info = "\n".join([f"{i+1}. {scheduler}" 
                                      for i, scheduler in enumerate(WANVIDEO_SCHEDULERS)])
        else:  # list format
            scheduler_info = "\n".join(WANVIDEO_SCHEDULERS)
        
        return (scheduler_info, total_count)


# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "WanVideoSchedulerSelector": WanVideoSchedulerSelector,
    "WanVideoSchedulerLoop": WanVideoSchedulerLoop,
    "WanVideoSchedulerInfo": WanVideoSchedulerInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanVideoSchedulerSelector": "WanVideo Scheduler Selector",
    "WanVideoSchedulerLoop": "WanVideo Scheduler Loop",
    "WanVideoSchedulerInfo": "WanVideo Scheduler Info",
}

# Export for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]