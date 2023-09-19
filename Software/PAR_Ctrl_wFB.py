from bpdefs import PROPERTIES, GROUP, ASSIGN, WHILE, IF, COMMENT, SHOW, SETCONTROL, ELIF, ELSE, WAIT, Nothing, CheckBox, Text, Button, DropDown, RadioBtns, EditBox, DataDict

steps=[
# Set program properties: PROPERTIES([verbose=False] [,pause=False])
PROPERTIES(verbose="False",pause="False"),
# Collection: GROUP(enabled, label)
GROUP("True","Define registers",
	steps=(
		# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
		ASSIGN("prev_DAC1",
			exp="0"),
		# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
		ASSIGN("Qin_factor",
			exp="1"),
		# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
		ASSIGN("FB_factor",
			exp="1"),
	)
),
# Loop while something is True: WHILE("bool_expression", [,var='elapsed_seconds'] [,mininc="secs"])
WHILE("True",
	steps=(
		# Collection: GROUP(enabled, label)
		GROUP("True","Update variables",
			steps=(
				# Assign a variable to a Data Dictionary entry: ASSIGN('varname', dd=DataDict('group', 'name' [,bool_logged]) [,track=False] [,optvar='varname'] [dlg=Nothing()))])
				ASSIGN("needed_DAC1",
					dd=DataDict('Lamp_PAR_DAC1_Ctrl','UserDefVar')),
				# Assign a variable to a Data Dictionary entry: ASSIGN('varname', dd=DataDict('group', 'name' [,bool_logged]) [,track=False] [,optvar='varname'] [dlg=Nothing()))])
				ASSIGN("PAR_set",
					dd=DataDict('Lamp_PAR_Ctrl','UserDefCon')),
				# Assign a variable to a Data Dictionary entry: ASSIGN('varname', dd=DataDict('group', 'name' [,bool_logged]) [,track=False] [,optvar='varname'] [dlg=Nothing()))])
				ASSIGN("PAR_real",
					dd=DataDict('PPFD_in','Meas')),
			)
		),
		IF("round(float(PAR_set), 4) > 0",
			steps=(
				IF("abs(1 - (prev_DAC1 / needed_DAC1)) >= 0.1",
					steps=(
						# Comment for ui: COMMENT(text)
						COMMENT("PAR change of more than 10%, preadjusting without FB factor "),
						# Print to run log: SHOW([items=(list of items)] or [string='string_to_print'])
						SHOW(string="'PAR change of more than 25%, pre-adjusting without FB factor'"),
						# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
						ASSIGN("FB_factor",
							exp="1"),
						# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
						SETCONTROL("Dac1","min(max(0, needed_DAC1), 5)","float"),
					)
				),
				ELIF("abs(1 - (float(PAR_set) / PAR_real)) >= 0.001",
					steps=(
						# Comment for ui: COMMENT(text)
						COMMENT("Difference between PAR_set and PAR_real of more than 0.1%, adjusting FB factor"),
						# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
						ASSIGN("Qin_factor",
							exp="(PAR_real / FB_factor) / float(PAR_set)"),
						# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
						SETCONTROL("User:Lamp_Qamb_in_Factor","Qin_factor","string"),
						# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
						ASSIGN("FB_factor",
							exp="1/Qin_factor"),
						# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
						SETCONTROL("Dac1","min(max(0, (needed_DAC1 * FB_factor)), 5)","float"),
					)
				),
				ELIF("round(needed_DAC1, 4) != prev_DAC1",
					steps=(
						# Comment for ui: COMMENT(text)
						COMMENT("Small change in needed DAC1, adjusting with current FB factor "),
						# Print to run log: SHOW([items=(list of items)] or [string='string_to_print'])
						SHOW(string="'Small change in needed DAC1, adjusting with current FB_factor'"),
						# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
						SETCONTROL("Dac1","min(max(0, (needed_DAC1 * FB_factor)), 5)","float"),
					)
				),
				# Assign a variable to an expression: ASSIGN('varname', exp="expression" [,dlg=Nothing()])
				ASSIGN("prev_DAC1",
					exp="round(needed_DAC1, 4)"),
			)
		),
		ELSE(steps=(
				# Set a control: SETCONTROL('target', 'value', 'eval' [,opt_target=''])
				SETCONTROL("Dac1","0","float"),
			)
		),
		# Wait for a time duration: WAIT(dur="float" [,units='Seconds' (Seconds|Minutes|Hours)])
		WAIT(dur="6",units="Seconds"),
	)
),
]
