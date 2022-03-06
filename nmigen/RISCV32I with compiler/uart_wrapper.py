from typing import List

from nmigen import *
from nmigen.back.pysim import Simulator, Delay, Settle
from nmigen import Elaboratable,Module,Signal
from nmigen.build import Platform
from nmigen.cli import main_parser,main_runner
from adder import Adder
from Wrapper_class import Wrapper

class UART(Elaboratable):
    """
    Parameters
    ----------
    divisor : int
        Set to ``round(clk-rate / baud-rate)``.
        E.g. ``12e6 / 115200`` = ``104``.
    """
    def __init__(self, divisor, data_bits=8):
        assert divisor >= 4

        self.data_bits = data_bits
        self.divisor   = divisor

        self.tx_o    = Signal()
        self.rx_i    = Signal()

        self.tx_data = Signal(data_bits)
        self.tx_rdy  = Signal()
        self.tx_ack  = Signal()

        self.rx_data = Signal(data_bits)
        self.rx_err  = Signal()
        self.rx_ovf  = Signal()
        self.rx_rdy  = Signal()
        self.rx_ack  = Signal()
        self.rx_rdy_count = Signal(1)
        self.pc = Signal(10)
        self.data_counter = Signal(3)
        self.b1 = Signal(8)
        self.b2 = Signal(8)
        self.b3 = Signal(8)
        self.b4 = Signal(8)
        self.delay = Signal(1)
        self.done = Signal(1)
    def elaborate(self, platform):
        m = Module()

        m.submodules.wrapper = wrapper = Wrapper()
        m.submodules.adder = adder = Adder()

        tx_phase = Signal(range(self.divisor))
        tx_shreg = Signal(1 + self.data_bits + 1, reset=-1)
        tx_count = Signal(range(len(tx_shreg) + 1))

        m.d.comb += self.tx_o.eq(tx_shreg[0])
        with m.If(tx_count == 0):
            m.d.comb += self.tx_ack.eq(1)
            with m.If(self.tx_rdy):
                m.d.sync += [
                    tx_shreg.eq(Cat(C(0, 1), self.tx_data, C(1, 1))),
                    tx_count.eq(len(tx_shreg)),
                    tx_phase.eq(self.divisor - 1),
                ]
        with m.Else():
            with m.If(tx_phase != 0):
                m.d.sync += tx_phase.eq(tx_phase - 1)
            with m.Else():
                m.d.sync += [
                    tx_shreg.eq(Cat(tx_shreg[1:], C(1, 1))),
                    tx_count.eq(tx_count - 1),
                    tx_phase.eq(self.divisor - 1),
                ]

        rx_phase = Signal(range(self.divisor))
        rx_shreg = Signal(1 + self.data_bits + 1, reset=-1)
        rx_count = Signal(range(len(rx_shreg) + 1))

        m.d.comb += self.rx_data.eq(rx_shreg[1:-1])
        with m.If(rx_count == 0):
            m.d.comb += self.rx_err.eq(~(~rx_shreg[0] & rx_shreg[-1]))
            with m.If(~self.rx_i):
                with m.If(self.rx_ack | ~self.rx_rdy):
                    m.d.sync += [
                        self.rx_rdy.eq(0),
                        self.rx_ovf.eq(0),
                        rx_count.eq(len(rx_shreg)),
                        rx_phase.eq(self.divisor // 2),
                    ]
                with m.Else():
                    m.d.sync += self.rx_ovf.eq(1)
        with m.Else():
            with m.If(rx_count == 10):
                with m.If(rx_phase == 0):
                    with m.If(self.data_counter == 4):
                        m.d.sync += self.data_counter.eq(Const(1))
                    with m.Else():
                        m.d.sync += self.data_counter.eq(self.data_counter + 1)


            with m.If(rx_phase != 0):
                m.d.sync += rx_phase.eq(rx_phase - 1)
            with m.Else():
                m.d.sync += [
                    rx_shreg.eq(Cat(rx_shreg[1:], self.rx_i)),
                    rx_count.eq(rx_count - 1),
                    rx_phase.eq(self.divisor - 1),
                ]
                with m.If(rx_count == 1):
                    m.d.sync += self.rx_rdy.eq(1)

        with m.If(self.data_counter == 1): 
            with m.If(self.rx_rdy == 1): 
                m.d.sync +=self.b1.eq(self.rx_data)
        with m.Elif(self.data_counter == 2): 
            with m.If(self.rx_rdy == 1): 
                m.d.sync +=self.b2.eq(self.rx_data)
        with m.Elif(self.data_counter == 3): 
            with m.If(self.rx_rdy == 1): 
                m.d.sync +=self.b3.eq(self.rx_data)
        with m.Elif(self.data_counter == 4): 
            with m.If(self.rx_rdy == 1): 
                m.d.sync +=self.b4.eq(self.rx_data)
                #m.d.sync +=self.data_counter.eq(Const(1))
                #m.d.sync += wrapper.IF.mem[self.pc].eq(Cat(self.b4,self.b3,self.b2,self.b1))
                m.d.sync += self.delay.eq(Const(1))  
                with m.If(self.rx_rdy_count == 0):
                    m.d.sync += self.pc.eq(self.pc+1)
                    m.d.sync += self.rx_rdy_count.eq(Const(1))
        with m.If(self.rx_rdy == 0):
            m.d.sync += self.rx_rdy_count.eq(Const(0)) 
        with m.If(self.delay==1):
            m.d.sync += wrapper.IF.mem[self.pc].eq(Cat(self.b4,self.b3,self.b2,self.b1))
            m.d.sync += self.delay.eq(Const(0))  
        return m

    
    def ports(self)->List[Signal]:
        return [self.tx_o, self.rx_i,
        self.tx_data, self.tx_rdy, self.tx_ack,
        self.rx_data, self.rx_rdy, self.rx_err, self.rx_ovf, self.rx_ack
    ]

if __name__ == "__main__":

    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)

    m.submodules.uart = uart = UART(divisor=5)

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")

    #  sim = Simulator(uart)
    #     sim.add_clock(1e-6)

    def loopback_proc():
        while True:
            yield uart.rx_i.eq((yield uart.tx_o))
            yield
    sim.add_sync_process(loopback_proc)

    def transmit_proc1():
        #inst = [[0x00,0x31,0x00,0xB3],[0x00,0x20,0x82,0x33],[0x00,0x30,0x82,0x33]]
        inst = [[0xFC,0xE0,0x87,0x93],[0x00,0x73, 0x02,0xB3],[0xFC,0xE0,0x87,0x93],[0x00,0x73, 0x02,0xB3]]#
        for i in range(len(inst)):
            for j in range(4):
                assert (yield uart.tx_ack)
                if(i==0 and j==0):
                      assert not (yield uart.rx_rdy)
                yield uart.tx_data.eq(inst[i][j])
                yield uart.tx_rdy.eq(1)
                yield
                yield uart.tx_rdy.eq(0)
                yield
                assert not (yield uart.tx_ack)

                for _ in range(uart.divisor * 12): yield
                assert (yield uart.tx_ack)
                if(i==0 and j==0):
                      assert not (yield uart.tx_rdy)
                assert not (yield uart.rx_err)
                assert (yield uart.rx_data) == inst[i][j]

                yield uart.rx_ack.eq(1)
                yield      

                
       

       
                    



        

        
      

       

       
        
        
    sim.add_sync_process(transmit_proc1)

