"""
Define crystallographic proper rotations and build their
multiplication tables.

Provides tools to construct lists of proper rotations belonging
to cubic and hexagonal crystallographic groups, and to construct
their multiplication tables.  Functions :func:`get_hex_table`
and :func:`get_cub_table` are intended to be accessed from outside
this module.

Notes
-----
In the context of this module, all point group operations are proper
rotations (determinant +1).
"""

import numpy as np


def get_hex_table(if_print=False):
    """
    Build a dictionary of proper rotations for hexagonal group 622
    and compute its multiplication table.

    Parameters
    ----------
    if_print : bool, optional
        If ``True``, print the rotation list and multiplication table
        to stdout.  Default is ``False``.

    Returns
    -------
    rot_dict : dict
        Dictionary mapping rotation names (str) to rotation matrices
        (numpy 3x3 float array).
    table_dict : dict
        Dictionary embodying the multiplication table; keys are tuples
        of two rotation names and values are the resulting rotation name.
    """

    rot_dict = get_hex_rot_dict()
    table_dict = get_mult_table(rot_dict)

    if if_print:
        print_dict("hex_info", rot_dict, table_dict)

    return rot_dict, table_dict


def get_cub_table(if_print=False):
    """
    Build a dictionary of proper rotations for cubic group 432
    and compute its multiplication table.

    Parameters
    ----------
    if_print : bool, optional
        If ``True``, print the rotation list and multiplication table
        to stdout.  Default is ``False``.

    Returns
    -------
    rot_dict : dict
        Dictionary mapping rotation names (str) to rotation matrices
        (numpy 3x3 float array).
    table_dict : dict
        Dictionary embodying the multiplication table; keys are tuples
        of two rotation names and values are the resulting rotation name.
    """

    rot_dict = get_cub_rot_dict()
    table_dict = get_mult_table(rot_dict)

    if if_print:
        print_dict("cub_info", rot_dict, table_dict)

    return rot_dict, table_dict


# ----------------------------------------------------------------
# The remaining functions are tools internal to this module
# ----------------------------------------------------------------


def get_hex_rot_dict():
    """
    Construct the rotation dictionary for hexagonal group 622.

    Returns
    -------
    rot_dict : dict
        Dictionary mapping rotation names (str of 1 or 2 characters)
        to rotation matrices (numpy 3x3 float array).
    """

    rot_dict = {}

    rot_dict["1"] = rot_mat([0, 0, 1], 0, 1)
    rot_dict["2z"] = rot_mat([0, 0, 1], 1, 2)
    rot_dict["3z"] = rot_mat([0, 0, 1], 1, 3)
    rot_dict["3Z"] = rot_mat([0, 0, 1], 2, 3)
    rot_dict["6z"] = rot_mat([0, 0, 1], 1, 6)
    rot_dict["6Z"] = rot_mat([0, 0, 1], 5, 6)

    half = 1 / 2
    r32 = np.sqrt(3) / 2

    rot_dict["2r"] = rot_mat([1, 0, 0], 1, 2)
    rot_dict["2s"] = rot_mat([r32, half, 0], 1, 2)
    rot_dict["2t"] = rot_mat([half, r32, 0], 1, 2)
    rot_dict["2u"] = rot_mat([0, 1, 0], 1, 2)
    rot_dict["2v"] = rot_mat([-half, r32, 0], 1, 2)
    rot_dict["2w"] = rot_mat([-r32, half, 0], 1, 2)

    # Dictionary contains 12 hexagonal point operations
    return rot_dict


