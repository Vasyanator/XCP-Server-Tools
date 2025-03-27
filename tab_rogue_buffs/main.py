#rogue_buffs_main.py
import tkinter as tk
from tkinter import ttk
from tkinter import VERTICAL, RIGHT, LEFT, Y, StringVar, messagebox

from tab_rogue_buffs.virtual_universe_blessings import VirtualUniverseBlessingsTab
from tab_rogue_buffs.virtual_universe_miracles import VirtualUniverseMiraclesTab
from tab_rogue_buffs.virtual_universe_extras import VirtualUniverseMiscTab

class RogueBuffsTab:
    def __init__(self, notebook, rogue_buffs_su, rogue_buffs_food, rogue_buffs_various, rogue_buffs_from_entities, rogue_buffs_other, rogue_buffs_unknown, rogue_miracles, command_manager, localization):
        self.notebook = notebook
        self.rogue_buffs_su = rogue_buffs_su
        self.rogue_buffs_food = rogue_buffs_food
        self.rogue_buffs_various = rogue_buffs_various
        self.rogue_buffs_from_entities = rogue_buffs_from_entities
        self.rogue_buffs_other = rogue_buffs_other
        self.rogue_buffs_unknown = rogue_buffs_unknown
        self.rogue_miracles = rogue_miracles
        self.command_manager = command_manager
        self.localization = localization

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=localization["RogueBuffs"])
        self.init_tab()

    def init_tab(self):
        # Create notebook for sub-tabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # Create "Virtual Universe Blessings" tab
        self.virtual_universe_blessings_tab = VirtualUniverseBlessingsTab(
            self.sub_notebook,
            self.rogue_buffs_su,
            self.command_manager,
            self.localization
        )

        # Create "Virtual Universe Miracles" tab
        self.virtual_universe_miracles_tab = VirtualUniverseMiraclesTab(
            self.sub_notebook,
            self.rogue_miracles,
            self.command_manager,
            self.localization
        )
        self.virtual_universe_misc_tab = VirtualUniverseMiscTab(
            self.sub_notebook,
            self.rogue_buffs_food,
            self.rogue_buffs_various,
            self.rogue_buffs_from_entities,
            self.rogue_buffs_other,
            self.command_manager,
            self.localization
        )
    
