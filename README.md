# XCP-Server-Tools
A program that parses the handbook from DanghengServer or LunarCore and provides a convenient interface for composing commands.

## Features
- Support for DanhengServer and LunarCore servers
  - Ability to work with new versions of the game without updating the program. Just give it a new Handbook and it will find the IDs of all new items by itself.
- Creating relics with the right affixes
- Convenient automatic selection of subaffixes based on priorities
- Easily find and give away various items
- Easily find and issue virtual universe blessings and miracles. They are sorted by universe type, rarity and path
- Create characters and customize their properties
- Support item names in any language supported by the game. Simply specify a language in the server settings to create a Handbook in that language and then pass it to this program.
- Localization in English and Russian, other languages can also be added.


## Soon to be realized:
- Overlaying all effects, including character and food effects
- List of starting and frequently used commands, as well as a list of custom commands
- Execution of commands on the server if someone develops OpenCommand Plugin. I don't know C# or Java.
- Mission Management
- Scenes management for DanhengServer


## Running

It requires a guide, which can be found in the root folder of the LunarCore server or the config folder of the Danheng server after their first run. This allows you not to update XCP-Tools when a new version of the game is released, but just give it a new handbook and it will find the IDs of new items on its own. To make it work, simply place `Handbook.txt` next to `DanghengServer_Tools.exe`, or manually select the desired Handbook when you run it.

---
![image](https://github.com/user-attachments/assets/e0024010-ea40-4f36-9f35-434dbe0ba044)
![image](https://github.com/user-attachments/assets/2f2eb206-8b3f-448c-b1b8-ce85602ab03d)

