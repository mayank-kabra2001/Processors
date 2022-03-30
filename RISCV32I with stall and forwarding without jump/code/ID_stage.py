from typing import List

from nmigen import *
from nmigen.sim import *
from nmigen import Elaboratable,Module,Signal
from nmigen.build import Platform
from nmigen.cli import main_parser,main_runner

class ID(Elaboratable):
    # 32 reg, reg address source 1 ,2, write back reg address, 
    def __init__(self):
        #inputs
        self.instruction = Signal(32) 
        self.s1_data_in = Signal(32)
        self.s2_data_in = Signal(32)
        #local variables
        self.immediate = Signal(12)
        self.immediate_B_type = Signal(13)
        self.immediate_U_type = Signal (20)
        self.immediate_J_type = Signal(21)
        self.instruction_type = Signal(3)
        self.sig0 = Const(0)
        #outputs
        self.des = Signal(5)
        self.s1 = Signal(5)
        self.s2 = Signal(5)
        self.s1data_out = Signal(32)
        self.s2data_out = Signal(32)
        self.signextended_immediate = Signal(signed(32))
        self.instruction_type = Signal(3)
        self.it1 = Signal(11)
        self.it2 = Signal(10)
        self.it3 = Signal(7)
        self.ifload = Signal(1)
        
        #type encoding
        self.LUI 	=	0b0110111
        self.AUIPC 	=	0b0010111
        self.JAL 	=	0b1101111
        self.JALB	=	0b0001100111
        self.BEQ	=	0b0001100011
        self.BNE 	=	0b0011100011
        self.BLT 	=	0b1001100011
        self.BGE 	=	0b1011100011
        self.BLTU 	=	0b1101100011
        self.BGEU 	=	0b1111100011
        self.LB 	=	0b0000000011
        self.LH		=	0b0010000011
        self.LW		=	0b0100000011
        self.LBU 	=	0b1000000011
        self.LHU 	=	0b1010000011
        self.SB 	=	0b0000100011
        self.SH		=	0b0010100011
        self.SW		=	0b0100100011
        self.ADDI 	=	0b0000010011
        self.SLTI 	=	0b0100010011
        self.SLTIU 	=	0b0110010011
        self.XORI	=	0b1000010011
        self.ORI	=	0b1100010011
        self.ANDI	=	0b1110010011
        self.SLLI 	=	0b00010010011
        self.SRLI 	=	0b01010010011
        self.SRAI 	=	0b11010010011
        self.ADD 	=	0b00000110011
        self.SUB 	=	0b10000110011
        self.SLL 	=	0b00010110011
        self.SLT 	=	0b00100110011
        self.SLTU 	=	0b00110110011
        self.XOR 	=	0b01000110011
        self.SRL 	=	0b01010110011
        self.SRA 	=	0b11010110011
        self.OR 	=	0b01100110011
        self.AND 	=	0b01110110011

        self.R_type = 0b111
        self.I_type = 0b001
        self.S_type = 0b011
        self.B_type = 0b100
        self.U_type = 0b101
        self.J_type = 0b110 

        self.zero20 = Const(0x00000) 

    def elaborate(self,platform:Platform)->Module:
        m = Module()
       # m.d.comb+=self.instruction.eq(0xFCE08793)#0b00000000011100110000001010110011)#0xCD40CE00)
        
        m.d.comb+=self.it3.eq(self.instruction[0:7])#self.instruction type
        m.d.comb+=self.it2.eq(Cat(self.instruction[0:7],self.instruction[12:15]))#concatinate opcode and funct3
        m.d.comb+=self.it1.eq(Cat(self.instruction[0:7],self.instruction[12:15],self.instruction[30]))# concatinate opcode, funct3, funct7

        m.d.comb+=self.s1.eq(self.instruction[15:20])
        m.d.comb+=self.s2.eq(self.instruction[20:25])
        #m.d.comb+=self.des.eq(self.instruction[7:12])

        #m.d.comb+=self.regfile[self.s1].eq(0xAAAAAAAA)
        #m.d.comb+=self.regfile[self.s2].eq(0xBBBBBBBB)

        #assigning the self.instruction type based on type of self.instruction
        with m.Switch(self.it1):
            with m.Case(self.ADD, self.SUB,  self.SLL, self.SLT, self.SLTU, self.XOR, self.SRL, self.SRA,self.OR, self.AND):
                m.d.comb+=self.instruction_type.eq(0b111)#Inst_type.R_type
                m.d.comb+=self.s1data_out.eq(self.s1_data_in)
                m.d.comb+=self.s2data_out.eq(self.s2_data_in)
                m.d.comb+=self.des.eq(self.instruction[7:12])

        
        with m.Switch(self.it2):
            with m.Case(self.ADDI,self.SLTI,self.SLTIU,self.XORI,self.ORI,self.ANDI):#didnot implement SLLI,SRAI, SRLI
                m.d.comb+=self.instruction_type.eq(0b001)#I type
                m.d.comb+=self.s1data_out.eq(self.s1_data_in)
                m.d.comb+=self.des.eq(self.instruction[7:12])
                with m.If(self.instruction[31]==Const(0)):
                    m.d.comb+=self.signextended_immediate.eq(Cat(self.instruction[20:],Const(0x00000)))
                with m.Else():
                    m.d.comb+=self.signextended_immediate.eq(Cat(self.instruction[20:],Const(0xFFFFF)))  
            with m.Case(self.LB,self.LH,self.LW,self.LBU,self.LHU):
                m.d.comb+=self.instruction_type.eq(0b001)#I type 
                m.d.comb+=self.s1data_out.eq(self.s1_data_in)
                m.d.comb+=self.des.eq(self.instruction[7:12])
                m.d.comb+=self.signextended_immediate.eq(Cat(self.instruction[20:],Const(0x00000)))
                m.d.comb+=self.ifload.eq(Const(1))
                
            with m.Case(self.BEQ,self.BNE,self.BLT,self.BGE,self.BLTU,self.BGEU):
                m.d.comb+=self.instruction_type.eq(0b100)#B type
                with m.If(self.instruction[31]==Const(0)):
                    m.d.comb+=self.signextended_immediate.eq(Cat(Const(0b0),self.instruction[8:12],self.instruction[25:31],self.instruction[7],self.instruction[31],Const(0x0000),Const(0b000)))
                with m.Else():
                    m.d.comb+=self.signextended_immediate.eq(Cat(Const(0b0),self.instruction[8:12],self.instruction[25:31],self.instruction[7],self.instruction[31],Const(0xFFFF),Const(0b111)))  
                m.d.comb+=self.s1data_out.eq(self.s1_data_in)
                m.d.comb+=self.s2data_out.eq(self.s2_data_in)
            with m.Case(self.SB, self.SH, self.SW):
                m.d.comb+=self.instruction_type.eq(0b011)#S type
                m.d.comb+=self.s1data_out.eq(self.s1_data_in)
                m.d.comb+=self.s2data_out.eq(self.s2_data_in)
                m.d.comb+=self.signextended_immediate.eq(Cat(self.instruction[7:12],self.instruction[25:],Const(0x00000)))
        with m.Switch(self.it3):
            with m.Case(self.LUI,self.AUIPC):
                m.d.comb+=self.instruction_type.eq(0b101)#U type
                m.d.comb+=self.signextended_immediate.eq(Cat(Const(0x000),self.instruction[12:]))#msb bits are immediate
                m.d.comb+=self.des.eq(self.instruction[7:12])
            with m.Case(self.JAL):
                m.d.comb+=self.instruction_type.eq(0b110)#J type
                m.d.comb+=self.des.eq(self.instruction[7:12])
                m.d.comb+=self.signextended_immediate.eq(Cat(Const(0b0),self.instruction[21:31],self.instruction[20],self.instruction[12:20],self.instruction[31],Const(0b00000000000)))


        return m

    def ports(self)->List[Signal]:
        return [self.instruction,self.s1,self.s2,self.ifload,self.s1_data_in,self.s2_data_in,self.s1data_out, self.s2data_out,self.instruction_type,self.it3,self.it2,self.it1,self.des,self.signextended_immediate]

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()


    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.id_stage = id_stage = ID()

    instruction = Signal(32)
    s1_data_in = Signal(32)
    s2_data_in = Signal(32)
    m.d.sync += id_stage.instruction.eq(instruction)
    m.d.sync += id_stage.s1_data_in.eq(s1_data_in)
    m.d.sync += id_stage.s2_data_in.eq(s2_data_in)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")


    def process():
        yield instruction.eq(0b11100000111000010000010001100011)
        yield s1_data_in.eq(0x000000AA)
        yield s2_data_in.eq(0x000000BB)
        #yield Delay(1e-6)

        yield
        #yield Delay(1e-6)

#sim.add_sync_process(process,domain = "sync")
#sim.add_sync_process(process)
#with sim.write_vcd("id.vcd","id.gtkw",traces=[instruction,s1_data_in,s2_data_in]+id_stage.ports()):
#    sim.run_until(100e-6, run_passive=True)


