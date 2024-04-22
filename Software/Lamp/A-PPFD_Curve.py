from bpdefs import PROPERTIES, GROUP, ASSIGN, IF, DIALOG, RETURN, ELSE, RUN, SETCONTROL, LOOP, ELIF, WAIT, LOG, Nothing, CheckBox, Text, Button, DropDown, RadioBtns, EditBox, DataDict

steps=[
# Set program properties: PROPERTIES([verbose=False] [,pause=False])
PROPERTIES(verbose="True",pause="False"),
# Collection: GROUP(enabled, label)
GROUP("True","Check log file",
	steps=(
		# Assign a variable to a Status Dictionary entry: ASSIGN('varname', sd='status_name' [,track=False] [,optvar='varname'] [dlg=Nothing()])
		ASSIGN("LogOpen",
			sd="LOG:IsFileOpen"),
		IF("LogOpen",
			steps=(
				# Assign a variable to a Status Dictionary entry: ASSIGN('varname', sd='status_name' [,track=False] [,optvar='varname'] [dlg=Nothing()])
				ASSIGN("LogName",
					sd="LOG:FileName"),
				# Open a dialog: DIALOG(title=string [,sub=string] [,text=string] [,items=list_of_edit_items] [,buttons=list_of_buttons] [var=pressed_btn_name])
				DIALOG(title="'Ready to start'",
					sub="'A-PAR curve'",
					text="'Loging to:\\n' + LogName",
					buttons="'Continue','Cancel'",
					var="button1"),
				IF("button1 == 'Cancel'",
					steps=(
						RETURN(),
					)
				),
			)
		),
		ELSE(steps=(
				# Open a dialog: DIALOG(title=string [,sub=string] [,text=string] [,items=list_of_edit_items] [,buttons=list_of_buttons] [var=pressed_btn_name])
				DIALOG(title="'Error'",
					sub="'No log file open'",
					text="'Open log file and try again'",
					buttons="'Cancel'",
					var="button2"),
				RETURN(),
			)
		),
	)
),
# Collection: GROUP(enabled, label)
GROUP("True","Settings",
	steps=(
		# Collection: GROUP(enabled, label)
		GROUP("True","Def. environment settings",
			steps=(
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Low_flow_set",
					exp="275"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Medium_flow_set",
					exp="575"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("High_flow_set",
					exp="775"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("VPD_set",
					exp="1.2"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("CO2s_set",
					exp="400"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Fan_rpm_set",
					exp="9000"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Tleaf_set",
					exp="25"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Pressure_set",
					exp="0.05"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Dac2_set",
					exp="1.1658"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("PAR_set",
					exp="260"),
			)
		),
		# Collection: GROUP(enabled, label)
		GROUP("True","A-PPFD settings",
			steps=(
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("Low_flow_PAR_end",
					exp="121"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("High_flow_PAR_start",
					exp="401"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("PAR_levels",
					exp="0,40,80,120,260,400,700,1000,1500,2000"),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("PAR_wait",
					exp="6,10,14,12,10,6,5,5,5,5"),
			)
		),
	)
),
# Collection: GROUP(enabled, label)
GROUP("True","Run PAR_Ctrl.py script",
	steps=(
		# Launch a BP: RUN("filename")
		RUN("\"/home/licor/apps/PAR_Ctrl_wFB.py\""),
	)
),
# Collection: GROUP(enabled, label)
GROUP("True","Set def. environment",
	steps=(
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Flow","Low_flow_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("VPD_leaf","VPD_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("CO2_s","CO2s_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Fan_rpm","Fan_rpm_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Tleaf","Tleaf_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Pressure","Pressure_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Power5","On",""),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Dac2","Dac2_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("User:Lamp_PAR_Ctrl","PAR_set","string"),
	)
),
# Collection: GROUP(enabled, label)
GROUP("True","A-PAR_Curve",
	steps=(
		# Loop n times: LOOP(count="int_exp" [,var=''] [,mininc=''])
		LOOP(count="len(PAR_levels)",
			var="i",
			steps=(
				# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
				SETCONTROL("User:Lamp_PAR_Ctrl","PAR_levels[i]","string"),
				# Collection: GROUP(enabled, label)
				GROUP("True","Set flow",
					steps=(
						IF("PAR_levels[i]<Low_flow_PAR_end",
							steps=(
								# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
								SETCONTROL("Flow","Low_flow_set","float"),
							)
						),
						ELIF("PAR_levels[i]<High_flow_PAR_start",
							steps=(
								# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
								SETCONTROL("Flow","Medium_flow_set","float"),
							)
						),
						ELSE(steps=(
								# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
								SETCONTROL("Flow","High_flow_set","float"),
							)
						),
					)
				),
				# Wait for statility: WAIT(min="float_seconds", max="float_seconds" [,early=False])]
				WAIT(min="PAR_wait[i]*60",max="PAR_wait[i]*2*60",early="False"),
				# Log a data record: LOG([avg='Default'] [,match='Default'] [,matchH2O='Default'] [,flr='Default'] [flash='Default'])
				LOG(),
			)
		),
	)
),
# Collection: GROUP(enabled, label)
GROUP("True","Set def. environment",
	steps=(
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Flow","Low_flow_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("VPD_leaf","VPD_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("CO2_s","CO2s_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Fan_rpm","Fan_rpm_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Tleaf","Tleaf_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Pressure","Pressure_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Power5","On",""),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("Dac2","Dac2_set","float"),
		# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
		SETCONTROL("User:Lamp_PAR_Ctrl","PAR_set","string"),
	)
),
]
