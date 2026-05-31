"""
Provide externally callable functions for querying magnetic point
group properties corresponding to given Jahn symbols.

The two public functions are:

``get_mpg_info``
    Return symmetry and classification information for each MPG.
``get_num_indep``
    Return the number of independent tensor components for each
    combination of Jahn symbol and MPG.

Both functions are currently called from ``spreadsheet.py`` but are
designed to be used flexibly for other purposes.  This module also
contains a number of internally called helper functions, with
dependencies on modules ``mpg_dicts`` and ``pg_elements``.
"""

from itertools import permutations
import numpy as np
from copy import copy, deepcopy

from pythmpg.mpg_dicts import hex_rot_dict, cub_rot_dict
from pythmpg.mpg_dicts import hex_table_dict, cub_table_dict
from pythmpg.mpg_dicts import mpg_dict, bns_dict
from pythmpg.parse_jahn import parse_jahn_symbol, jahn_rank

rot_dict = {}
table_dict = {}
# These dictionaries are globally available in this module

# --------------------------------------------------------------
# Functions intended to be imported and used from outside module
# --------------------------------------------------------------


def get_mpg_info(mpg_list="All"):
    """
    Return and basic information for a list of MPGs.

    For each MPG, determines the group order and classification as
    'Grey', 'Black-White', or 'Colorless', and reports the presence
    or absence of six key symmetries (P, T, PT, PR, TR, PTR).

    Parameters
    ----------
    mpg_list : list of str or 'All', optional
        MPG names to process.  Pass ``'All'`` (default) to process
        all 122 MPGs in ``mpg_dict``.

    Returns
    -------
    mpg_info_dict : dict
        Dictionary with the following keys, each mapping to a list
        whose entries correspond to the MPGs in ``mpg_list``:

        ``'bns'`` : list of str
            BNS serial number of each MPG.
        ``'order'`` : list of int
            Number of elements (order) of each MPG.
        ``'group_type'`` : list of str
            Classification as ``'Grey'``, ``'Black-White'``,
            or ``'Colorless'``.
        ``'symm_info'`` : list of list of bool
            For each MPG, a 6-element list of booleans indicating
            presence of P, T, PT, PR, TR, and PTR symmetries.
    """

    # Declare global variables
    global rot_dict, table_dict

    # By default, works on all 122 MPGs
    if mpg_list == "All":
        mpg_list = list(mpg_dict)

    # initialize lists
    order_list = []
    group_type_list = []
    symm_info_list = []

    # Loop over MPG's
    for mpg in mpg_list:
        # Set global dictionaries according to cubic or hexagonal frame
        frame, generators, gen_orders = mpg_dict[mpg]
        rot_dict = hex_rot_dict if frame == "hex" else cub_rot_dict
        table_dict = hex_table_dict if frame == "hex" else cub_table_dict

        # create list of all symmetry operators in mpg
        full_list = [("1", 0, 0)]
        for k in range(len(generators)):
            new_list = []
            gen = generators[k]
            order = gen_orders[k]
            s = ("1", 0, 0)
            for j in range(order):
                for op in full_list:
                    new_list.append(product(op, s))
                s = product(s, gen)
            full_list = new_list

        # Get the order (number of elements) of the  MPG
        order = len(full_list)
        order_list.append(order)

        # Check for presence of six symmetries P, T, PT, PR, TR, PTR.
        # Define six Boolean variable for presence of symmetries
        #
        P_symm = ("1", 1, 0) in full_list
        T_symm = ("1", 0, 1) in full_list
        PT_symm = ("1", 1, 1) in full_list
        #
        P_T_parts = [(s[1], s[2]) for s in full_list]
        PR_symm = (1, 0) in P_T_parts
        TR_symm = (0, 1) in P_T_parts
        PTR_symm = (1, 1) in P_T_parts
        #
        symm_info = [P_symm, T_symm, PT_symm, PR_symm, TR_symm, PTR_symm]
        symm_info_list.append(symm_info)

        # Define group_type (Grey, Black-White, or Colorless)
        group_type = ""
        if T_symm:
            group_type = "Grey"
        else:
            if TR_symm or PTR_symm:
                group_type = "Black-White"
            else:
                group_type = "Colorless"
        group_type_list.append(group_type)

    # Make bns_list
    bns_list = [bns_dict[x] for x in mpg_list]

    # Pack lists into dictionary
    mpg_info_dict = {}
    mpg_info_dict["bns"] = bns_list
    mpg_info_dict["order"] = order_list
    mpg_info_dict["group_type"] = group_type_list
    mpg_info_dict["symm_info"] = symm_info_list

    return mpg_info_dict


