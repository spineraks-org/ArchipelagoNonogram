from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from .Options import NonograhmmOptions
import json
import os
from pathlib import Path
from worlds.generic.Rules import set_rule
from .puzzle_generator.build_puzzle import build_puzzle
from typing import Dict, Any, Optional

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

class NonograhmmLocation(Location):
    game: str = "Nonograhmm"

    def __init__(self, player: int, name: str, step: int, address: Optional[int], parent):
        super().__init__(player, name, address, parent)
        self.nonograhmm_step = step

class NonograhmmWorld(World):
    game: str = "Nonograhmm"
    options_dataclass = NonograhmmOptions
    web = NonograhmmWeb()
    item_name_to_id = {"Nonograhmm clues": 67, ":)": 69}
    location_name_to_id = {f"{i} correct": 67 + i for i in range(1,401)}
    ap_world_version = "0.2.2"
    
    def create_item(self, name: str) -> Item:
        return Item(name, ItemClassification.progression, self.item_name_to_id[name], self.player)
    
    def get_filler_item_name(self) -> str:
        return ":)"   
    
    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"puzzle": slot_data["puzzle"]} 
        
    def generate_early(self):
        if hasattr(self.multiworld, "re_gen_passthrough"):
            self.puzzle = json.loads(self.multiworld.re_gen_passthrough[self.game]["puzzle"])
        else:
            self.puzzle = build_puzzle(self.options, self.random)
        if not self.puzzle:
            raise Exception("Failed to generate a valid Nonograhmm puzzle aaaaaaaaaaaaaa.")
        self.clue_list = sorted(list(set([clue[1] for clue in self.puzzle['G']]+[0])))
        self.num_steps = len(self.clue_list) - 1
        
    def create_items(self):
        #items - equal to the number of steps + 1, you start with one
        self.multiworld.itempool += [self.create_item("Nonograhmm clues") for _ in range(self.num_steps)]
        self.multiworld.push_precollected(self.create_item("Nonograhmm clues"))
    
    def create_regions(self):
        #locations - equal to the number of steps
        self.menu = Region("Menu", self.player, self.multiworld)
        self.menu.locations = [
            NonograhmmLocation(self.player, f"{C} correct", step=i, address=67+C, parent=self.menu) 
                for i, C in enumerate(self.clue_list[1:], start=1)
        ]
        self.multiworld.regions.append(self.menu)
    
    def set_rules(self):
        #rules - each step requires having that many clues
        for i, loc in enumerate(self.menu.locations):
            set_rule(loc, lambda state, step=loc.nonograhmm_step: state.has(f"Nonograhmm clues", self.player, step))
        
        #victory - have number of clues equal to number of steps
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Nonograhmm clues", self.player, self.num_steps)
        
    def fill_slot_data(self):
        return {'puzzle': json.dumps(self.puzzle, separators=(',',':')), 
                'apworld_version': self.ap_world_version,
                'enables_nonograhmm_hints': self.options.enables_nonograhmm_hints.value}
    
    def write_spoiler(self, spoiler_handle) -> None:
        spoiler_handle.write(f"Puzzle: {self.puzzle}\n")
        