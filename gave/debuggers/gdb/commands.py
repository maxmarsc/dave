import gdb  # type: ignore
import gdb.types  # type: ignore

from ...process import GaveProcess

from ...container_factory import ContainerFactory, ContainerError
from .value import GdbValue


def exit_handler(event):
    if GaveProcess().is_alive():
        # pass
        GaveProcess().should_stop()
        GaveProcess().join()


def stop_handler(event: gdb.StopEvent):
    if GaveProcess().is_alive():
        GaveProcess().dbgr_update_callback()


class GdbCommand(gdb.Command):
    """Custom GDB 'gave' command for advanced debugging tasks."""

    def __init__(self):
        super(GdbCommand, self).__init__("gave", gdb.COMMAND_USER, gdb.COMPLETE_SYMBOL)

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
            print("Usage: gave <subcommand> [args]")
            return

        if not GdbCommand.__check_for_running_inferior():
            print("Error: no processus detected")
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
        else:
            print(f"Unknown subcommand '{subcommand}'")

    def show(self, args):
        if len(args) < 1 or len(args) > 2:
            raise gdb.GdbError("Usage: gave show VARIABLE [DIM1[,DIM2]]")

        varname = args[0]
        if len(args) > 1:
            dims = [int(val) for val in args[1].split(",")]
        else:
            dims = list()
        var = GdbValue(gdb.parse_and_eval(varname))
        typename = var.typename()
        try:
            container = ContainerFactory().build(var, typename, varname, dims)
            print(f"Built {varname} : {container.id}")
        except (ContainerError, TypeError) as e:
            raise gdb.GdbError(e.args[0])
        if not GaveProcess().is_alive():
            GaveProcess().start()
        GaveProcess().add_to_model(container)

    def delete_container(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: gave delete VARIABLE|CONTAINER_ID")

        if not GaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not GaveProcess().delete_container(args[0]):
            raise gdb.GdbError(f"{args[0]} is not a valid name or container id")

    def freeze_container(self, args):
        if len(args) != 1:
            raise gdb.GdbError("Usage: gave freeze VARIABLE|CONTAINER_ID")

        if not GaveProcess().is_alive():
            raise gdb.GdbError("Dave is not started")

        if not GaveProcess().freeze_container(args[0]):
            raise gdb.GdbError(f"{args[0]} is not a valid name or container id")

    def print_attribute(self, args):
        if len(args) != 2:
            raise gdb.GdbError("Usage: gave p2 <variable> <attribute>")

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
            raise gdb.GdbError("Usage: gave p <variable>")

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