def get_num_indep(jahn_list, mpg_list="All"):
    """
    Return the number of independent tensor components for Jahn symbol / MPG pairs.

    For each Jahn symbol, parses the symbol to obtain index-symmetrization
    instructions, constructs a basis of symmetrized orthonormal tensors,
    and then further reduces that basis under each MPG's symmetry
    operations to count the remaining independent components.

    Parameters
    ----------
    jahn_list : list of str
        Jahn symbols to process (may include leading ``'a'`` or ``'e'``
        parity characters).
    mpg_list : list of str or 'All', optional
        MPG names to process.  Pass ``'All'`` (default) to process
        all 122 MPGs in ``mpg_dict``.

    Returns
    -------
    num_indep_dict : dict
        Maps each Jahn symbol (str) to a list of integers (one per MPG
        in ``mpg_list``) giving the number of independent tensor
        components for that symbol and MPG combination.
    """

    # Declare global variables
    global rot_dict, table_dict

    # By default, works on all 122 MPGs
    if mpg_list == "All":
        mpg_list = list(mpg_dict)

    # Initialize dictionary to be returned
    num_indep_dict = {}

    # Loop over Jahn symbols
    for jahn in jahn_list:
        # Remove leading space and time parity flags
        time_parity = jahn.count("a") % 2
        space_parity = jahn.count("e") % 2
        jahn_bare = jahn.replace("a", "").replace("e", "")

        # Parse rest of Jahn symbol to get instruction set
        instructions = parse_jahn_symbol(jahn_bare, if_print=False)

        # In case an exception was raised:
        if instructions is None:
            raise RuntimeError(
                f"Invalid Jahn symbol '{jahn}'. Correct the syntax and try again."
            )

        rank = jahn_rank(instructions)
        space_parity = (space_parity + rank) % 2

        # Create list of basis tensors
        orth_list_basis = init_orth_list(rank)

        # Loop over basis tensors and create orthonormalized
        # list of symmetrized tensors
        orth_list = []
        for tensor in orth_list_basis:
            # Symmetrize under index exchanges
            #   Follow instructions to arbitrary depth of the Jahn
            #   symbol using recursive function process_block()
            tensor = process_block(instructions, tensor)[1]

            # Orthogonalize to tensors already in the list
            for otensor in orth_list:
                tensor = tensor - otensor * t_prod(otensor, tensor)
            if not is_zero(tensor):
                tensor = tensor / norm(tensor)  # normalize tensor
                orth_list.append(tensor)  # add it to the list

        # Now 'orth_list' is the list of independent orthonormal
        # tensors after symmetrizing under interchange of indices
        # as specified by the Jahn symbol

        # Initialize list that will contain the number of independent
        # tensors for each MPG
        num_indep_list = []

        # Loop over MPGs
        for mpg in mpg_list:
            # Set global dictionaries according to cubic or hexagonal frame
            frame, generators, gen_orders = mpg_dict[mpg]
            rot_dict = hex_rot_dict if frame == "hex" else cub_rot_dict
            table_dict = hex_table_dict if frame == "hex" else cub_table_dict

            # generators: list (of tuples) giving generators
            # gen_orders: list (of integers) giving order of that generator

            # Get working copy of orthonormalized tensor list
            reduced_list = deepcopy(orth_list)

            # Reduce the tensor list further using MPG symmetry
            for j, generator in enumerate(generators):
                # Unpack details of 3x3 symmetry generator R
                rot, op_space, op_time = generator
                R = rot_dict[rot]  # 3x3 numpy array
                order = gen_orders[j]  # order of the generator
                parity = op_space * space_parity + op_time * time_parity

                # Symmetrize each tensor with respect to this generator,
                # and retain only linearly independent ones
                reduced_list = reduce_orth_list(reduced_list, R, order, parity)

                # If no independent tensors, break out of the loop
                if not reduced_list:
                    break

            # Record final number of independent tensors
            num_indep_list.append(len(reduced_list))

        # Save to list
        num_indep_dict[jahn] = num_indep_list

        print(f"  Finished Jahn {jahn}")

    # Return dictionary
    return num_indep_dict


