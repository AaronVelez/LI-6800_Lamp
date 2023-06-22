from bpdefs import PROPERTIES, ASSIGN, WHILE, IF, SHOW, SETCONTROL, WAIT, Nothing, CheckBox, Text, Button, DropDown, RadioBtns, EditBox, DataDict

steps=[
# Set program properties: PROPERTIES([verbose=False] [,pause=False])
PROPERTIES(verbose="False",pause="False"),
# Assign a variable to a Data Dictionary entry: ASSIGN('varname', dd=DataDict('group', 'name' [,bool_logged]) [,track=False] [,optvar='varname'] [dlg=Nothing()))])
ASSIGN("PAR_set",
	dd=DataDict('Lamp_PAR_Ctrl','UserDefCon'),
	track=True),
# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
ASSIGN("prev_DAC1",
	exp="100"),
# Assign a variable to a Data Dictionary entry: ASSIGN('varname', dd=DataDict('group', 'name' [,bool_logged]) [,track=False] [,optvar='varname'] [dlg=Nothing()))])
ASSIGN("needed_DAC1",
	dd=DataDict('Lamp_PAR_DAC1_Ctrl','UserDefVar'),
	track=True),
# Loop while something is True: WHILE("bool_expression", [,var='elapsed_seconds'] [,mininc="secs"])
WHILE("True",
	steps=(
		IF("needed_DAC1 >= 0",
			steps=(
				IF("round(needed_DAC1, 4) != prev_DAC1",
					steps=(
						# Print to run log: SHOW([items=(list of items)] or [string='string_to_print'])
						SHOW(string="'TRUE'"),
						# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
						SETCONTROL("Dac1","needed_DAC1","float"),
						# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
						ASSIGN("prev_DAC1",
							exp="round(needed_DAC1, 4)"),
					)
				),
			)
		),
		# Wait for a time duration: WAIT(dur="float" [,units='Seconds' (Seconds|Minutes|Hours)])
		WAIT(dur="6",units="Seconds"),
	)
),
]
