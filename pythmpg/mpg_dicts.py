"""
Construct dictionaries describing the operations and structure
of magnetic point groups.

Upon being imported, this module constructs six dictionaries and makes
them available to external modules as module-level attributes.  The
first four are built from functions imported from ``pg_elements``; the
remaining two are built by :func:`get_mpg_dict` and
:func:`get_bns_dict`, which are called at module level at the end of
this file.  Following normal Python import rules, these module-level
statements execute once per session on first import.

Attributes
----------
hex_rot_dict : dict
    Maps rotation name (str, 1-2 characters) to rotation matrix
    (numpy 3×3 float array) for the hexagonal setting.
cub_rot_dict : dict
    Maps rotation name (str, 1-2 characters) to rotation matrix
    (numpy 3×3 float array) for the cubic setting.
hex_table_dict : dict
    Multiplication table for hexagonal operations.  Keys are 2-tuples
    of rotation names; values are the resulting rotation name (str).
cub_table_dict : dict
    Multiplication table for cubic rotations.  Keys are 2-tuples of
    rotation names; values are the resulting rotation name (str).
mpg_dict : dict
    Maps each MPG name (str) to a 3-tuple
    ``(frame, generators, gen_orders)`` where ``frame`` is ``'hex'``
    or ``'cub'``, ``generators`` is a list of polycyclic generator
    3-tuples, and ``gen_orders`` is a list of their corresponding
    orders (int).
bns_dict : dict
    Maps each MPG name (str) to its BNS (Belov-Neronova-Smirnova)
    serial number (str).
"""

from copy import copy
import math

# Import two functions from module 'pg_elements'
from pythmpg.pg_elements import get_hex_table, get_cub_table

# -----------------------
# Define helper functions
# -----------------------


def get_mpg_dict():
    """
    Construct the dictionary of all 122 magnetic point groups (MPGs).

    Each MPG is represented as a polycyclic group: its elements can be
    written uniquely as ``g_1^k_1 ... g_M^k_M``, where ``g_m`` is the
    m-th polycyclic generator of order ``N_m`` and ``k_m`` ranges from
    0 to ``N_m - 1``.  The order of the MPG is therefore the product of
    the generator orders.  Polycyclic generators are used in preference
    to the generators listed in the International Tables or the Bilbao
    Crystallographic server (which are not generally polycyclic) because
    they make subsequent operations more straightforward and efficient.

    All individual MPG operations are 3-tuples
    ``(rot, p_space, p_time)`` where ``rot`` is the proper rotation
    name (str, 1-2 characters), and ``p_space`` and ``p_time`` are 0
    or 1 indicating composition with spatial inversion or time reversal
    respectively.

    Returns
    -------
    mpg_dict : dict
        Maps each MPG name (str) to a 3-tuple
        ``(frame, generators, gen_orders)``:

        frame : str
            ``'hex'`` for hexagonal setting, ``'cub'`` for cubic.
        generators : list of tuple
            Polycyclic generators, each a 3-tuple
            ``(rot, p_space, p_time)``.
        gen_orders : list of int
            Order of each polycyclic generator.

    Notes
    -----
    The 'generators' listed in the International Tables and in the
    Bilbao Crystallographic server are not generally polycyclic.
    The construction of polycyclic generators in this module makes
    the coding of some later operations more straightforward and
    efficient.

    """

    # List of magnetic point groups
    mpg_list = [
        "1",
        "1'",
        "-1",
        "-11'",
        "-1'",
        "2",
        "21'",
        "2'",
        "m",
        "m1'",
        "m'",
        "2/m",
        "2/m1'",
        "2'/m",
        "2/m'",
        "2'/m'",
        "222",
        "2221'",
        "2'2'2",
        "mm2",
        "mm21'",
        "m'm2'",
        "m'm'2",
        "mmm",
        "mmm1'",
        "m'mm",
        "m'm'm",
        "m'm'm'",
        "4",
        "41'",
        "4'",
        "-4",
        "-41'",
        "-4'",
        "4/m",
        "4/m1'",
        "4'/m",
        "4/m'",
        "4'/m'",
        "422",
        "4221'",
        "4'22'",
        "42'2'",
        "4mm",
        "4mm1'",
        "4'm'm",
        "4m'm'",
        "-42m",
        "-42m1'",
        "-4'2'm",
        "-4'2m'",
        "-42'm'",
        "4/mmm",
        "4/mmm1'",
        "4/m'mm",
        "4'/mm'm",
        "4'/m'm'm",
        "4/mm'm'",
        "4/m'm'm'",
        "3",
        "31'",
        "-3",
        "-31'",
        "-3'",
        "32",
        "321'",
        "32'",
        "3m",
        "3m1'",
        "3m'",
        "-3m",
        "-3m1'",
        "-3'm",
        "-3'm'",
        "-3m'",
        "6",
        "61'",
        "6'",
        "-6",
        "-61'",
        "-6'",
        "6/m",
        "6/m1'",
        "6'/m",
        "6/m'",
        "6'/m'",
        "622",
        "6221'",
        "6'22'",
        "62'2'",
        "6mm",
        "6mm1'",
        "6'mm'",
        "6m'm'",
        "-6m2",
        "-6m21'",
        "-6'm'2",
        "-6'm2'",
        "-6m'2'",
        "6/mmm",
        "6/mmm1'",
        "6/m'mm",
        "6'/mmm'",
        "6'/m'mm'",
        "6/mm'm'",
        "6/m'm'm'",
        "23",
        "231'",
        "m-3",
        "m-31'",
        "m'-3'",
        "432",
        "4321'",
        "4'32'",
        "-43m",
        "-43m1'",
        "-4'3m'",
        "m-3m",
        "m-3m1'",
        "m'-3'm",
        "m-3m'",
        "m'-3'm'",
    ]

    # Process each of the 122 magnetic point groups
    mpg_dict = {}
    for mpg in mpg_list:
        frame, generators, gen_orders = parse_mpg(mpg)
        mpg_dict[mpg] = (frame, generators, gen_orders)

    return mpg_dict


