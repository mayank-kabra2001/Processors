from typing import List

from nmigen import *
from nmigen.sim import *
#from nmigen.sim import *
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner


class IF_stage(Elaboratable):

    def __init__(self):
        # code
        self.Pc = Signal(10)  # input
        self.out = Signal(32)

        self.mem = Array([Signal(32) for i in range(2**10)])

        """
         Equivalent program if(a > b){ a-b} else{a+b}

		"""

    def elaborate(self, platform: Platform) -> Module:

        m = Module()

        m.d.comb += self.out.eq(self.mem[self.Pc])

        return m

    def ports(self):
        return [self.Pc, self.out]


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.if_stage = if_stage = IF_stage()
    Pc = Signal(5)
    mem = Array([Signal(32) for i in range(2**5)])
    m.d.sync += if_stage.Pc.eq(Pc)

    for i in range(2**5):
        m.d.sync += if_stage.mem[i].eq(mem[i])

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")

    def process():
        yield mem[0].eq(0b00000000000000000000000000000000)
        yield mem[1].eq(0b00000000000000000000000000000000)
        yield mem[2].eq(0b00000000000000000000000000000100)
        yield mem[3].eq(0b00000000000000000000000000000000)
        yield mem[4].eq(0b00000000000000000000010100110011)
        yield mem[5].eq(0b00000000101001010000011000010011)
        yield mem[6].eq(0b00000000101001010000011000010011)
        yield mem[7].eq(0b00000000000001010000011010110011)
        yield mem[8].eq(0b00000000111001101000011100110011)
        yield mem[9].eq(0b00000000000001110000010100110011)
        yield mem[10].eq(0b00000000101000000010100000100011)
        yield mem[11].eq(0b00000001000000000010100010000011)
        yield

        yield Pc.eq(0b00000)
        yield

        yield Pc.eq(0b00001)
        yield

        yield Pc.eq(0b00010)
        yield

        yield Pc.eq(0b00011)
        yield

        yield Pc.eq(0b00100)
        yield

        yield Pc.eq(0b00101)
        yield

        yield Pc.eq(0b00110)
        yield

        yield Pc.eq(0b00111)
        yield

        yield Pc.eq(0b01000)
        yield

        yield Pc.eq(0b01001)
        yield

        yield Pc.eq(0b01010)
        yield

        yield Pc.eq(0b01011)
        yield


#sim.add_sync_process(process, domain="sync")
#with sim.write_vcd("if_stage.vcd", "if_stage.gtkw", traces=[Pc]+if_stage.ports()):
#    sim.run_until(100e-6, run_passive=True)
