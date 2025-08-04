(aloha_lite) root@MACCS-HBJ2NL3:/home/hafnium/aloha-lite/robot_service# python sequential_execute.py left_arm_serving_standoff left_arm_standoff_with_beaker left_arm_standoff_yellow right_arm_standoff_yellow dispensing_yellow_to_beaker right_arm_standoff_yellow right_arm_standoff left_arm_standoff_yellow left_arm_standoff_with_beaker left_arm_serving_standoff left_arm_serving_beaker --smooth
✅ Robot initialization DISABLED by default (safer)
🎬 Using SMOOTH trajectory planning
🤖 Starting sequential execution of 11 steps
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY
======================================================================
🔧 Left arm ID: 2 (5A68011258)
🔧 Right arm ID: 3 (5A68009540)
📊 Trajectory settings:
   ⏱️  Duration: Auto
   🎚️  Max velocity: 0.300 rad/s
   📍 Waypoints: Auto-adaptive
======================================================================
✅ Initialized phosphobot joint controller
🔗 Server: http://localhost:80
🔧 Left arm ID: 2 (5A68011529)
🔧 Right arm ID: 3 (5A68009540)

⚠️  Skipping robot initialization to prevent collisions

🔄 Step 1/11: left_arm_serving_standoff

🎯 Executing configuration: left_arm_serving_standoff
==================================================
✅ Loaded configuration 'left_arm_serving_standoff' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_serving_standoff
📝 Description: Left arm serving standoff position - current position captured with preserved gripper position
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['-0.767', '0.092', '1.490', '-1.564', '-1.637', '0.555']
  ✅ left_arm: Complete configuration (all 6 joints)

🎯 Moving to: left_arm_serving_standoff
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['-0.767', '0.092', '1.490', '-1.564', '-1.637', '0.555']
📍 Current: ['-0.767', '0.092', '1.490', '-1.564', '-1.637', '0.555']
🎯 Target:  ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.600', '0.270', '-0.091', '-0.143', '0.130']
   📊 Weighted squared sum: 0.838
   📍 Calculated waypoints: 13 → 13 (range: 5-50)
🛡️  Auto-calculated duration: 3.7s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 3.7 seconds
   📍 Waypoints: 13
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 13 → Enhanced waypoints: 25
   📊 Shape: (25, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 13 → 25 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['-0.767', '0.092', '1.490', '-1.564', '-1.637', '0.555'] rad
   📊 Progress:   4% (waypoint 1/25, t=0.1s)
✅ Robot 2 joints set to: ['-0.766', '0.092', '1.490', '-1.564', '-1.637', '0.555'] rad
✅ Robot 2 joints set to: ['-0.764', '0.093', '1.489', '-1.564', '-1.636', '0.555'] rad
✅ Robot 2 joints set to: ['-0.755', '0.093', '1.489', '-1.564', '-1.636', '0.555'] rad
✅ Robot 2 joints set to: ['-0.746', '0.102', '1.487', '-1.569', '-1.633', '0.555'] rad
✅ Robot 2 joints set to: ['-0.725', '0.102', '1.487', '-1.569', '-1.633', '0.555'] rad
   📊 Progress:  24% (waypoint 6/25, t=0.9s)
✅ Robot 2 joints set to: ['-0.705', '0.120', '1.480', '-1.578', '-1.624', '0.553'] rad
✅ Robot 2 joints set to: ['-0.673', '0.120', '1.480', '-1.578', '-1.624', '0.553'] rad
✅ Robot 2 joints set to: ['-0.641', '0.149', '1.471', '-1.593', '-1.610', '0.550'] rad
✅ Robot 2 joints set to: ['-0.600', '0.149', '1.471', '-1.593', '-1.610', '0.550'] rad
✅ Robot 2 joints set to: ['-0.559', '0.186', '1.458', '-1.613', '-1.592', '0.547'] rad
   📊 Progress:  44% (waypoint 11/25, t=1.7s)
✅ Robot 2 joints set to: ['-0.513', '0.186', '1.458', '-1.613', '-1.592', '0.547'] rad
✅ Robot 2 joints set to: ['-0.467', '0.227', '1.445', '-1.635', '-1.572', '0.543'] rad
✅ Robot 2 joints set to: ['-0.421', '0.227', '1.445', '-1.635', '-1.572', '0.543'] rad
✅ Robot 2 joints set to: ['-0.375', '0.269', '1.431', '-1.657', '-1.552', '0.539'] rad
✅ Robot 2 joints set to: ['-0.334', '0.269', '1.431', '-1.657', '-1.552', '0.539'] rad
   📊 Progress:  64% (waypoint 16/25, t=2.5s)
✅ Robot 2 joints set to: ['-0.293', '0.305', '1.418', '-1.676', '-1.534', '0.535'] rad
✅ Robot 2 joints set to: ['-0.261', '0.305', '1.418', '-1.676', '-1.534', '0.535'] rad
✅ Robot 2 joints set to: ['-0.229', '0.334', '1.409', '-1.691', '-1.520', '0.533'] rad
✅ Robot 2 joints set to: ['-0.209', '0.334', '1.409', '-1.691', '-1.520', '0.533'] rad
✅ Robot 2 joints set to: ['-0.189', '0.353', '1.403', '-1.701', '-1.511', '0.531'] rad
   📊 Progress:  84% (waypoint 21/25, t=3.3s)
✅ Robot 2 joints set to: ['-0.179', '0.353', '1.403', '-1.701', '-1.511', '0.531'] rad
✅ Robot 2 joints set to: ['-0.170', '0.361', '1.400', '-1.705', '-1.507', '0.530'] rad
✅ Robot 2 joints set to: ['-0.169', '0.361', '1.400', '-1.705', '-1.507', '0.530'] rad
✅ Robot 2 joints set to: ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530'] rad
   📊 Progress: 100% (waypoint 25/25, t=3.9s)

📖 Verifying final position...
📖 Robot 2 joints: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566']
✅ Trajectory completed!
   📏 Max error: 0.0362 rad (2.07°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566']

✅ Successfully completed: left_arm_serving_standoff

⏳ Pausing 2.0s before next step...

🔄 Step 2/11: left_arm_standoff_with_beaker

🎯 Executing configuration: left_arm_standoff_with_beaker
==================================================
✅ Loaded configuration 'left_arm_standoff_with_beaker' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_standoff_with_beaker
📝 Description: Left arm standoff position with beaker - updated joints j1-j5 from current robot position, right arm stays in current position
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566']
  🔄 left_arm: Partial configuration (missing ['j6'])
  🔄 Merging with current joint positions...
  📝 j1 → 0.707 rad
  📝 j2 → 0.542 rad
  📝 j3 → 1.163 rad
  📝 j4 → -1.686 rad
  📝 j5 → -1.611 rad

🎯 Moving to: left_arm_standoff_with_beaker
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.566']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566']
📍 Current: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566']
🎯 Target:  ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.566']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.882', '0.181', '-0.245', '-0.002', '-0.092']
   📊 Weighted squared sum: 1.658
   📍 Calculated waypoints: 21 → 21 (range: 5-50)