def get_bns_dict():
    """
    Build the dictionary mapping MPG names to BNS serial numbers.

    BNS refers to the Belov-Neronova-Smirnova notation for magnetic
    point groups.  Serial numbers have the form ``'c.p.m'`` where
    ``c`` is the index of the classical (non-magnetic) parent group,
    ``p`` is the index of the MPG within that parent, and ``m`` is the
    overall 1-based index across all 122 MPGs.

    Returns
    -------
    bns_dict : dict
        Maps each MPG name (str) to its BNS serial number (str).
    """
    bns_dict = {}
    c = 0
    cname_old = ""
    for m, mpg in enumerate(mpg_dict):
        cname = mpg.replace("1'", "").replace("'", "")
        if cname == "" or cname == "-":
            cname += "1"
        if cname != cname_old:
            c += 1
            p = 1
            cname_old = cname
        else:
            p += 1
        bns_dict[mpg] = f"{c}.{p}.{m + 1}"
    return bns_dict


# -----------------------
# Helper functions (internal to module)
# -----------------------


def product(op1, op2):
    """
    Compute the product of two MPG operations.

    Each MPG operation is a 3-tuple ``(rot, p_space, p_time)`` where
    ``rot`` is a proper rotation name (str, 1-2 characters) and
    ``p_space``, ``p_time`` are 0 or 1.  The proper-rotation part
    of the product is looked up in the module-level ``table_dict``.
    Spatial and time parities combine by addition modulo 2.

    Parameters
    ----------
    op1 : tuple
        First MPG operation, as a 3-tuple ``(rot, p_space, p_time)``.
    op2 : tuple
        Second MPG operation, as a 3-tuple ``(rot, p_space, p_time)``.

    Returns
    -------
    product : tuple
        Resulting MPG operation, as a 3-tuple ``(rot, p_space, p_time)``.
    """

    # Makes use of 'table_dict' defined in calling routine
    rot_name = table_dict[(op1[0], op2[0])]
    p_space = (op1[1] + op2[1]) % 2
    p_time = (op1[2] + op2[2]) % 2
    return (rot_name, p_space, p_time)