with sim.write_vcd("uart.vcd", "uart.gtkw"):
    sim.run_until(10000e-6, run_passive=True)

#     def process():
#         assert (yield uart.tx_ack)
#         assert not (yield uart.rx_rdy)

#         yield uart.tx_data.eq(0x5A)
#         yield uart.tx_rdy.eq(1)
#         yield
#         yield uart.tx_rdy.eq(0)
#         yield
#         assert not (yield uart.tx_ack)

#         for _ in range(uart.divisor * 12): yield

#         assert (yield uart.tx_ack)
#         assert (yield uart.rx_rdy)
#         # assert not (yield uart.rx_err)
#         assert (yield uart.rx_data) == 0x5A

#         yield uart.rx_ack.eq(1)
#         yield

# sim.add_sync_process(process,domain = "sync")
# # sim.add_sync_process(process)
# with sim.write_vcd("test.vcd","test.gtkw",traces=uart.ports()):
#     sim.run_until(100e-6, run_passive=True)

    # args = parser.parse_args()
    # if args.action == "simulate":
    #     from nmigen.back.pysim import Simulator, Passive

    #     sim = Simulator(uart)
    #     sim.add_clock(1e-6)

    #     def loopback_proc():
    #         yield Passive()
    #         while True:
    #             yield uart.rx_i.eq((yield uart.tx_o))
    #             yield
    #     sim.add_sync_process(loopback_proc)

    #     def transmit_proc():
    #         assert (yield uart.tx_ack)
    #         assert not (yield uart.rx_rdy)

    #         yield uart.tx_data.eq(0x5A)
    #         yield uart.tx_rdy.eq(1)
    #         yield
    #         yield uart.tx_rdy.eq(0)
    #         yield
    #         assert not (yield uart.tx_ack)

    #         for _ in range(uart.divisor * 12): yield

    #         assert (yield uart.tx_ack)
    #         assert (yield uart.rx_rdy)
    #         assert not (yield uart.rx_err)
    #         assert (yield uart.rx_data) == 0x5A

    #         yield uart.rx_ack.eq(1)
    #         yield
    #     sim.add_sync_process(transmit_proc)

    #     with sim.write_vcd("uart.vcd", "uart.gtkw"):
    #         sim.run()

    # if args.action == "generate":
    #    from nmigen.back import verilog

    #    print(verilog.convert(uart, ports=ports))