# --------------------------------------------------------------
# Helper functions intended as local
# --------------------------------------------------------------


def permutation_sign(p):
    """
    Return the sign of a permutation.

    Parameters
    ----------
    p : sequence of int
        A permutation of integers.

    Returns
    -------
    sign : int
        ``+1`` if the permutation is even, ``-1`` if odd.
    """
    inv = sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
    return -1 if inv % 2 else 1


def symmetrize_indices(T, indices, antisym=False):
    """
    Symmetrize or antisymmetrize a tensor over a list of indices.

    Averages over all permutations of the specified axes, optionally
    weighted by the permutation sign for antisymmetrization.

    Parameters
    ----------
    T : numpy.ndarray
        Tensor to be symmetrized.
    indices : list of int
        Axes over which to symmetrize.
    antisym : bool, optional
        If ``True``, antisymmetrize (weight each permutation by its
        sign).  Default is ``False``.

    Returns
    -------
    result : numpy.ndarray
        (Anti)-symmetrized tensor with the same shape as ``T``.
    """
    axes = np.arange(T.ndim)
    result = np.zeros_like(T, dtype=float)
    count = 0

    for p in permutations(indices):
        new_axes = axes.copy()
        new_axes[np.array(indices)] = np.array(p)
        term = np.transpose(T, new_axes)

        if antisym:
            term = permutation_sign(p) * term
        result += term
        count += 1

    return result / count


def symmetrize_index_blocks(T, blocks, antisym=False):
    """
    Symmetrize or antisymmetrize a tensor over permutations of blocks
    of indices.

    Averages over all permutations of the supplied index blocks,
    optionally weighted by the permutation sign for antisymmetrization.
    All blocks must contain the same number of indices.

    Parameters
    ----------
    T : numpy.ndarray
        Tensor to be symmetrized.
    blocks : list of list of int
        Each inner list gives the axes belonging to one block.
        All inner lists must have the same length.
    antisym : bool, optional
        If ``True``, antisymmetrize.  Default is ``False``.

    Returns
    -------
    result : numpy.ndarray
        (Anti)-symmetrized tensor with the same shape as ``T``.
    """
    axes = np.arange(T.ndim)
    result = np.zeros_like(T, dtype=float)
    count = 0

    for block_perm in permutations(blocks):
        # Flatten the permuted blocks
        new_axes = []
        for b in block_perm:
            new_axes.extend(b)
        # Add axes not in any block
        remaining_axes = [i for i in axes if i not in new_axes]
        for i in remaining_axes:
            new_axes.insert(i, i)
        term = np.transpose(T, new_axes)

        if antisym:
            term = permutation_sign(block_perm) * term
        result += term
        count += 1

    return result / count


