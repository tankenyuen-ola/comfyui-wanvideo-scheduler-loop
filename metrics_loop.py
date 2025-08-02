"""
ComfyUI-WanVideo-Scheduler-Loop
A custom node for looping through WanVideo schedulers in ComfyUI
"""

import random
import sys
import os
from .scheduler_list_getter import get_wanvideo_scheduler_list

# WanVideo scheduler list from ComfyUI-WanVideoWrapper
# This is the exact list from wanvideo/schedulers/__init__.py

#  WanVideo scheduler fallback list
WANVIDEO_FALLBACK_SCHEDULERS = [
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

# WanVideo schedulers, from ComfyUI-WanVideoWrapper
WANVIDEOWRAPPER_SCHEDULERS = get_wanvideo_scheduler_list()

if WANVIDEOWRAPPER_SCHEDULERS:
    WANVIDEO_SCHEDULERS = WANVIDEOWRAPPER_SCHEDULERS
    print("WanVideoWrapper schedulers loaded successfully")
else:
    WANVIDEO_SCHEDULERS = WANVIDEO_FALLBACK_SCHEDULERS

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

class WanVideoSchedulerLoop:
    """
    A more advanced node that provides automatic looping functionality
    with internal state management - no manual step increment needed
    """
    
    # Global counters for different modes
    _global_counters = {"sequential": 0, "ping_pong": 0, "random": 0}
    _last_execution_ids = {"sequential": None, "ping_pong": None, "random": None}
    
    RETURN_TYPES = (WANVIDEO_SCHEDULERS, "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("scheduler", "scheduler_name", "current_index", "total_combinations", "current_combination")
    FUNCTION = "loop_scheduler"
    CATEGORY = "WanVideo/Schedulers"

    @classmethod
    def INPUT_TYPES(cls):
        # Generate individual skip options for each scheduler
        skip_inputs = {}
        for scheduler in WANVIDEO_SCHEDULERS:
            skip_inputs[f"skip_{scheduler.replace('/', '_').replace('+', 'plus')}"] = ("BOOLEAN", {"default": False})
        
        return {
            "required": {
                "mode": (["sequential", "random", "ping_pong"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset": ("BOOLEAN", {"default": False}),
            },
            "optional": skip_inputs
        }

    def loop_scheduler(self, mode, seed, reset=False, **kwargs):
        """
        Advanced scheduler looping with automatic state management
        """
        import threading
        import time
        
        # Parse skip list from boolean inputs
        skip_list = []
        for scheduler in WANVIDEO_SCHEDULERS:
            skip_key = f"skip_{scheduler.replace('/', '_').replace('+', 'plus')}"
            if kwargs.get(skip_key, False):
                skip_list.append(scheduler)
        
        # Filter schedulers
        available_schedulers = [s for s in WANVIDEO_SCHEDULERS if s not in skip_list]
        total_combinations = len(available_schedulers)
        
        if not available_schedulers:
            available_schedulers = WANVIDEO_SCHEDULERS
        
        # Reset counter if requested
        if reset:
            WanVideoSchedulerLoop._global_counters[mode] = 0
            print(f"WanVideo Scheduler Loop: {mode} counter reset to 0")
        
        # Create a unique execution identifier (timestamp + thread + mode)
        current_execution_id = f"{time.time()}_{threading.current_thread().ident}_{mode}"
        
        # Only increment if this is a new execution
        if WanVideoSchedulerLoop._last_execution_ids[mode] != current_execution_id:
            WanVideoSchedulerLoop._last_execution_ids[mode] = current_execution_id
            # Don't increment on first call
            if WanVideoSchedulerLoop._global_counters[mode] > 0 or hasattr(self, f'_first_call_done_{mode}'):
                WanVideoSchedulerLoop._global_counters[mode] += 1
            else:
                setattr(self, f'_first_call_done_{mode}', True)
        
        step = WanVideoSchedulerLoop._global_counters[mode]
        
        if mode == "sequential":
            # Sequential loop through schedulers (cycles back to first when complete)
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

        current_combination = f"Scheduler: {selected_scheduler}"
        # Log current selection for debugging
        print(f"WanVideo Scheduler Loop: Selected '{selected_scheduler}' (index: {index}, step: {step}, mode: {mode}) [Global: {WanVideoSchedulerLoop._global_counters[mode]}]")
        
        return (selected_scheduler, selected_scheduler, index, total_combinations, current_combination)

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

class FloatRangeLoop:
    """
    A node for looping through combinations of cfg and shift float values
    """
    
    # Global counter for sequential mode
    _global_counter = 0
    _last_execution_id = None
    
    RETURN_TYPES = ("FLOAT", "FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("cfg", "shift", "current_index", "total_combinations", "current_combination")
    FUNCTION = "loop_floats"
    CATEGORY = "WanVideo/FloatRange"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "cfg_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "cfg_end": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "cfg_step": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "shift_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "shift_end": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "shift_step": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset": ("BOOLEAN", {"default": False}),
            }
        }

    def loop_floats(self, cfg_start, cfg_end, cfg_step, shift_start, shift_end, shift_step, seed, reset=False):
        """
        Loop through combinations of cfg and shift values sequentially
        """
        import threading
        import time
        
        # Generate cfg values with proper floating point handling
        cfg_values = []
        current_cfg = cfg_start
        while current_cfg <= cfg_end + 1e-10:  # Add small epsilon for floating point comparison
            cfg_values.append(round(current_cfg, 2))
            current_cfg = round(current_cfg + cfg_step, 2)  # Round to avoid floating point drift
        
        # Generate shift values with proper floating point handling
        shift_values = []
        current_shift = shift_start
        while current_shift <= shift_end + 1e-10:  # Add small epsilon for floating point comparison
            shift_values.append(round(current_shift, 2))
            current_shift = round(current_shift + shift_step, 2)  # Round to avoid floating point drift
        
        # Calculate total combinations
        total_combinations = len(cfg_values) * len(shift_values)
        
        if total_combinations == 0:
            return (cfg_start, shift_start, 0, 0)
        
        # Reset counter if requested
        if reset:
            FloatRangeLoop._global_counter = 0
            print(f"FloatRange Loop: counter reset to 0")
        
        # Create a unique execution identifier (timestamp + thread)
        current_execution_id = f"{time.time()}_{threading.current_thread().ident}"
        
        # Only increment if this is a new execution
        if FloatRangeLoop._last_execution_id != current_execution_id:
            FloatRangeLoop._last_execution_id = current_execution_id
            # Don't increment on first call
            if FloatRangeLoop._global_counter > 0 or hasattr(self, '_first_call_done'):
                FloatRangeLoop._global_counter += 1
            else:
                setattr(self, '_first_call_done', True)
        
        step = FloatRangeLoop._global_counter
        
        # Sequential loop through combinations (cycles back to first when complete)
        index = step % total_combinations
        
        # Calculate cfg and shift indices from combined index
        cfg_index = index // len(shift_values)
        shift_index = index % len(shift_values)
        
        selected_cfg = cfg_values[cfg_index]
        selected_shift = shift_values[shift_index]

        current_combination = f"CFG {selected_cfg:.2f}, Shift {selected_shift:.2f}"
        
        # Log current selection for debugging
        print(f"FloatRange Loop: Selected cfg={selected_cfg}, shift={selected_shift} (index: {index}, step: {step}) [Global: {FloatRangeLoop._global_counter}]")
        print(f"  Available cfg values: {cfg_values}")
        print(f"  Available shift values: {shift_values}")
        print(f"  Total combinations: {total_combinations}")
        
        return (selected_cfg, selected_shift, index, total_combinations, current_combination)

class ParametersRangeLoop:
    """
    A node for looping through combinations of cfg, shift, and steps values
    """
    
    # Global counter for sequential mode
    _global_counter = 0
    _last_execution_id = None
    
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("steps", "cfg", "shift" , "current_index", "total_combinations", "current_combination")
    FUNCTION = "loop_parameters"
    CATEGORY = "WanVideo/ParametersRange"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps_start": ("INT", {"default": 20, "min": 1, "max": 1000}),
                "steps_end": ("INT", {"default": 50, "min": 1, "max": 1000}),
                "steps_interval": ("INT", {"default": 5, "min": 1, "max": 100}),
                "cfg_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "cfg_end": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "cfg_interval": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "shift_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "shift_end": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "shift_interval": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 5.0, "step": 0.1}),
                
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset": ("BOOLEAN", {"default": False}),
            }
        }

    def loop_parameters(self, cfg_start, cfg_end, cfg_interval, shift_start, shift_end, shift_interval, 
                       steps_start, steps_end, steps_interval, seed=0, reset=False):
        """
        Loop through combinations of cfg, shift, and steps values sequentially
        """
        import threading
        import time
        
        # Error prevention: Check if start values are smaller than end values
        warnings = []
        if cfg_start > cfg_end:
            warnings.append(f"Warning: cfg_start ({cfg_start}) is greater than cfg_end ({cfg_end})")
        if shift_start > shift_end:
            warnings.append(f"Warning: shift_start ({shift_start}) is greater than shift_end ({shift_end})")
        if steps_start > steps_end:
            warnings.append(f"Warning: steps_start ({steps_start}) is greater than steps_end ({steps_end})")
        
        # Print warnings if any
        for warning in warnings:
            print(warning)
        
        # Generate cfg values with proper floating point handling
        cfg_values = []
        current_cfg = cfg_start
        if cfg_start <= cfg_end:
            while current_cfg <= cfg_end + 1e-10:  # Add small epsilon for floating point comparison
                cfg_values.append(round(current_cfg, 2))
                current_cfg = round(current_cfg + cfg_interval, 2)  # Round to avoid floating point drift
        else:
            # If start > end, use only start value
            cfg_values = [cfg_start]
        
        # Generate shift values with proper floating point handling
        shift_values = []
        current_shift = shift_start
        if shift_start <= shift_end:
            while current_shift <= shift_end + 1e-10:  # Add small epsilon for floating point comparison
                shift_values.append(round(current_shift, 2))
                current_shift = round(current_shift + shift_interval, 2)  # Round to avoid floating point drift
        else:
            # If start > end, use only start value
            shift_values = [shift_start]
        
        # Generate steps values (always integers)
        steps_values = []
        if steps_start <= steps_end:
            current_steps = steps_start
            while current_steps <= steps_end:
                steps_values.append(current_steps)
                current_steps += steps_interval
        else:
            # If start > end, use only start value
            steps_values = [steps_start]
        
        # Calculate total combinations
        total_combinations = len(cfg_values) * len(shift_values) * len(steps_values)
        
        if total_combinations == 0:
            return (cfg_start, shift_start, steps_start, 0, 0, 0)
        
        # Reset counter if requested
        if reset:
            ParametersRangeLoop._global_counter = 0
            print(f"Parameters Range Loop: counter reset to 0")
        
        # Create a unique execution identifier (timestamp + thread)
        current_execution_id = f"{time.time()}_{threading.current_thread().ident}"
        
        # Only increment if this is a new execution
        if ParametersRangeLoop._last_execution_id != current_execution_id:
            ParametersRangeLoop._last_execution_id = current_execution_id
            # Don't increment on first call
            if ParametersRangeLoop._global_counter > 0 or hasattr(self, '_first_call_done'):
                ParametersRangeLoop._global_counter += 1
            else:
                setattr(self, '_first_call_done', True)
        
        step = ParametersRangeLoop._global_counter
        
        # Sequential loop through combinations (cycles back to first when complete)
        index = step % total_combinations
        
        # Calculate cfg, shift, and steps indices from combined index
        steps_index = index // (len(cfg_values) * len(shift_values))
        remaining = index % (len(cfg_values) * len(shift_values))
        cfg_index = remaining // len(shift_values)
        shift_index = remaining % len(shift_values)
        
        selected_cfg = cfg_values[cfg_index]
        selected_shift = shift_values[shift_index]
        selected_steps = steps_values[steps_index]

        current_combination = f"{selected_steps} steps, CFG {selected_cfg:.2f}, Shift {selected_shift:.2f}"
        
        # Log current selection for debugging
        print(f"Parameters Range Loop: Selected steps={selected_steps}, cfg={selected_cfg}, shift={selected_shift} (index: {index}, step: {step}) [Global: {ParametersRangeLoop._global_counter}]")
        print(f"  Available cfg values: {cfg_values}")
        print(f"  Available shift values: {shift_values}")
        print(f"  Available steps values: {steps_values}")
        print(f"  Total combinations: {total_combinations}")
        
        return (selected_steps, selected_cfg, selected_shift, index, total_combinations, current_combination)

