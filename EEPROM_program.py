from enum import Enum

HLT =    0b10000000000000000000
MI =     0b01000000000000000000
CS =     0b00100000000000000000
WR =     0b00010000000000000000
IRLOAD = 0b00001000000000000000
IROUT =   0b00000100000000000000
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
FI =     0b00000000000000000001


class Mnemonics(Enum):
    NOP = 0b0000 * 2 ** 5
    LDA = 0b0001 * 2 ** 5
    ADD = 0b0010 * 2 ** 5
    SUB = 0b0011 * 2 ** 5
    STA = 0b0100 * 2 ** 5
    LDI = 0b0101 * 2 ** 5
    JMP = 0b0110 * 2 ** 5
    OUT = 0b1110 * 2 ** 5
    HLT = 0b1111 * 2 ** 5

class Instructions(Enum):
    NOP = 0b00000000000000000000 
    FETCH = [
        MI | CO,
        CS | IRLOAD | CE
    ]
    LDA = [
        MI | IROUT,
        CS | AIN
    ]
    ADD = [
        MI | IROUT,
        CS | BIN,
        EO | AIN | FI
    ]
    SUB = [
        MI | IROUT,
        CS | BIN,
        EO | AIN | SU | FI
    ]
    STA = [
        MI | IROUT,
        CS  | AIN
    ]
    LDI = IROUT | AIN
    JMP = IROUT | JMP
    JZ = IROUT | JMP
    JC = IROUT | JMP
    OUT = AOUT | DISPLAY
    HLT = HLT


class EEPROM():
    _locations: int = 0b1000000000
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
            if self.memory[i] == Instructions.NOP.value: print('{:02x}'.format(i) + ": " + "NOP")
            else: print('{:02x}'.format(i) + ": " + '{:05x}'.format(self.memory[i]))

        with open("eeprom_out.txt", 'w') as outfile:
            outfile.write(output)

def write_flags(address: int, micro: int, eeprom: EEPROM):
    flags_count = 0b100
    for i in range(0, flags_count):
        eeprom.write_data(address + i, micro)

def write_fetch_command(eeprom: EEPROM):
    step_and_flags_offset = int((2 ** 5))
    flags_offset = int((2 ** 2))
    fetch_addresses_count: int = 0b1111
    for i in range(0, fetch_addresses_count):
        for step, micro in enumerate(Instructions.FETCH.value):
            write_flags(i * step_and_flags_offset + step * flags_offset, micro, eeprom)

def write_multi_step_command(eeprom: EEPROM, mnemonic: int, micros: list[int]):
    step = 0b010 * int((2 ** 2))
    for micro in micros:
        write_flags(mnemonic + step, micro, eeprom)
        step += 1

def write_single_step_command(eeprom: EEPROM, mnemonic: int, micro: int):
    step = 0b010 * int((2 ** 2))
    write_flags(mnemonic + step, micro, eeprom)

if __name__ == "__main__":
    eeprom = EEPROM()

    # WRITING ALL FETCH MICRO INSTRUCTIONS TO EEPROM
    write_fetch_command(eeprom)

    # WRITING ALL LDA MICRO INSTRUCTIONS TO EEPROM
    write_multi_step_command(eeprom, Mnemonics.LDA.value, Instructions.LDA.value)

    # WRITING ALL ADD MICRO INSTRUCTIONS TO EEPROM
    write_multi_step_command(eeprom, Mnemonics.ADD.value, Instructions.ADD.value)

    # WRITING ALL SUB MICRO INSTRUCTIONS TO EEPROM
    write_multi_step_command(eeprom, Mnemonics.SUB.value, Instructions.SUB.value)

    # WRITING ALL STA MICRO INSTRUCTIONS TO EEPROM
    write_multi_step_command(eeprom, Mnemonics.STA.value, Instructions.STA.value)

    # WRITING LDI MICRO INSTRUCTIONS TO EEPROM
    write_single_step_command(eeprom, Mnemonics.LDI.value, Instructions.LDI.value)

    # WRITING JMP MICRO INSTRUCTIONS TO EEPROM
    write_single_step_command(eeprom, Mnemonics.JMP.value, Instructions.JMP.value)

    # WRITING OUT MICRO INSTRUCTIONS TO EEPROM
    write_single_step_command(eeprom, Mnemonics.OUT.value, Instructions.OUT.value)
    
    # WRITING HLT MICRO INSTRUCTIONS TO EEPROM
    write_single_step_command(eeprom, Mnemonics.HLT.value, Instructions.HLT.value)

    eeprom.flush()
    