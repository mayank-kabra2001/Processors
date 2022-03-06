from typing import List

from nmigen import *
from nmigen.sim import *
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner


class WriteBack(Elaboratable):
    def __init__(self):
        self.register_addr = Signal(5)
        self.data_in = Signal(32)

        self.load = Signal(1)
        self.update_register_addr = Signal(5)
        self.load_value = Signal(32)
        self.pc_inc = Signal(1)
        
        self.inst_type = Signal(3)
        self.R_type = 0b111
        self.I_type = 0b001
        self.S_type = 0b011
        self.B_type = 0b100
        self.U_type = 0b101
        self.J_type = 0b110
        
        
        self.inst_type1 = Signal(11)
        self.SLLI = 0b00010010011
        self.SRLI = 0b01010010011
        self.SRAI = 0b11010010011
        self.ADD = 0b00000110011
        self.SUB = 0b10000110011
        self.SLL = 0b00010110011
        self.SLT = 0b00100110011
        self.SLTU = 0b00110110011
        self.XOR = 0b01000110011
        self.SRL = 0b01010110011
        self.SRA = 0b11010110011
        self.OR = 0b01100110011
        self.AND = 0b01110110011
        
        self.inst_type2 = Signal(10)
        self.JALB = 0b0001100111
        self.BEQ = 0b0001100011
        self.BNE = 0b0011100011
        self.BLT = 0b1001100011
        self.BGE = 0b1011100011
        self.BLTU = 0b1101100011
        self.BGEU = 0b1111100011
        self.LB = 0b0000000011
        self.LH = 0b0010000011
        self.LW = 0b0100000011
        self.LBU = 0b1000000011
        self.LHU = 0b1010000011
        self.SB = 0b0000100011
        self.SH = 0b0010100011
        self.SW = 0b0100100011
        self.ADDI = 0b0000010011
        self.SLTI = 0b0100010011
        self.SLTIU = 0b0110010011
        self.XORI = 0b1000010011
        self.ORI = 0b1100010011
        self.ANDI = 0b1110010011
        
        self.inst_type3 = Signal(7)
        self.LUI = 0b0110111
        self.AUIPC = 0b0010111
        self.JAL = 0b1101111
        
        
    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        # mydomain = ClockDomain("clk", clk_edge="pos")
        # m.domains += mydomain
        # print(mydomain.clk)
        m.d.comb += self.load.eq(0b0)
        m.d.comb += self.update_register_addr.eq(0b00000)
        m.d.comb += self.load_value.eq(0x00000000)
        
        with m.Switch(self.inst_type):
            with m.Case(self.R_type,self.I_type,self.U_type,self.J_type):
                m.d.comb += self.load.eq(0b1)
                m.d.comb += self.update_register_addr.eq(self.register_addr)
                m.d.comb += self.load_value.eq(self.data_in)
                m.d.comb += self.pc_inc.eq(Const(1))
                
        # m.d.sync += self.data_out.eq(self.data_in)
        # m.d.sync += self.register_addr_out.eq(self.register_addr_in)
        return m

    def ports(self) -> List[Signal]:
        return [self.inst_type, self.register_addr, self.data_in, self.load, self.update_register_addr,  self.load_value]


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.writeback = writeback = WriteBack()

    data_in = Signal(32)
    register_addr = Signal(5)
    inst_type = Signal(3)
    
    m.d.sync += writeback.inst_type.eq(inst_type)
    m.d.sync += writeback.data_in.eq(data_in)
    m.d.sync += writeback.register_addr.eq(register_addr)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")

    def process():
        yield data_in.eq(0x0000FFFF)
        yield register_addr.eq(0b01001)
        yield inst_type.eq(0b111)  # add
        yield
        #yield Delay(1e-6)
        yield data_in.eq(0x0000FFFF)
        yield register_addr.eq(0b01001)
        yield inst_type.eq(0b111)  # sub
        yield
        #yield Delay(1e-6)
        yield data_in.eq(0x0000FFFF)
        yield register_addr.eq(0b01001)
        yield inst_type.eq(0b111)  # slt
        yield

        yield data_in.eq(0x0000FFFF)
        yield register_addr.eq(0b01001)
        yield inst_type.eq(0b111)  # sltu
        yield

        yield data_in.eq(0x00001FFF)
        yield register_addr.eq(0b01110)
        yield inst_type.eq(0b111) # xor
        yield

        yield data_in.eq(0x00001FFF)
        yield register_addr.eq(0b01110)
        yield inst_type.eq(0b111) # or
        yield

        yield data_in.eq(0x00001FFF)
        yield register_addr.eq(0b01110)
        yield inst_type.eq(0b111)  # and
        yield

        yield data_in.eq(0x00001FFF)
        yield register_addr.eq(0b01110)
        yield inst_type.eq(0b001)    # addi
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b001)  # slti
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b001)  # ori
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b001)   # andi
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b001)  # xori
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b001)  # lw
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b100)  # blt
        yield

        yield data_in.eq(0xAAAAAAAA)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b011)  # sw
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b101)  # lui
        yield

        yield data_in.eq(0x0000F36F)
        yield register_addr.eq(0b10010)
        yield inst_type.eq(0b110)  # jal
        yield

#sim.add_sync_process(process, domain="sync")
# sim.add_sync_process(process)
#with sim.write_vcd("wb.vcd", "wb.gtkw", traces=[inst_type, register_addr, data_in]+writeback.ports()):
#    sim.run_until(100e-6, run_passive=True)
