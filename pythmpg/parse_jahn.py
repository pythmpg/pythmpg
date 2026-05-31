"""
Parser for index symmetrization information in Jahn symbols.

Defines two functions intended to be called externally:
:func:`parse_jahn_symbol`, which parses Jahn symbols
into structured instruction blocks describing the needed
symmetrization or antisymmetrization over tensor axes, and
:func:`jahn_rank` to return the rank of the tensor.

Notes
-----
Jahn symbols passed to the parser should lack any preceding ``'a'``
or ``'e'`` characters.  Results are cached in the module-level
``jahn_dict`` to avoid redundant parsing of repeated symbols.
"""

# Dictionary used to hold results for Jahn symbols that have
# already been parsed as a result of earlier function calls
jahn_dict = {}

# Digits allowed in Jahn symbols
digits = set("12345678")
# Characters allowed in Jahn symbols
valid_chars = set("V[]{}12345678")

# Dictionary mapping open bracket to type of symmetrization
s_dict = {"[": "symm", "{": "asymm"}

# Current axis of tensor
# Global variable incremented as parsing proceeds
axis = 0


# define custom exception
class ParsingError(Exception):
    pass


# Global print control variable
if_pr = False


# Define custom print function conditional on if_print
# Note that parsing errors are printed regardless
def jprint(text):
    if if_pr:
        print("  " + text)


def parse_jahn_symbol(jahn, if_print=False):
    """
    Parse the index symmetrization information in a Jahn symbol.

    Converts the Jahn symbol into an instruction set represented
    as a nested tuple structure specifying which tensor axes are
    subject to symmetrization or antisymmetrization.  Results are
    cached in ``jahn_dict`` so that repeated calls with the same
    symbol entail no overhead.

    Parameters
    ----------
    jahn : str
        Jahn symbol to parse, lacking any preceding ``'a'`` or ``'e'``
        characters.
    if_print : bool, optional
        If ``True``, print intermediate parsing steps to stdout.
        Default is ``False``.

    Returns
    -------
    instructions : tuple or None
        Nested tuple specifying tensor axes and the symmetrization
        operations to be applied to them.  Returns ``None`` if the
        symbol contains illegal characters or if the parser fails.
    """

    global axis, if_pr
    if_pr = if_print

    # If Jahn symbol has already been parsed, return saved result
    if jahn in jahn_dict:
        return jahn_dict[jahn]

    # Preliminary clean-up, e.g., 'V[V2V2]V' -> '1[22]1'
    if not set(jahn).issubset(valid_chars):
        jprint(f"\n  {jahn}  ->")
        print(f"\n  PARSING ERROR: Illegal characters in Jahn symbol {jahn}")
        jahn_dict[jahn] = None
        return None

    # Get rid of 'V' symbols to construct block text b_text
    j_len = len(jahn)
    b_text = ""
    i = 0
    while i < j_len:
        if jahn[i] == "V":
            if i + 1 == j_len:
                b_text += "1"
            else:
                if jahn[i + 1] in digits:
                    b_text += jahn[i + 1]
                    i += 1
                else:
                    b_text += "1"
        else:
            b_text += jahn[i]
        i += 1
    # Print cleaned-up Jahn symbol as block text
    jprint(f"\n  {jahn}  ->  {b_text}")

    # Now prepare for main parsing procedure
    axis = 0  # Will be incremented inside recursive procedure
    depth = 0  # Will go up and down with recursive calls and returns
    try:
        instructions = list_to_tuple("nosymm", b_text, depth)
    except ParsingError as e:
        print(f"\n  PARSING ERROR for '{jahn}': {e}")
        jahn_dict[jahn] = None
        return None

    jprint(f"Operation specification for tensor of rank {axis}:")
    jprint(f"{instructions}")

    jahn_dict[jahn] = instructions
    return instructions


# ----------------------------------------
# Define rank function (called externally)
# ----------------------------------------


def jahn_rank(instructions):
    """
    Determine the tensor rank from a parsed operation specification.

    Parameters
    ----------
    instructions : tuple
        Nested instruction specification as returned by
        :func:`parse_jahn_symbol`.

    Returns
    -------
    rank : int
        Rank of the tensor (zero in the case of scalars).
    """
    # Find largest digit in string representation of instructions
    x = [int(char) for char in str(instructions) if char.isdigit()]
    # Add one to obtain the rank (or return 0 for a scalar)
    rank = 0 if len(x) == 0 else 1 + max(x)
    return rank


# --------------------------------------------------------------
# The remaining functions are intended as private to this module
# --------------------------------------------------------------


