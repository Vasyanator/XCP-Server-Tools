# XCP-Server-Tools
A program that parses the handbook from DanghengServer or LunarCore and provides a convenient interface for composing commands.

## Features
- Support for DanhengServer and LunarCore servers
  - Ability to work with new versions of the game without updating the program. Just give it a new Handbook and it will find the IDs of all new items by itself.
- Use the Handbook in your language
- Creating relics with specific affixes
  - Subaffixes levels are available for HotaruSR
  - Convenient automatic selection of subaffixes based on priorities
- Easily find and give away various items
- Easily find and issue virtual universe blessings and miracles. They are sorted by universe type, rarity and path
- Getting characters and changing their properties
- Localization in English and Russian, other languages can also be added.

## SUbaffix priority list:
Allows you to automatically select additional characteristics for relics. Add 5-6 desired characteristics by specifying the priority. Then click the “Select additional characteristics” button. The 4 characteristics with the highest priority that do not conflict with MainAffix will be selected, and their enhancements will be similarly distributed depending on the priority, up to a maximum of 5 in total.
![image](https://github.com/user-attachments/assets/76646d91-d4c9-4997-9af8-4c3a81c29d9c)


## Soon to be realized:
- Execution of commands on the server if someone develops OpenCommand Plugin. I don't know C# or Java.
- Mission Management
- Scenes management for DanhengServer


## Running

It requires a handbook, which can be found in the root folder of the LunarCore server or the config folder of the Danheng server after their first run. This allows you not to update XCP-Tools when a new version of the game is released, just give it a new handbook and it will find the IDs of new items on its own. Select the desired Handbook when starting the program, or in the settings.

---

# Screenshots
![image](https://github.com/user-attachments/assets/0c527879-5989-4d29-abc6-27fcef096ca8)

![image](https://github.com/user-attachments/assets/a43a56a9-34e9-4531-af9e-b2c688cbe1de)
![image](https://github.com/user-attachments/assets/1eba7b27-ae5e-41b1-aee2-86363f47622d)
![image](https://github.com/user-attachments/assets/ec006742-e8cb-40de-bb3f-3de1128a022d)
![image](https://github.com/user-attachments/assets/7fbe933a-bd63-4e15-8752-219386ee629e)
![image](https://github.com/user-attachments/assets/68c90d5a-d197-4377-9920-8060b80b9a9e)




