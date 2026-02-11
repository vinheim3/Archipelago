import base64
import logging
import time

from NetUtils import ClientStatus, NetworkItem

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from worlds._bizhawk import read, write, guarded_write

from .items import ITEM_ID_TO_ITEM
from .locations import LOCATION_GLOBAL_FLAG_TO_ID

nes_logger = logging.getLogger("NES")
logger = logging.getLogger("Client")

# ROM locations
UFOURIA_NAME = 0x3f6f
UFOURIA_STR = bytes([0x1e, 0x0f, 0x18, 0x1e, 0x1b, 0x12, 0xa])

# RAM locations
SCANLINE_IRQ_SETUP = 0x28
FIRST_ENTITY_ID_LOADED = 0x408
GOAL_FLAG = 0x46a
GLOBAL_FLAGS = 0x4e0
LOCATIONS_CHECKED = 0x7f0  # todo: check if truly free
ITEMS_RECEIVED = 0x7ff # todo: check if truly free

# todo: Could be more optimized, but the global flags set for chests are
# in the ranges $01-$0a, $10-$13, $30-$39 excluding $36 to $37,
# and $e0 to $e5 excluding $e2
# so we just reserve 9 * 8 bytes = $48 ($e0-$e5 are in the last 8 bytes)
LEN_LOCATIONS_CHECKED = 9


class UfouriaClient(BizHawkClient):
    system = "NES"
    game = "Ufouria"
    patch_suffix = ".apufouria"

    def __init__(self):
        self.wram = "RAM"
        self.rom = "PRG ROM"

    async def validate_rom(self, ctx):
        # UFOURIA in the game's ascii decoding
        try:
            if (await bizhawk.get_memory_size(ctx.bizhawk_ctx, self.rom)) < 0x20_000:
                return False
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(UFOURIA_NAME, len(UFOURIA_STR), self.rom)]))[0])
            if rom_name != UFOURIA_STR:
                return False
        except bizhawk.RequestFailedError:
            return False
        
        ctx.game = self.game
        ctx.items_handling = 0b111
        
        return True
    
    async def game_watcher(self, ctx):
        if ctx.server is None:
            return

        if ctx.slot is None:
            return
        
        writes = []

        scanline_irq_setup, first_entity_id_loaded, goal_flag, global_flags, locations_checked, items_received = (
            await bizhawk.read(ctx.bizhawk_ctx, [
                (SCANLINE_IRQ_SETUP, 1, self.wram),
                (FIRST_ENTITY_ID_LOADED, 1, self.wram),
                (GOAL_FLAG, 1, self.wram),
                (GLOBAL_FLAGS, 0x20, self.wram),
                (LOCATIONS_CHECKED, LEN_LOCATIONS_CHECKED, self.wram),
                (ITEMS_RECEIVED, 1, self.wram),
            ])
        )

        # Return if not "playable"
        if scanline_irq_setup[0] != 2:
            return
        
        # Handle goal - entity 0x11 is the final boss, and 0x10
        # is set on this ram address when the boss is about to explode
        if first_entity_id_loaded[0] == 0x11 and goal_flag[0] == 0x10:
            await ctx.send_msgs([{
                "cmd": "StatusUpdate",
                "status": ClientStatus.CLIENT_GOAL
            }])

        # Handle receiving items
        recv_amount = items_received[0]
        if recv_amount < len(ctx.items_received):
            item: NetworkItem = ctx.items_received[recv_amount]
            ufouria_item = ITEM_ID_TO_ITEM[item.item]
            if global_flag := ufouria_item.global_flag:
                flag_byte_offset, flag_bit = global_flag // 8, global_flag % 8
                curr_val = global_flags[flag_byte_offset]
                new_val = curr_val | (1 << flag_bit)
                writes.append((GLOBAL_FLAGS + flag_byte_offset, new_val.to_bytes(1, 'little'), "RAM"))

            recv_amount += 1
            writes.append((ITEMS_RECEIVED, recv_amount.to_bytes(1, 'little'), "RAM"))

        # Sync back locations checked from the server
        # eg in case the game is restarted
        for byte_offset in range(LEN_LOCATIONS_CHECKED):
            location_checked_byte = locations_checked[byte_offset]
            new_byte = location_checked_byte
            for bit in range(8):
                location_global_flag = byte_offset * 8 + bit
                if location_global_flag in LOCATION_GLOBAL_FLAG_TO_ID:
                    location_id = LOCATION_GLOBAL_FLAG_TO_ID[location_global_flag]
                    if location_id in ctx.checked_locations:
                        new_byte |= (1 << bit)
            if location_checked_byte != new_byte:
                writes.append((LOCATIONS_CHECKED + byte_offset, new_byte.to_bytes(1, 'little'), "RAM"))

        if writes:
            await write(ctx.bizhawk_ctx, writes)

        # Handle location checks
        new_checks: list[int] = []
        for byte_offset in range(LEN_LOCATIONS_CHECKED):
            location_checked_byte = locations_checked[byte_offset]
            for bit in range(8):
                if location_checked_byte & (1 << bit):
                    location_global_flag = byte_offset * 8 + bit
                    # Ignore medicine/water of life global flags
                    if location_global_flag != 0x36 and location_global_flag != 0x37:
                        if location_global_flag in LOCATION_GLOBAL_FLAG_TO_ID:
                            location_id = LOCATION_GLOBAL_FLAG_TO_ID[location_global_flag]
                            if location_id not in ctx.checked_locations:
                                new_checks.append(location_id)
                        else:
                            logger.error(
                                f"Invalid global flag checked: ${location_global_flag:02x}"
                            )

        for new_check_id in new_checks:
            ctx.locations_checked.add(new_check_id)
            location = ctx.location_names.lookup_in_game(new_check_id)
            # Copied from MM2, but no idea where it logs
            nes_logger.info(
                f'New Check: {location} ({len(ctx.locations_checked)}/'
                f'{len(ctx.missing_locations) + len(ctx.checked_locations)})')
            await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": [new_check_id]}])
