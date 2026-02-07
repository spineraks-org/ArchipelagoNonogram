from Options import OptionSet, PerGameCommonOptions, Range, Toggle
from dataclasses import dataclass

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