def get_closure(in_list):
    """
    Compute the closure of a set of MPG operations under multiplication.

    Starting from the supplied operations, repeatedly forms all pairwise
    products and adds any new results until the set is closed.

    Parameters
    ----------
    in_list : list of tuple
        Initial MPG operations, each a 3-tuple ``(rot, p_space, p_time)``.

    Returns
    -------
    op_list : list of tuple
        Smallest closed set of MPG operations containing all elements
        of ``in_list``.
    """
    op_list = copy(in_list)
    ind = 0
    while ind < len(op_list):
        i = op_list[ind]
        for j in op_list[: ind + 1]:
            k = product(i, j)
            if k not in op_list:
                op_list.append(k)
            k = product(j, i)
            if k not in op_list:
                op_list.append(k)
        ind += 1
    return op_list


def get_cycle(op):
    """
    Compute all elements of the cyclic group generated by one MPG operation.

    Repeatedly multiplies ``op`` by itself (starting from the identity)
    until the identity is recovered.  No MPG operation has order greater
    than 6, so the loop is bounded accordingly.

    Parameters
    ----------
    op : tuple
        A single MPG operation as a 3-tuple ``(rot, p_space, p_time)``.

    Returns
    -------
    cycle : list of tuple
        All elements of the cyclic group generated by ``op``, beginning
        with the identity ``('1', 0, 0)``.
    """
    cycle = [("1", 0, 0)]  # list containing only identity op
    for i in range(6):  # no MPG operation has order greater than 6
        prod = product(cycle[-1], op)
        if prod == ("1", 0, 0):
            return cycle
        cycle.append(prod)
    raise RuntimeError(f"Failed to find cycle for operation {op}")


