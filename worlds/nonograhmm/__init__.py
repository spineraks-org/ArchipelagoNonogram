from worlds.AutoWorld import WebWorld, World
from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from .Options import NonograhmmOptions
import json
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
    item_name_to_id = {"Nonograhmm clues": 67}
    for i in range(50):
        item_name_to_id["No" + "no" * i] = 68 + i
    location_name_to_id = {f"{i} correct": 67 + i for i in range(1,25*25+1)}
    ap_world_version = "0.3.1"
    
    def create_item(self, name: str) -> Item:
        return Item(name, ItemClassification.progression if name == "Nonograhmm clues" else ItemClassification.filler, 
                    self.item_name_to_id[name], self.player)
    
    def get_filler_item_name(self) -> str:
        return self.random.choices(["No" + "no" * i for i in range(50)], weights=[0.5**i for i in range(50)])[0]   
    
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
        self.num_cells = self.options.width_of_grid.value * self.options.height_of_grid.value
        
    def create_items(self):
        #items - equal to the number of steps + 1, you start with one
        self.multiworld.push_precollected(self.create_item("Nonograhmm clues"))
        self.multiworld.itempool += [self.create_item("Nonograhmm clues") for _ in range(self.num_steps)]
        if self.options.add_extra_items:
            self.multiworld.itempool += [self.create_item("Nonograhmm clues") for _ in range(self.num_extra_clues)]
            self.multiworld.itempool += [self.create_item(self.get_filler_item_name()) for _ in range(self.num_fillers_itempool)]

    def create_regions(self):
        #locations - equal to the number of steps
        self.menu = Region("Menu", self.player, self.multiworld)
        clues = self.clue_list[1:]
        
        self.added_clues = 0
        if self.options.add_extra_items:
            items_to_add = self.num_cells - self.num_steps
            self.num_extra_clues = round(self.options.percentage_extra_clues.value * self.num_steps / 100)
            self.num_extra_clues = min(self.num_extra_clues, items_to_add)
            num_fillers = items_to_add - self.num_extra_clues
            self.num_fillers_itempool = round(self.options.percentage_fillers_itempool.value * num_fillers / 100)
            self.num_filler_local = num_fillers - self.num_fillers_itempool
            locations = list(range(1, self.num_cells + 1))
            locations_not_in_clues = [l for l in locations if l not in clues]
            self.random.shuffle(locations_not_in_clues)
            lock_filler = locations_not_in_clues[0:self.num_filler_local]
        else:
            locations = clues
            lock_filler = []
        for C in locations:
            # find the index of the lowest number in self.clue_list[1:] that is higher or equal to i
            idx = 0
            while idx < len(clues) and clues[idx] < C:
                idx += 1
            loc = NonograhmmLocation(self.player, f"{C} correct", step=idx+1, address=67+C, parent=self.menu)
            self.menu.locations.append(loc)
            if C in lock_filler:
                self.multiworld.get_location(loc.name, self.player).place_locked_item(self.create_item(self.get_filler_item_name()))
                
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
                'enables_nonograhmm_hints': self.options.enables_nonograhmm_hints.value,
                'show_all_clues': self.options.show_all_clues.value,}
    
    def write_spoiler(self, spoiler_handle) -> None:
        spoiler_handle.write(f"Puzzle: {self.puzzle}\n")
        