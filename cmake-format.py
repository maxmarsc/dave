with section("format"):
    # If an argument group contains more than this many sub-groups (parg or kwarg
    # groups) then force it to a vertical layout.
    max_subgroups_hwrap = 2

    # If a positional argument group contains more than this many arguments, then
    # force it to a vertical layout.
    max_pargs_hwrap = 4

    # If a statement is wrapped to more than one line, than dangle the closing
    # parenthesis on its own line.
    dangle_parens = True

    # A list of command names which should always be wrapped
    always_wrap = [
        "target_compile_definitions",
        "target_compile_options",
        "target_link_libraries",
        "target_link_directories",
        "target_include_directories",
        "set_target_properties",
        "add_library",
        "add_executable",
        "ExternalProject_Add",
    ]
