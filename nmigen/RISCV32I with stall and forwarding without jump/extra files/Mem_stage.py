from typing import List

from nmigen import *
#from nmigen.sim import *
from nmigen.sim import *
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner


class Memory_stage(Elaboratable):
    def __init__(self):
        self.reg_addr_in = Signal(5)   #rd
        self.data_in_decode = Signal(32)     #used in sw, sent by decode
        self.result_from_alu = Signal(32) # alu_result
        self.data_in_memory = Signal(32)  #data sent by memory
        self.inst_type = Signal(3)  # R, S, U etc.
        self.inst_type1 = Signal(11)  # 11 bit opcode + funct3 + funct7
        self.inst_type2 = Signal(10)  # 10 bit opcode + funct3
        self.inst_type3 = Signal(7)  # 7 bit opcode

        self.write = Signal(2) 
        self.load = Signal(2) 
        self.inst_type_out = Signal(3)
        self.data_to_mem = Signal(32) #to store in memory
        self.address = Signal(32) #mem_location
        self.data_to_wb = Signal(32)
        self.reg_addr_out = Signal(5)

        self.R_type = 0b111
        self.I_type = 0b001
        self.S_type = 0b011
        self.B_type = 0b100
        self.U_type = 0b101
        self.J_type = 0b110

        self.LUI = 0b0110111
        self.AUIPC = 0b0010111
        self.JAL = 0b1101111
        
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
        self.SLLI = 0b0010010011 #starting 1 bit removed
        self.SRLI = 0b1010010011 #starting 1 bit removed
        self.SRAI = 0b1010010011 #starting 1 bit removed
        
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
    
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.comb += self.reg_addr_out.eq(self.reg_addr_in)
        m.d.comb += self.inst_type_out.eq(self.inst_type)

        with m.Switch(self.inst_type):
            
            with m.Case(self.I_type):
                with m.Switch(self.inst_type2):  
                    with m.Case(self.LB):
                        m.d.comb += self.load.eq(0b01)
                        m.d.comb += self.write.eq(0b00)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_wb.eq(self.data_in_memory)
                    with m.Case(self.LH):
                        m.d.comb += self.load.eq(0b10)
                        m.d.comb += self.write.eq(0b00)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_wb.eq(self.data_in_memory)
                    with m.Case(self.LW):
                        m.d.comb += self.load.eq(0b11)
                        m.d.comb += self.write.eq(0b00)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_wb.eq(self.data_in_memory)
                    with m.Case(self.LBU):
                        m.d.comb += self.load.eq(0b01)
                        m.d.comb += self.write.eq(0b00)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_wb.eq(self.data_in_memory)
                        #self.write = 0b0
                    with m.Case(self.LHU):
                        m.d.comb += self.load.eq(0b10)
                        m.d.comb += self.write.eq(0b00)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_wb.eq(self.data_in_memory)
                    with m.Case(self.ADDI,self.SLTI,self.SLTIU,self.XORI,self.ORI,self.ANDI,self.SLLI,self.SRLI,self.SRAI):
                        m.d.comb += self.data_to_wb.eq(self.result_from_alu) 

            with m.Case(self.S_type):
                with m.Switch(self.inst_type2):
                    with m.Case(self.SB):
                        m.d.comb += self.load.eq(0b00)
                        m.d.comb += self.write.eq(0b01)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_mem.eq(self.data_in_decode)
                    with m.Case(self.SH):
                        m.d.comb += self.load.eq(0b00)
                        m.d.comb += self.write.eq(0b10)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_mem.eq(self.data_in_decode)
                    with m.Case(self.SW):
                        m.d.comb += self.load.eq(0b00)
                        m.d.comb += self.write.eq(0b11)
                        m.d.comb += self.address.eq(self.result_from_alu)
                        m.d.comb += self.data_to_mem.eq(self.data_in_decode)   

            with m.Case(self.R_type): 
                m.d.comb += self.data_to_wb.eq(self.result_from_alu)

        return m

    def ports(self)->List[Signal]:
        return [
            self.reg_addr_in,
        self.data_in_decode,
        self.result_from_alu,
        self.data_in_memory,
        self.inst_type,
        self.inst_type1,
        self.inst_type2,
        self.inst_type3,

        self.write, 
        self.load, 
        self.inst_type_out,
        self.data_to_mem,
        self.address,
        self.data_to_wb,
        self.reg_addr_out,
        ]   

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    m.submodules.memory_stage = memory_stage  = Memory_stage()

    inst_type = Signal(3)  # R, S, U etc.
    inst_type1 = Signal(11)  # 11 bit opcode + funct3 + funct7
    inst_type2 = Signal(10)  # 10 bit opcode + funct3
    inst_type3 = Signal(7)  # 7 bit opcode    
    reg_addr_in = Signal(5)   #rd
    data_in_decode = Signal(32)     #used in sw, sent by decode
    result_from_alu = Signal(32) # alu_result
    data_in_memory = Signal(32)  #data sent by memory 

    m.d.sync += memory_stage.data_in_decode.eq(data_in_decode)
    m.d.sync += memory_stage.result_from_alu.eq(result_from_alu)
    m.d.sync += memory_stage.data_in_memory.eq(data_in_memory)
    m.d.sync += memory_stage.reg_addr_in.eq(reg_addr_in)
    
    m.d.sync += memory_stage.inst_type.eq(inst_type)
    m.d.sync += memory_stage.inst_type1.eq(inst_type1)
    m.d.sync += memory_stage.inst_type2.eq(inst_type2)
    m.d.sync += memory_stage.inst_type3.eq(inst_type3)    

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")

    def process():
        yield inst_type.eq(0b011)
        yield inst_type2.eq(0b0100100011)
        yield result_from_alu.eq(0x000000AA)
        yield data_in_decode.eq(0x000000BB)
        yield reg_addr_in.eq(0x000000CC)




#sim.add_sync_process(process,domain = "sync")

#with sim.write_vcd("mem.vcd","mem.gtkw",traces=[data_in_decode, data_in_memory, result_from_alu, reg_addr_in, inst_type, inst_type1, inst_type2, inst_type3]+memory_stage.ports()):
#    sim.run_until(100e-6, run_passive=True) 
                       
                    
