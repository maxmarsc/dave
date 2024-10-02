import gdb  # type: ignore
import gdb.types  # type: ignore

from dave.server.process import DaveProcess
from dave.server.container_factory import ContainerFactory, ContainerError
from dave.common.logger import Logger

from .value import GdbValue

last_frame = None  # type: gdb.Frame


def exit_handler(event):
    if DaveProcess().is_alive():
        # pass
        DaveProcess().should_stop()
        DaveProcess().join()


def stop_handler(event: gdb.StopEvent):
    if DaveProcess().is_alive():
        DaveProcess().dbgr_update_callback()


def frame_checker():
    global last_frame  # type: gdb.Frame
    try:
        current_frame = gdb.selected_frame()
        if current_frame != last_frame and DaveProcess().is_alive():
            if last_frame is not None:
                DaveProcess().dbgr_update_callback()
            last_frame = current_frame
    except gdb.error:
        pass


class GdbCommand(gdb.Command):
    """Custom GDB 'dave' command for advanced debugging tasks."""

    def __init__(self):
        super(GdbCommand, self).__init__("dave", gdb.COMMAND_USER, gdb.COMPLETE_SYMBOL)

    @staticmethod
    def __check_for_running_inferior() -> bool:
        """Return True if the current inferior is actually started"""
        if gdb.selected_inferior().pid <= 0:
            return False
        else:
            return True

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) < 1:
            print("Usage: dave <subcommand> [args]")
            return

        if not GdbCommand.__check_for_running_inferior():
            Logger().get().error("no processus detected")
            return

        subcommand = args[0]
        # self.msg_queue.put(args[1])
        if subcommand == "p":
            self.print_variable(args[1:])
        elif subcommand == "p2":
            self.print_attribute(args[1:])
        elif subcommand == "show":
            self.show(args[1:])
        elif subcommand == "delete":
            self.delete_container(args[1:])
        elif subcommand == "freeze":
            self.freeze_container(args[1:])
        elif subcommand == "concat":
            self.concat_container(args[1:])
        else:
            Logger().get().error(f"Unknown subcommand '{subcommand}'")

    def show(self, args):
        if len(args) < 1 or len(args) > 2:
            raise gdb.GdbError("Usage: dave show VARIABLE [DIM1[,DIM2]]")

        varname = args[0]
        if len(args) > 1:
            dims = [int(val) for val in args[1].split(",")]
        else:
            dims = list()
        var = GdbValue(gdb.parse_and_eval(varname), varname)
        typename = var.typename()
        try:
            container = ContainerFactory().build(var, typename, varname, dims)
            Logger().get().info(f"Added {varname} : {container.id}")
        except (ContainerError, TypeError) as e:
            raise gdb.GdbError(e.args[0])
        if not DaveProcess().is_alive():
            DaveProcess().start()
        DaveProcess().add_to_model(container)

    def delete_container(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: dave delete VARIABLE|CONTAINER_ID")

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().delete_container(args[0]):
            raise gdb.GdbError(f"{args[0]} is not a valid name or container id")

    def freeze_container(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: dave freeze VARIABLE|CONTAINER_ID")

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().freeze_container(args[0]):
            raise gdb.GdbError(f"{args[0]} is not a valid name or container id")

    def concat_container(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: dave concat VARIABLE|CONTAINER_ID")

        if not DaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not DaveProcess().concat_container(args[0]):
            raise gdb.GdbError(f"{args[0]} is not a valid name or container id")

    def print_attribute(self, args):
        if len(args) != 2:
            raise gdb.GdbError("Usage: dave p2 <variable> <attribute>")

        var_name = args[0]
        attr_name = args[1].split(".")
        try:
            attr = gdb.parse_and_eval(var_name)
            for name in attr_name:
                attr = attr[name]
            # attr = gdb.parse_and_eval(var_name)[attr_name]
            print(f"Type: {attr.type}")
            print(
                f"(real) Type: {gdb.types.get_basic_type(attr.type).strip_typedefs()}"
            )
            print(f"Address: {attr.address}")
            print(f"Value: {attr}")
            print(f"(hex) Value: {hex(attr)}")
        except (gdb.error, RuntimeError) as e:
            print(f"Error accessing variable '{var_name}': {str(e)}")

    def print_variable(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: dave p <variable>")

        var_name = args[0]
        try:
            var = gdb.parse_and_eval(var_name)
            if var.is_optimized_out:
                print(f"Variable '{var_name}' is optimized out.")
            else:
                print(f"Type: {var.type}")
                print(f"(real) Type: {gdb.types.get_basic_type(var.type)}")
                print(f"Value: {var}")
                # print(f"(hex) Value: {hex(var)}")
                if var.address is not None:
                    print(f"Address: {var.address}")
                else:
                    print(f"Address: <not available>")
        except (gdb.error, RuntimeError) as e:
            print(f"Error accessing variable '{var_name}': {str(e)}")
