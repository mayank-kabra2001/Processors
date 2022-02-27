from typing import List

from nmigen import *
from nmigen.back.pysim import Simulator, Delay, Settle
from nmigen import Elaboratable,Module,Signal
from nmigen.build import Platform
from nmigen.cli import main_parser,main_runner

class Adder(Elaboratable):
    def __init__(self):
        self.x = Signal(8)
        self.y = Signal(8)
        self.out = Signal(8)

    def elaborate(self,platform:Platform)->Module:
        m = Module()
        # mydomain = ClockDomain("clk", clk_edge="pos")
        # m.domains += mydomain

        # print(mydomain.clk)

        m.d.sync += self.out.eq(self.x+self.y)

        return m

    def ports(self)->List[Signal]:
        return [self.x,self.y,self.out]

if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()


    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.adder = adder = Adder()

    x = Signal(8)
    y = Signal(8)
    m.d.sync += adder.x.eq(x)
    m.d.sync += adder.y.eq(y)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")


    def process():
        yield x.eq(0x00)
        yield y.eq(0x00)
        yield
        #yield Delay(1e-6)
        yield x.eq(0xFF)
        yield y.eq(0xFF)
        yield 
        #yield Delay(1e-6)
        yield x.eq(0x00)
        yield y.eq(0xFF)
        yield 
        #yield Delay(1e-6)

#sim.add_sync_process(process,domain = "sync")
## sim.add_sync_process(process)
#with sim.write_vcd("test.vcd","test.gtkw",traces=[x,y]+adder.ports()):
    #sim.run_until(100e-6, run_passive=True)