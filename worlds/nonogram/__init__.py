from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from dataclasses import dataclass
from Options import PerGameCommonOptions, Range
import json
import os
from pathlib import Path
from worlds.generic.Rules import set_rule
from .puzzle_generator.build_puzzle import build_puzzle

class NonogramWeb(WebWorld):
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Nonogram. This guide covers single-player, multiworld, and website.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Spineraks"],
        )
    ]

class WidthOfGrid(Range):
    """
    Width of the Nonogram grid.
    """
    display_name = "Width of Grid"
    range_start = 5
    range_end = 15
    default = 5
    
class HeightOfGrid(Range):
    """
    Height of the Nonogram grid.
    """
    display_name = "Height of Grid"
    range_start = 5
    range_end = 15
    default = 5

@dataclass
class NonogramOptions(PerGameCommonOptions):
    width_of_grid: WidthOfGrid
    height_of_grid: HeightOfGrid

class NonogramWorld(World):
    game: str = "Nonogram"
    options_dataclass = NonogramOptions
    web = NonogramWeb()
    item_name_to_id = {"Nonogram clues": 67}
    location_name_to_id = {f"Progress {i}": 67 + i for i in range(1,101)}
    ap_world_version = "0.1.0"
    
    def create_item(self, name: str, code: int) -> Item:
        return Item(name, ItemClassification.progression, code, self.player)
    
    def get_filler_item_name(self) -> str:
        return "Nonogram clues"    
        
    def generate_early(self):
        self.puzzle = build_puzzle(self.options.width_of_grid.value, self.options.height_of_grid.value, [], self.random)
        num_steps = len(list(set([clue[1] for clue in self.puzzle['G']])))
        
        #items - equal to the number of steps + 1, you start with one
        self.multiworld.itempool += [self.create_item("Nonogram clues", 67) for _ in range(num_steps)]
        self.multiworld.push_precollected(self.create_item("Nonogram clues", 67))
        
        #locations - equal to the number of steps
        menu = Region("Menu", self.player, self.multiworld)
        menu.locations = [
            Location(self.player, f"Step {i}", address=67+i, parent=menu) for i in range(1, num_steps + 1)
        ]
        self.multiworld.regions.append(menu)
        
        #rules - each step requires having that many clues
        for i, loc in enumerate(menu.locations):
            set_rule(loc, lambda state, step=i+1: state.has(f"Nonogram clues", self.player, step))
        
        #victory - have number of clues equal to number of steps
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Nonogram clues", self.player, num_steps)
        
    def fill_slot_data(self):
        return {'puzzle': json.dumps(self.puzzle, separators=(',',':')), 'apworld_version': self.ap_world_version}
    
    def write_spoiler(self, spoiler_handle) -> None:
        spoiler_handle.write(f"Puzzle: {self.puzzle}\n")
        