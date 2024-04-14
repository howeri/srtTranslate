from openai import OpenAI
import shutil
import os
import argparse
import re

key = ""

def runChatGPT(language, subtitles_N_i):
    # Put index in front of each line and join list to one string
    N_i = len(subtitles_N_i)
    subtitles_N_i_join=''
    for index, item in enumerate(subtitles_N_i):
        subtitles_N_i_join += f"{index}: {item}"

    # ChatGPT loop
    client = OpenAI(api_key=key)
    prompt = f'Translate the following to {language} while maintaining the number of lines. Use 존댓말.\n' # For Korean only
    # prompt = f'Translate the following to {language} while maintaining the number of lines: \n' # For other languages
    prompt += subtitles_N_i_join
    chat_log = []
    chat_log.append({"role": "user", "content": prompt})

    trialLimit = 2
    trial = 1
    while trial<=trialLimit:
        # Run ChatGPT
        response= client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = chat_log
        )
        assistant_response = response.choices[0].message.content
        trial += 1

        # Remove unrelated entries
        assistant_response_list = assistant_response.split("\n")
        assistant_response_list_corrected = []
        for i, s in enumerate(assistant_response_list):
            if s.startswith(str(i)):
                assistant_response_list_corrected.append(s)

        # If number of lines is correct, return it as string. If not, try again.
        assistant_response_corrected = '\n'.join(assistant_response_list_corrected)
        if len(assistant_response_list_corrected)==N_i:
            return assistant_response_corrected
        else: 
            chat_log.append({"role": "assistant", "content": assistant_response_corrected})
            chat_log.append({"role": "user", "content": f"Try again and make sure all 0 to {len(subtitles_N_i)-1} lines are still there."})
    
    # If number of lines still wrong, add/combine lines and add *** for easy tracking. Later fix manually.
    print('!!! Number of lines still differs after max number of trials!!! Fixing number of lines and adding *** for easy tracking...')
    pattern = r'(\d+): '
    assistant_response_star = re.sub(pattern, r'\1: ***', assistant_response)
    if len(assistant_response.split("\n"))<N_i:
        for i in range(N-len(assistant_response.split("\n"))-1,-1,-1):
            assistant_response_star += '\n'+str(19-i)+': ***'
    elif len(assistant_response.split("\n"))>N_i:
        index = assistant_response_star.find("\n20: ")
        assistant_response_star = assistant_response_star[0:index]
    return assistant_response_star

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '♡' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")

# Define arguments
parser = argparse.ArgumentParser(description='Eric code to make Lucy work faster.')
parser.add_argument('--language', type=str, help='Language to translate to')
parser.add_argument('--inputFile', type=str, help='File to translate')
args = parser.parse_args()
language = args.language
inputFile = args.inputFile

# Extract subtitles
with open(inputFile+'.srt', 'r') as file:
    lines = file.readlines()
subtitles = []
next_line_is_sub = 0
for line in lines:
    if next_line_is_sub == 1:
        subtitles.append(line)
        next_line_is_sub = 0
    elif line[0:3]=='00:':
        next_line_is_sub = 1
count = len(subtitles)
if int(lines[-3].strip()) != count:
    print('!!! Last subtitile index is different from the number of subtitles!!! Terminating...')
    exit()

# Translate every N subtitles
N = 20
subtitles_translated = ''
for i in range(0, count, N):
    progress_bar(i+1, count)
    if i != count//N*N: # Normal case
        subtitles_N_i = subtitles[i: i+N]
        subtitles_N_translated_i = runChatGPT(language, subtitles_N_i)
        subtitles_translated += subtitles_N_translated_i +'\n '
      
    else: # Last group case 
        subtitlesRemaining_i = subtitles[i:i+count%N]
        subtitlesRemaining_translated_i = runChatGPT(language, subtitlesRemaining_i)
        subtitles_translated += subtitlesRemaining_translated_i
progress_bar(1, 1)

# Remove indeces
pattern = r'(\d+): '
subtitles_translated = re.sub(pattern, '', subtitles_translated)

# Save temp files
subtitles_translated = subtitles_translated.split("\n")
with open("temp/before.txt", "w") as file:
    for item in subtitles:
        file.write(f"{item}") # already have \n
with open("temp/after.txt", "w") as file:
    for item in subtitles_translated:
        file.write(f"{item}\n") # doesnt have \n

# Check if the number of subtitiles changed
count_translated = len(subtitles_translated)
if count != count_translated:
    print('!!! Number of subtitile after translating is different from that before!!! Terminating...')
    exit()

# Copy original srt and replace with new subtitles 
with open(inputFile+'.srt', "r") as file:
    lines = file.readlines()

for i, line in enumerate(lines):
    for s, sub in enumerate(subtitles):
        if sub in line:
            lines[i] = subtitles_translated[s] +'\n'

output_file = inputFile + '_new_' + language
with open(output_file+'.srt', "w") as file:
    file.writelines(lines)