🛡️  Auto-calculated duration: 5.5s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 5.5 seconds
   📍 Waypoints: 21
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 21 → Enhanced waypoints: 41
   📊 Shape: (41, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 21 → 41 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['-0.175', '0.361', '1.409', '-1.685', '-1.519', '0.566'] rad
   📊 Progress:   2% (waypoint 1/41, t=0.1s)
✅ Robot 2 joints set to: ['-0.174', '0.361', '1.409', '-1.685', '-1.519', '0.566'] rad
✅ Robot 2 joints set to: ['-0.174', '0.361', '1.408', '-1.685', '-1.519', '0.566'] rad
✅ Robot 2 joints set to: ['-0.171', '0.361', '1.408', '-1.685', '-1.519', '0.566'] rad
✅ Robot 2 joints set to: ['-0.167', '0.362', '1.406', '-1.685', '-1.520', '0.566'] rad
✅ Robot 2 joints set to: ['-0.159', '0.362', '1.406', '-1.685', '-1.520', '0.566'] rad
✅ Robot 2 joints set to: ['-0.151', '0.365', '1.402', '-1.685', '-1.521', '0.566'] rad
✅ Robot 2 joints set to: ['-0.138', '0.365', '1.402', '-1.685', '-1.521', '0.566'] rad
✅ Robot 2 joints set to: ['-0.124', '0.371', '1.394', '-1.685', '-1.524', '0.566'] rad
   📊 Progress:  22% (waypoint 9/41, t=1.2s)
✅ Robot 2 joints set to: ['-0.104', '0.371', '1.394', '-1.685', '-1.524', '0.566'] rad
✅ Robot 2 joints set to: ['-0.084', '0.379', '1.383', '-1.685', '-1.529', '0.566'] rad
✅ Robot 2 joints set to: ['-0.057', '0.379', '1.383', '-1.685', '-1.529', '0.566'] rad
✅ Robot 2 joints set to: ['-0.031', '0.390', '1.369', '-1.685', '-1.534', '0.566'] rad
✅ Robot 2 joints set to: ['0.001', '0.390', '1.369', '-1.685', '-1.534', '0.566'] rad
✅ Robot 2 joints set to: ['0.033', '0.403', '1.351', '-1.685', '-1.541', '0.566'] rad
✅ Robot 2 joints set to: ['0.069', '0.403', '1.351', '-1.685', '-1.541', '0.566'] rad
✅ Robot 2 joints set to: ['0.105', '0.418', '1.331', '-1.685', '-1.548', '0.566'] rad
   📊 Progress:  41% (waypoint 17/41, t=2.3s)
✅ Robot 2 joints set to: ['0.145', '0.418', '1.331', '-1.685', '-1.548', '0.566'] rad
✅ Robot 2 joints set to: ['0.184', '0.434', '1.309', '-1.685', '-1.556', '0.566'] rad
✅ Robot 2 joints set to: ['0.225', '0.434', '1.309', '-1.685', '-1.556', '0.566'] rad
✅ Robot 2 joints set to: ['0.266', '0.451', '1.286', '-1.685', '-1.565', '0.566'] rad
✅ Robot 2 joints set to: ['0.307', '0.451', '1.286', '-1.685', '-1.565', '0.566'] rad
✅ Robot 2 joints set to: ['0.348', '0.468', '1.263', '-1.686', '-1.574', '0.566'] rad
✅ Robot 2 joints set to: ['0.388', '0.468', '1.263', '-1.686', '-1.574', '0.566'] rad
✅ Robot 2 joints set to: ['0.427', '0.484', '1.241', '-1.686', '-1.582', '0.566'] rad
   📊 Progress:  61% (waypoint 25/41, t=3.4s)
✅ Robot 2 joints set to: ['0.464', '0.484', '1.241', '-1.686', '-1.582', '0.566'] rad
✅ Robot 2 joints set to: ['0.500', '0.499', '1.221', '-1.686', '-1.589', '0.566'] rad
✅ Robot 2 joints set to: ['0.532', '0.499', '1.221', '-1.686', '-1.589', '0.566'] rad
✅ Robot 2 joints set to: ['0.563', '0.512', '1.203', '-1.686', '-1.596', '0.566'] rad
✅ Robot 2 joints set to: ['0.590', '0.512', '1.203', '-1.686', '-1.596', '0.566'] rad
✅ Robot 2 joints set to: ['0.616', '0.523', '1.188', '-1.686', '-1.602', '0.566'] rad
✅ Robot 2 joints set to: ['0.636', '0.523', '1.188', '-1.686', '-1.602', '0.566'] rad
✅ Robot 2 joints set to: ['0.656', '0.531', '1.177', '-1.686', '-1.606', '0.566'] rad
   📊 Progress:  80% (waypoint 33/41, t=4.5s)
✅ Robot 2 joints set to: ['0.670', '0.531', '1.177', '-1.686', '-1.606', '0.566'] rad
✅ Robot 2 joints set to: ['0.684', '0.537', '1.170', '-1.686', '-1.609', '0.566'] rad
✅ Robot 2 joints set to: ['0.692', '0.537', '1.170', '-1.686', '-1.609', '0.566'] rad
✅ Robot 2 joints set to: ['0.700', '0.540', '1.165', '-1.686', '-1.610', '0.566'] rad
✅ Robot 2 joints set to: ['0.703', '0.540', '1.165', '-1.686', '-1.610', '0.566'] rad
✅ Robot 2 joints set to: ['0.706', '0.541', '1.163', '-1.686', '-1.611', '0.566'] rad
✅ Robot 2 joints set to: ['0.707', '0.541', '1.163', '-1.686', '-1.611', '0.566'] rad
✅ Robot 2 joints set to: ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.566'] rad
   📊 Progress: 100% (waypoint 41/41, t=5.6s)

📖 Verifying final position...
📖 Robot 2 joints: ['0.698', '0.545', '1.178', '-1.680', '-1.600', '0.575']
✅ Trajectory completed!
   📏 Max error: 0.0153 rad (0.88°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575']

✅ Successfully completed: left_arm_standoff_with_beaker

⏳ Pausing 2.0s before next step...

🔄 Step 3/11: left_arm_standoff_yellow

🎯 Executing configuration: left_arm_standoff_yellow
==================================================
✅ Loaded configuration 'left_arm_standoff_yellow' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_standoff_yellow
📝 Description: Left arm standoff position during yellow dispensing operation - current position captured
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575']
  ✅ left_arm: Complete configuration (all 6 joints)

🎯 Moving to: left_arm_standoff_yellow
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575']
📍 Current: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575']
🎯 Target:  ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.005', '-0.976', '-0.115', '1.016', '-0.081']
   📊 Weighted squared sum: 2.004
   📍 Calculated waypoints: 25 → 25 (range: 5-50)
🛡️  Auto-calculated duration: 6.3s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 6.3 seconds
   📍 Waypoints: 25
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 25 → Enhanced waypoints: 49
   📊 Shape: (49, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 25 → 49 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575'] rad
   📊 Progress:   2% (waypoint 1/49, t=0.1s)
✅ Robot 2 joints set to: ['0.700', '0.545', '1.178', '-1.680', '-1.600', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.544', '1.178', '-1.679', '-1.600', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.544', '1.178', '-1.679', '-1.600', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.540', '1.178', '-1.675', '-1.601', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.540', '1.178', '-1.675', '-1.601', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.529', '1.177', '-1.664', '-1.602', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.529', '1.177', '-1.664', '-1.602', '0.575'] rad
✅ Robot 2 joints set to: ['0.700', '0.510', '1.174', '-1.644', '-1.603', '0.574'] rad
✅ Robot 2 joints set to: ['0.699', '0.510', '1.174', '-1.644', '-1.603', '0.574'] rad
   📊 Progress:  20% (waypoint 10/49, t=1.3s)
✅ Robot 2 joints set to: ['0.699', '0.482', '1.171', '-1.615', '-1.606', '0.572'] rad
✅ Robot 2 joints set to: ['0.699', '0.482', '1.171', '-1.615', '-1.606', '0.572'] rad
✅ Robot 2 joints set to: ['0.699', '0.444', '1.166', '-1.575', '-1.609', '0.571'] rad
✅ Robot 2 joints set to: ['0.699', '0.444', '1.166', '-1.575', '-1.609', '0.571'] rad
✅ Robot 2 joints set to: ['0.699', '0.396', '1.161', '-1.525', '-1.613', '0.568'] rad
✅ Robot 2 joints set to: ['0.699', '0.396', '1.161', '-1.525', '-1.613', '0.568'] rad
✅ Robot 2 joints set to: ['0.699', '0.340', '1.154', '-1.467', '-1.617', '0.566'] rad
✅ Robot 2 joints set to: ['0.699', '0.340', '1.154', '-1.467', '-1.617', '0.566'] rad
✅ Robot 2 joints set to: ['0.698', '0.276', '1.147', '-1.401', '-1.623', '0.563'] rad
   📊 Progress:  39% (waypoint 19/49, t=2.5s)
✅ Robot 2 joints set to: ['0.698', '0.276', '1.147', '-1.401', '-1.623', '0.563'] rad
✅ Robot 2 joints set to: ['0.698', '0.206', '1.138', '-1.328', '-1.629', '0.560'] rad
✅ Robot 2 joints set to: ['0.698', '0.206', '1.138', '-1.328', '-1.629', '0.560'] rad
✅ Robot 2 joints set to: ['0.698', '0.133', '1.130', '-1.251', '-1.635', '0.556'] rad
✅ Robot 2 joints set to: ['0.698', '0.133', '1.130', '-1.251', '-1.635', '0.556'] rad
✅ Robot 2 joints set to: ['0.697', '0.057', '1.121', '-1.172', '-1.641', '0.553'] rad
✅ Robot 2 joints set to: ['0.697', '0.057', '1.121', '-1.172', '-1.641', '0.553'] rad
✅ Robot 2 joints set to: ['0.697', '-0.019', '1.112', '-1.093', '-1.647', '0.549'] rad
✅ Robot 2 joints set to: ['0.697', '-0.019', '1.112', '-1.093', '-1.647', '0.549'] rad
   📊 Progress:  57% (waypoint 28/49, t=3.7s)
✅ Robot 2 joints set to: ['0.697', '-0.093', '1.103', '-1.016', '-1.653', '0.546'] rad
✅ Robot 2 joints set to: ['0.696', '-0.093', '1.103', '-1.016', '-1.653', '0.546'] rad
✅ Robot 2 joints set to: ['0.696', '-0.163', '1.095', '-0.944', '-1.659', '0.542'] rad
✅ Robot 2 joints set to: ['0.696', '-0.163', '1.095', '-0.944', '-1.659', '0.542'] rad
✅ Robot 2 joints set to: ['0.696', '-0.226', '1.087', '-0.878', '-1.665', '0.540'] rad
✅ Robot 2 joints set to: ['0.696', '-0.226', '1.087', '-0.878', '-1.665', '0.540'] rad
✅ Robot 2 joints set to: ['0.696', '-0.283', '1.081', '-0.819', '-1.669', '0.537'] rad
✅ Robot 2 joints set to: ['0.696', '-0.283', '1.081', '-0.819', '-1.669', '0.537'] rad
✅ Robot 2 joints set to: ['0.696', '-0.330', '1.075', '-0.770', '-1.673', '0.535'] rad
   📊 Progress:  76% (waypoint 37/49, t=4.9s)
✅ Robot 2 joints set to: ['0.695', '-0.330', '1.075', '-0.770', '-1.673', '0.535'] rad
✅ Robot 2 joints set to: ['0.695', '-0.368', '1.071', '-0.730', '-1.676', '0.533'] rad
✅ Robot 2 joints set to: ['0.695', '-0.368', '1.071', '-0.730', '-1.676', '0.533'] rad
✅ Robot 2 joints set to: ['0.695', '-0.397', '1.067', '-0.700', '-1.679', '0.532'] rad
✅ Robot 2 joints set to: ['0.695', '-0.397', '1.067', '-0.700', '-1.679', '0.532'] rad
✅ Robot 2 joints set to: ['0.695', '-0.415', '1.065', '-0.681', '-1.680', '0.531'] rad
✅ Robot 2 joints set to: ['0.695', '-0.415', '1.065', '-0.681', '-1.680', '0.531'] rad
✅ Robot 2 joints set to: ['0.695', '-0.426', '1.064', '-0.670', '-1.681', '0.530'] rad
✅ Robot 2 joints set to: ['0.695', '-0.426', '1.064', '-0.670', '-1.681', '0.530'] rad
   📊 Progress:  94% (waypoint 46/49, t=6.1s)
✅ Robot 2 joints set to: ['0.695', '-0.430', '1.063', '-0.665', '-1.682', '0.530'] rad
✅ Robot 2 joints set to: ['0.695', '-0.430', '1.063', '-0.665', '-1.682', '0.530'] rad
✅ Robot 2 joints set to: ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530'] rad
   📊 Progress: 100% (waypoint 49/49, t=6.5s)

📖 Verifying final position...
📖 Robot 2 joints: ['0.698', '-0.377', '1.119', '-0.667', '-1.671', '0.583']
✅ Trajectory completed!
   📏 Max error: 0.0552 rad (3.16°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583']

✅ Successfully completed: left_arm_standoff_yellow

⏳ Pausing 2.0s before next step...

🔄 Step 4/11: right_arm_standoff_yellow

🎯 Executing configuration: right_arm_standoff_yellow
==================================================
✅ Loaded configuration 'right_arm_standoff_yellow' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: right_arm_standoff_yellow
📝 Description: Right arm standoff position during yellow dispensing operation - current position captured
📊 Source: current_robot_state
🎯 Mode: Right arm only (left arm stays steady)
📖 Robot 3 joints: ['0.374', '-1.797', '1.452', '-1.754', '-1.606', '1.568']
  ✅ right_arm: Complete configuration (all 6 joints)

🎯 Moving to: right_arm_standoff_yellow
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY
Left arm (ID 2): keeping current position

🦾 Right arm (ID 3) target: ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846']

🎯 Executing smooth trajectory for robot 3
============================================================
📖 Reading current position...
📖 Robot 3 joints: ['0.374', '-1.797', '1.452', '-1.754', '-1.606', '1.568']
📍 Current: ['0.374', '-1.797', '1.452', '-1.754', '-1.606', '1.568']
🎯 Target:  ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.279', '0.531', '-0.046', '1.249', '0.230']
   📊 Weighted squared sum: 2.053
   📍 Calculated waypoints: 25 → 25 (range: 5-50)
🛡️  Auto-calculated duration: 7.8s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 7.8 seconds
   📍 Waypoints: 25
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 25 → Enhanced waypoints: 49
   📊 Shape: (49, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 25 → 49 points

🎬 Executing enhanced trajectory...
✅ Robot 3 joints set to: ['0.374', '-1.797', '1.452', '-1.754', '-1.606', '1.568'] rad
   📊 Progress:   2% (waypoint 1/49, t=0.1s)
✅ Robot 3 joints set to: ['0.374', '-1.797', '1.452', '-1.754', '-1.606', '1.568'] rad
✅ Robot 3 joints set to: ['0.374', '-1.796', '1.451', '-1.753', '-1.606', '1.568'] rad
✅ Robot 3 joints set to: ['0.374', '-1.796', '1.451', '-1.753', '-1.606', '1.568'] rad
✅ Robot 3 joints set to: ['0.373', '-1.794', '1.451', '-1.747', '-1.605', '1.570'] rad
✅ Robot 3 joints set to: ['0.371', '-1.794', '1.451', '-1.747', '-1.605', '1.570'] rad
✅ Robot 3 joints set to: ['0.370', '-1.788', '1.451', '-1.734', '-1.603', '1.573'] rad
✅ Robot 3 joints set to: ['0.367', '-1.788', '1.451', '-1.734', '-1.603', '1.573'] rad
✅ Robot 3 joints set to: ['0.364', '-1.778', '1.450', '-1.709', '-1.598', '1.578'] rad
✅ Robot 3 joints set to: ['0.360', '-1.778', '1.450', '-1.709', '-1.598', '1.578'] rad
   📊 Progress:  20% (waypoint 10/49, t=1.6s)
✅ Robot 3 joints set to: ['0.356', '-1.762', '1.449', '-1.673', '-1.592', '1.586'] rad
✅ Robot 3 joints set to: ['0.351', '-1.762', '1.449', '-1.673', '-1.592', '1.586'] rad
✅ Robot 3 joints set to: ['0.345', '-1.742', '1.447', '-1.624', '-1.583', '1.597'] rad
✅ Robot 3 joints set to: ['0.339', '-1.742', '1.447', '-1.624', '-1.583', '1.597'] rad
✅ Robot 3 joints set to: ['0.332', '-1.716', '1.444', '-1.564', '-1.571', '1.610'] rad
✅ Robot 3 joints set to: ['0.324', '-1.716', '1.444', '-1.564', '-1.571', '1.610'] rad
✅ Robot 3 joints set to: ['0.316', '-1.685', '1.442', '-1.492', '-1.558', '1.626'] rad
✅ Robot 3 joints set to: ['0.307', '-1.685', '1.442', '-1.492', '-1.558', '1.626'] rad
✅ Robot 3 joints set to: ['0.298', '-1.651', '1.439', '-1.410', '-1.543', '1.645'] rad
   📊 Progress:  39% (waypoint 19/49, t=3.0s)
✅ Robot 3 joints set to: ['0.288', '-1.651', '1.439', '-1.410', '-1.543', '1.645'] rad
✅ Robot 3 joints set to: ['0.278', '-1.613', '1.436', '-1.321', '-1.527', '1.664'] rad
✅ Robot 3 joints set to: ['0.267', '-1.613', '1.436', '-1.321', '-1.527', '1.664'] rad
✅ Robot 3 joints set to: ['0.256', '-1.573', '1.432', '-1.226', '-1.509', '1.685'] rad
✅ Robot 3 joints set to: ['0.246', '-1.573', '1.432', '-1.226', '-1.509', '1.685'] rad
✅ Robot 3 joints set to: ['0.235', '-1.531', '1.428', '-1.129', '-1.491', '1.707'] rad
✅ Robot 3 joints set to: ['0.224', '-1.531', '1.428', '-1.129', '-1.491', '1.707'] rad
✅ Robot 3 joints set to: ['0.213', '-1.490', '1.425', '-1.032', '-1.473', '1.729'] rad
✅ Robot 3 joints set to: ['0.202', '-1.490', '1.425', '-1.032', '-1.473', '1.729'] rad
   📊 Progress:  57% (waypoint 28/49, t=4.5s)
✅ Robot 3 joints set to: ['0.192', '-1.450', '1.421', '-0.938', '-1.456', '1.750'] rad
✅ Robot 3 joints set to: ['0.182', '-1.450', '1.421', '-0.938', '-1.456', '1.750'] rad
✅ Robot 3 joints set to: ['0.172', '-1.412', '1.418', '-0.849', '-1.440', '1.769'] rad
✅ Robot 3 joints set to: ['0.163', '-1.412', '1.418', '-0.849', '-1.440', '1.769'] rad
✅ Robot 3 joints set to: ['0.154', '-1.377', '1.415', '-0.767', '-1.425', '1.788'] rad
✅ Robot 3 joints set to: ['0.146', '-1.377', '1.415', '-0.767', '-1.425', '1.788'] rad
✅ Robot 3 joints set to: ['0.138', '-1.347', '1.412', '-0.695', '-1.411', '1.804'] rad
✅ Robot 3 joints set to: ['0.131', '-1.347', '1.412', '-0.695', '-1.411', '1.804'] rad
✅ Robot 3 joints set to: ['0.124', '-1.321', '1.410', '-0.634', '-1.400', '1.817'] rad
   📊 Progress:  76% (waypoint 37/49, t=6.0s)
✅ Robot 3 joints set to: ['0.119', '-1.321', '1.410', '-0.634', '-1.400', '1.817'] rad
✅ Robot 3 joints set to: ['0.113', '-1.300', '1.408', '-0.585', '-1.391', '1.828'] rad
✅ Robot 3 joints set to: ['0.109', '-1.300', '1.408', '-0.585', '-1.391', '1.828'] rad
✅ Robot 3 joints set to: ['0.105', '-1.285', '1.407', '-0.549', '-1.384', '1.836'] rad
✅ Robot 3 joints set to: ['0.102', '-1.285', '1.407', '-0.549', '-1.384', '1.836'] rad
✅ Robot 3 joints set to: ['0.100', '-1.274', '1.406', '-0.525', '-1.380', '1.841'] rad
✅ Robot 3 joints set to: ['0.098', '-1.274', '1.406', '-0.525', '-1.380', '1.841'] rad
✅ Robot 3 joints set to: ['0.097', '-1.269', '1.406', '-0.511', '-1.377', '1.844'] rad
✅ Robot 3 joints set to: ['0.096', '-1.269', '1.406', '-0.511', '-1.377', '1.844'] rad
   📊 Progress:  94% (waypoint 46/49, t=7.4s)
✅ Robot 3 joints set to: ['0.095', '-1.266', '1.406', '-0.506', '-1.376', '1.846'] rad
✅ Robot 3 joints set to: ['0.095', '-1.266', '1.406', '-0.506', '-1.376', '1.846'] rad
✅ Robot 3 joints set to: ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846'] rad
   📊 Progress: 100% (waypoint 49/49, t=7.9s)

📖 Verifying final position...
📖 Robot 3 joints: ['0.100', '-1.272', '1.464', '-0.509', '-1.382', '1.834']
✅ Trajectory completed!
   📏 Max error: 0.0583 rad (3.34°)

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 3 joints: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834']

✅ Successfully completed: right_arm_standoff_yellow

⏳ Pausing 2.0s before next step...

🔄 Step 5/11: dispensing_yellow_to_beaker

🎯 Executing configuration: dispensing_yellow_to_beaker
==================================================
✅ Loaded configuration 'dispensing_yellow_to_beaker' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: dispensing_yellow_to_beaker
📝 Description: Robot configuration for dispensing yellow solution to beaker - left and right arms updated with current joint readings (j1-j5), preserving original gripper positions (j6)
📊 Source: Hafnium49/example_dataset
🎯 Mode: Dual-arm movement
📖 Robot 2 joints: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583']
📖 Robot 3 joints: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834']
  ✅ left_arm: Complete configuration (all 6 joints)
  ✅ right_arm: Complete configuration (all 6 joints)

🎯 Moving to: dispensing_yellow_to_beaker
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['0.417', '-0.549', '0.499', '-0.186', '-2.162', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583']
📍 Current: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583']
🎯 Target:  ['0.417', '-0.549', '0.499', '-0.186', '-2.162', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.281', '-0.170', '-0.620', '0.482', '-0.491']
   📊 Weighted squared sum: 1.044
   📍 Calculated waypoints: 15 → 15 (range: 5-50)
🛡️  Auto-calculated duration: 3.9s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 3.9 seconds
   📍 Waypoints: 15
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 15 → Enhanced waypoints: 29
   📊 Shape: (29, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 15 → 29 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583'] rad
   📊 Progress:   3% (waypoint 1/29, t=0.1s)
✅ Robot 2 joints set to: ['0.698', '-0.379', '1.119', '-0.667', '-1.671', '0.583'] rad
✅ Robot 2 joints set to: ['0.697', '-0.380', '1.117', '-0.666', '-1.673', '0.583'] rad
✅ Robot 2 joints set to: ['0.694', '-0.380', '1.117', '-0.666', '-1.673', '0.583'] rad
✅ Robot 2 joints set to: ['0.692', '-0.383', '1.104', '-0.656', '-1.682', '0.582'] rad
✅ Robot 2 joints set to: ['0.685', '-0.383', '1.104', '-0.656', '-1.682', '0.582'] rad
   📊 Progress:  21% (waypoint 6/29, t=0.8s)
✅ Robot 2 joints set to: ['0.679', '-0.391', '1.075', '-0.634', '-1.705', '0.579'] rad
✅ Robot 2 joints set to: ['0.668', '-0.391', '1.075', '-0.634', '-1.705', '0.579'] rad
✅ Robot 2 joints set to: ['0.658', '-0.404', '1.029', '-0.598', '-1.742', '0.575'] rad
✅ Robot 2 joints set to: ['0.643', '-0.404', '1.029', '-0.598', '-1.742', '0.575'] rad
✅ Robot 2 joints set to: ['0.629', '-0.421', '0.966', '-0.549', '-1.792', '0.570'] rad
   📊 Progress:  38% (waypoint 11/29, t=1.5s)
✅ Robot 2 joints set to: ['0.612', '-0.421', '0.966', '-0.549', '-1.792', '0.570'] rad
✅ Robot 2 joints set to: ['0.595', '-0.442', '0.891', '-0.490', '-1.852', '0.564'] rad
✅ Robot 2 joints set to: ['0.576', '-0.442', '0.891', '-0.490', '-1.852', '0.564'] rad
✅ Robot 2 joints set to: ['0.558', '-0.464', '0.809', '-0.427', '-1.916', '0.557'] rad
✅ Robot 2 joints set to: ['0.539', '-0.464', '0.809', '-0.427', '-1.916', '0.557'] rad
   📊 Progress:  55% (waypoint 16/29, t=2.2s)
✅ Robot 2 joints set to: ['0.521', '-0.487', '0.727', '-0.363', '-1.981', '0.550'] rad
✅ Robot 2 joints set to: ['0.504', '-0.487', '0.727', '-0.363', '-1.981', '0.550'] rad
✅ Robot 2 joints set to: ['0.487', '-0.507', '0.651', '-0.304', '-2.041', '0.543'] rad
✅ Robot 2 joints set to: ['0.472', '-0.507', '0.651', '-0.304', '-2.041', '0.543'] rad
✅ Robot 2 joints set to: ['0.458', '-0.525', '0.588', '-0.255', '-2.091', '0.538'] rad
   📊 Progress:  72% (waypoint 21/29, t=2.9s)
✅ Robot 2 joints set to: ['0.447', '-0.525', '0.588', '-0.255', '-2.091', '0.538'] rad
✅ Robot 2 joints set to: ['0.437', '-0.537', '0.542', '-0.219', '-2.128', '0.534'] rad
✅ Robot 2 joints set to: ['0.430', '-0.537', '0.542', '-0.219', '-2.128', '0.534'] rad
✅ Robot 2 joints set to: ['0.424', '-0.545', '0.513', '-0.197', '-2.150', '0.531'] rad
✅ Robot 2 joints set to: ['0.421', '-0.545', '0.513', '-0.197', '-2.150', '0.531'] rad
   📊 Progress:  90% (waypoint 26/29, t=3.6s)
✅ Robot 2 joints set to: ['0.418', '-0.549', '0.501', '-0.187', '-2.160', '0.530'] rad
✅ Robot 2 joints set to: ['0.418', '-0.549', '0.501', '-0.187', '-2.160', '0.530'] rad
✅ Robot 2 joints set to: ['0.417', '-0.549', '0.499', '-0.186', '-2.162', '0.530'] rad
   📊 Progress: 100% (waypoint 29/29, t=4.0s)

📖 Verifying final position...
📖 Robot 2 joints: ['0.428', '-0.502', '0.568', '-0.190', '-2.154', '0.588']
✅ Trajectory completed!
   📏 Max error: 0.0690 rad (3.96°)

🦾 Right arm (ID 3) target: ['0.018', '-0.574', '0.904', '-0.262', '-1.447', '0.858']

🎯 Executing smooth trajectory for robot 3
============================================================
📖 Reading current position...
📖 Robot 3 joints: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834']
📍 Current: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834']
🎯 Target:  ['0.018', '-0.574', '0.904', '-0.262', '-1.447', '0.858']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.081', '0.695', '-0.560', '0.247', '-0.064']
   📊 Weighted squared sum: 0.875
   📍 Calculated waypoints: 13 → 13 (range: 5-50)
🛡️  Auto-calculated duration: 6.1s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 6.1 seconds
   📍 Waypoints: 13
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 13 → Enhanced waypoints: 25
   📊 Shape: (25, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 13 → 25 points

🎬 Executing enhanced trajectory...
✅ Robot 3 joints set to: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834'] rad
   📊 Progress:   4% (waypoint 1/25, t=0.1s)
✅ Robot 3 joints set to: ['0.100', '-1.269', '1.464', '-0.509', '-1.382', '1.834'] rad
✅ Robot 3 joints set to: ['0.099', '-1.265', '1.461', '-0.508', '-1.383', '1.829'] rad
✅ Robot 3 joints set to: ['0.098', '-1.265', '1.461', '-0.508', '-1.383', '1.829'] rad
✅ Robot 3 joints set to: ['0.097', '-1.244', '1.444', '-0.501', '-1.385', '1.799'] rad
✅ Robot 3 joints set to: ['0.094', '-1.244', '1.444', '-0.501', '-1.385', '1.799'] rad
   📊 Progress:  24% (waypoint 6/25, t=1.4s)
✅ Robot 3 joints set to: ['0.091', '-1.197', '1.406', '-0.484', '-1.389', '1.733'] rad
✅ Robot 3 joints set to: ['0.087', '-1.197', '1.406', '-0.484', '-1.389', '1.733'] rad
✅ Robot 3 joints set to: ['0.083', '-1.123', '1.346', '-0.458', '-1.396', '1.629'] rad
✅ Robot 3 joints set to: ['0.077', '-1.123', '1.346', '-0.458', '-1.396', '1.629'] rad
✅ Robot 3 joints set to: ['0.072', '-1.028', '1.270', '-0.424', '-1.405', '1.495'] rad
   📊 Progress:  44% (waypoint 11/25, t=2.6s)
✅ Robot 3 joints set to: ['0.065', '-1.028', '1.270', '-0.424', '-1.405', '1.495'] rad
✅ Robot 3 joints set to: ['0.059', '-0.921', '1.184', '-0.386', '-1.415', '1.346'] rad
✅ Robot 3 joints set to: ['0.053', '-0.921', '1.184', '-0.386', '-1.415', '1.346'] rad
✅ Robot 3 joints set to: ['0.047', '-0.815', '1.098', '-0.348', '-1.425', '1.196'] rad
✅ Robot 3 joints set to: ['0.041', '-0.815', '1.098', '-0.348', '-1.425', '1.196'] rad
   📊 Progress:  64% (waypoint 16/25, t=3.9s)
✅ Robot 3 joints set to: ['0.035', '-0.720', '1.021', '-0.314', '-1.433', '1.063'] rad
✅ Robot 3 joints set to: ['0.031', '-0.720', '1.021', '-0.314', '-1.433', '1.063'] rad
✅ Robot 3 joints set to: ['0.027', '-0.646', '0.962', '-0.288', '-1.440', '0.959'] rad
✅ Robot 3 joints set to: ['0.024', '-0.646', '0.962', '-0.288', '-1.440', '0.959'] rad
✅ Robot 3 joints set to: ['0.021', '-0.599', '0.924', '-0.271', '-1.445', '0.892'] rad
   📊 Progress:  84% (waypoint 21/25, t=5.2s)
✅ Robot 3 joints set to: ['0.020', '-0.599', '0.924', '-0.271', '-1.445', '0.892'] rad
✅ Robot 3 joints set to: ['0.019', '-0.577', '0.907', '-0.264', '-1.447', '0.863'] rad
✅ Robot 3 joints set to: ['0.019', '-0.577', '0.907', '-0.264', '-1.447', '0.863'] rad
✅ Robot 3 joints set to: ['0.018', '-0.574', '0.904', '-0.262', '-1.447', '0.858'] rad
   📊 Progress: 100% (waypoint 25/25, t=6.2s)

📖 Verifying final position...
📖 Robot 3 joints: ['0.029', '-0.583', '0.942', '-0.269', '-1.441', '0.867']
✅ Trajectory completed!
   📏 Max error: 0.0384 rad (2.20°)

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['0.428', '-0.503', '0.568', '-0.190', '-2.157', '0.588']
📖 Robot 3 joints: ['0.029', '-0.583', '0.939', '-0.269', '-1.441', '0.864']

✅ Successfully completed: dispensing_yellow_to_beaker

⏳ Pausing 2.0s before next step...

🔄 Step 6/11: right_arm_standoff_yellow

🎯 Executing configuration: right_arm_standoff_yellow
==================================================
✅ Loaded configuration 'right_arm_standoff_yellow' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: right_arm_standoff_yellow
📝 Description: Right arm standoff position during yellow dispensing operation - current position captured
📊 Source: current_robot_state
🎯 Mode: Right arm only (left arm stays steady)
📖 Robot 3 joints: ['0.029', '-0.582', '0.939', '-0.269', '-1.441', '0.864']
  ✅ right_arm: Complete configuration (all 6 joints)

🎯 Moving to: right_arm_standoff_yellow
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY
Left arm (ID 2): keeping current position

🦾 Right arm (ID 3) target: ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846']

🎯 Executing smooth trajectory for robot 3
============================================================
📖 Reading current position...
📖 Robot 3 joints: ['0.029', '-0.582', '0.939', '-0.269', '-1.441', '0.864']
📍 Current: ['0.029', '-0.582', '0.939', '-0.269', '-1.441', '0.864']
🎯 Target:  ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.066', '-0.684', '0.466', '-0.236', '0.064']
   📊 Weighted squared sum: 0.755
   📍 Calculated waypoints: 12 → 12 (range: 5-50)
🛡️  Auto-calculated duration: 6.1s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 6.1 seconds
   📍 Waypoints: 12
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 12 → Enhanced waypoints: 23
   📊 Shape: (23, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 12 → 23 points

🎬 Executing enhanced trajectory...
✅ Robot 3 joints set to: ['0.029', '-0.582', '0.939', '-0.269', '-1.441', '0.864'] rad
   📊 Progress:   4% (waypoint 1/23, t=0.1s)
✅ Robot 3 joints set to: ['0.029', '-0.582', '0.939', '-0.269', '-1.441', '0.864'] rad
✅ Robot 3 joints set to: ['0.030', '-0.586', '0.942', '-0.270', '-1.440', '0.870'] rad
✅ Robot 3 joints set to: ['0.031', '-0.586', '0.942', '-0.270', '-1.440', '0.870'] rad
✅ Robot 3 joints set to: ['0.032', '-0.612', '0.960', '-0.279', '-1.438', '0.908'] rad
   📊 Progress:  22% (waypoint 5/23, t=1.2s)
✅ Robot 3 joints set to: ['0.035', '-0.612', '0.960', '-0.279', '-1.438', '0.908'] rad
✅ Robot 3 joints set to: ['0.038', '-0.670', '0.999', '-0.299', '-1.432', '0.990'] rad
✅ Robot 3 joints set to: ['0.042', '-0.670', '0.999', '-0.299', '-1.432', '0.990'] rad
✅ Robot 3 joints set to: ['0.046', '-0.757', '1.059', '-0.329', '-1.424', '1.116'] rad
   📊 Progress:  39% (waypoint 9/23, t=2.3s)
✅ Robot 3 joints set to: ['0.051', '-0.757', '1.059', '-0.329', '-1.424', '1.116'] rad
✅ Robot 3 joints set to: ['0.057', '-0.866', '1.133', '-0.367', '-1.414', '1.272'] rad
✅ Robot 3 joints set to: ['0.062', '-0.866', '1.133', '-0.367', '-1.414', '1.272'] rad
✅ Robot 3 joints set to: ['0.068', '-0.982', '1.212', '-0.407', '-1.403', '1.438'] rad
   📊 Progress:  57% (waypoint 13/23, t=3.5s)
✅ Robot 3 joints set to: ['0.073', '-0.982', '1.212', '-0.407', '-1.403', '1.438'] rad
✅ Robot 3 joints set to: ['0.078', '-1.090', '1.286', '-0.444', '-1.393', '1.594'] rad
✅ Robot 3 joints set to: ['0.082', '-1.090', '1.286', '-0.444', '-1.393', '1.594'] rad
✅ Robot 3 joints set to: ['0.087', '-1.178', '1.345', '-0.474', '-1.385', '1.719'] rad
   📊 Progress:  74% (waypoint 17/23, t=4.6s)
✅ Robot 3 joints set to: ['0.089', '-1.178', '1.345', '-0.474', '-1.385', '1.719'] rad
✅ Robot 3 joints set to: ['0.092', '-1.235', '1.385', '-0.494', '-1.379', '1.802'] rad
✅ Robot 3 joints set to: ['0.093', '-1.235', '1.385', '-0.494', '-1.379', '1.802'] rad
✅ Robot 3 joints set to: ['0.095', '-1.261', '1.402', '-0.503', '-1.377', '1.839'] rad
   📊 Progress:  91% (waypoint 21/23, t=5.7s)
✅ Robot 3 joints set to: ['0.095', '-1.261', '1.402', '-0.503', '-1.377', '1.839'] rad
✅ Robot 3 joints set to: ['0.095', '-1.266', '1.405', '-0.505', '-1.376', '1.846'] rad
   📊 Progress: 100% (waypoint 23/23, t=6.3s)

📖 Verifying final position...
📖 Robot 3 joints: ['0.084', '-1.244', '1.413', '-0.485', '-1.382', '1.834']
✅ Trajectory completed!
   📏 Max error: 0.0215 rad (1.23°)

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 3 joints: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837']

✅ Successfully completed: right_arm_standoff_yellow

⏳ Pausing 2.0s before next step...

🔄 Step 7/11: right_arm_standoff

🎯 Executing configuration: right_arm_standoff
==================================================
✅ Loaded configuration 'right_arm_standoff' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: right_arm_standoff
📝 Description: Right arm standoff position - extracted from standoff_configuration_stage1
📊 Source: Hafnium49/aloha_lite
🎯 Mode: Right arm only (left arm stays steady)
📖 Robot 3 joints: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837']
  ✅ right_arm: Complete configuration (all 6 joints)

🎯 Moving to: right_arm_standoff
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY
Left arm (ID 2): keeping current position

🦾 Right arm (ID 3) target: ['0.379', '-1.804', '1.413', '-1.755', '-1.614', '1.580']

🎯 Executing smooth trajectory for robot 3
============================================================
📖 Reading current position...
📖 Robot 3 joints: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837']
📍 Current: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837']
🎯 Target:  ['0.379', '-1.804', '1.413', '-1.755', '-1.614', '1.580']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.295', '-0.557', '0.000', '-1.270', '-0.232']
   📊 Weighted squared sum: 2.152
   📍 Calculated waypoints: 26 → 26 (range: 5-50)
🛡️  Auto-calculated duration: 7.9s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 7.9 seconds
   📍 Waypoints: 26
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 26 → Enhanced waypoints: 51
   📊 Shape: (51, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 26 → 51 points

🎬 Executing enhanced trajectory...
✅ Robot 3 joints set to: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837'] rad
   📊 Progress:   2% (waypoint 1/51, t=0.1s)
✅ Robot 3 joints set to: ['0.084', '-1.247', '1.413', '-0.485', '-1.382', '1.837'] rad
✅ Robot 3 joints set to: ['0.085', '-1.248', '1.413', '-0.486', '-1.383', '1.836'] rad
✅ Robot 3 joints set to: ['0.085', '-1.248', '1.413', '-0.486', '-1.383', '1.836'] rad
✅ Robot 3 joints set to: ['0.086', '-1.250', '1.413', '-0.491', '-1.384', '1.835'] rad
✅ Robot 3 joints set to: ['0.087', '-1.250', '1.413', '-0.491', '-1.384', '1.835'] rad
✅ Robot 3 joints set to: ['0.089', '-1.255', '1.413', '-0.503', '-1.386', '1.833'] rad
✅ Robot 3 joints set to: ['0.091', '-1.255', '1.413', '-0.503', '-1.386', '1.833'] rad
✅ Robot 3 joints set to: ['0.094', '-1.265', '1.413', '-0.525', '-1.390', '1.828'] rad
✅ Robot 3 joints set to: ['0.098', '-1.265', '1.413', '-0.525', '-1.390', '1.828'] rad
✅ Robot 3 joints set to: ['0.101', '-1.280', '1.413', '-0.558', '-1.396', '1.822'] rad
   📊 Progress:  22% (waypoint 11/51, t=1.7s)
✅ Robot 3 joints set to: ['0.107', '-1.280', '1.413', '-0.558', '-1.396', '1.822'] rad
✅ Robot 3 joints set to: ['0.112', '-1.299', '1.413', '-0.603', '-1.404', '1.813'] rad
✅ Robot 3 joints set to: ['0.118', '-1.299', '1.413', '-0.603', '-1.404', '1.813'] rad
✅ Robot 3 joints set to: ['0.125', '-1.324', '1.413', '-0.660', '-1.414', '1.801'] rad
✅ Robot 3 joints set to: ['0.133', '-1.324', '1.413', '-0.660', '-1.414', '1.801'] rad
✅ Robot 3 joints set to: ['0.141', '-1.354', '1.413', '-0.727', '-1.427', '1.788'] rad
✅ Robot 3 joints set to: ['0.149', '-1.354', '1.413', '-0.727', '-1.427', '1.788'] rad
✅ Robot 3 joints set to: ['0.158', '-1.387', '1.413', '-0.804', '-1.441', '1.772'] rad
✅ Robot 3 joints set to: ['0.168', '-1.387', '1.413', '-0.804', '-1.441', '1.772'] rad
✅ Robot 3 joints set to: ['0.178', '-1.424', '1.413', '-0.888', '-1.456', '1.755'] rad
   📊 Progress:  41% (waypoint 21/51, t=3.3s)
✅ Robot 3 joints set to: ['0.188', '-1.424', '1.413', '-0.888', '-1.456', '1.755'] rad
✅ Robot 3 joints set to: ['0.199', '-1.464', '1.413', '-0.979', '-1.472', '1.737'] rad
✅ Robot 3 joints set to: ['0.210', '-1.464', '1.413', '-0.979', '-1.472', '1.737'] rad
✅ Robot 3 joints set to: ['0.221', '-1.505', '1.413', '-1.072', '-1.490', '1.718'] rad
✅ Robot 3 joints set to: ['0.232', '-1.505', '1.413', '-1.072', '-1.490', '1.718'] rad
✅ Robot 3 joints set to: ['0.243', '-1.547', '1.413', '-1.168', '-1.507', '1.699'] rad
✅ Robot 3 joints set to: ['0.254', '-1.547', '1.413', '-1.168', '-1.507', '1.699'] rad
✅ Robot 3 joints set to: ['0.265', '-1.588', '1.413', '-1.262', '-1.524', '1.680'] rad
✅ Robot 3 joints set to: ['0.275', '-1.588', '1.413', '-1.262', '-1.524', '1.680'] rad
✅ Robot 3 joints set to: ['0.285', '-1.628', '1.413', '-1.352', '-1.541', '1.662'] rad
   📊 Progress:  61% (waypoint 31/51, t=4.9s)
✅ Robot 3 joints set to: ['0.295', '-1.628', '1.413', '-1.352', '-1.541', '1.662'] rad
✅ Robot 3 joints set to: ['0.305', '-1.665', '1.413', '-1.437', '-1.556', '1.645'] rad
✅ Robot 3 joints set to: ['0.314', '-1.665', '1.413', '-1.437', '-1.556', '1.645'] rad
✅ Robot 3 joints set to: ['0.323', '-1.698', '1.413', '-1.513', '-1.570', '1.629'] rad
✅ Robot 3 joints set to: ['0.331', '-1.698', '1.413', '-1.513', '-1.570', '1.629'] rad
✅ Robot 3 joints set to: ['0.338', '-1.728', '1.413', '-1.580', '-1.582', '1.616'] rad
✅ Robot 3 joints set to: ['0.345', '-1.728', '1.413', '-1.580', '-1.582', '1.616'] rad
✅ Robot 3 joints set to: ['0.352', '-1.752', '1.413', '-1.637', '-1.593', '1.604'] rad
✅ Robot 3 joints set to: ['0.357', '-1.752', '1.413', '-1.637', '-1.593', '1.604'] rad
✅ Robot 3 joints set to: ['0.362', '-1.772', '1.413', '-1.682', '-1.601', '1.595'] rad
   📊 Progress:  80% (waypoint 41/51, t=6.5s)
✅ Robot 3 joints set to: ['0.366', '-1.772', '1.413', '-1.682', '-1.601', '1.595'] rad
✅ Robot 3 joints set to: ['0.370', '-1.787', '1.413', '-1.715', '-1.607', '1.589'] rad
✅ Robot 3 joints set to: ['0.372', '-1.787', '1.413', '-1.715', '-1.607', '1.589'] rad
✅ Robot 3 joints set to: ['0.375', '-1.796', '1.413', '-1.737', '-1.611', '1.584'] rad
✅ Robot 3 joints set to: ['0.376', '-1.796', '1.413', '-1.737', '-1.611', '1.584'] rad
✅ Robot 3 joints set to: ['0.378', '-1.802', '1.413', '-1.750', '-1.613', '1.582'] rad
✅ Robot 3 joints set to: ['0.378', '-1.802', '1.413', '-1.750', '-1.613', '1.582'] rad
✅ Robot 3 joints set to: ['0.379', '-1.804', '1.413', '-1.755', '-1.614', '1.581'] rad
✅ Robot 3 joints set to: ['0.379', '-1.804', '1.413', '-1.755', '-1.614', '1.581'] rad
✅ Robot 3 joints set to: ['0.379', '-1.804', '1.413', '-1.755', '-1.614', '1.580'] rad
   📊 Progress: 100% (waypoint 51/51, t=8.0s)

📖 Verifying final position...
📖 Robot 3 joints: ['0.374', '-1.789', '1.418', '-1.751', '-1.606', '1.591']
✅ Trajectory completed!
   📏 Max error: 0.0153 rad (0.88°)

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 3 joints: ['0.374', '-1.789', '1.418', '-1.754', '-1.606', '1.591']

✅ Successfully completed: right_arm_standoff

⏳ Pausing 2.0s before next step...

🔄 Step 8/11: left_arm_standoff_yellow

🎯 Executing configuration: left_arm_standoff_yellow
==================================================
✅ Loaded configuration 'left_arm_standoff_yellow' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_standoff_yellow
📝 Description: Left arm standoff position during yellow dispensing operation - current position captured
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['0.428', '-0.503', '0.568', '-0.190', '-2.157', '0.588']
  ✅ left_arm: Complete configuration (all 6 joints)

🎯 Moving to: left_arm_standoff_yellow
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['0.428', '-0.503', '0.568', '-0.190', '-2.157', '0.588']
📍 Current: ['0.428', '-0.503', '0.568', '-0.190', '-2.157', '0.588']
🎯 Target:  ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.267', '0.072', '0.496', '-0.474', '0.476']
   📊 Weighted squared sum: 0.844
   📍 Calculated waypoints: 13 → 13 (range: 5-50)
🛡️  Auto-calculated duration: 3.1s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 3.1 seconds
   📍 Waypoints: 13
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 13 → Enhanced waypoints: 25
   📊 Shape: (25, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 13 → 25 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['0.428', '-0.503', '0.568', '-0.190', '-2.157', '0.588'] rad
   📊 Progress:   4% (waypoint 1/25, t=0.1s)
✅ Robot 2 joints set to: ['0.429', '-0.503', '0.568', '-0.190', '-2.157', '0.588'] rad
✅ Robot 2 joints set to: ['0.429', '-0.503', '0.570', '-0.193', '-2.155', '0.587'] rad
✅ Robot 2 joints set to: ['0.434', '-0.503', '0.570', '-0.193', '-2.155', '0.587'] rad
✅ Robot 2 joints set to: ['0.438', '-0.501', '0.585', '-0.207', '-2.140', '0.586'] rad
✅ Robot 2 joints set to: ['0.447', '-0.501', '0.585', '-0.207', '-2.140', '0.586'] rad
   📊 Progress:  24% (waypoint 6/25, t=0.7s)
✅ Robot 2 joints set to: ['0.456', '-0.496', '0.619', '-0.239', '-2.108', '0.582'] rad
✅ Robot 2 joints set to: ['0.470', '-0.496', '0.619', '-0.239', '-2.108', '0.582'] rad
✅ Robot 2 joints set to: ['0.484', '-0.488', '0.672', '-0.290', '-2.057', '0.576'] rad
✅ Robot 2 joints set to: ['0.502', '-0.488', '0.672', '-0.290', '-2.057', '0.576'] rad
✅ Robot 2 joints set to: ['0.521', '-0.478', '0.739', '-0.355', '-1.992', '0.568'] rad
   📊 Progress:  44% (waypoint 11/25, t=1.4s)
✅ Robot 2 joints set to: ['0.541', '-0.478', '0.739', '-0.355', '-1.992', '0.568'] rad
✅ Robot 2 joints set to: ['0.562', '-0.467', '0.816', '-0.427', '-1.919', '0.559'] rad
✅ Robot 2 joints set to: ['0.582', '-0.467', '0.816', '-0.427', '-1.919', '0.559'] rad
✅ Robot 2 joints set to: ['0.603', '-0.456', '0.892', '-0.500', '-1.847', '0.550'] rad
✅ Robot 2 joints set to: ['0.621', '-0.456', '0.892', '-0.500', '-1.847', '0.550'] rad
   📊 Progress:  64% (waypoint 16/25, t=2.0s)
✅ Robot 2 joints set to: ['0.639', '-0.446', '0.959', '-0.565', '-1.781', '0.542'] rad
✅ Robot 2 joints set to: ['0.653', '-0.446', '0.959', '-0.565', '-1.781', '0.542'] rad
✅ Robot 2 joints set to: ['0.667', '-0.439', '1.012', '-0.615', '-1.731', '0.536'] rad
✅ Robot 2 joints set to: ['0.677', '-0.439', '1.012', '-0.615', '-1.731', '0.536'] rad
✅ Robot 2 joints set to: ['0.686', '-0.434', '1.046', '-0.648', '-1.699', '0.532'] rad
   📊 Progress:  84% (waypoint 21/25, t=2.7s)
✅ Robot 2 joints set to: ['0.690', '-0.434', '1.046', '-0.648', '-1.699', '0.532'] rad
✅ Robot 2 joints set to: ['0.694', '-0.432', '1.061', '-0.662', '-1.684', '0.530'] rad
✅ Robot 2 joints set to: ['0.694', '-0.432', '1.061', '-0.662', '-1.684', '0.530'] rad
✅ Robot 2 joints set to: ['0.695', '-0.431', '1.063', '-0.664', '-1.682', '0.530'] rad
   📊 Progress: 100% (waypoint 25/25, t=3.2s)

📖 Verifying final position...
📖 Robot 2 joints: ['0.692', '-0.428', '1.066', '-0.641', '-1.692', '0.589']
✅ Trajectory completed!
   📏 Max error: 0.0592 rad (3.39°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589']

✅ Successfully completed: left_arm_standoff_yellow

⏳ Pausing 2.0s before next step...

🔄 Step 9/11: left_arm_standoff_with_beaker

🎯 Executing configuration: left_arm_standoff_with_beaker
==================================================
✅ Loaded configuration 'left_arm_standoff_with_beaker' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_standoff_with_beaker
📝 Description: Left arm standoff position with beaker - updated joints j1-j5 from current robot position, right arm stays in current position
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589']
  🔄 left_arm: Partial configuration (missing ['j6'])
  🔄 Merging with current joint positions...
  📝 j1 → 0.707 rad
  📝 j2 → 0.542 rad
  📝 j3 → 1.163 rad
  📝 j4 → -1.686 rad
  📝 j5 → -1.611 rad

🎯 Moving to: left_arm_standoff_with_beaker
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.589']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589']
📍 Current: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589']
🎯 Target:  ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.589']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['0.015', '0.970', '0.095', '-1.045', '0.081']
   📊 Weighted squared sum: 2.048
   📍 Calculated waypoints: 25 → 25 (range: 5-50)
🛡️  Auto-calculated duration: 6.5s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 6.5 seconds
   📍 Waypoints: 25
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 25 → Enhanced waypoints: 49
   📊 Shape: (49, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 25 → 49 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589'] rad
   📊 Progress:   2% (waypoint 1/49, t=0.1s)
✅ Robot 2 joints set to: ['0.692', '-0.428', '1.068', '-0.641', '-1.692', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.427', '1.068', '-0.642', '-1.692', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.427', '1.068', '-0.642', '-1.692', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.423', '1.068', '-0.647', '-1.692', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.423', '1.068', '-0.647', '-1.692', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.413', '1.069', '-0.658', '-1.691', '0.589'] rad
✅ Robot 2 joints set to: ['0.692', '-0.413', '1.069', '-0.658', '-1.691', '0.589'] rad
✅ Robot 2 joints set to: ['0.693', '-0.394', '1.071', '-0.678', '-1.690', '0.589'] rad
✅ Robot 2 joints set to: ['0.693', '-0.394', '1.071', '-0.678', '-1.690', '0.589'] rad
   📊 Progress:  20% (waypoint 10/49, t=1.3s)
✅ Robot 2 joints set to: ['0.693', '-0.366', '1.074', '-0.709', '-1.687', '0.589'] rad
✅ Robot 2 joints set to: ['0.693', '-0.366', '1.074', '-0.709', '-1.687', '0.589'] rad
✅ Robot 2 joints set to: ['0.694', '-0.328', '1.078', '-0.750', '-1.684', '0.589'] rad
✅ Robot 2 joints set to: ['0.694', '-0.328', '1.078', '-0.750', '-1.684', '0.589'] rad
✅ Robot 2 joints set to: ['0.694', '-0.280', '1.082', '-0.800', '-1.680', '0.589'] rad
✅ Robot 2 joints set to: ['0.695', '-0.280', '1.082', '-0.800', '-1.680', '0.589'] rad
✅ Robot 2 joints set to: ['0.695', '-0.225', '1.088', '-0.861', '-1.675', '0.589'] rad
✅ Robot 2 joints set to: ['0.696', '-0.225', '1.088', '-0.861', '-1.675', '0.589'] rad
✅ Robot 2 joints set to: ['0.696', '-0.161', '1.094', '-0.929', '-1.670', '0.589'] rad
   📊 Progress:  39% (waypoint 19/49, t=2.5s)
✅ Robot 2 joints set to: ['0.697', '-0.161', '1.094', '-0.929', '-1.670', '0.589'] rad
✅ Robot 2 joints set to: ['0.697', '-0.092', '1.101', '-1.004', '-1.664', '0.589'] rad
✅ Robot 2 joints set to: ['0.698', '-0.092', '1.101', '-1.004', '-1.664', '0.589'] rad
✅ Robot 2 joints set to: ['0.698', '-0.019', '1.108', '-1.083', '-1.658', '0.589'] rad
✅ Robot 2 joints set to: ['0.699', '-0.019', '1.108', '-1.083', '-1.658', '0.589'] rad
✅ Robot 2 joints set to: ['0.700', '0.057', '1.115', '-1.164', '-1.652', '0.589'] rad
✅ Robot 2 joints set to: ['0.700', '0.057', '1.115', '-1.164', '-1.652', '0.589'] rad
✅ Robot 2 joints set to: ['0.701', '0.132', '1.123', '-1.245', '-1.645', '0.589'] rad
✅ Robot 2 joints set to: ['0.701', '0.132', '1.123', '-1.245', '-1.645', '0.589'] rad
   📊 Progress:  57% (waypoint 28/49, t=3.8s)
✅ Robot 2 joints set to: ['0.702', '0.206', '1.130', '-1.324', '-1.639', '0.589'] rad
✅ Robot 2 joints set to: ['0.703', '0.206', '1.130', '-1.324', '-1.639', '0.589'] rad
✅ Robot 2 joints set to: ['0.703', '0.275', '1.137', '-1.399', '-1.633', '0.589'] rad
✅ Robot 2 joints set to: ['0.704', '0.275', '1.137', '-1.399', '-1.633', '0.589'] rad
✅ Robot 2 joints set to: ['0.704', '0.338', '1.143', '-1.467', '-1.628', '0.589'] rad
✅ Robot 2 joints set to: ['0.705', '0.338', '1.143', '-1.467', '-1.628', '0.589'] rad
✅ Robot 2 joints set to: ['0.705', '0.394', '1.149', '-1.527', '-1.623', '0.589'] rad
✅ Robot 2 joints set to: ['0.705', '0.394', '1.149', '-1.527', '-1.623', '0.589'] rad
✅ Robot 2 joints set to: ['0.706', '0.441', '1.153', '-1.578', '-1.619', '0.589'] rad
   📊 Progress:  76% (waypoint 37/49, t=5.0s)
✅ Robot 2 joints set to: ['0.706', '0.441', '1.153', '-1.578', '-1.619', '0.589'] rad
✅ Robot 2 joints set to: ['0.706', '0.479', '1.157', '-1.619', '-1.616', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.479', '1.157', '-1.619', '-1.616', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.507', '1.160', '-1.649', '-1.614', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.507', '1.160', '-1.649', '-1.614', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.526', '1.162', '-1.669', '-1.612', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.526', '1.162', '-1.669', '-1.612', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.537', '1.163', '-1.681', '-1.611', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.537', '1.163', '-1.681', '-1.611', '0.589'] rad
   📊 Progress:  94% (waypoint 46/49, t=6.2s)
✅ Robot 2 joints set to: ['0.707', '0.541', '1.163', '-1.686', '-1.611', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.541', '1.163', '-1.686', '-1.611', '0.589'] rad
✅ Robot 2 joints set to: ['0.707', '0.542', '1.163', '-1.686', '-1.611', '0.589'] rad
   📊 Progress: 100% (waypoint 49/49, t=6.6s)

📖 Verifying final position...
📖 Robot 2 joints: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597']
✅ Trajectory completed!
   📏 Max error: 0.0246 rad (1.41°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597']

✅ Successfully completed: left_arm_standoff_with_beaker

⏳ Pausing 2.0s before next step...

🔄 Step 10/11: left_arm_serving_standoff

🎯 Executing configuration: left_arm_serving_standoff
==================================================
✅ Loaded configuration 'left_arm_serving_standoff' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_serving_standoff
📝 Description: Left arm serving standoff position - current position captured with preserved gripper position
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597']
  ✅ left_arm: Complete configuration (all 6 joints)

🎯 Moving to: left_arm_serving_standoff
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597']
📍 Current: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597']
🎯 Target:  ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.867', '-0.181', '0.244', '-0.044', '0.115']
   📊 Weighted squared sum: 1.611
   📍 Calculated waypoints: 21 → 21 (range: 5-50)
🛡️  Auto-calculated duration: 5.4s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 5.4 seconds
   📍 Waypoints: 21
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 21 → Enhanced waypoints: 41
   📊 Shape: (41, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 21 → 41 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['0.700', '0.543', '1.155', '-1.662', '-1.622', '0.597'] rad
   📊 Progress:   2% (waypoint 1/41, t=0.1s)
✅ Robot 2 joints set to: ['0.699', '0.543', '1.155', '-1.662', '-1.622', '0.597'] rad
✅ Robot 2 joints set to: ['0.699', '0.543', '1.156', '-1.662', '-1.622', '0.597'] rad
✅ Robot 2 joints set to: ['0.695', '0.543', '1.156', '-1.662', '-1.622', '0.597'] rad
✅ Robot 2 joints set to: ['0.692', '0.542', '1.157', '-1.662', '-1.621', '0.596'] rad
✅ Robot 2 joints set to: ['0.684', '0.542', '1.157', '-1.662', '-1.621', '0.596'] rad
✅ Robot 2 joints set to: ['0.677', '0.538', '1.162', '-1.663', '-1.619', '0.595'] rad
✅ Robot 2 joints set to: ['0.663', '0.538', '1.162', '-1.663', '-1.619', '0.595'] rad
✅ Robot 2 joints set to: ['0.649', '0.533', '1.169', '-1.664', '-1.615', '0.593'] rad
   📊 Progress:  22% (waypoint 9/41, t=1.2s)
✅ Robot 2 joints set to: ['0.630', '0.533', '1.169', '-1.664', '-1.615', '0.593'] rad
✅ Robot 2 joints set to: ['0.610', '0.524', '1.181', '-1.666', '-1.610', '0.590'] rad
✅ Robot 2 joints set to: ['0.584', '0.524', '1.181', '-1.666', '-1.610', '0.590'] rad
✅ Robot 2 joints set to: ['0.558', '0.514', '1.195', '-1.669', '-1.603', '0.586'] rad
✅ Robot 2 joints set to: ['0.527', '0.514', '1.195', '-1.669', '-1.603', '0.586'] rad
✅ Robot 2 joints set to: ['0.496', '0.501', '1.213', '-1.672', '-1.595', '0.581'] rad
✅ Robot 2 joints set to: ['0.460', '0.501', '1.213', '-1.672', '-1.595', '0.581'] rad
✅ Robot 2 joints set to: ['0.424', '0.486', '1.233', '-1.676', '-1.585', '0.576'] rad
   📊 Progress:  41% (waypoint 17/41, t=2.3s)
✅ Robot 2 joints set to: ['0.386', '0.486', '1.233', '-1.676', '-1.585', '0.576'] rad
✅ Robot 2 joints set to: ['0.347', '0.469', '1.255', '-1.680', '-1.575', '0.570'] rad
✅ Robot 2 joints set to: ['0.307', '0.469', '1.255', '-1.680', '-1.575', '0.570'] rad
✅ Robot 2 joints set to: ['0.266', '0.453', '1.277', '-1.684', '-1.564', '0.563'] rad
✅ Robot 2 joints set to: ['0.226', '0.453', '1.277', '-1.684', '-1.564', '0.563'] rad
✅ Robot 2 joints set to: ['0.185', '0.436', '1.300', '-1.688', '-1.554', '0.557'] rad
✅ Robot 2 joints set to: ['0.147', '0.436', '1.300', '-1.688', '-1.554', '0.557'] rad
✅ Robot 2 joints set to: ['0.108', '0.420', '1.322', '-1.692', '-1.543', '0.551'] rad
   📊 Progress:  61% (waypoint 25/41, t=3.4s)
✅ Robot 2 joints set to: ['0.072', '0.420', '1.322', '-1.692', '-1.543', '0.551'] rad
✅ Robot 2 joints set to: ['0.037', '0.405', '1.342', '-1.696', '-1.534', '0.546'] rad
✅ Robot 2 joints set to: ['0.005', '0.405', '1.342', '-1.696', '-1.534', '0.546'] rad
✅ Robot 2 joints set to: ['-0.026', '0.392', '1.360', '-1.699', '-1.526', '0.541'] rad
✅ Robot 2 joints set to: ['-0.052', '0.392', '1.360', '-1.699', '-1.526', '0.541'] rad
✅ Robot 2 joints set to: ['-0.078', '0.381', '1.374', '-1.702', '-1.519', '0.537'] rad
✅ Robot 2 joints set to: ['-0.097', '0.381', '1.374', '-1.702', '-1.519', '0.537'] rad
✅ Robot 2 joints set to: ['-0.117', '0.373', '1.385', '-1.704', '-1.513', '0.534'] rad
   📊 Progress:  80% (waypoint 33/41, t=4.4s)
✅ Robot 2 joints set to: ['-0.131', '0.373', '1.385', '-1.704', '-1.513', '0.534'] rad
✅ Robot 2 joints set to: ['-0.144', '0.367', '1.393', '-1.705', '-1.510', '0.532'] rad
✅ Robot 2 joints set to: ['-0.152', '0.367', '1.393', '-1.705', '-1.510', '0.532'] rad
✅ Robot 2 joints set to: ['-0.160', '0.364', '1.397', '-1.706', '-1.508', '0.531'] rad
✅ Robot 2 joints set to: ['-0.163', '0.364', '1.397', '-1.706', '-1.508', '0.531'] rad
✅ Robot 2 joints set to: ['-0.166', '0.362', '1.399', '-1.706', '-1.507', '0.530'] rad
✅ Robot 2 joints set to: ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530'] rad
✅ Robot 2 joints set to: ['-0.167', '0.362', '1.399', '-1.706', '-1.507', '0.530'] rad
   📊 Progress: 100% (waypoint 41/41, t=5.5s)

📖 Verifying final position...
📖 Robot 2 joints: ['-0.160', '0.416', '1.386', '-1.685', '-1.519', '0.589']
✅ Trajectory completed!
   📏 Max error: 0.0592 rad (3.39°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['-0.160', '0.405', '1.387', '-1.685', '-1.519', '0.589']

✅ Successfully completed: left_arm_serving_standoff

⏳ Pausing 2.0s before next step...

🔄 Step 11/11: left_arm_serving_beaker

🎯 Executing configuration: left_arm_serving_beaker
==================================================
✅ Loaded configuration 'left_arm_serving_beaker' from: /home/hafnium/aloha-lite/robot_service/../temp_rules/robot_configurations.json
📋 Configuration: left_arm_serving_beaker
📝 Description: Left arm serving beaker position - current position captured for beaker serving operations
📊 Source: current_robot_state
🎯 Mode: Left arm only (right arm stays steady)
📖 Robot 2 joints: ['-0.160', '0.404', '1.387', '-1.685', '-1.519', '0.589']
  ✅ left_arm: Complete configuration (all 6 joints)

🎯 Moving to: left_arm_serving_beaker
🎯 Execution mode: 🎬 SMOOTH TRAJECTORY

🦾 Left arm (ID 2) target: ['-0.775', '0.072', '1.527', '-1.562', '-1.642', '0.530']

🎯 Executing smooth trajectory for robot 2
============================================================
📖 Reading current position...
📖 Robot 2 joints: ['-0.160', '0.404', '1.387', '-1.685', '-1.519', '0.589']
📍 Current: ['-0.160', '0.404', '1.387', '-1.685', '-1.519', '0.589']
🎯 Target:  ['-0.775', '0.072', '1.527', '-1.562', '-1.642', '0.530']
📊 Adaptive waypoints calculation (Joint 1 gets 2x weighting):
   📐 Joint displacements (J1-J5): ['-0.615', '-0.331', '0.140', '0.123', '-0.123']
   📊 Weighted squared sum: 0.917
   📍 Calculated waypoints: 14 → 14 (range: 5-50)
🛡️  Auto-calculated duration: 3.8s (max_vel: 0.300 rad/s)
📈 Generating trajectory...
   ⏱️  Duration: 3.8 seconds
   📍 Waypoints: 14
   📈 Method: Quintic time scaling
   🔄 Joint 1 gets double waypoint density for smoother motion
✅ Enhanced trajectory generated successfully!
   📊 Base waypoints: 14 → Enhanced waypoints: 27
   📊 Shape: (27, 6) (waypoints x joints)
   ⏱️  Time step: variable (denser for joint 1)
   🎯 Joint 1 interpolation: 14 → 27 points

🎬 Executing enhanced trajectory...
✅ Robot 2 joints set to: ['-0.160', '0.404', '1.387', '-1.685', '-1.519', '0.589'] rad
   📊 Progress:   4% (waypoint 1/27, t=0.1s)
✅ Robot 2 joints set to: ['-0.161', '0.404', '1.387', '-1.685', '-1.519', '0.589'] rad
✅ Robot 2 joints set to: ['-0.162', '0.402', '1.388', '-1.684', '-1.520', '0.589'] rad
✅ Robot 2 joints set to: ['-0.170', '0.402', '1.388', '-1.684', '-1.520', '0.589'] rad
✅ Robot 2 joints set to: ['-0.177', '0.394', '1.391', '-1.681', '-1.523', '0.588'] rad
✅ Robot 2 joints set to: ['-0.194', '0.394', '1.391', '-1.681', '-1.523', '0.588'] rad
   📊 Progress:  22% (waypoint 6/27, t=0.8s)
✅ Robot 2 joints set to: ['-0.211', '0.376', '1.399', '-1.674', '-1.529', '0.584'] rad
✅ Robot 2 joints set to: ['-0.239', '0.376', '1.399', '-1.674', '-1.529', '0.584'] rad
✅ Robot 2 joints set to: ['-0.266', '0.346', '1.411', '-1.663', '-1.540', '0.579'] rad
✅ Robot 2 joints set to: ['-0.303', '0.346', '1.411', '-1.663', '-1.540', '0.579'] rad
✅ Robot 2 joints set to: ['-0.339', '0.307', '1.428', '-1.649', '-1.555', '0.572'] rad
   📊 Progress:  41% (waypoint 11/27, t=1.6s)
✅ Robot 2 joints set to: ['-0.381', '0.307', '1.428', '-1.649', '-1.555', '0.572'] rad
✅ Robot 2 joints set to: ['-0.423', '0.262', '1.447', '-1.632', '-1.572', '0.564'] rad
✅ Robot 2 joints set to: ['-0.467', '0.262', '1.447', '-1.632', '-1.572', '0.564'] rad
✅ Robot 2 joints set to: ['-0.511', '0.214', '1.467', '-1.615', '-1.589', '0.555'] rad
✅ Robot 2 joints set to: ['-0.554', '0.214', '1.467', '-1.615', '-1.589', '0.555'] rad
   📊 Progress:  59% (waypoint 16/27, t=2.3s)
✅ Robot 2 joints set to: ['-0.596', '0.169', '1.486', '-1.598', '-1.606', '0.547'] rad
✅ Robot 2 joints set to: ['-0.632', '0.169', '1.486', '-1.598', '-1.606', '0.547'] rad
✅ Robot 2 joints set to: ['-0.668', '0.130', '1.502', '-1.583', '-1.620', '0.540'] rad
✅ Robot 2 joints set to: ['-0.696', '0.130', '1.502', '-1.583', '-1.620', '0.540'] rad
✅ Robot 2 joints set to: ['-0.723', '0.100', '1.515', '-1.572', '-1.631', '0.535'] rad
   📊 Progress:  78% (waypoint 21/27, t=3.1s)
✅ Robot 2 joints set to: ['-0.740', '0.100', '1.515', '-1.572', '-1.631', '0.535'] rad
✅ Robot 2 joints set to: ['-0.757', '0.082', '1.523', '-1.565', '-1.638', '0.532'] rad
✅ Robot 2 joints set to: ['-0.765', '0.082', '1.523', '-1.565', '-1.638', '0.532'] rad
✅ Robot 2 joints set to: ['-0.772', '0.073', '1.526', '-1.562', '-1.641', '0.530'] rad
✅ Robot 2 joints set to: ['-0.774', '0.073', '1.526', '-1.562', '-1.641', '0.530'] rad
   📊 Progress:  96% (waypoint 26/27, t=3.8s)
✅ Robot 2 joints set to: ['-0.775', '0.072', '1.527', '-1.562', '-1.642', '0.530'] rad
   📊 Progress: 100% (waypoint 27/27, t=3.9s)

📖 Verifying final position...
📖 Robot 2 joints: ['-0.766', '0.103', '1.488', '-1.567', '-1.631', '0.589']
✅ Trajectory completed!
   📏 Max error: 0.0592 rad (3.39°)
Right arm (ID 3): keeping current position

⏱️  Pausing 1.5s to complete movement...

📖 Reading final joint positions...
📖 Robot 2 joints: ['-0.770', '0.103', '1.488', '-1.567', '-1.631', '0.589']

✅ Successfully completed: left_arm_serving_beaker

🎉 Sequence completed! 11/11 steps executed successfully
🔌 Controller disconnected

🎉 All configurations executed successfully!