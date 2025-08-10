**The Power of Planning Mode**

In the wind turbine example above, when a user asks: *"Analyze turbine performance over the past 2 weeks and identify which turbines need maintenance"*, the orchestrator creates a complete execution plan that shows exactly how it will approach this complex task.

.. dropdown:: 🎯 **Interactive Execution Plan Editor** - See the actual plan generated for the wind turbine example
   :open:
   :color: primary
   :icon: tools

   The execution plan below shows the exact 6-step approach the orchestrator designed for the wind turbine analysis task. This is the real plan that gets generated and can be reviewed/modified before execution:

   .. raw:: html

      <div id="plan-demo-container" style="margin: 20px 0; min-height: 300px;">
          <div style="text-align: center; color: #666; padding: 20px; background: #f8f9fa; border: 1px solid #e0e5e5; border-radius: 6px;">
              <div style="font-size: 16px; margin-bottom: 8px;">🔄 Loading Interactive Execution Plan Editor...</div>
              <div style="font-size: 13px;">This may take a moment to initialize...</div>
          </div>
      </div>

      <script>
      // Ensure the ExecutionPlanViewer is loaded before initializing
      function initializeExecutionPlanDemo() {
          if (typeof ExecutionPlanViewer === 'undefined') {
              console.warn('ExecutionPlanViewer not yet loaded, retrying in 500ms...');
              setTimeout(initializeExecutionPlanDemo, 500);
              return;
          }

          // Real execution plan data from the wind turbine example
          const windTurbinePlan = {
              "__metadata__": {
                  "version": "1.0",
                  "original_task": "Analyze wind turbine performance over the past 2 weeks, identify turbines operating below industry standards, rank them by efficiency, and determine which require immediate maintenance attention",
                  "created_at": "2025-08-09T23:33:48.402473",
                  "serialization_type": "pending_execution_plan"
              },
              "steps": [
                  {
                      "context_key": "past_two_weeks_timerange",
                      "capability": "time_range_parsing",
                      "task_objective": "Parse the relative time reference 'past 2 weeks' to create start and end datetime objects for data retrieval",
                      "success_criteria": "Time range converted to datetime objects spanning exactly 2 weeks from current time",
                      "expected_output": "TIME_RANGE",
                      "parameters": null,
                      "inputs": []
                  },
                  {
                      "context_key": "historical_turbine_data", 
                      "capability": "turbine_data_archiver",
                      "task_objective": "Retrieve historical turbine performance data for all turbines over the past 2 weeks to analyze efficiency and identify maintenance needs",
                      "success_criteria": "Complete turbine performance data retrieved with timestamps, turbine IDs, and power outputs for the specified time period",
                      "expected_output": "TURBINE_DATA",
                      "parameters": null,
                      "inputs": [{"TIME_RANGE": "past_two_weeks_timerange"}]
                  },
                  {
                      "context_key": "historical_weather_data",
                      "capability": "weather_data_retrieval", 
                      "task_objective": "Retrieve historical weather data including wind speeds for the past 2 weeks to correlate with turbine performance analysis",
                      "success_criteria": "Weather data retrieved with timestamps and wind speeds for accurate performance correlation",
                      "expected_output": "WEATHER_DATA",
                      "parameters": null,
                      "inputs": [{"TIME_RANGE": "past_two_weeks_timerange"}]
                  },
                  {
                      "context_key": "industry_standards",
                      "capability": "knowledge_retrieval",
                      "task_objective": "Retrieve industry performance standards, efficiency thresholds, and maintenance criteria for wind turbines to benchmark against current performance",
                      "success_criteria": "Industry standards retrieved including efficiency thresholds, capacity factor benchmarks, and maintenance trigger criteria",
                      "expected_output": "TURBINE_KNOWLEDGE",
                      "parameters": null,
                      "inputs": []
                  },
                  {
                      "context_key": "performance_analysis",
                      "capability": "turbine_analysis",
                      "task_objective": "Analyze turbine performance against industry standards, identify underperforming turbines, rank by efficiency, and determine maintenance priorities",
                      "success_criteria": "Complete performance analysis with efficiency rankings, identification of below-standard turbines, and maintenance recommendations", 
                      "expected_output": "ANALYSIS_RESULTS",
                      "parameters": null,
                      "inputs": [
                          {"TURBINE_DATA": "historical_turbine_data"},
                          {"WEATHER_DATA": "historical_weather_data"},
                          {"TURBINE_KNOWLEDGE": "industry_standards"}
                      ]
                  },
                  {
                      "context_key": "final_response",
                      "capability": "respond",
                      "task_objective": "Present comprehensive turbine performance analysis with efficiency rankings, below-standard turbines identified, and maintenance priority recommendations",
                      "success_criteria": "User receives structured analysis with turbine rankings, performance against industry standards, and clear maintenance action items",
                      "expected_output": null,
                      "parameters": null,
                      "inputs": [
                          {"ANALYSIS_RESULTS": "performance_analysis"},
                          {"TURBINE_KNOWLEDGE": "industry_standards"}
                      ]
                  }
              ]
          };

          // Mock capabilities for demonstration
          const demoCapabilities = [
              {
                  "name": "time_range_parsing",
                  "description": "Parse relative time references into datetime objects",
                  "provides": ["TIME_RANGE"],
                  "requires": []
              },
              {
                  "name": "turbine_data_archiver", 
                  "description": "Retrieve historical turbine performance data",
                  "provides": ["TURBINE_DATA"],
                  "requires": ["TIME_RANGE"]
              },
              {
                  "name": "weather_data_retrieval",
                  "description": "Retrieve weather data for wind analysis", 
                  "provides": ["WEATHER_DATA"],
                  "requires": ["TIME_RANGE"]
              },
              {
                  "name": "knowledge_retrieval",
                  "description": "Retrieve technical standards and performance benchmarks",
                  "provides": ["TURBINE_KNOWLEDGE"], 
                  "requires": []
              },
              {
                  "name": "turbine_analysis",
                  "description": "Analyze turbine performance against industry benchmarks",
                  "provides": ["ANALYSIS_RESULTS"],
                  "requires": ["TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE"]
              },
              {
                  "name": "respond",
                  "description": "Generate final response to user",
                  "provides": [],
                  "requires": []
              }
          ];

          try {
              // Initialize and render the execution plan viewer in documentation mode
              const viewer = new ExecutionPlanViewer();
              viewer.init({
                  capabilities: demoCapabilities,
                  contextTypes: ["TIME_RANGE", "TURBINE_DATA", "WEATHER_DATA", "TURBINE_KNOWLEDGE", "ANALYSIS_RESULTS"],
                  pendingPlan: windTurbinePlan,
                  callbacks: {
                      // Documentation mode - no actual functionality, just display
                      onStepEdit: (index) => console.log('Demo: Would edit step', index),
                      onStepDelete: (index) => console.log('Demo: Would delete step', index),
                      onPlanApprove: () => console.log('Demo: Would approve plan'),
                      onPlanReject: () => console.log('Demo: Would reject plan')
                  }
              });
              
              const container = document.getElementById('plan-demo-container');
              if (container) {
                  // Configure for embedded/inline mode (not modal)
                  viewer.render(container, { 
                      documentationMode: true,
                      modal: false  // This is key - renders inline instead of as modal overlay
                  });
                  console.log('Execution plan viewer successfully initialized');
              } else {
                  console.error('Container element not found: plan-demo-container');
              }
          } catch (error) {
              console.error('Error initializing execution plan viewer:', error);
              const container = document.getElementById('plan-demo-container');
              if (container) {
                  container.innerHTML = `
                      <div style="text-align: center; color: #d66e6e; padding: 40px;">
                          <div style="font-size: 18px; margin-bottom: 10px;">⚠️ Execution Plan Editor Failed to Load</div>
                          <div style="font-size: 14px;">Error: ${error.message}</div>
                      </div>
                  `;
              }
          }
      }

      // Initialize when DOM is ready
      if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initializeExecutionPlanDemo);
      } else {
          initializeExecutionPlanDemo();
      }
      </script>

   **Key Planning Features Demonstrated:**

   📊 **Dependency Visualization**: Notice how steps 2-3 depend on step 1's TIME_RANGE output, and step 5 requires outputs from steps 2, 3, and 4.

   🔗 **Context Flow Management**: The orchestrator ensures data flows correctly: TIME_RANGE → TURBINE_DATA + WEATHER_DATA + TURBINE_KNOWLEDGE → ANALYSIS_RESULTS → Response.

   🎯 **Task Decomposition**: A complex request is automatically broken into 6 logical, manageable steps that build upon each other.

   🛡️ **Human Oversight**: In the actual Open Web UI, this plan would require approval before execution, allowing you to review and modify the approach.

   **In the Open Web UI Interface:**

   When you use planning mode (``/planning`` command), you'll see this exact interface with additional functionality:

   - **Edit Individual Steps**: Click the ✏️ button to modify task objectives, success criteria, or dependencies
   - **Add/Remove Steps**: Insert new capabilities or remove unnecessary steps
   - **Approve/Reject**: Decide whether to execute the plan as-is or request modifications
   - **Real-time Validation**: The editor validates dependencies and highlights potential issues

   This transparency ensures you understand exactly what your agent will do before it starts, providing confidence in complex multi-step operations.

   **Production Benefits:**

   - **Auditability**: Every execution has a clear, reviewable plan
   - **Optimization**: Identify inefficient step sequences before execution
   - **Learning**: Understand how the orchestrator approaches different types of problems
   - **Control**: Modify the approach when domain expertise suggests better alternatives