def get_cub_rot_dict():
    """
    Construct the rotation dictionary for cubic group 432.

    Returns
    -------
    rot_dict : dict
        Dictionary mapping rotation names (str of 1 or 2 characters)
        to rotation matrices (numpy 3x3 float array).
    """

    rot_dict = {}

    rot_dict["1"] = rot_mat([0, 0, 1], 0, 1)

    rot_dict["2x"] = rot_mat([1, 0, 0], 1, 2)
    rot_dict["2y"] = rot_mat([0, 1, 0], 1, 2)
    rot_dict["2z"] = rot_mat([0, 0, 1], 1, 2)

    rot_dict["4x"] = rot_mat([1, 0, 0], 1, 4)
    rot_dict["4X"] = rot_mat([1, 0, 0], 3, 4)
    rot_dict["4y"] = rot_mat([0, 1, 0], 1, 4)
    rot_dict["4Y"] = rot_mat([0, 1, 0], 3, 4)
    rot_dict["4z"] = rot_mat([0, 0, 1], 1, 4)
    rot_dict["4Z"] = rot_mat([0, 0, 1], 3, 4)

    rot_dict["2a"] = rot_mat([0, 1, 1], 1, 2)
    rot_dict["2b"] = rot_mat([0, 1, -1], 1, 2)
    rot_dict["2c"] = rot_mat([1, 0, 1], 1, 2)
    rot_dict["2d"] = rot_mat([-1, 0, 1], 1, 2)
    rot_dict["2e"] = rot_mat([1, 1, 0], 1, 2)
    rot_dict["2f"] = rot_mat([1, -1, 0], 1, 2)

    rot_dict["3a"] = rot_mat([1, 1, 1], 1, 3)
    rot_dict["3A"] = rot_mat([1, 1, 1], 2, 3)
    rot_dict["3b"] = rot_mat([1, -1, -1], 1, 3)
    rot_dict["3B"] = rot_mat([1, -1, -1], 2, 3)
    rot_dict["3c"] = rot_mat([-1, 1, -1], 1, 3)
    rot_dict["3C"] = rot_mat([-1, 1, -1], 2, 3)
    rot_dict["3d"] = rot_mat([-1, -1, 1], 1, 3)
    rot_dict["3D"] = rot_mat([-1, -1, 1], 2, 3)

    # Dictionary contains 24 cubic point operations
    return rot_dict


def rot_mat(axis, m, n):
    """
    Construct a rotation matrix using the Rodrigues formula.

    Parameters
    ----------
    axis : array-like of length 3
        Rotation axis vector; need not be normalized.
    m : int
        Numerator of the rotation angle fraction.
    n : int
        Denominator of the rotation angle fraction; the rotation
        angle is ``2 * pi * m / n``.

    Returns
    -------
    rot : numpy.ndarray, shape (3, 3)
        Rotation matrix corresponding to the specified axis and angle.
    """

    r_axis = np.array(axis)
    r_axis = r_axis / np.linalg.norm(r_axis)  # In case not normalized
    angle = m * 2 * np.pi / n

    iden = np.identity(3)
    skew = np.cross(iden, r_axis)
    # Rodriguez formula for rotation matrix
    rot = iden + np.sin(angle) * skew + (1 - np.cos(angle)) * skew @ skew

    return rot


def get_mult_table(rot_dict):
    """
    Compute the multiplication table for a set of rotation matrices.

    Parameters
    ----------
    rot_dict : dict
        Dictionary mapping rotation names (str) to 3x3 rotation
        matrices (numpy float arrays).

    Returns
    -------
    table_dict : dict
        Dictionary embodying the multiplication table.  Keys are
        2-tuples of rotation names ``(rot1, rot2)`` and values are
        the name of the rotation equal to the matrix product
        ``mat1 @ mat2``.

    Raises
    ------
    ValueError
        If the product of any two rotations has no match in
        ``rot_dict`` (group not closed) or more than one match
        (internal inconsistency).
    """

    table_dict = {}

    for rot1, mat1 in rot_dict.items():
        for rot2, mat2 in rot_dict.items():
            rmat = mat1 @ mat2  # numpy matrix product
            match_list = []
            for rot3, mat3 in rot_dict.items():
                if np.linalg.norm(rmat - mat3) < 0.0001:
                    match_list.append(rot3)

            matches = len(match_list)
            # check for closure and uniqueness
            if matches == 1:
                table_dict[(rot1, rot2)] = match_list[0]
            elif matches == 0:
                raise ValueError(
                    f"No match found for {rot1}, {rot2};" + " group is not closed"
                )
            else:
                raise ValueError(
                    f"{matches} matches found for {rot1}, {rot2};"
                    + " something is wrong"
                )

    return table_dict


def print_dict(name, rot_dict, table_dict):
    """
    Print the rotation dictionary and multiplication table.

    Parameters
    ----------
    name : str
        Label printed as a header above the output.
    rot_dict : dict
        Dictionary mapping rotation names (str) to rotation matrices
        (numpy 3x3 float array).
    table_dict : dict
        Multiplication table dictionary as returned by
        :func:`get_mult_table`.
    """

    n = len(rot_dict)
    print("\n" + name)
    print(f"\nOrder of group = {n}\n")
    for key, mat in rot_dict.items():
        print(key, np.round(mat, 3).tolist())
    print("\nMultiplication table\n")
    for rot1 in rot_dict:
        line = ""
        for rot2 in rot_dict:
            line += f"{table_dict[(rot1, rot2)]:3}"
        print(line)
