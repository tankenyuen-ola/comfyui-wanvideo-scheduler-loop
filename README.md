# ComfyUI WanVideo Scheduler Loop

A comprehensive ComfyUI custom node collection for automated testing and optimization of WanVideo generation parameters. This extension provides intelligent looping capabilities for schedulers, CFG values, shift parameters, and sampling steps - perfect for finding optimal parameter combinations through batch processing.

## 🙏 Special Thanks

Special thanks to [ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) by **kijai** for providing the excellent WanVideo integration that makes this scheduler loop extension possible. This project builds upon their fantastic work to enhance the parameter testing workflow.

## 📋 Prerequisites

- **ComfyUI** installed and running
- **[ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)** - **HIGHLY RECOMMENDED**
  - Without WanVideoWrapper, the extension will use a fallback scheduler list which may be outdated
  - With WanVideoWrapper installed, you get the latest and most accurate scheduler list automatically

## 🚀 Installation

1. Clone this repository into your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/tankenyuen-ola/comfyui-wanvideo-schedulerloop.git
```

2. Restart ComfyUI

3. The nodes will appear under the **WanVideo/** category in your node browser

## 💡 Why Use This Extension?

Finding the optimal combination of parameters for WanVideo generation can be extremely tedious when done manually. Instead of:
- Manually changing scheduler → Generate → Check result
- Manually adjusting CFG → Generate → Check result  
- Manually modifying shift values → Generate → Check result
- Repeating hundreds of times...

This extension automates the entire process by:
- **Automatically cycling through parameter combinations**
- **Supporting batch processing for systematic testing**
- **Providing multiple looping modes (sequential, random, ping-pong)**
- **Offering granular control over parameter ranges**
- **Enabling skip functionality for unwanted schedulers**
- **Generating descriptive tags for easy result organization**

## 🔧 Available Nodes

### 1. WanVideo Scheduler Loop
**Category:** `WanVideo/Schedulers`

Automatically cycles through different WanVideo schedulers with various looping modes.

#### Inputs:
- **mode** (required): 
  - `sequential`: Goes through schedulers in order (1→2→3→1...)
  - `random`: Randomly selects schedulers based on seed
  - `ping_pong`: Forward then backward (1→2→3→2→1→2...)
- **seed** (required): Random seed for random mode (0 to max int)
- **reset** (required): Boolean to reset the loop counter to start over
- **skip_[scheduler_name]** (optional): Individual boolean toggles to skip specific schedulers

#### Outputs:
- **scheduler**: The selected scheduler name (connects to WanVideo nodes)
- **scheduler_name**: String representation of the scheduler name
- **current_index**: Current position in the scheduler list (0-based)
- **total_combinations**: Total number of available schedulers (excluding skipped ones)
- **current_combination**: Descriptive string of current scheduler selection (e.g., "Scheduler: dpm++")

#### Usage Example:
1. Set mode to "sequential" for systematic testing
2. Connect **scheduler** output to your WanVideo sampler node
3. Connect **current_combination** output to filename prefix or save metadata for easy identification
4. Enable batch processing in ComfyUI
5. Set batch count to **total_combinations** value
6. Run to test all schedulers automatically

---

### 2. WanVideo Scheduler Info
**Category:** `WanVideo/Schedulers`

Displays information about available WanVideo schedulers.

#### Inputs:
- **format** (optional): Output format
  - `list`: One scheduler per line
  - `comma_separated`: All schedulers in one comma-separated line
  - `numbered`: Numbered list format

#### Outputs:
- **scheduler_list**: Formatted string of all available schedulers
- **total_count**: Total number of available schedulers

#### Usage Example:
Connect to a "Show Text" node to see what schedulers are available on your system.

---

### 3. Float Range Loop
**Category:** `WanVideo/FloatRange`

Cycles through combinations of CFG and shift parameter ranges.

#### Inputs:
- **cfg_start/cfg_end/cfg_step**: CFG value range (e.g., 1.0 to 8.0, step 1.0)
- **shift_start/shift_end/shift_step**: Shift value range (e.g., 1.0 to 3.0, step 0.5)
- **seed**: Random seed (currently used for future random modes)
- **reset**: Boolean to reset the loop counter

#### Outputs:
- **cfg**: Current CFG value
- **shift**: Current shift value  
- **current_index**: Current combination index
- **total_combinations**: Total number of CFG×shift combinations
- **current_combination**: Descriptive string of current parameters (e.g., "CFG 4.0, Shift 1.5")

#### Usage Example:
Test CFG values from 1.0 to 8.0 (step 1.0) and shift from 1.0 to 3.0 (step 0.5):
- This creates 8 CFG values × 5 shift values = 40 total combinations
- Connect **current_combination** to your save node's filename prefix
- Set batch count to 40 and run to test all combinations
- Each saved file will be automatically tagged with its parameter combination

---

### 4. Parameters Range Loop  
**Category:** `WanVideo/ParametersRange`

Cycles through combinations of steps, CFG, and shift parameters.

#### Inputs:
- **steps_start/steps_end/steps_interval**: Sampling steps range (e.g., 20 to 50, interval 5)
- **cfg_start/cfg_end/cfg_interval**: CFG range (e.g., 1.0 to 8.0, interval 1.0)
- **shift_start/shift_end/shift_interval**: Shift range (e.g., 1.0 to 3.0, interval 0.5)
- **seed**: Random seed for future use
- **reset**: Boolean to reset the loop counter

#### Outputs:
- **steps**: Current sampling steps value
- **cfg**: Current CFG value
- **shift**: Current shift value
- **current_index**: Current combination index  
- **total_combinations**: Total number of steps×CFG×shift combinations
- **current_combination**: Descriptive string of current parameters (e.g., "30 steps, CFG 4.0, Shift 1.5")

#### Usage Example:
Test comprehensive parameter combinations:
- Steps: 20, 30, 40, 50 (4 values)
- CFG: 1.0, 2.0, 3.0, 4.0 (4 values)  
- Shift: 1.0, 1.5, 2.0 (3 values)
- Total: 4×4×3 = 48 combinations
- Use **current_combination** for organized file naming and easy result tracking

---

### 5. WanVideo All Parameters Loop
**Category:** `WanVideo/AllParameters`

The ultimate testing node - combines scheduler selection with parameter ranges for comprehensive optimization.

#### Inputs:
- **mode**: Looping mode (sequential/random/ping_pong)
- **cfg_start/cfg_end/cfg_interval**: CFG parameter range
- **shift_start/shift_end/shift_interval**: Shift parameter range  
- **steps_start/steps_end/steps_interval**: Sampling steps range
- **seed**: Random seed for random mode
- **reset**: Boolean to reset loop counter
- **skip_[scheduler_name]**: Individual scheduler skip toggles

#### Outputs:
- **steps**: Current sampling steps
- **cfg**: Current CFG value
- **shift**: Current shift value
- **scheduler**: Current scheduler name
- **current_index**: Current combination index
- **total_combinations**: Total number of all possible combinations
- **current_combination**: Comprehensive descriptive string (e.g., "Scheduler: dpm++, 30 steps, CFG 4.0, Shift 1.5")

#### Usage Example:
Ultimate parameter optimization setup:
1. Set parameter ranges for steps, CFG, and shift
2. Skip unwanted schedulers using the boolean toggles
3. Choose "sequential" mode for systematic testing
4. Connect outputs to corresponding WanVideo node inputs
5. Connect **current_combination** to save node for automatic file tagging
6. Set batch count to **total_combinations** value
7. Run batch to test every possible combination automatically

**Example calculation:**
- 3 schedulers (after skipping unwanted ones)
- 4 CFG values (1.0 to 4.0, step 1.0)
- 3 shift values (1.0 to 2.0, step 0.5)  
- 5 steps values (20 to 60, step 10)
- Total: 3×4×3×5 = **180 combinations**

## 🎯 Typical Workflow

### For Scheduler Testing:
1. Add **WanVideo Scheduler Loop** node
2. Set mode to "sequential"
3. Skip any problematic schedulers using the boolean inputs
4. Connect **scheduler** output to your WanVideo sampler
5. Connect **current_combination** to save node filename prefix
6. Note the **total_combinations** value
7. Set ComfyUI batch count to this number
8. Queue batch and let it run through all schedulers
9. Each output file will be automatically named with the scheduler used

### For Parameter Optimization:
1. Add **WanVideo All Parameters Loop** node
2. Set your desired parameter ranges:
   - **Steps:** 20-50, interval 10 (4 values)
   - **CFG:** 1.0-8.0, interval 1.0 (8 values)  
   - **Shift:** 1.0-3.0, interval 0.5 (5 values)
3. Skip unwanted schedulers
4. Connect all outputs to corresponding WanVideo inputs
5. Connect **current_combination** to save node for descriptive filenames
6. Set batch count to **total_combinations** (160 in this example)
7. Run batch for comprehensive testing
8. Results will be saved with descriptive names like "Scheduler_dpm++_30steps_CFG4.0_Shift1.5.mp4"

### For Quick Range Testing:
1. Use **Float Range Loop** for just CFG and shift testing
2. Use **Parameters Range Loop** for steps, CFG, and shift testing
3. Smaller combination counts = faster testing
4. Always connect **current_combination** for easy result identification

## 📂 Organizing Results with current_combination

The **current_combination** output is specifically designed to help you organize and identify your test results:

### File Naming Examples:
- **Scheduler Loop**: "Scheduler_dpm++"
- **Float Range Loop**: "CFG_4.0_Shift_1.5"  
- **Parameters Range Loop**: "30steps_CFG_4.0_Shift_1.5"
- **All Parameters Loop**: "Scheduler_dpm++_30steps_CFG_4.0_Shift_1.5"

### Best Practices for File Organization:
1. **Connect to filename prefix**: Use **current_combination** as a prefix to your base filename
2. **Create result folders**: Organize by test session using folder names with timestamps
3. **Use metadata**: Some save nodes support metadata - **current_combination** can be stored there too
4. **Batch comparison**: With descriptive names, you can easily compare results side-by-side
5. **Result analysis**: Sort files alphabetically to group similar parameter combinations

### Example Save Node Setup:
```
[WanVideo All Parameters Loop] → current_combination → [Text Concatenate] → "TestBatch_" + current_combination + "_" + timestamp → [Save Video]
```
This creates filenames like: `TestBatch_Scheduler_dpm++_30steps_CFG_4.0_Shift_1.5_20240102_143052.mp4`

## 🔍 Tips & Best Practices

### Understanding Loop Behavior:
- **Sequential mode**: Predictable, systematic testing - best for comprehensive evaluation
- **Random mode**: Good for sampling the parameter space when full testing isn't feasible  
- **Ping-pong mode**: Useful for finding optimal ranges by testing boundaries first

### Optimizing Test Runs:
- Start with wide parameter ranges and fewer steps to identify promising areas
- Use scheduler skipping to focus on schedulers that work well with your content
- Monitor the console output - each node logs its current selection for debugging
- Always use **current_combination** for result organization - it saves hours of manual sorting

### Console Output Example:
```
WanVideo All Parameters Loop: Selected scheduler='dpm++', cfg=4.0, shift=1.5, steps=30 (index: 45, step: 45, mode: sequential) [Global: 45]
  Available schedulers: ['unipc', 'dpm++', 'euler', 'lcm']
  Available cfg values: [1.0, 2.0, 3.0, 4.0, 5.0]
  Available shift values: [1.0, 1.5, 2.0]  
  Available steps values: [20, 30, 40]
  Total combinations: 60
