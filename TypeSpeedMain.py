import PySimpleGUI as sg
import os
import datetime
import time 
import pandas as pd

theme_dict = {'BACKGROUND': '#2B475D',
                'TEXT': '#FFFFFF',
                'INPUT': '#F2EFE8',
                'TEXT_INPUT': '#000000',
                'SCROLL': '#F2EFE8',
                'BUTTON': ('#000000', '#C2D4D8'),
                'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

# sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#C7D5E0'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((20,20), (20, 10))
BPAD_LEFT = ((20,10), (0, 10))
BPAD_LEFT_INSIDE = (0, 10)
BPAD_RIGHT = ((10,20), (10, 20))

top_banner = [[sg.Text('  ' + 'TypeSpeedPy'+ ' '*72, font='Any 20', background_color=DARK_HEADER_COLOR),
               sg.Text((datetime.datetime.now()).strftime("%b %d, %Y"), font='Any 20', background_color=DARK_HEADER_COLOR)]]

top1  = [[sg.Text('Questionaire: ', font='Any 20', pad=((5,10), (5, 36))), sg.Text('No File Chosen',size=(20, 2), key = '-FileName-' , pad=((20,10), (20, 30))), sg.Input(key='-FILE-', visible=False, enable_events=True,  pad=((0,0), (5, 36))), sg.FileBrowse(pad=((0,0), (5, 36)))]]
top2  = [[sg.Text('00:00.00',size=(10, 2), font=('Helvetica', 20), pad=((5,5), (10, 5)), key='-CLOCK-'), sg.T(' ' * 3), sg.Button('Start/Stop', pad=((0,20), (5, 36)), focus=True), sg.T(' ' * 25)]]

block_2 = [[sg.Text('Question', size=(15, 1), font='Any 20', key = '-QN-')],
            [sg.Multiline(size=(58,15), disabled = True, key='INPUTSTR1', pad = (8,0))],
            [sg.Button(' >> ', pad=((405,0), (5, 36)))]]

block_3 = [[sg.Text('Block 3', font='Any 20')],
            [sg.Input(), sg.Text('Some Text')],      ]

block_4 = [[sg.Text('Answer', font='Any 20')],
            [sg.Multiline(size=(58,15), key='INPUTSTR2', pad = (8,0))],
            [sg.Button('Finish', pad=((390,0), (5, 36)))]]

layout = [[sg.Column(top_banner, size=(960, 60), pad=(0,0), background_color=DARK_HEADER_COLOR)],

          [sg.Column([[sg.Column(top1, size=(450,60), pad=BPAD_LEFT_INSIDE)],
                      ], pad=BPAD_LEFT, background_color=BORDER_COLOR),
           sg.Column(top2, size=(450, 60), pad=BPAD_RIGHT)],
          
          [sg.Column([[sg.Column(block_2, size=(450,320), pad=BPAD_LEFT_INSIDE)],
                      ], pad=BPAD_LEFT, background_color=BORDER_COLOR),
           sg.Column(block_4, size=(450, 320), pad=BPAD_RIGHT)]]

timer_running, counter = False, 0

window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)
window.Finalize()

count = 0
attemptlist = allstr = fieldnames = []
str2state = True
fileflag = False
window['INPUTSTR2'].update(disabled=str2state)

#Event Loop
while True:
  event, values = window.read(timeout=10)

  #exit without file i/o operations
  if event == sg.WIN_CLOSED or event == 'Finish' and not fileflag:
    break
  
  #exit after performing file i/o operations
  if event == sg.WIN_CLOSED or event == 'Finish' and fileflag:
    
    csv_input = pd.read_csv(values['-FILE-'])

    #pandas doesnt accept non square entires as it is in df
    #So we add '' values to the unfinished question's attempt list
    for i in range(0, len(allstr) - len(attemptlist)):
      attemptlist.append('')
    
    csv_input['Attempt:' + str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))] = attemptlist
    csv_input.to_csv(values['-FILE-'], index=False)
    attemptlist = []
    
    break
  
  if event == '-FILE-' and not fileflag:

    #considering if -File- event was called at beginning    
    window['-FileName-'].update(os.path.basename(values['-FILE-']))
    
    csv_input = pd.read_csv(values['-FILE-'])
    allstr = csv_input['Questions']
    allstr = allstr.values.tolist()

    window['-QN-'].update('Question ' + str(1) + '/' + str(len(allstr)))
    
    window['INPUTSTR1'].update(allstr[0])
    fileflag = True

  if event == '-FILE-' and fileflag and (len(attemptlist) != 0):
    
    #considering if -File- event was called at middle/end of practice; save progress
    window['-FileName-'].update(os.path.basename(values['-FILE-']))
    
    csv_input = pd.read_csv(values['-FILE-'])
    allstr = csv_input['Questions']
    allstr = allstr.values.tolist()

    window['-QN-'].update('Question ' + str(1) + '/' + str(len(allstr)))
    
    window['INPUTSTR1'].update(allstr[0])

    count = 0
    window[' >> '].update(disabled = False)
    csv_input = pd.read_csv(values['-FILE-'])
    
    #pandas doesnt accept non square entires as it is in df
    #So we add '' values to the unfinished question's attempt list

    for i in range(0, len(allstr) - len(attemptlist)):
      attemptlist.append('')
      
    csv_input['Attempt#' + str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))] = attemptlist
    csv_input.to_csv(values['-FILE-'], index=False)
    attemptlist = []
    counter = 0
    window['-CLOCK-'].update('00:00.00')
    
  if event == 'Start/Stop':
    timer_running = not timer_running
    if(fileflag == True):
      str2state = not(str2state)
      window['INPUTSTR2'].update(disabled = str2state)

  if (event == ' >> ' and fileflag and not timer_running):

    if(count + 1 < len(allstr)):
      count = count + 1
      window['-QN-'].update('Question ' + str(count + 1) + '/' + str(len(allstr)))
      window['INPUTSTR1'].update(allstr[count])
      attemptlist.append('{:02d}:{:02d}.{:02d}'.format((counter // 45) // 60, (counter // 45) % 60, counter % 100))
      counter = 0      
    else:
      window['INPUTSTR1'].update('End of Questionnaire!')
      attemptlist.append('{:02d}:{:02d}.{:02d}'.format((counter // 45) // 60, (counter // 45) % 60, counter % 100))
      count = counter = 0
      window[' >> '].update(disabled = True)


  if timer_running:
    #45 is a number used to best imitate one second in comparison with global time
    window['-CLOCK-'].update('{:02d}:{:02d}.{:02d}'.format((counter // 45) // 60, (counter // 45) % 60, counter % 100))
    counter += 1
    
    
window.close()