def process_block(block, tensor):
    """
    Recursively apply Jahn-symbol symmetrization instructions to a tensor.

    Uses the nested instruction block structure produced by
    ``parse_jahn_symbol`` to carry out symmetrization over tensor indices
    to arbitrary depth.

    Parameters
    ----------
    block : tuple
        Parsed instruction block tuple of the form ``(code, obj_list)``
        as returned by :func:`parse_jahn_symbol`.  ``code`` is one of
        ``'nosymm'``, ``'symm'``, or ``'asymm'``; ``obj_list`` is a list
        of integer axis indices or nested sub-block tuples.
    tensor : numpy.ndarray
        Tensor to symmetrize.

    Returns
    -------
    axis_list : list of int
        Axes (consecutive integers) belonging to this block, for which
        symmetrization has been completed.
    tensor : numpy.ndarray
        Partially symmetrized tensor when called during inner recursion;
        fully symmetrized when called initially from :func:`get_num_indep`.
    """
    code, obj_list = block
    #  code     = one of 'nosymm', 'symm', or 'asymm'
    #  obj_list = list of axes or subblocks belonging to calling block

    if code == "nosymm":
        new_obj_list = []
        for el in obj_list:
            if isinstance(el, int):
                # Add this axis to the list to be returned
                new_obj_list.append(el)

            elif isinstance(el, tuple):
                # Recursively call 'process_block' to process this
                # block to arbitrary depth
                axis_list, tensor = process_block(el, tensor)
                new_obj_list.append(axis_list)

        return new_obj_list, tensor

    elif code in ["symm", "asymm"]:
        antisym = code == "asymm"

        # The elemeents in obj_list will either all be:
        #   Integers (axes to be symmetrized)
        #   Sub-blocks of identical size (to be block-symmetrized)

        if all(isinstance(el, int) for el in obj_list):
            tensor = symmetrize_indices(tensor, obj_list, antisym)
            return obj_list, tensor

        elif all(isinstance(el, tuple) for el in obj_list):
            axis_lists = []

            for el in obj_list:
                # First do any lower-level symmetrization on block
                # by recursively calling 'process_block' to process
                # this block to arbitrary depth
                axis_list, tensor = process_block(el, tensor)
                axis_lists.append(axis_list)
            # Each sub-block has now been symmetrized if needed

            # Now symmetrize over blocks
            tensor = symmetrize_index_blocks(tensor, axis_lists, antisym)

            axis_lists = [x for aux in axis_lists for x in aux]

            return axis_lists, tensor

        else:
            raise RuntimeError(
                f"Mixed types in obj_list under symmetrizing job '{code}': {obj_list}"
            )


def product(op1, op2):
    """
    Return the product of two MPG symmetry elements.

    Each element is a 3-tuple ``(rot, p_space, p_time)`` where
    ``rot`` is the proper rotation name (str) and ``p_space``,
    ``p_time`` are 0 or 1.  The rotation part is looked up in the
    module-level ``table_dict``; parities combine modulo 2.

    Parameters
    ----------
    op1 : tuple
        First MPG operation as ``(rot, p_space, p_time)``.
    op2 : tuple
        Second MPG operation as ``(rot, p_space, p_time)``.

    Returns
    -------
    result : tuple
        Product MPG operation as ``(rot, p_space, p_time)``.
    """
    rot = table_dict[(op1[0], op2[0])]
    p_space = (op1[1] + op2[1]) % 2
    p_time = (op1[2] + op2[2]) % 2

    return (rot, p_space, p_time)


def t_prod(t1, t2):
    """
    Return the Frobenius inner product of two numpy tensors.

    Parameters
    ----------
    t1, t2 : numpy.ndarray
        Tensors of identical shape.

    Returns
    -------
    result : float
        Sum of element-wise products of ``t1`` and ``t2``.
    """
    return np.dot(np.ravel(t1), np.ravel(t2))


def norm(t):
    """
    Return the Frobenius norm of a numpy tensor.

    Parameters
    ----------
    t : numpy.ndarray
        Input tensor.

    Returns
    -------
    result : float
        Square root of the Frobenius inner product of ``t`` with itself.
    """
    return np.sqrt(t_prod(t, t))


def is_zero(t):
    """
    Test whether a numpy tensor has (approximately) zero Frobenius norm.

    Parameters
    ----------
    t : numpy.ndarray
        Input tensor.

    Returns
    -------
    result : bool
        ``True`` if the Frobenius norm of ``t`` is less than ``1e-8``.
    """
    return norm(t) < 1.0e-08  # Return boolean: True if (approx) zero


