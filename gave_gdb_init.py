from gave import GaveCommand, exit_handler, stop_handler
import gdb

GaveCommand()
gdb.events.exited.connect(exit_handler)
gdb.events.stop.connect(stop_handler)
