# About
collection of pdf tools

made for personal use & learning purposes 



## Life-hack
### open a new text file - copy code and paste - then save as .bat file
1. Run the venv (change venv-name)
   ```
   @echo off
   CALL .\venv-name\Scripts\activate
   cmd /k
   ```

2. Run the script (change script-name)
   ```
   @echo off
   CALL .\venv\Scripts\activate
   py .\script-name.py
   cmd /k
   ```

