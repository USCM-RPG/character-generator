# USCM Character Generator

Application for creating characters for the USCM roleplaying game.

## Installation

### Prerequisites

- UV Python package manager -> installed automatically if not available.
- Windows, Linux, macOS

### Quick Start

Download the content of this repo.

Install UV yourself or let the script below help you.

#### Windows
run `Start_USCM_Character_Generator_for_Windows.bat`.

#### Linux / macOS

***First time only:***
```bash
chmod +x Start_USCM_Character_Generator_for_linux_or_Mac.sh
```

***Then:***
```bash
./Start_USCM_Character_Generator_for_linux_or_Mac.sh
```
Next time you start your terminal, UV will be detected and will not ask to be installed again.

### Getting Started

1. **Launch the application** using the appropriate script for your OS
2. **Create a new character** by clicking "Create New Character", or load an existing character from your save folder
3. **Fill in player info**: Name, platoon, rank, age, and specialization
4. **Distribute stats**: Assign attributes, skills, expertises, and traits
6. **Save** your character
7. **Export the character to PDF** when it is finished and send it to one of the game masters

### Tips

- Keep an eye on the available XP and attribute points. They should be at zero when you are done.
- See the Gameworld reference for details and the source of truth. Not all details are covered by the application. 
- Save you character while working so your choices are not lost.
- If you want to edit a saved character that is still under construction, select it from the list, check *Admin Mode* to allow full edit, then click *Edit Character*. 

## 🔧 For Developers

### Character Template

- A character (and the template) is stored as a JSON file that is divided into a general section
  followed by sections for all attributes, skills, experise, and traits.
- Each item typically contains the current value, cost, and tooltip.
- Some items are also tagged as "extended" which is a way to filter what is to be shown depending on the current world setting (for example navy, colony, and other military).
- Some items have the possibility to describe dependencies such as "Not Canary" or "Charisma < 3".
- Currently the dependencies can only be listed as AND. OR is not supported.
- Some items can result in bonuses. Currently they are only used as a printout for the base stats in the GUI.

## Troubleshooting

### Characters not saving

- Check that the save location has the proper write permissions
- Verify that the character name doesn't contain invalid characters (spaces work, but avoid special symbols)

### PDF export failing

- Ensure a PDF reader is installed on your system

## Resources

- **Website**: https://www.uscm.se

