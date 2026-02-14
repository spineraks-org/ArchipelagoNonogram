from Options import OptionGroup, OptionSet, PerGameCommonOptions, Range, Toggle
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
    
class AddExtraItems(Toggle):
    """
    Enabling this option makes every marking a check and adds more items.
    These items are either extra clues, of useless filler items.
    The next options allow you to:
    - choose what percentage of these extra items are clues,
    - choose what percentage of these extra filler items are shuffled in the multiworld.
    """
    display_name = "Add extra items"
    default = True
    
class PercentageExtraClues(Range):
    """
    This option determines how many extra clues are added. (There is already one extra clue by default.)
    Example: if there are 20 clues and this setting is 20%, there are 20 * 20% = 4 extra clues.
    This option only works if "Add extra items" is enabled.
    """
    display_name = "Extra clues"
    range_start = 0
    range_end = 100
    default = 10
    
class PercentageFillersInItempool(Range):
    """
    Percentage of extra filler items that are shuffled in the multiworld.
    Other filler items are forced into your own world, in order not to bother other players with useless items.
    """
    display_name = "Percentage extra items itempool"
    range_start = 0
    range_end = 100
    default = 0
    
class ShowAllClues(Toggle):
    """
    By default, the next clues are displayed only after you have marked all you can with your current clues.
    So even if you have already received several clues, they pop up one by one.
    This is the intended way to play, because the beautiful logic is gone when you show many clues at once.
    But if you want to see all clues once you receive them, and possibly miss some of the fun logic, you can enable this option.
    """
    display_name = "Show all clues"
    default = False
    
@dataclass
class NonograhmmOptions(PerGameCommonOptions):
    width_of_grid: WidthOfGrid
    height_of_grid: HeightOfGrid
    clue_types: ClueTypes
    enables_nonograhmm_hints: EnableNonograhmmHints
    add_extra_items: AddExtraItems
    percentage_extra_clues: PercentageExtraClues
    percentage_fillers_itempool: PercentageFillersInItempool
    show_all_clues: ShowAllClues
    
nonograhmm_option_groups = [
    OptionGroup("Gameplay",
        [
            WidthOfGrid,
            HeightOfGrid,
            ClueTypes,
        ],
    ),
    OptionGroup(
        "In-game settings",
        [
            EnableNonograhmmHints,
            ShowAllClues,
        ],
    ),
    OptionGroup(
        "Extra items",
        [
            AddExtraItems,
            PercentageExtraClues,
            PercentageFillersInItempool,
        ],
    ),
]