```

### Result Analysis Workflow:
1. Run batch with **current_combination** connected to filename
2. Review generated files - names indicate exact parameters used
3. Identify best-performing combinations from filenames
4. Use those parameters for fine-tuning with smaller ranges
5. Create focused test batches around optimal settings

### Error Prevention:
- The nodes automatically handle cases where start > end values
- Warnings are displayed in console for invalid ranges
- Fallback values are used when necessary
- **current_combination** always provides valid output even with edge cases

## 🐛 Troubleshooting

**"Warning: ComfyUI-WanVideoWrapper not found"**
- Install [ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper) for best results
- The extension will work with fallback schedulers, but may miss newer schedulers

**"No schedulers available"**  
- Ensure WanVideoWrapper is properly installed
- Check that the scheduler list isn't completely filtered by skip options

**Loop not progressing**
- Check that you're running in batch mode, not single generation
- Verify the batch count matches or exceeds the total_combinations value
- Use the reset option if the loop seems stuck

**Floating point precision issues**
- The nodes automatically handle floating point rounding
- Check console output to verify the actual values being generated
- **current_combination** shows the exact values being used

**File naming issues**
- Ensure **current_combination** is properly connected to your save node
- Some characters in scheduler names (like "/", "+") are automatically handled
- Check your save node's filename formatting requirements

## 📝 License

This project is open source. Please check the license file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Happy parameter optimization! 🚀**