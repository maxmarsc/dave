from typing import List


def find_all(to_parse: str, to_find: str) -> List[int]:
    found = []
    last = -1
    while (last := to_parse.find(to_find, last + 1)) != -1:
        found.append(last)
    return found


def parse_template(typename: str) -> List[str]:
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
