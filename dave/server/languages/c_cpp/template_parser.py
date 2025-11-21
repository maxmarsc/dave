from typing import List


def find_all(to_parse: str, to_find: str) -> List[int]:
    found = []
    last = -1
    while (last := to_parse.find(to_find, last + 1)) != -1:
        found.append(last)
    return found


def parse_template(typename: str) -> List[str]:
    """
    Parse a C++/Rust instantiated template class or struct.

    This function parses the template name and parameters. Parameters themselves
    could be templates.

    This function only works on instantiated template typenames as returned by the
    debugger.
    ```
    std::array<float, 16ul>                     # C++ OK
    alloc::vec::Vec<f32, alloc::alloc::Global>  # Rust OK
    ```

    It won't work on templated function call or templated struct definition as you
    could see them in your code:
    ```
    Vec::<i32>::new()                           # Rust NOT OK
    struct Foo<T, const N: usize>               # Rust NOT OK
    ```

    (you shouldn't encounter this, it's just to prevent a use of this function
    in the bad context)

    Parameters
    ----------
    typename : str
        The templated typename to parse

    Returns
    -------
    List[str]
        A list containing all the types in the template. The first value is the
        name of the templated class itself. The following values are, in order,
        the template parameters.

    Raises
    ------
    ValueError
        If it fails to parse the template
    """
    starts = find_all(typename, "<")
    ends = find_all(typename, ">")
    if len(starts) != len(ends):
        raise ValueError(f"{typename} is not a valid template")

    if len(starts) == 0:
        return [typename]

    template_name = typename[: starts[0]]
    template_parameters = typename[starts[0] + 1 : ends[-1]]
    template_parameters_starts = [start - (starts[0] + 1) for start in starts[1:]]
    template_parameters_ends = [end - (starts[0] + 1) for end in ends[:-1]]

    if "," not in template_parameters:
        return [template_name, template_parameters]

    ret = [template_name + typename[ends[-1] + 1 :]]
    commas = find_all(template_parameters, ",")
    prev_i_comma = -1
    for i_comma in commas:
        # count how many < and > between the last comma and this one
        starts_count = sum(
            [
                1 if prev_i_comma < i_start < i_comma else 0
                for i_start in template_parameters_starts
            ]
        )
        ends_count = sum(
            [
                1 if prev_i_comma < i_end < i_comma else 0
                for i_end in template_parameters_ends
            ]
        )

        if starts_count == ends_count:
            ret.append(template_parameters[prev_i_comma + 1 : i_comma].replace(" ", ""))
            prev_i_comma = i_comma

    ret.append(template_parameters[prev_i_comma + 1 :].replace(" ", ""))
    return ret