class WanVideoAllParametersLoop:
    """
    A comprehensive node that combines scheduler looping with parameter range looping
    Loops through combinations of schedulers, cfg, shift, and steps values
    """
    
    # Global counters for different modes
    _global_counters = {"sequential": 0, "ping_pong": 0, "random": 0}
    _last_execution_ids = {"sequential": None, "ping_pong": None, "random": None}
    
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", WANVIDEO_SCHEDULERS, "INT", "INT", "STRING")
    RETURN_NAMES = ("steps", "cfg", "shift", "scheduler","current_index", "total_combinations", "current_combination")
    FUNCTION = "loop_all_parameters"
    CATEGORY = "WanVideo/AllParameters"

    @classmethod
    def INPUT_TYPES(cls):
        # Generate individual skip options for each scheduler
        skip_inputs = {}
        for scheduler in WANVIDEO_SCHEDULERS:
            skip_inputs[f"skip_{scheduler.replace('/', '_').replace('+', 'plus')}"] = ("BOOLEAN", {"default": False})
        
        base_inputs = {
            "required": {
                "mode": (["sequential", "random", "ping_pong"],),
                "cfg_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "cfg_end": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "cfg_interval": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "shift_start": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "shift_end": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "shift_interval": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 5.0, "step": 0.1}),
                "steps_start": ("INT", {"default": 20, "min": 1, "max": 1000}),
                "steps_end": ("INT", {"default": 50, "min": 1, "max": 1000}),
                "steps_interval": ("INT", {"default": 10, "min": 1, "max": 100}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset": ("BOOLEAN", {"default": False}),
            },
            "optional": skip_inputs
        }
        
        return base_inputs

    def loop_all_parameters(self, mode, cfg_start, cfg_end, cfg_interval, shift_start, shift_end, shift_interval,
                           steps_start, steps_end, steps_interval, seed=0, reset=False, **kwargs):
        """
        Advanced looping combining scheduler selection with parameter ranges
        """
        import threading
        import time
        
        # Error prevention: Check if start values are smaller than end values
        warnings = []
        if cfg_start > cfg_end:
            warnings.append(f"Warning: cfg_start ({cfg_start}) is greater than cfg_end ({cfg_end})")
        if shift_start > shift_end:
            warnings.append(f"Warning: shift_start ({shift_start}) is greater than shift_end ({shift_end})")
        if steps_start > steps_end:
            warnings.append(f"Warning: steps_start ({steps_start}) is greater than steps_end ({steps_end})")
        
        # Print warnings if any
        for warning in warnings:
            print(warning)
        
        # Parse skip list from boolean inputs for schedulers
        skip_list = []
        for scheduler in WANVIDEO_SCHEDULERS:
            skip_key = f"skip_{scheduler.replace('/', '_').replace('+', 'plus')}"
            if kwargs.get(skip_key, False):
                skip_list.append(scheduler)
        
        # Filter schedulers
        available_schedulers = [s for s in WANVIDEO_SCHEDULERS if s not in skip_list]
        if not available_schedulers:
            available_schedulers = WANVIDEO_SCHEDULERS
        
        # Generate cfg values with proper floating point handling
        cfg_values = []
        current_cfg = cfg_start
        if cfg_start <= cfg_end:
            while current_cfg <= cfg_end + 1e-10:  # Add small epsilon for floating point comparison
                cfg_values.append(round(current_cfg, 2))
                current_cfg = round(current_cfg + cfg_interval, 2)  # Round to avoid floating point drift
        else:
            # If start > end, use only start value
            cfg_values = [cfg_start]
        
        # Generate shift values with proper floating point handling
        shift_values = []
        current_shift = shift_start
        if shift_start <= shift_end:
            while current_shift <= shift_end + 1e-10:  # Add small epsilon for floating point comparison
                shift_values.append(round(current_shift, 2))
                current_shift = round(current_shift + shift_interval, 2)  # Round to avoid floating point drift
        else:
            # If start > end, use only start value
            shift_values = [shift_start]
        
        # Generate steps values (always integers)
        steps_values = []
        if steps_start <= steps_end:
            current_steps = steps_start
            while current_steps <= steps_end:
                steps_values.append(current_steps)
                current_steps += steps_interval
        else:
            # If start > end, use only start value
            steps_values = [steps_start]
        
        # Calculate total combinations
        total_combinations = len(available_schedulers) * len(cfg_values) * len(shift_values) * len(steps_values)
        
        if total_combinations == 0:
            return (available_schedulers[0] if available_schedulers else WANVIDEO_SCHEDULERS[0], 
                    available_schedulers[0] if available_schedulers else WANVIDEO_SCHEDULERS[0], 
                    cfg_start, shift_start, steps_start, 0, 0, 0)
        
        # Reset counter if requested
        if reset:
            WanVideoAllParametersLoop._global_counters[mode] = 0
            print(f"WanVideo All Parameters Loop: {mode} counter reset to 0")
        
        # Create a unique execution identifier (timestamp + thread + mode)
        current_execution_id = f"{time.time()}_{threading.current_thread().ident}_{mode}"
        
        # Only increment if this is a new execution
        if WanVideoAllParametersLoop._last_execution_ids[mode] != current_execution_id:
            WanVideoAllParametersLoop._last_execution_ids[mode] = current_execution_id
            # Don't increment on first call
            if WanVideoAllParametersLoop._global_counters[mode] > 0 or hasattr(self, f'_first_call_done_{mode}'):
                WanVideoAllParametersLoop._global_counters[mode] += 1
            else:
                setattr(self, f'_first_call_done_{mode}', True)
        
        step = WanVideoAllParametersLoop._global_counters[mode]
        
        if mode == "sequential":
            # Sequential loop through all combinations
            index = step % total_combinations
            
        elif mode == "random":
            # Random selection with seed
            random.seed(seed + step)  # Different random for each step
            index = random.randint(0, total_combinations - 1)
            
        elif mode == "ping_pong":
            # Ping pong pattern: forward then backward
            cycle_length = total_combinations * 2 - 2
            if cycle_length <= 0:
                cycle_length = 1
            
            pos = step % cycle_length
            if pos < total_combinations:
                index = pos
            else:
                index = total_combinations - 2 - (pos - total_combinations)
            
            index = max(0, min(index, total_combinations - 1))
        
        else:
            # Fallback
            index = 0
        
        # Calculate scheduler, cfg, shift, and steps indices from combined index
        steps_index = index // (len(available_schedulers) * len(cfg_values) * len(shift_values))
        remaining = index % (len(available_schedulers) * len(cfg_values) * len(shift_values))
        
        shift_index = remaining // (len(available_schedulers) * len(cfg_values))
        remaining = remaining % (len(available_schedulers) * len(cfg_values))
        
        cfg_index = remaining // len(available_schedulers)
        scheduler_index = remaining % len(available_schedulers)
        
        selected_scheduler = available_schedulers[scheduler_index]
        selected_cfg = cfg_values[cfg_index]
        selected_shift = shift_values[shift_index]
        selected_steps = steps_values[steps_index]

        current_combination = f"Scheduler: {selected_scheduler}, {selected_steps} steps, CFG {selected_cfg:.2f}, Shift {selected_shift:.2f}"
        
        # Log current selection for debugging
        print(f"WanVideo All Parameters Loop: Selected scheduler='{selected_scheduler}', cfg={selected_cfg}, shift={selected_shift}, steps={selected_steps} (index: {index}, step: {step}, mode: {mode}) [Global: {WanVideoAllParametersLoop._global_counters[mode]}]")
        print(f"  Available schedulers: {available_schedulers}")
        print(f"  Available cfg values: {cfg_values}")
        print(f"  Available shift values: {shift_values}")
        print(f"  Available steps values: {steps_values}")
        print(f"  Total combinations: {total_combinations}")
        
        return (selected_cfg, selected_shift, selected_steps, selected_scheduler, index, total_combinations, current_combination)


# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    # "WanVideoSchedulerSelector": WanVideoSchedulerSelector,
    "WanVideoSchedulerLoop": WanVideoSchedulerLoop,
    "WanVideoSchedulerInfo": WanVideoSchedulerInfo,
    "FloatRangeLoop": FloatRangeLoop,
    "ParametersRangeLoop": ParametersRangeLoop,
    "WanVideoAllParametersLoop": WanVideoAllParametersLoop
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # "WanVideoSchedulerSelector": "WanVideo Scheduler Selector",
    "WanVideoSchedulerLoop": "WanVideo Scheduler Loop",
    "WanVideoSchedulerInfo": "WanVideo Scheduler Info",
    "FloatRangeLoop": "Float Range Loop",
    "ParametersRangeLoop": "Parameters Range Loop",
    "WanVideoAllParametersLoop": "WanVideo All Parameters Loop"
}

# Export for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]