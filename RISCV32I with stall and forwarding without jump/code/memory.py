from typing import List

from nmigen import *
from nmigen.sim import *

from nmigen import Elaboratable,Module,Signal
from nmigen.build import Platform
from nmigen.cli import main_parser,main_runner

class Memory_file(Elaboratable):
    def __init__(self):
        #inputs
        self.load = Signal(2) 
        self.addr = Signal(10)
        self.write = Signal(2)
        self.data_in = Signal(32)

        #output 
        self.data_out = Signal(32)

        self.mem = Array([Signal(32) for i in range(2**10)])

        self.nothing = 0b00
        self.byte = 0b01
        self.halfword = 0b01
        self.word = 0b11

        self.load_wb = Signal(1)
        self.reg_addr_out = Signal(5)
        self.alu_result = Signal(32)
        


    def elaborate(self,platform:Platform)->Module:
        m = Module()
        with m.Switch(self.load):
            with m.Case(self.nothing):
                m.d.sync += self.data_out.eq(self.alu_result)
            with m.Case(self.byte):
                m.d.sync += self.data_out.eq(self.mem[self.addr][0:8])
            with m.Case(self.halfword):
                m.d.sync += self.data_out.eq(self.mem[self.addr][0:16])
            with m.Case(self.word):
                m.d.sync += self.data_out.eq(self.mem[self.addr])

        with m.Switch(self.write):
            with m.Case(self.nothing):
                m.d.sync += self.mem[0].eq(0)
            with m.Case(self.byte):
                m.d.sync += self.mem[self.addr][0:7].eq(self.data_in[0:8])
            with m.Case(self.halfword):
                m.d.sync += self.mem[self.addr][0:15].eq(self.data_in[0:16])
            with m.Case(self.word):
                m.d.sync += self.mem[self.addr].eq(self.data_in)

        return m
                

    def ports(self)->List[Signal]:
        return [self.load,
        self.addr,
        self.write,
        self.data_in,
        self.data_out] 

if(__name__=="__main__"):
    parser = main_parser()
    args = parser.parse_args()


    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.Memory_file = Memory_file = Memory_file()

    load = Signal(2) 
    addr = Signal(10)
    write = Signal(2)
    data_in = Signal(32)

    m.d.comb += Memory_file.load.eq(load)
    m.d.comb += Memory_file.addr.eq(addr)
    m.d.comb += Memory_file.write.eq(write)
    m.d.comb += Memory_file.data_in.eq(data_in)



    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    def process():
        yield write.eq(0b01)
        yield addr.eq(0b0000000100)
        yield data_in.eq(0x11111110)
        yield
        yield write.eq(0b10)
        yield addr.eq(0b0000000010)
        yield data_in.eq(0x11111000)
        yield
        yield write.eq(0b11)
        yield addr.eq(0b0000000001)
        yield data_in.eq(0x10000000)
        yield        
        yield load.eq(0b01)
        yield addr.eq(0b0000000100)
        yield 
        yield load.eq(0b10)
        yield addr.eq(0b0000000010)
        yield
        yield load.eq(0b11)
        yield addr.eq(0b0000000001)
        yield


#sim.add_sync_process(process)
#with sim.write_vcd("mem.vcd","mem.gtkw",traces=Memory_file.ports()):
#	sim.run_until(100e-6, run_passive=True)

