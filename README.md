# USCM Character Generator
Used for building a new character.

## Prerequisite
If you do not use a pre build binary/installer you need Python with `venv`. 
The application is expected to work with Python 3.12 or newer.

## Setup and run
1. Clone the repo or download the code.

2. Inside the folder `character_gui`, setup virtual environment, install requred packages and activate environment:
```
python -m venv venv/
```
Windows:
```
source venv/Scripts/activate
```
Linux:
```
source venv/bin/activate
```

```
python -m pip install -r requirements.txt
```
3. Start
```
python character_generator.py
```

## Build a binary with python included
Build with PyInstaller:
```
pyinstaller character_generator.py extra_types.py -F -p . --add-data=local_characters/template/:local_characters/template --runtime-hook environment.py --name uscm_character_generator
```
The binary can be found in the `dist`-folder. 
