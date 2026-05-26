from enum import Enum

HLT =    0b10000000000000000000
MI =     0b01000000000000000000
CS =     0b00100000000000000000
WR =     0b00010000000000000000
IRLOAD = 0b00001000000000000000
IRIN =   0b00000100000000000000
AIN =    0b00000010000000000000
AOUT =   0b00000001000000000000
EO =     0b00000000100000000000
SU =     0b00000000010000000000
S2 =     0b00000000001000000000
S1 =     0b00000000000100000000
SIGNED = 0b00000000000010000000
BIN =    0b00000000000001000000
BOUT =   0b00000000000000100000
DISPLAY =0b00000000000000010000
CE =     0b00000000000000001000
CO =     0b00000000000000000100
JMP =    0b00000000000000000010


class Mnemonics(Enum):
    NOP = 0b0000 * 2 ** 3
    LDA = 0b0001 * 2 ** 3
    ADD = 0b0010 * 2 ** 3
    SUB = 0b0011 * 2 ** 3
    OUT = 0b1110 * 2 ** 3
    HLT = 0b1111 * 2 ** 3

class Instructions(Enum):
    NOP = 0b00000000000000000000 
    FETCH = [
        MI | CO,
        CS | IRLOAD | CE
    ]
    LDA = [
        MI | IRIN,
        CS | AIN
    ]
    ADD = [
        MI | IRIN,
        CS | BIN,
        EO | AIN
    ]
    SUB = [
        MI | IRIN,
        CS | BIN,
        EO | AIN | SU
    ]
    OUT = AOUT | DISPLAY
    HLT = HLT


class EEPROM():
    _locations: int = 0b10000000
    _location_width: int = 0b11111111111111111110 

    def get_locations_count(self) -> int:
        return self._locations

    def __init__(self):
        self.memory: list[int] = [Instructions.NOP.value] * self._locations

    def _check_if_empty(self, location: int) -> bool:
        return location == Instructions.NOP.value

    def write_data(self, address: int, data_to_write: int):
        if address >= self._locations or address < 0: raise RuntimeError(f"Invalid address {address}")
        if data_to_write > self._location_width or data_to_write < Instructions.NOP.value: raise RuntimeError(f"Invalid data - contents: {data_to_write}")

        self.memory[address] = data_to_write

    def read_data(self, address: int) -> int:
        if address >= self._locations or address < 0: raise RuntimeError(f"Invalid address {address}")

        return self.memory[address]

    def flush(self):
        zeros: int = 0

        output: str = ""

        for location in self.memory:
            if self._check_if_empty(location):
                zeros += 1
                continue
            else:
                output += "0 " if zeros == 1 else f"{zeros}*0 " if zeros > 1 else ""
                zeros = 0

            hex_val = '{:02x}'.format(location)

            output += f"{hex_val} "
        
        # print contents
        for i in range(self._locations):
            if i % 8 == 0: print("---------")
            if (i - 2) % 8 == 0:
                if self.memory[i - 1] == Instructions.FETCH.value[1]: print("")
            if self.memory[i] == Instructions.NOP.value: print('{:02x}'.format(i) + ": " + "NOP")
            else: print('{:02x}'.format(i) + ": " + '{:05x}'.format(self.memory[i]))

        with open("eeprom_out.txt", 'w') as outfile:
            outfile.write(output)


if __name__ == "__main__":
    eeprom = EEPROM()

    # WRITING ALL FETCH MICRO INSTRUCTIONS TO EEPROM

    step_offset = int((2 ** 3))
    fetch_addresses_count: int = 0b1111
    for i in range(0, fetch_addresses_count):
        for step, micro in enumerate(Instructions.FETCH.value):
            eeprom.write_data(i * step_offset + step, micro)


    # WRITING ALL LDA MICRO INSTRUCTIONS TO EEPROM
    step = 0b010
    for micro in Instructions.LDA.value:
        eeprom.write_data(Mnemonics.LDA.value + step, micro)
        step += 1


    # WRITING ALL ADD MICRO INSTRUCTIONS TO EEPROM
    step = 0b010
    for micro in Instructions.ADD.value:
        eeprom.write_data(Mnemonics.ADD.value + step, micro)
        step += 1

    # WRITING ALL SUB MICRO INSTRUCTIONS TO EEPROM
    step = 0b010
    for micro in Instructions.SUB.value:
        eeprom.write_data(Mnemonics.SUB.value + step, micro)
        step += 1

    # WRITING ALL OUT MICRO INSTRUCTIONS TO EEPROM
    step = 0b010
    eeprom.write_data(Mnemonics.OUT.value + step, Instructions.OUT.value)

    # WRITING ALL HLT MICRO INSTRUCTIONS TO EEPROM
    step = 0b010
    eeprom.write_data(Mnemonics.HLT.value + step, Instructions.HLT.value)

    eeprom.flush()
    