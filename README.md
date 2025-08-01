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
git clone https://github.com/yourusername/comfyui-wanvideo-schedulerloop.git
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

#### Usage Example:
1. Set mode to "sequential" for systematic testing
2. Connect **scheduler** output to your WanVideo sampler node
3. Enable batch processing in ComfyUI
4. Set batch count to **total_combinations** value
5. Run to test all schedulers automatically

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

#### Usage Example:
Test CFG values from 1.0 to 8.0 (step 1.0) and shift from 1.0 to 3.0 (step 0.5):
- This creates 8 CFG values × 5 shift values = 40 total combinations
- Set batch count to 40 and run to test all combinations

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

#### Usage Example:
Test comprehensive parameter combinations:
- Steps: 20, 30, 40, 50 (4 values)
- CFG: 1.0, 2.0, 3.0, 4.0 (4 values)  
- Shift: 1.0, 1.5, 2.0 (3 values)
- Total: 4×4×3 = 48 combinations

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

#### Usage Example:
Ultimate parameter optimization setup:
1. Set parameter ranges for steps, CFG, and shift
2. Skip unwanted schedulers using the boolean toggles
3. Choose "sequential" mode for systematic testing
4. Connect outputs to corresponding WanVideo node inputs
5. Set batch count to **total_combinations** value
6. Run batch to test every possible combination automatically

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
5. Note the **total_combinations** value
6. Set ComfyUI batch count to this number
7. Queue batch and let it run through all schedulers

### For Parameter Optimization:
1. Add **WanVideo All Parameters Loop** node
2. Set your desired parameter ranges:
   - **Steps:** 20-50, interval 10 (4 values)
   - **CFG:** 1.0-8.0, interval 1.0 (8 values)  
   - **Shift:** 1.0-3.0, interval 0.5 (5 values)
3. Skip unwanted schedulers
4. Connect all outputs to corresponding WanVideo inputs
5. Set batch count to **total_combinations** (160 in this example)
6. Run batch for comprehensive testing

### For Quick Range Testing:
1. Use **Float Range Loop** for just CFG and shift testing
2. Use **Parameters Range Loop** for steps, CFG, and shift testing
3. Smaller combination counts = faster testing

## 🔍 Tips & Best Practices

### Understanding Loop Behavior:
- **Sequential mode**: Predictable, systematic testing - best for comprehensive evaluation
- **Random mode**: Good for sampling the parameter space when full testing isn't feasible  
- **Ping-pong mode**: Useful for finding optimal ranges by testing boundaries first

### Optimizing Test Runs:
- Start with wide parameter ranges and fewer steps to identify promising areas
- Use scheduler skipping to focus on schedulers that work well with your content
- Monitor the console output - each node logs its current selection for debugging

### Console Output Example:
```
WanVideo All Parameters Loop: Selected scheduler='dpm++', cfg=4.0, shift=1.5, steps=30 (index: 45, step: 45, mode: sequential) [Global: 45]
  Available schedulers: ['unipc', 'dpm++', 'euler', 'lcm']
  Available cfg values: [1.0, 2.0, 3.0, 4.0, 5.0]
  Available shift values: [1.0, 1.5, 2.0]  
  Available steps values: [20, 30, 40]
  Total combinations: 60
```

### Error Prevention:
- The nodes automatically handle cases where start > end values
- Warnings are displayed in console for invalid ranges
- Fallback values are used when necessary

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

## 📝 License

This project is open source. Please check the license file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Happy parameter optimization! 🚀**