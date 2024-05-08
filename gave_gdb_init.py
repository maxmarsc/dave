from gave import GaveCommand, exit_handler
import gdb

GaveCommand()
gdb.events.exited.connect(exit_handler)
