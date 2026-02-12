from Options import OptionSet, PerGameCommonOptions, Range, Toggle
from dataclasses import dataclass

class WidthOfGrid(Range):
    """
    Width of the Nonograhmm grid.
    Note: this game is harder than you think so start small!
    Also with big grids, please test if it fits on your screen :')
    """
    display_name = "Width of Grid"
    range_start = 5
    range_end = 25
    default = 5
    
class HeightOfGrid(Range):
    """
    Height of the Nonograhmm grid.
    Did I already say this game is harder than you think?
    And that you should probably test it solo first?
    """
    display_name = "Height of Grid"
    range_start = 5
    range_end = 25
    default = 5
    
class ClueTypes(OptionSet):
    """
    Clues that a '?' may get replaced by before a number is shown.
    It is recommended to first play without these extra clue types.
    Put them in the yaml like this: ['O', 'E', '/', '-', '+']
    O: number is odd (will show as 'Ω' (Omega) in the game)
    E: number is even
    /: number is one of two possible values (e.g., "2/4" means the number is either 2 or 4)
    -: number is at most a certain value (e.g., "3-" means the number is 1, 2, or 3)
    +: number is at least a certain value (e.g., "3+" means the number is 3 or greater)
    random: every clue type is added with 50/50 chance
    all: all clue types are added
    """
    display_name = "Clue types"
    valid_keys = ['O', 'E', '/', '-', '+', 'random', 'all']
    default = [] 
    
class EnableNonograhmmHints(Toggle):
    """
    Whether the website has a hint button that shows where the next steps in solving the puzzle are.
    """
    display_name = "Enable Nonograhmm hints"
    default = True
    
@dataclass
class NonograhmmOptions(PerGameCommonOptions):
    width_of_grid: WidthOfGrid
    height_of_grid: HeightOfGrid
    clue_types: ClueTypes
    enables_nonograhmm_hints: EnableNonograhmmHints