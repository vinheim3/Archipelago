import hashlib

from worlds.Files import APDeltaPatch

EU_CHECKSUM = "75190f8724f5541ad30234374432dd5c"


class UfouriaDeltaPatch(APDeltaPatch):
    hash = EU_CHECKSUM
    game = "Ufouria"
    patch_file_ending = ".apufouria"
    result_file_ending = ".nes"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name = get_base_rom_path()
        base_rom_bytes = bytes(open(file_name, "rb").read())

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if EU_CHECKSUM != basemd5.hexdigest():
            raise Exception('Supplied Base Rom does not match known MD5 for EU release. '
                            'Get the correct game and version, then dump it')
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes


def get_base_rom_path() -> str:
    from . import UfouriaWorld
    return UfouriaWorld.settings.rom_file
