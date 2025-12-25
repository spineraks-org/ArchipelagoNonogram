from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from dataclasses import dataclass
from Options import PerGameCommonOptions, Choice
import json
from pathlib import Path
from worlds.generic.Rules import set_rule

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

class SizeOfGrid(Choice):
    """
    Size of the Nonogram grid.
    """
    display_name = "Size of Grid"
    option_5x5 = 5
    option_10x10 = 10
    default = 5

@dataclass
class NonogramOptions(PerGameCommonOptions):
    size_of_grid: SizeOfGrid

class NonogramWorld(World):
    game: str = "Nonogram"
    options_dataclass = NonogramOptions
    web = NonogramWeb()
    item_name_to_id = {"Nonogram clues": 67}
    location_name_to_id = {f"Progress {i}": 67 + i for i in range(1,101)}
    ap_world_version = "0.0.1"
    
    def create_item(self, name: str, code: int) -> Item:
        return Item(name, ItemClassification.progression, code, self.player)
    
    def get_filler_item_name(self) -> str:
        return "Nonogram clues"    
        
    def generate_early(self):
        #load puzzle data and read number of steps
        data_path = Path(__file__).parent / "data" / f"pl_{self.options.size_of_grid.value}.json"
        with open(data_path, "r", encoding="utf-8") as file:  data = json.load(file)
        self.chosen_puzzle = self.random.choice(data)
        spl = self.chosen_puzzle.split("_")
        num_steps = int(spl[3])
        
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
        return {'puzzle': self.chosen_puzzle, 'apworld_version': self.ap_world_version}
    
    def write_spoiler(self, spoiler_handle) -> None:
        spoiler_handle.write(f"Puzzle: {self.chosen_puzzle}\n")
        