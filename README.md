# USCM Character Generator

Application for creating characters for USCM roleplaying game.

## Installation

### Prerequisites

- UV python package manager -> installed automatically if not available.
- Windows, macOS, Linux

### Quick Start

Download the content of this repo.

Install UV yourself or let the script below help you.

#### Windows
run `Start_USCM_Character_Generator_for_Windows.bat`.

#### Linux / macOS

# First time only:
```bash
chmod +x Start_USCM_Character_Generator_for_linux_or_Mac.sh
```

# Then:
```bash
./Start_USCM_Character_Generator_for_linux_or_Mac.sh
```
Next time you start your terminal UV will be detected and will not ask to be installed again.

### Getting Started

1. **Launch the application** using the appropriate script for your OS
2. **Create a new character** by clicking "Create New Character" or load an existing character from your save folder
3. **Fill in player info**: Name, platoon, rank, age, and specialization
4. **Distribute stats**: Assign attributes, skills, expertises and traits
6. **Save** your character
7. **Export to PDF** when you are ready and send to one of the game masters

### Tips

- Keep an eye on the available XP and attribute points. They should be at zero when you are done.
- See the Gameworld reference for details. Not all details are covered by the application. 
- Save you character while working so your choices are not lost.
- If you are loading a character that is under construction, choose "admin-mode" to allow full edit. 

## 🔧 For Developers

### Character Template

A character (and the template) is stored as a JSON file that is divided into a general section
followed by sections for all attributes, skills, experise and traits.
Each item typically contains the current value, cost and tooltip.
Some items are also tagged as "extended" which is a way to filter what is to be visible depending on the current world setting.
Some items have the possibility to describe dependencies such as "Not Canary" or "Charisma < 3".
Currently the dependencies can only be listed as AND. OR is not supported.
Some items can result in bonuses. Currently they are only used as a printout for the base stats.

## Troubleshooting

### Characters not saving

- Check that the save location has proper write permissions
- Verify that the character name doesn't contain invalid characters (spaces work, but avoid special symbols)

### PDF export failing

- Ensure a PDF reader is installed on your system

## Resources

- **Website**: https://www.uscm.se

