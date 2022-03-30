from typing import List
from nmigen.back import rtlil, verilog
from nmigen import *
#from nmigen.back.pysim import Simulator, Delay, Settle
from nmigen.sim import *
from nmigen import Elaboratable,Module,Signal
from nmigen.build import Platform
from nmigen.cli import main_parser,main_runner

class ALU(Elaboratable):
    def __init__(self):
        self.Ra_unsigned = Signal(32)
        self.Rb_unsigned = Signal(32)
        self.Ra = Signal(signed(32))
        self.Rb= Signal(signed(32))
        self.result = Signal(signed(32))
        self.result64 = Signal(signed(64))
        self.inst_type = Signal(3)
        self.inst_type0 = Signal(17)
        self.inst_type1 = Signal(11)
        self.inst_type2 = Signal(10)
        self.reg_addr_in = Signal(5)
        self.immediate = Signal(signed(32))
        self.branching = Signal(1)
        self.inst_type3 = Signal(7)
        self.data_to_mem = Signal(32)
        self.inst_type_out = Signal(3)
        self.inst_type1_out = Signal(11)
        self.inst_type2_out = Signal(10)
        self.inst_type3_out = Signal(7)
        self.reg_addr_out = Signal(5)
        self.jump = Signal(1)
        self.pc = Signal(10)

        self.R_type = 0b111

        self.ADD = 0b00000110011
        self.SUB = 0b10000110011   
        self.SLT = 0b00100110011
        self.SLTU = 0b00110110011
        self.XOR = 0b01000110011
        self.OR = 0b01100110011
        self.AND = 0b01110110011

        self.M_type = 0b010

        self.MUL =   0b00000010000110011 
        self.MULH =  0b00000010010110011 
        self.MULHSU =0b00000010100110011
        self.MULHU = 0b00000010110110011
        self.DIV =   0b00000011000110011
        self.DIVU =  0b00000011010110011
        self.REM =   0b00000011100110011
        self.REMU =  0b00000011110110011
       
        self.I_type = 0b001

        self.JALR	=	0b0001100111
        self.ADDI    =   0b0000010011
        self.SLTI    =   0b0100010011
        self.SLTIU   =   0b0110010011
        self.XORI    =   0b1000010011
        self.ORI     =   0b1100010011
        self.ANDI    =   0b1110010011
        self.LW      =   0b0100000011
        self.LB 	=	0b0000000011
        self.LH		=	0b0010000011
        self.LBU 	=	0b1000000011
        self.LHU 	=	0b1010000011

        self.B_type = 0b100

        self.BEQ     =   0b0001100011
        self.BNE     =   0b0011100011
        self.BLT     =   0b1001100011
        self.BGE     =   0b1011100011
        self.BLTU    =   0b1101100011
        self.BGEU    =   0b1111100011

        self.S_type = 0b011

        self.SB 	=	0b0000100011
        self.SH		=	0b0010100011
        self.SW		=	0b0100100011

        self.U_type = 0b101

        self.LUI     =   0b0110111
        self.AUIPC   =   0b0010111

        self.J_type = 0b110
        self.JAL     =   0b1101111

        self.load_mem = Signal(2)
        self.write_mem = Signal(2)

        self.load_wb = Signal(1)

    def elaborate(self,platform:Platform)->Module:
        m = Module()
        m.d.comb += self.inst_type_out.eq(self.inst_type)

        m.d.comb += self.inst_type1_out.eq(self.inst_type1)
        m.d.comb += self.inst_type2_out.eq(self.inst_type2)
        m.d.comb += self.inst_type3_out.eq(self.inst_type3)
        m.d.comb += self.reg_addr_out.eq(self.reg_addr_in)

        with m.Switch(self.inst_type):

            with m.Case(self.R_type):
                m.d.comb += self.load_wb.eq(0b1)
                m.d.comb += self.load_mem.eq(0b00)
                m.d.comb += self.write_mem.eq(0b00)
                with m.Switch(self.inst_type1):

                    with m.Case(self.ADD):
                        m.d.comb += self.result.eq(self.Ra+self.Rb)

                    with m.Case(self.SUB):
                        m.d.comb += self.result.eq(self.Rb-self.Ra)  
                          
                    with m.Case(self.SLT):
                        with m.If(self.Ra<self.Rb):
                            m.d.comb+=self.result.eq(1)
                        with m.Else():
                            m.d.comb+=self.result.eq(0)  

                    with m.Case(self.SLTU):
                        with m.If(self.Ra<self.Rb):
                            m.d.comb+=self.result.eq(1)
                        with m.Else():
                            m.d.comb+=self.result.eq(0)

                    with m.Case(self.XOR):
                        m.d.comb+=self.result.eq((self.Ra & (~self.Rb)) | ((~self.Ra) & self.Rb))
                            
                    with m.Case(self.OR):
                        m.d.comb+=self.result.eq(self.Rb | self.Ra)

                    with m.Case(self.AND):
                        m.d.comb+=self.result.eq(self.Rb & self.Ra)

                      
                            
            with m.Case(self.I_type):
                m.d.comb += self.load_wb.eq(0b1)
                m.d.comb += self.write_mem.eq(0b00)
                with m.Switch(self.inst_type2):

                    with m.Case(self.JALR):
                        m.d.comb += self.result.eq(self.pc-Const(1))
                        m.d.comb += self.jump.eq(Const(1))

                    with m.Case(self.ADDI):
                            m.d.comb += self.result.eq(self.Ra+self.immediate)

                    with m.Case(self.SLTI):
                        with m.If(self.Ra<self.immediate):
                            m.d.comb+=self.result.eq(1)
                        with m.Else():
                            m.d.comb+=self.result.eq(0)  

                    with m.Case(self.SLTIU):
                        with m.If(self.Ra<self.immediate):
                            m.d.comb+=self.result.eq(1)
                        with m.Else():
                            m.d.comb+=self.result.eq(0)

                    with m.Case(self.XORI):
                        m.d.comb+=self.result.eq((self.Ra & (~self.immediate))|((~self.Ra) & self.immediate))

                    with m.Case(self.ORI):
                        m.d.comb+=self.result.eq(self.Ra|self.immediate)

                    with m.Case(self.ANDI):
                        m.d.comb+=self.result.eq(self.Ra&self.immediate)  

                    with m.Case(self.LW):
                        m.d.comb += self.load_mem.eq(0b11)
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                    with m.Case(self.LHU,self.LH):
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                        m.d.comb += self.load_mem.eq(0b10)
                    with m.Case(self.LBU,self.LB):
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                        m.d.comb += self.load_mem.eq(0b01)


            with m.Case(self.B_type):
                m.d.comb += self.load_wb.eq(0b0)
                with m.Switch(self.inst_type2):
                    with m.Case(self.BEQ):
                        with m.If(self.Ra==self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.immediate)

                    with m.Case(self.BNE):
                        with m.If(self.Ra!=self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.Ra + self.immediate)

                    with m.Case(self.BLT):
                        with m.If(self.Ra<self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.immediate)

                    with m.Case(self.BGE):
                         with m.If(self.Ra>=self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.immediate)

                    with m.Case(self.BLTU):
                         with m.If(self.Ra<self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.immediate)

                    with m.Case(self.BGEU):
                         with m.If(self.Ra>=self.Rb):
                            m.d.comb+=self.branching.eq(0b1)
                            m.d.comb+=self.result.eq(self.immediate)

                    with m.Default():
                        m.d.comb+=self.branching.eq(0b0)                                                                       

            with m.Case(self.S_type):
                m.d.comb += self.load_wb.eq(0b0)
                m.d.comb += self.load_mem.eq(0b00)
                with m.Switch(self.inst_type2):
                    with m.Case(self.SB):
                        m.d.comb += self.data_to_mem.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                        m.d.comb += self.write_mem.eq(0b01)
                    with m.Case(self.SH):
                        m.d.comb += self.data_to_mem.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                        m.d.comb += self.write_mem.eq(0b10)
                    with m.Case(self.SW):
                        m.d.comb += self.data_to_mem.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra + self.immediate)
                        m.d.comb += self.write_mem.eq(0b11)        

            with m.Case(self.U_type):
                m.d.comb += self.load_wb.eq(0b1)
                m.d.comb += self.load_mem.eq(0b00)
                m.d.comb += self.write_mem.eq(0b00)
                with m.Switch(self.inst_type3):
                    with m.Case(self.LUI):
                        m.d.comb+=self.result.eq(self.immediate)

                    with m.Case(self.AUIPC):
                        m.d.comb+=self.result.eq(self.immediate+self.pc-Const(2)) 

            with m.Case(self.J_type):
                m.d.comb += self.load_wb.eq(0b1)
                m.d.comb += self.load_mem.eq(0b00)
                m.d.comb += self.write_mem.eq(0b00)
                with m.Switch(self.inst_type3):
                    with m.Case(self.JAL):
                        m.d.comb+=self.branching.eq(0b1)
                        m.d.comb+=self.result.eq(self.pc-Const(1)) 
            
            with m.Case(self.M_type):
                m.d.comb += self.load_wb.eq(0b1)
                m.d.comb += self.load_mem.eq(0b00)
                m.d.comb += self.write_mem.eq(0b00)
                with m.Switch(self.inst_type0):
                    with m.Case(self.MUL):#Both the numbers are unsigned and are stored in signed register so, if 1 in MSB its an overflow 
                        m.d.comb+=self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result64.eq(self.Ra_unsigned*self.Rb_unsigned)
                        m.d.comb+=self.result.eq(self.result64[0:32])
                    with m.Case(self.MULH):#Both are signed 
                        #m.d.comb+=self.result64.eq(self.Ra*self.Rb)
                        m.d.comb+=self.result64.eq(self.Ra*self.Rb)
                        m.d.comb+=self.result.eq(self.result64[32:64])
                    with m.Case(self.MULHSU):
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result64.eq(self.Ra*self.Rb_unsigned)
                        m.d.comb+=self.result.eq(self.result64[32:64])

                    with m.Case(self.MULHU):
                        m.d.comb+=self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result64.eq(self.Ra_unsigned*self.Rb_unsigned)
                        m.d.comb+=self.result.eq(self.result64[32:64])
                    with m.Case(self.DIV):
                        self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra_unsigned//self.Rb_unsigned)
                    with m.Case(self.DIVU):
                        m.d.comb+=self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra_unsigned//self.Rb_unsigned)
                    with m.Case(self.REM):
                        m.d.comb+=self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra_unsigned%self.Rb_unsigned)
                    with m.Case(self.REMU):
                        m.d.comb+=self.Ra_unsigned.eq(self.Ra)
                        m.d.comb+=self.Rb_unsigned.eq(self.Rb)
                        m.d.comb+=self.result.eq(self.Ra_unsigned%self.Rb_unsigned)
              
        return m

    def ports(self)->List[Signal]:
        return [self.reg_addr_in,self.reg_addr_out,self.data_to_mem,self.inst_type_out,self.inst_type1_out,self.inst_type2_out,self.inst_type3_out,self.Ra,self.Rb,self.result,self.inst_type,self.inst_type1,self.inst_type2,self.immediate,self.branching,self.inst_type3]

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()


    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.alu = alu = ALU()

    Ra = Signal(32)
    Rb = Signal(32)
    inst_type = Signal(3)
    inst_type1 = Signal(11)
    inst_type2 = Signal(10)
    immediate = Signal(32)
    branching = Signal(1)
    inst_type3 = Signal(7)
    reg_addr_in = Signal(5)
    m.d.sync += alu.Ra.eq(Ra)
    m.d.sync += alu.Rb.eq(Rb)
    m.d.sync += alu.inst_type.eq(inst_type)
    m.d.sync += alu.inst_type1.eq(inst_type1)
    m.d.sync += alu.inst_type2.eq(inst_type2)
    m.d.sync += alu.immediate.eq(immediate)
    m.d.sync += alu.inst_type3.eq(inst_type3)
    m.d.sync += alu.reg_addr_in.eq(reg_addr_in)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")


    def process():
    
        yield Ra.eq(0xFF000000)
        yield Rb.eq(0xFF000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b00000110011)   #add
        yield reg_addr_in.eq(0b10101)
        yield
        #yield Delay(1e-6)
        #yield Delay(1e-6)
        yield Ra.eq(0x0F000000)
        yield Rb.eq(0xF0000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b10000110011) #sub
        yield reg_addr_in.eq(0b10101)
        yield 
        #yield Delay(1e-6)
        yield Ra.eq(0xFE000000)
        yield Rb.eq(0xFF000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b00100110011)   #slt
        yield reg_addr_in.eq(0xA0A00000)
        yield 

        yield Ra.eq(0xFF000000)
        yield Rb.eq(0xFE000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b00110110011)   #sltu
        yield reg_addr_in.eq(0xA0A00000)
        yield 

        yield Ra.eq(0xFF000000)
        yield Rb.eq(0xFD000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b01000110011)   #xor
        yield reg_addr_in.eq(0xA0A00000)
        yield 

        yield Ra.eq(0xFF000000)
        yield Rb.eq(0xFD000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b01100110011)   #or
        yield reg_addr_in.eq(0xA0A00000)
        yield 


        yield Ra.eq(0xFF000000)
        yield Rb.eq(0xFD000000)
        yield inst_type.eq(0b111)
        yield inst_type1.eq(0b01110110011)   #and
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FF0000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b0000010011)   #addi
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FF0000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b0100010011)   #slti
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FF0000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b1100010011)   #ori
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FF0000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b1110010011)   #andi
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FF0000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b1000010011)   #xori
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFF000000)
        yield immediate.eq(0x00FFF000)
        yield inst_type.eq(0b001)
        yield inst_type2.eq(0b0100000011)   #lw
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFD000000)
        yield Rb.eq(0xFF000000)
        yield inst_type.eq(0b100)
        yield inst_type2.eq(0b1001100011)   #blt
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield Ra.eq(0xFD000000)
        yield immediate.eq(0x000000FF)
        yield inst_type.eq(0b011)      #sw
        yield reg_addr_in.eq(0xA0A00000)
        yield

        yield immediate.eq(0x000000FF)
        yield inst_type.eq(0b101)      #lui
        yield reg_addr_in.eq(0xA0A00000)
        yield inst_type3.eq(0b0110111)
        yield

        yield immediate.eq(0x000000FD)
        yield inst_type.eq(0b110)      #jal
        yield reg_addr_in.eq(0xA0A00000)
        yield inst_type3.eq(0b1101111)
        yield


#sim.add_sync_process(process,domain = "sync")
#sim.add_sync_process(process)
#with sim.write_vcd("alu.vcd","alu.gtkw",traces=[reg_addr_in,Ra,Rb,inst_type,inst_type1,inst_type2,immediate,inst_type3]+alu.ports()):
#    sim.run_until(100e-6, run_passive=True)

      

    