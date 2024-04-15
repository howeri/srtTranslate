# Automation of SRT Translation with ChatGPT
This project automates ChatGPT translation for SRT files. Originally, users had to manually segment SRT texts into smaller portions for translation due to ChatGPT's limitation with larger texts. Additionally, the translated output often resulted in a reduction in the number of lines, disrupting the timing of the SRT file.
In this code, it begins by extracting subtitles. Every 20 lines, it runs ChatGPT for translation. Then, it ensures that the output line count remains consistent. If not, the code repeatedly prompts ChatGPT to retry until the maximum limit is reached. If issue persists, the code marks problematic lines with "***" for manual handling by the user. The process iterates until the translation is complete.

## Examples:
1. Create API key from OpenAI website
2. Download repo and open main.py
3. Add API key and check if the question in "prompt" makes sense.
4. Install OpenAI with pip
6. Run `python3 main.py --language [Language] --intputFile [intputFileWithoutExtension]`
7. The output file name will be [OrigianlFileName_new_Language]

## Note:
For questions, queries and bug reports, please feel free to contact: huangeric@ucla.edu
