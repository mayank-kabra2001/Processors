from typing import List

from nmigen import *
from nmigen.sim import *
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from all_stages.If_stage import *
from all_stages.ID_stage import *
from all_stages.ALU import *
from all_stages.Mem_stage import *
from all_stages.Writeback_stage import *
from all_stages.memory import *
from all_stages.register_file import *

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    pos = ClockDomain("pos", async_reset=True)
    neg = ClockDomain("neg",clk_edge="neg",async_reset=True)
    neg.clk = pos.clk
    m.domains += [neg,pos]

    m.submodules.IF = IF = IF_stage()
    m.submodules.ID = ID = ID()
    m.submodules.ALU = ALU = ALU()
    m.submodules.MEM = MEM = Memory_stage()
    m.submodules.WB = WB = WriteBack()
    m.submodules.reg_file = reg_file = Register_file()
    m.submodules.memory = memory = Memory_file()

    pc = Signal(10)
    wb_stop_beq = Signal(1)
    counter_branch = Signal(3)
    counter_jump = Signal(3)
    Busy = Array([Signal(1) for i in range(32)])
    Busy1 = Array([Signal(1) for i in range(32)])
    nthforwarding = Array([Signal(1) for i in range(32)])

    #m.d.sync += IF.mem[Const(0)].eq(0b00000000100000010010011110000011)
    #m.d.sync += IF.mem[Const(1)].eq(0b11111111111100000000001000010011)
    m.d.sync += IF.mem[Const(0)].eq(0b00000000000100000010000110100011)
    
    m.d.sync += IF.mem[Const(1)].eq(0b00000000001000000010000100100011)   #132547698
    m.d.sync += IF.mem[Const(2)].eq(0b00000000001100000010000010100011)
    m.d.sync += IF.mem[Const(3)].eq(0b00000000000100000000001100010011)
    m.d.sync += IF.mem[Const(4)].eq(0b00000000001100000000010100010011)
    m.d.sync += IF.mem[Const(5)].eq(0b11111111111100000000001000010011)

    #main_loop

    m.d.sync += IF.mem[Const(6)].eq(0b00000000000100100000001000010011)
    m.d.sync += IF.mem[Const(7)].eq(0b00000110101000100101111101100011)
    m.d.sync += IF.mem[Const(8)].eq(0b00000000000100100000001010010011)
  
    #inner_loop

    m.d.sync += IF.mem[Const(9)].eq(0b11111110101000101101111011100011)
    m.d.sync += IF.mem[Const(10)].eq(0b00000000011000101000010000110011)
    m.d.sync += IF.mem[Const(11)].eq(0b00000000011000100000010010110011)
    m.d.sync += IF.mem[Const(12)].eq(0b00000000000001000010010110000011)
    m.d.sync += IF.mem[Const(14)].eq(0b00000000000001001010011000000011)
    m.d.sync += IF.mem[Const(16)].eq(0b00000000110001011101010001100011)
    m.d.sync += IF.mem[Const(17)].eq(0b00000000110001000010000000100011)
    m.d.sync += IF.mem[Const(18)].eq(0b00000000101101001010000000100011)
    m.d.sync += IF.mem[Const(19)].eq(0b00000000000100101000001010010011)
    m.d.sync += IF.mem[Const(20)].eq(0b11111110000000000000101011100011)


    #b1
    m.d.sync += IF.mem[Const(24)].eq(0b00000000000100101000001010010011)
    m.d.sync += IF.mem[Const(26)].eq(0b11111110000000000000011111100011)
    

    


    #m.d.sync += IF.mem[Const(1)].eq(0xFCE08793)
    with m.If(ID.ifload==Const(1)):
        m.d.sync += IF.Pc.eq(pc-1) #mem of IF needed to be hardcoded 
        m.d.sync += ID.instruction.eq(0x00000000) 
    with m.Else():
        m.d.sync += IF.Pc.eq(pc)
        m.d.sync += ID.instruction.eq(IF.out) 
    m.d.comb += reg_file.load_Rs1_addr.eq(ID.s1)
    m.d.comb += reg_file.load_Rs2_addr.eq(ID.s2)
    
    with m.If(ID.des != Const(0)):
        m.d.sync += Busy[ID.des].eq(Const(1))#Busy[ID.des]+Const(1))


    with m.If(Busy[ID.s1] == Const(1)):
        with m.If(Busy1[ID.s1] == Const(0)):
            m.d.neg += ID.s1_data_in.eq(ALU.result)
        with m.Else():
            m.d.neg += ID.s1_data_in.eq(memory.data_out)

    with m.If(Busy[ID.s2] == Const(1)):
        with m.If(Busy1[ID.s2] == Const(0)):
            m.d.neg += ID.s2_data_in.eq(ALU.result)
        with m.Else():
            m.d.neg += ID.s2_data_in.eq(memory.data_out)

    with m.If(Busy[ID.s1]==Const(0)):
        m.d.neg += ID.s1_data_in.eq(reg_file.write_Rs1_data)

    with m.If(Busy[ID.s2]==Const(0)):
        m.d.neg += ID.s2_data_in.eq(reg_file.write_Rs2_data)

     
    

    

    m.d.sync += ALU.reg_addr_in.eq(ID.des)
    #m.d.sync += ALU.reg_addr_in.eq(ID.des)
    m.d.sync += ALU.inst_type.eq(ID.instruction_type)
    m.d.sync += ALU.inst_type1.eq(ID.it1)
    m.d.sync += ALU.inst_type2.eq(ID.it2)
    m.d.sync += ALU.inst_type3.eq(ID.it3)
    m.d.sync += ALU.Ra.eq(ID.s1data_out)
    m.d.sync += ALU.Rb.eq(ID.s2data_out)
    m.d.sync += ALU.immediate.eq(ID.signextended_immediate)
    with m.If(ID.des!=ALU.reg_addr_in):
        m.d.sync += Busy1[ALU.reg_addr_in].eq(Const(1))
    with m.If(ALU.branching == Const(1)):
        m.d.sync += pc.eq(pc+ALU.immediate-Const(2))
    with m.Elif(ID.ifload == Const(1)):
        m.d.sync += pc.eq(pc)  
    with m.Else():
        m.d.sync += pc.eq(pc+Const(1))  
    with m.If(ALU.branching == Const(1)):
        m.d.sync += counter_branch.eq(counter_branch+Const(1))


    with m.If(counter_branch == Const(0)):
        m.d.comb += memory.load.eq(ALU.load_mem)
        m.d.comb += memory.write.eq(ALU.write_mem)
        m.d.comb += memory.data_in.eq(ALU.Rb)
        m.d.comb += memory.addr.eq(ALU.result)

    
        m.d.sync += memory.load_wb.eq(ALU.load_wb)
        m.d.sync += memory.reg_addr_out.eq(ALU.reg_addr_out)
        m.d.comb += memory.alu_result.eq(ALU.result)

        
    with m.Elif(counter_branch == Const(4)):
        m.d.comb += memory.load.eq(ALU.load_mem)
        m.d.comb += memory.write.eq(ALU.write_mem)
        m.d.comb += memory.data_in.eq(ALU.Rb)
        m.d.comb += memory.addr.eq(ALU.result)

    
        m.d.sync += memory.load_wb.eq(ALU.load_wb)
        m.d.sync += memory.reg_addr_out.eq(ALU.reg_addr_out)
        m.d.comb += memory.alu_result.eq(ALU.result)
        m.d.sync += counter_branch.eq(Const(0))

    with m.Else():
        m.d.sync += counter_branch.eq(counter_branch+Const(1))
        m.d.comb += memory.load.eq(0b00)
        m.d.comb += memory.write.eq(0b00)
        m.d.comb += memory.data_in.eq(0x00000000)
        m.d.comb += memory.addr.eq(0x00000000)

    
        m.d.sync += memory.load_wb.eq(0b0)
        m.d.sync += memory.reg_addr_out.eq(0b00000)
        m.d.comb += memory.alu_result.eq(0x00000000)





    m.d.comb += reg_file.write.eq(memory.load_wb)  #pos->comb
    m.d.comb += reg_file.write_addr.eq(memory.reg_addr_out)
    m.d.comb += reg_file.write_data.eq(memory.data_out)
    
    with m.If(ALU.reg_addr_out !=reg_file.write_addr):
        m.d.sync += Busy[reg_file.write_addr].eq(Const(0))#Busy[reg_file.write_addr]-Const(1))
        m.d.sync += Busy1[reg_file.write_addr].eq(Const(0))
    
    #m.d.sync += Busy[reg_file.write_addr].eq(Busy[reg_file.write_addr]-Const(1))
    #m.d.neg += nthforwarding[reg_file.write_addr].eq(Const(0))



    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    sim.add_clock(1e-6,domain="pos")
    sim.add_clock(1e-6,domain = "neg")

    def process():
        yield

sim.add_sync_process(process,domain="sync")  # or sim.add_sync_process(process), see below
with sim.write_vcd("test.vcd", "test.gtkw", traces=IF.ports()+ID.ports()+ALU.ports()+MEM.ports()+WB.ports()+reg_file.ports()+memory.ports()):
    sim.run_until(100e-6, run_passive=True)
