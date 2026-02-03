from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from dataclasses import dataclass
from Options import OptionSet, PerGameCommonOptions, Range
import json
import os
from pathlib import Path
from worlds.generic.Rules import set_rule
from .puzzle_generator.build_puzzle import build_puzzle
import typing

class NonograhmmWeb(WebWorld):
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Nonograhmm. This guide covers single-player, multiworld, and website.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Spineraks"],
        )
    ]

class WidthOfGrid(Range):
    """
    Width of the Nonograhmm grid.
    """
    display_name = "Width of Grid"
    range_start = 5
    range_end = 15
    default = 5
    
class HeightOfGrid(Range):
    """
    Height of the Nonograhmm grid.
    """
    display_name = "Height of Grid"
    range_start = 5
    range_end = 15
    default = 5
    
class ClueTypes(OptionSet):
    """
    Clues that a '?' may get replaced by before a number is shown.
    It is recommended to first play without these extra clue types.
    Put them in the yaml like this: ['Ω', 'E', '/']
    Ω: number is odd
    E: number is even
    /: number is one of two possible values (e.g., "2/4" means the number is either 2 or 4)
    -: number is at most a certain value (e.g., "3-" means the number is 1, 2, or 3)
    +: number is at least a certain value (e.g., "3+" means the number is 3 or greater)
    """

    display_name = "Clue types"
    valid_keys = ['Ω', 'E', '/', '-', '+']
    default = [] 

@dataclass
class NonograhmmOptions(PerGameCommonOptions):
    width_of_grid: WidthOfGrid
    height_of_grid: HeightOfGrid
    clue_types: ClueTypes
    
class NonograhmmLocation(Location):
    game: str = "Nonograhmm"

    def __init__(self, player: int, name: str, step: int, address: typing.Optional[int], parent):
        super().__init__(player, name, address, parent)
        self.nonograhmm_step = step

class NonograhmmWorld(World):
    game: str = "Nonograhmm"
    options_dataclass = NonograhmmOptions
    web = NonograhmmWeb()
    item_name_to_id = {"Nonograhmm clues": 67}
    location_name_to_id = {f"{i} correct": 67 + i for i in range(1,401)}
    ap_world_version = "0.2.0"
    
    def create_item(self, name: str) -> Item:
        return Item(name, ItemClassification.progression, self.item_name_to_id[name], self.player)
    
    def get_filler_item_name(self) -> str:
        return "Nonograhmm clues"    
        
    def generate_early(self):
        self.puzzle = build_puzzle(self.options, self.random)
        clue_list = sorted(list(set([clue[1] for clue in self.puzzle['G']]+[0])))
        num_steps = len(clue_list) - 1
        
        #items - equal to the number of steps + 1, you start with one
        self.multiworld.itempool += [self.create_item("Nonograhmm clues") for _ in range(num_steps)]
        self.multiworld.push_precollected(self.create_item("Nonograhmm clues"))
        
        #locations - equal to the number of steps
        menu = Region("Menu", self.player, self.multiworld)
        menu.locations = [
            NonograhmmLocation(self.player, f"{C} correct", step=i, address=67+C, parent=menu) 
                for i, C in enumerate(clue_list[1:], start=1)
        ]
        self.multiworld.regions.append(menu)
        
        #rules - each step requires having that many clues
        for i, loc in enumerate(menu.locations):
            set_rule(loc, lambda state, step=loc.nonograhmm_step: state.has(f"Nonograhmm clues", self.player, step))
        
        #victory - have number of clues equal to number of steps
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Nonograhmm clues", self.player, num_steps)
        
    def fill_slot_data(self):
        return {'puzzle': json.dumps(self.puzzle, separators=(',',':')), 'apworld_version': self.ap_world_version}
    
    def write_spoiler(self, spoiler_handle) -> None:
        spoiler_handle.write(f"Puzzle: {self.puzzle}\n")
        