**Planning Mode in Action**

Here's what the actual CLI interaction looks like when using planning mode:

.. code-block:: text

   👤 You: /planning Analyze turbine performance over the past 2 weeks and identify which turbines need maintenance

   🔄 Processing: /planning Analyze turbine performance over the past 2 weeks...
   ✅ Processed commands: ['planning']
   🔄 Extracting actionable task from conversation
   🔄 Analyzing task requirements...
   🔄 Generating execution plan...
   🔄 Requesting plan approval...
   
   ⚠️ **HUMAN APPROVAL REQUIRED** ⚠️
   
   **Planned Steps (6 total):**
   **Step 1:** Parse "past 2 weeks" timeframe → TIME_RANGE
   **Step 2:** Retrieve historical turbine data → TURBINE_DATA  
   **Step 3:** Retrieve weather data for correlation → WEATHER_DATA
   **Step 4:** Get industry performance benchmarks → TURBINE_KNOWLEDGE
   **Step 5:** Analyze performance against standards → ANALYSIS_RESULTS
   **Step 6:** Present findings and maintenance recommendations → Response
   
   **To proceed, respond with:**
   - **`yes`** to approve and execute the plan
   - **`edit`** to modify the plan in the interactive editor
   - **`no`** to cancel this operation
   
   👤 You: edit
   🔄 Opening execution plan editor...
   
   [Interactive editor opens with the plan shown above]

The execution plan editor provides unprecedented transparency into agentic system behavior, making complex multi-step operations both understandable and controllable. This is especially valuable in production environments where understanding the approach is as important as getting results.