def init_orth_list(rank):
    """
    Generate the primitive orthonormal basis of rank-``rank`` tensors.

    Creates one tensor for each possible index combination, with a
    single element equal to 1 and all others 0.

    Parameters
    ----------
    rank : int
        Rank of the tensors to generate.

    Returns
    -------
    orth_list : list of numpy.ndarray
        List of ``3**rank`` tensors, each of shape ``(3,) * rank``.
    """
    # generates primitive list of orthonormal tensors with unit
    #   element in one location
    orth_list = []
    for m in range(3**rank):
        # convert to digits of m in base 3
        mat = [0] * 3**rank
        mat[m] = 1
        tensor = np.reshape(mat, [3] * rank)
        orth_list.append(tensor)
    return orth_list


def reduce_orth_list(orth_list_orig, R, order, parity):
    """
    Reduce an orthonormal tensor list by applying one MPG generator.

    Symmetrize every tensor in the list under the full cycle of
    operations generated by ``R``, then re-orthonormalize to obtain
    the independent tensors that are invariant under this generator.

    Parameters
    ----------
    orth_list_orig : list of numpy.ndarray
        Orthonormal tensors surviving all previously applied generators.
    R : numpy.ndarray, shape (3, 3)
        Rotation matrix for the generator of a cyclic subgroup.
    order : int
        Order of the generator (``R ** order == identity``).
    parity : int
        Combined space/time parity for this generator (0 or 1);
        each application of ``R`` is multiplied by ``(-1)**parity``.

    Returns
    -------
    orth_list : list of numpy.ndarray
        Reduced, re-orthonormalized list of independent tensors.
    """
    orth_list = []

    # Convert list of numpy arrays into higher-rank array
    # Last (fast) index corresponds to loop over list index
    tensor_array = np.stack(orth_list_orig, axis=-1)

    # Apply the cycle of symmetry operations associated with the
    # generator and accumulate the sum
    t_a_sum = copy(tensor_array)
    for j in range(order - 1):
        tensor_array = transform_tensors(tensor_array, R, parity)
        t_a_sum += tensor_array
    tensor_array = t_a_sum

    # Convert back to a list of tensors.  The list conversion acts
    # on axis 0, so we move the last axis forward before converting.
    orth_list_symmetrized = list(np.moveaxis(tensor_array, -1, 0))

    # Now prune the list
    orth_list = []
    for tensor in orth_list_symmetrized:
        # Only add to list if orthogonal to previous ones
        if is_zero(tensor):
            continue
        for otensor in orth_list:
            tensor = tensor - otensor * t_prod(otensor, tensor)  # project out
        if is_zero(tensor):
            continue
        # we found a tensor that is orthogonal to previous ones
        tensor = tensor / norm(tensor)  # normalize it
        orth_list.append(tensor)  # and add it to the list

    return orth_list


def transform_tensors(tensor_array, R, parity):
    """
    Apply a rotation matrix to every axis of a collection of tensors.

    Contracts ``R`` along each axis of ``tensor_array`` except the last
    (which indexes the collection), optionally multiplying by a parity
    sign.

    Parameters
    ----------
    tensor_array : numpy.ndarray
        Stacked tensor collection; the last axis indexes individual
        tensors in the collection.
    R : numpy.ndarray, shape (3, 3)
        Symmetry operation (rotation matrix) to apply.
    parity : int
        If odd, multiplies the result by ``-1`` after transformation.

    Returns
    -------
    tensor_array : numpy.ndarray
        Transformed tensor collection with the same shape as the input.
    """
    # Transform along each axis of tensor except last one
    for axis in range(tensor_array.ndim - 1):
        # Contract R with the corresponding axis of the tensor
        tensor_array = np.tensordot(R, tensor_array, axes=(1, axis))
        # tensordot moves the new free index (from R) to the front,
        # so we roll it back
        tensor_array = np.moveaxis(tensor_array, 0, axis)
    tensor_array *= (-1) ** parity

    return tensor_array