# -----------------------------------
# Function that does most of the work
# -----------------------------------
def parse_mpg(mpg, if_print=False):
    """
    Parse an MPG name and derive its polycyclic generators and their orders.

    Reads the Hermann-Mauguin symbol, assigns rotation-axis suffixes,
    selects the hexagonal or cubic reference frame, inserts any extra
    generators required for cubic groups 23 and 432, removes redundant
    generators, and verifies that the resulting polycyclic generator set
    produces a group of the correct order with no duplicate elements.

    Parameters
    ----------
    mpg : str
        Magnetic point group name in Hermann-Mauguin notation,
        e.g. ``'4/mmm'``, ``"m'-3'm"``.
    if_print : bool, optional
        If ``True``, print intermediate results to stdout for debugging.
        Default is ``False``.

    Returns
    -------
    frame : str
        Reference frame: ``'hex'`` for hexagonal, ``'cub'`` for cubic.
    generators : list of tuple
        Polycyclic generators of the MPG, each a 3-tuple
        ``(rot, p_space, p_time)``.
    generator_orders : list of int
        Order of each polycyclic generator.
    """

    global rot_dict, table_dict  # module-level objects get modified here

    # -----------------------------------
    # Read and process list of generators
    # -----------------------------------

    gen_hm = []  # this will become a list of Hermann-Maugin generators
    targ = mpg.removeprefix("1.").removesuffix(".1")
    targ = targ.replace(".", "").replace("/m", "M")
    if targ == "1":
        targ = ""
    n = len(targ)
    p = 0  # pointer to index in string targ
    while p < n:
        op = ["1", 0, 0]  # proper rotation, space parity, time parity
        if targ[p] == "-":
            op[1] = 1
            p += 1
        c = targ[p]
        if c == "m":  # mirror m = 2 * inv
            c = "2"
            op[1] = 1
        if c == "M":  # special code for /m
            c = "T"  # special code for 2-fold rot from /m
            op[1] = 1
        op[0] = c
        p += 1
        if p < n and targ[p] == "'":
            op[2] = 1
            p += 1
        gen_hm.append(op)

    # list of proper rotations in list of generators
    prop = [hm[0] for hm in gen_hm]

    # Assign order of axes in list of generators
    ng = len(gen_hm)
    index_list = list(range(ng))  # [0,1,2,...]
    # the hm framework attaches meaning to an operation based on
    # its position in the list, but something like '4/m' is all
    # part of the first position, so the '4' and '/m' are both
    # assigned to the first position

    # treat special case of '/m'
    if ng > 1 and prop[1] == "T":
        prop[1] = "2"
        gen_hm[1][0] = "2"
        index_list = [0] + list(range(ng - 1))  # [0,0,1,...]
        # assigns same axis label to first two operations
    # if debug: print('  Index list =',index_list)

    # Add suffixes according to axes
    # Also decide whether to work in cubic or hexagonal frame
    if len(prop) > 0 and prop[0] in ["3", "6"]:
        # hexagonal framework
        frame = "hex"
        rot_dict = hex_rot_dict  # modifying global variable
        table_dict = hex_table_dict  # modifying global variable
        axis_label = ["z", "r", "u"]  # hex: unique 3-fold or 6-fold axis_label
    else:
        # cubic framework
        frame = "cub"
        rot_dict = cub_rot_dict  # modifying global variable
        table_dict = cub_table_dict  # modifying global variable
        if len(prop) > 1 and prop[1] == "3":
            axis_label = ["x", "a", "a"]  # cubic: axes are 100, 111, 110
        elif len(prop) > 0 and prop[0] == "4":
            axis_label = ["z", "x", "e"]  # higher-order axis_label is present
        else:
            axis_label = ["x", "y", "z"]  # no higher-order axis_label is present

    # Appending suffixes
    for j, hm in enumerate(gen_hm):
        k = index_list[j]
        if prop[j] != "1":
            hm[0] = hm[0] + axis_label[k]
    temp = [tuple(hm) for hm in gen_hm]
    if if_print:
        print(f"\n{mpg:9}{temp}")

    # Special treatment for cubic groups 23 and 43
    # We need to add an extra 2-fold generator for these groups
    if ng > 1 and prop[1] == "3":
        if gen_hm[0][0] == "2x":
            # this is a variant of group 23
            new_hm = ["2y"] + gen_hm[0][1:]  # picks up same parities as for '2x'
            gen_hm = gen_hm[:1] + [new_hm] + gen_hm[1:]
            if if_print:
                print("         Added generator")
        elif gen_hm[0][0] == "4x":
            new_hm = ["2y", 0, 0]  # even parity (2y ~ 2z = (-4')^2)
            # this is a variant of group 43
            gen_hm = gen_hm[:1] + [new_hm] + gen_hm[1:]
            if if_print:
                print("         Added generator")

    # Convert to tuples
    gen_list = [tuple(hm) for hm in gen_hm]
    if temp != gen_list and if_print:
        print(f"{'':9}{gen_list}")

    # -----------------------------
    # Check for unneeded generators
    # -----------------------------

    closed = [1]
    for depth in range(len(gen_list)):
        closed.append(len(get_closure(gen_list[: depth + 1])))
    order = closed[-1]

    generators = []
    for j in range(len(gen_list)):
        if closed[j + 1] == closed[j]:
            if if_print:
                print(8 * " ", "Redundant operation", j, "removed; orders =", closed)
        else:
            generators.append(gen_list[j])
    if len(generators) < len(gen_list) and if_print:
        print(f"{'':9}{generators}")

    # ---------------------------------------------
    # Check for duplicate operations and group size
    # ---------------------------------------------

    generated_ops = [("1", 0, 0)]
    generator_orders = []
    for depth in range(len(generators)):
        generated_ops_sav = copy(generated_ops)
        new_ops = get_cycle(generators[depth])
        generator_orders.append(len(new_ops))
        for op_n in new_ops[1:]:
            for op_o in generated_ops_sav:
                op_prod = product(op_o, op_n)
                if op_prod in generated_ops:
                    raise RuntimeError(
                        f"Duplicate operator found at depth {depth}: {op_prod}"
                    )
                generated_ops.append(op_prod)
    # check consistency of order of group
    num_ops = len(generated_ops)
    num_ops_t = math.prod(generator_orders)
    if num_ops != order or num_ops != num_ops_t:
        raise RuntimeError(f"Group size mismatch: {num_ops} != {order} or {num_ops_t}")
    if if_print:
        print(8 * " ", f"Success for group of order {order}")
        print(f"{'':9}{generator_orders}")

    return frame, generators, generator_orders


# --------------------------------------------------------------
# Now execute commands needed to construct the five dictionaries
# --------------------------------------------------------------

# Obtain four dictionaries using functions from module 'pg_elements'
hex_rot_dict, hex_table_dict = get_hex_table(if_print=False)
cub_rot_dict, cub_table_dict = get_cub_table(if_print=False)

# Construct the primary dictionary 'mpg_dict'
mpg_dict = get_mpg_dict()

# Also construct bns_dict
bns_dict = get_bns_dict()

print("Dictionaries have been constructed in module mpg_dicts\n")
