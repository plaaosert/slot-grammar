from enum import Enum
import random


class TriggerShape(Enum):
    NUMBER_TILES = 0
    NUMBER_MATCHES = 1


class MatchType(Enum):
    LTR = 0    # Match left to right no matter what horizontal position
    LINES = 1  # Match left to right, but only horizontally adjacent (NE, E, SE)


class ActionType(Enum):
    MAKE_STICKY = 0
    TRANSFORM = 1
    REMOVE_STICKY = 2


class Board:
    def __init__(self, ruleset):
        self.ruleset = ruleset
        self.state_counter = -1
        self.state = ruleset.default_state
        self.tiles = [
            [-1 for __ in range(self.ruleset.num_rows)] for _ in range(self.ruleset.num_reels)
        ]
        self.sticky_tiles = []
        self.tile_probability_caches = {}
        self.tile_probability_sums = {}
        for state in self.ruleset.states:
            total = 0
            tile_probability_cache = []
            for tile in self.ruleset.tiles[state].items():
                total += tile[1][0]
                tile_probability_cache.append((tile[0], total))

            self.tile_probability_caches[state] = tile_probability_cache
            self.tile_probability_sums[state] = total

    def render(self):
        tile_cols = {-1: -1}
        for num, tile in enumerate(self.ruleset.tiles[self.state].keys()):
            tile_cols[tile] = num

        print("\n".join(
            "  " + "  ".join(
                "{}{:^8}".format("\033[{};1m".format(31 + tile_cols[self.tiles[reel_id][row_id]]),
                                 self.tiles[reel_id][row_id]) for reel_id in range(self.ruleset.num_reels)
            ) for row_id in range(self.ruleset.num_rows)
        ) + "\u001b[0m")

    def select_random_tile(self):
        number = random.random() * self.tile_probability_sums[self.state]
        for tile in self.tile_probability_caches[self.state]:
            if tile[1] > number:
                return tile[0]

    def spin(self):
        for reel_id in range(self.ruleset.num_reels):
            for row_id in range(self.ruleset.num_rows):
                self.tiles[reel_id][row_id] = self.select_random_tile()

    def test_triggers(self):
        pass

    def value_matches(self, matches):
        return sum(
            (sum(self.ruleset.tiles[self.state][part[0]][1] for part in match) * len(match)) for match in matches
        )

    def check_matches(self):
        matches = []
        if self.ruleset.match_type == MatchType.LTR:
            in_progress = [((self.tiles[0][row_id], (0, row_id)),) for row_id in range(self.ruleset.num_rows)]
            for reel_id in range(1, self.ruleset.num_reels):
                extended = set()
                new_progress = []
                # For every tile, add it to the new progress for every previous match. Mark extended matches.
                # If any matches are unextended, add them to matches if they are long enough.
                for row_id in range(self.ruleset.num_rows):
                    for match in in_progress:
                        if self.tiles[reel_id][row_id] in self.ruleset.match_rules[self.state][match[-1][0]]:
                            extended.add(match)
                            new_progress.append(
                                (*match, (self.tiles[reel_id][row_id], (reel_id, row_id)))
                            )

                    orphaned_matches = in_progress
                    for match in orphaned_matches:
                        if len(match) > self.ruleset.num_to_match:
                            matches.append(match)

                in_progress = new_progress

            for match in in_progress:
                if len(match) >= self.ruleset.num_to_match:
                    matches.append(match)

        elif self.ruleset.match_type == MatchType.LINES:
            pass

        return matches


class Trigger:
    def __init__(self, shape, tileid, number):
        self.shape = shape
        self.tileid = tileid
        self.number = number

    def check(self, board):
        if self.shape == TriggerShape.NUMBER_TILES:
            tiles = board.get_tiles(self.tileid)
            if len(tiles) >= self.number:
                return tiles
        elif self.shape == TriggerShape.NUMBER_MATCHES:
            matches = board.get_matches_of_tile(self.tileid)
            if len(matches) >= self.number:
                return matches

        return []


class Action:
    def __init__(self, tileid, new_state, new_state_time, action, action_data):
        self.action_data = action_data
        self.action = action
        self.new_state_time = new_state_time
        self.new_state = new_state
        self.tileid = tileid  # if -2, target only the things which triggered the trigger.

    def get_target_tiles(self, trigger_tiles, board):
        if self.tileid == -2:
            return trigger_tiles
        else:
            return board.get_tiles(self.tileid)

    def do(self, trigger_tiles, board):
        tiles = self.get_target_tiles(trigger_tiles, board)

        if self.action == ActionType.MAKE_STICKY:
            board.sticky_tiles.extend(tiles)

        elif self.action == ActionType.TRANSFORM:
            for tile in tiles:
                board.tiles[tile[0]][tile[1]] = self.action_data

        elif self.action == ActionType.REMOVE_STICKY:
            board.tiles = list(filter(lambda t: t not in tiles, board.tiles))

    
class Ruleset:
    def __init__(self, num_reels, num_rows, tiles, destroy_matches, num_to_match, match_type, match_rules, triggers, states, default_state):
        self.states = states
        self.default_state = default_state
        self.triggers = triggers  # Dict of triggers based on current state.

        # Dict of dicts (key: state) with inner dicts containing
        # every tile as a key and all the tiles it should match with as a tuple.
        self.match_rules = match_rules

        self.match_type = match_type
        self.num_to_match = num_to_match
        self.destroy_matches = destroy_matches
        self.tiles = tiles  # Dict. {key: (chance_to_get, value)}
        self.num_rows = num_rows
        self.num_reels = num_reels