def list_to_tuple(job, b_text, depth):
    """
    Recursively parse a block text string into an instruction tuple

    Constructs and returns an instruction block of the form
    ``(job, obj_list)``, where ``obj_list`` is a list of axes
    or sub-blocks, built by recursively processing any nested
    bracket groups found in ``b_text``.  The global ``axis``
    counter is also incremented for each tensor axis encountered.

    Parameters
    ----------
    job : str
        Symmetrization mode for this block: ``'nosymm'``, ``'symm'``,
        or ``'asymm'``.
    b_text : str
        Block text string to be parsed, e.g., ``'1[22]1'``.
    depth : int
        Current recursion depth, used for indented debug printing
        and as a guard against runaway recursion.

    Returns
    -------
    result : tuple
        Parsed instruction block in the form of a tuple
        ``(job, obj_list)``, or the unwrapped inner tuple when the
        block reduces to a single sub-tuple under ``'nosymm'``.

    Raises
    ------
    ParsingError
        If ``b_text`` contains elements of inconsistent type under a
        symmetrizing job, an empty list is found, fewer than two
        sub-blocks appear where multiple are required, or an
        unexpected object type is encountered.
    """

    global axis

    b_list = parse_string(b_text)
    jprint(depth * "  " + f"String '{b_text}' parsed to block list: {b_list}")

    obj_list = []

    if job == "nosymm":
        # no symmetrization to be performed; can be mix of types
        for x in b_list:
            if type(x) is int:
                obj_list.extend([axis + j for j in range(x)])
                axis += x  # update global variable
            elif type(x) is str:
                sub_job = s_dict[x[0]]
                obj_list.append(list_to_tuple(sub_job, x[1:-1], depth + 1))
                # parse returns a tuple (and also updates axis)
            else:
                raise ParsingError("Wrong type in list")
    else:
        # now we symmetrize or antisymmetrize
        # all objects in b_list must be identical ints or identical strings
        if len(set(b_list)) > 1:
            raise ParsingError(f"Symmetrized elements differ in {b_list}")
        elif len(set(b_list)) == 0:
            raise ParsingError(f"Empty list {b_list}")
        x = b_list[0]
        n = len(b_list)
        if type(x) is int:
            if n == 1:  # n = 1 implies symmetrization within one block
                obj_list.extend([axis + j for j in range(x)])
                axis += x  # update global variable
            else:  # n > 1 implies block symmetrization
                for _ in range(n):
                    obj_list.append(list_to_tuple("nosymm", str(x), depth + 1))
        elif type(x) is str:  # block symmetrization of symmetrized subblocks
            if n < 2:
                raise ParsingError(f"Expecting 2 or more sublocks; found {n}")
            sub_job = s_dict[x[0]]
            for _ in range(n):
                obj_list.append(list_to_tuple(sub_job, x[1:-1], depth + 1))
        else:
            raise ParsingError(f"Wrong type of object in b_list {b_list}")

    jprint(depth * "  " + f"Block List parsed to object list:  {obj_list}")
    if depth > 8:
        raise ParsingError(f"Recursion depth exceeded for block '{b_text}'")

    if job == "nosymm" and len(obj_list) == 1 and type(obj_list[0]) is tuple:
        return obj_list[0]  # In this trivial case, return sub-tuple
    else:
        return (job, obj_list)  # Return constructed tuple


# ------------------------------------------
# Define helper functions for parsing
# ------------------------------------------


def parse_string(b_string):
    """
    Tokenise a block text string into a mixed list of ints and strings.

    Parameters
    ----------
    b_string : str
        String in Jahn block-text format, e.g., ``'1[{2}{2}]2'``.

    Returns
    -------
    b_list : list
        Mixed list of integers (single-digit axis counts) and strings
        (bracketed sub-blocks), e.g., ``[1, '[{2}{2}]', 2]``.

    Raises
    ------
    ParsingError
        If an unexpected character is encountered in ``b_string``.
    """
    i = 0
    b_list = []
    while i < len(b_string):
        c = b_string[i]
        if c in digits:  # add integer to b_list
            b_list.append(int(c))
            i += 1
        elif c in ["[", "{"]:
            i_end = i + find_match(b_string[i:])  # position of matching bracket
            # add sub_string to b_list
            b_list.append(b_string[i:i_end])
            i = i_end
        else:
            raise ParsingError(f"Function parse_string failed on {b_string}")

    return b_list


def find_match(text):
    """
    Find the closing bracket that matches the opening bracket at index 0.

    Parameters
    ----------
    text : str
        String whose first character is either ``'['`` or ``'{'``.

    Returns
    -------
    ic : int
        Index of the character immediately after the matching closing
        bracket (i.e., the length of the balanced sub-string).

    Raises
    ------
    ParsingError
        If the string ends before a matching closing bracket is found.
    """
    c_dict = {"[": "]", "{": "}"}  # matching closing brackets
    cl = text[0]
    cr = c_dict[cl]
    depth = 1
    ic = 1
    while depth > 0:
        if ic >= len(text):
            raise ParsingError(f"Closure failed on string '{text}'")
        if text[ic] == cl:
            depth += 1
        if text[ic] == cr:
            depth -= 1
        ic += 1
    return ic
