import numpy as np
import math
from math import pi


def rotation_matrix(angle, direction, point=None):
    """Return matrix to rotate about axis defined by point and direction.

    >>> R = rotation_matrix(math.pi/2, [0, 0, 1], [1, 0, 0])
    >>> np.allclose(np.dot(R, [0, 0, 0, 1]), [1, -1, 0, 1])
    True
    >>> angle = (random.random() - 0.5) * (2*math.pi)
    >>> direc = np.random.random(3) - 0.5
    >>> point = np.random.random(3) - 0.5
    >>> R0 = rotation_matrix(angle, direc, point)
    >>> R1 = rotation_matrix(angle-2*math.pi, direc, point)
    >>> is_same_transform(R0, R1)
    True
    >>> R0 = rotation_matrix(angle, direc, point)
    >>> R1 = rotation_matrix(-angle, -direc, point)
    >>> is_same_transform(R0, R1)
    True
    >>> I = np.identity(4, np.float64)
    >>> np.allclose(I, rotation_matrix(math.pi*2, direc))
    True
    >>> np.allclose(2, np.trace(rotation_matrix(math.pi/2,
    ...                                               direc, point)))
    True

    """
    sina = math.sin(angle)
    cosa = math.cos(angle)
    direction = unit_vector(direction[:3])
    # rotation matrix around unit vector
    R = np.diag([cosa, cosa, cosa])
    R += np.outer(direction, direction) * (1.0 - cosa)
    direction *= sina
    R += np.array([[0.0, -direction[2], direction[1]],
                   [direction[2], 0.0, -direction[0]],
                   [-direction[1], direction[0], 0.0]])
    M = np.identity(4)
    M[:3, :3] = R
    if point is not None:
        # rotation not around origin
        point = np.array(point[:3], dtype=np.float64, copy=False)
        M[:3, 3] = point - np.dot(R, point)
    return M


def unit_vector(data, axis=None, out=None):
    """Return ndarray normalized by length, i.e. Euclidean norm, along axis.

    >>> v0 = np.random.random(3)
    >>> v1 = unit_vector(v0)
    >>> np.allclose(v1, v0 / np.linalg.norm(v0))
    True
    >>> v0 = np.random.rand(5, 4, 3)
    >>> v1 = unit_vector(v0, axis=-1)
    >>> v2 = v0 / np.expand_dims(np.sqrt(np.sum(v0*v0, axis=2)), 2)
    >>> np.allclose(v1, v2)
    True
    >>> v1 = unit_vector(v0, axis=1)
    >>> v2 = v0 / np.expand_dims(np.sqrt(np.sum(v0*v0, axis=1)), 1)
    >>> np.allclose(v1, v2)
    True
    >>> v1 = np.empty((5, 4, 3))
    >>> unit_vector(v0, axis=1, out=v1)
    >>> np.allclose(v1, v2)
    True
    >>> list(unit_vector([]))
    []
    >>> list(unit_vector([1]))
    [1.0]

    """
    if out is None:
        data = np.array(data, dtype=np.float64, copy=True)
        if data.ndim == 1:
            data /= math.sqrt(np.dot(data, data))
            return data
    else:
        if out is not data:
            out[:] = np.array(data, copy=False)
        data = out
    length = np.atleast_1d(np.sum(data * data, axis))
    np.sqrt(length, length)
    if axis is not None:
        length = np.expand_dims(length, axis)
    data /= length
    if out is None:
        return data


def my_softmax(np_array):
    """
    Input must be 2 dimensional.
    Softmax is applied separately on each row
    """
    max_val = np.max(np_array, axis=1, keepdims=True)
    predsoft = np.exp(np_array - max_val) / \
        np.sum(np.exp(np_array - max_val), axis=1, keepdims=True)
    return predsoft


# def abline(slope, intercept, color='r'):
#     """
#     Plot a line from slope and intercept
#     """
#     axes = plt.gca()
#     x_vals = np.array(axes.get_xlim())
#     y_vals = intercept + slope * x_vals
#     plt.plot(x_vals, y_vals, color)


def get_vp_from_sphere_coordinate_xY(
        sphere_point,
        sphere_centre,
        sphere_radius):
    z_coords = sphere_radius - \
        np.sqrt(sphere_radius ** 2 -
                np.sum((sphere_point) ** 2, axis=1, keepdims=True))
    sphere_point_3d = np.hstack((sphere_point, z_coords))

    y_coords = ((-sphere_radius / (sphere_point_3d[:, 2] - sphere_radius)) * (
        sphere_point_3d[:, 1])) + sphere_centre[1]
    x_coords = ((-sphere_radius / (sphere_point_3d[:, 2] - sphere_radius)) * (
        sphere_point_3d[:, 0])) + sphere_centre[0]
    return x_coords, y_coords


def get_vp_from_sphere_coordinate_xZ(
        sphere_point,
        sphere_centre,
        sphere_radius):
    # As didn't subtract from 'sphere_radius', so basically y_coords from
    # centre of sphere
    y_coords = np.sqrt(sphere_radius ** 2 -
                       np.sum(sphere_point ** 2, axis=1, keepdims=True))
    sphere_point_3d = np.hstack(
        (sphere_point[:, 0], y_coords.squeeze(), sphere_point[:, 1])).reshape(1, -1)

    y_coords = (
        (-sphere_radius / (sphere_point_3d[:, 2])) * (sphere_point_3d[:, 1])) + sphere_centre[1]
    x_coords = (
        (-sphere_radius / (sphere_point_3d[:, 2])) * (sphere_point_3d[:, 0])) + sphere_centre[0]
    return x_coords, y_coords


def get_line_given_sphere_pointonspherenormaltoplane(sphere_centre, point):
    # adding sphere centre so that it is now in the coordinates of the world
    point = sphere_centre + point

    nor_to_plane = (point - sphere_centre)
    plane_eq = np.hstack((nor_to_plane, -np.dot(nor_to_plane, sphere_centre)))
    plane_eq /= plane_eq[2]

    pred_hor = np.hstack((plane_eq[:2], plane_eq[3]))
    pred_hor /= pred_hor[2]

    return pred_hor


def get_horvpz_from_projected_4indices_modified(
        output_label,
        all_bins,
        all_sphere_centres,
        all_sphere_radii):
    req_coords = np.zeros(4)
    input_points = np.zeros((2, 2))

    for label_no in range(4):
        ind = output_label[label_no]
        half_of_bin_size = (all_bins[label_no, 1] - all_bins[label_no, 0]) / 2
        req_coords[label_no] = all_bins[label_no, ind] + half_of_bin_size

    y_coord = -np.sqrt(all_sphere_radii[0] ** 2 -
                       (req_coords[0] ** 2 + req_coords[1] ** 2))
    input_points[0, :] = get_line_given_sphere_pointonspherenormaltoplane(
        all_sphere_centres[0, :], [req_coords[0], y_coord, req_coords[1]])[:2]

    vpzx_xy_coords = np.array([req_coords[2], 0]).reshape(1, -1)
    input_points[1,
                 0] = get_vp_from_sphere_coordinate_xY(vpzx_xy_coords,
                                                       sphere_centre=all_sphere_centres[2,
                                                                                        :],
                                                       sphere_radius=all_sphere_radii[2])[0][0]

    vpzy_xZ_coords = np.array([0, req_coords[3]]).reshape(1, -1)
    input_points[1,
                 1] = get_vp_from_sphere_coordinate_xZ(vpzy_xZ_coords,
                                                       sphere_centre=all_sphere_centres[3,
                                                                                        :],
                                                       sphere_radius=all_sphere_radii[3])[1][0]

    return input_points


# def plot_scaled_horizonvector_vpz_picture(
#         image,
#         horizonvector_vpz,
#         net_dims,
#         color='go',
#         show_vz=False,
#         verbose=False):
#     # because we are gonna rescale horizon line to these dimensions
#     re_height, re_width, re_channels = image.shape
#     net_width, net_height = net_dims

#     scaled_vpz = np.zeros_like(horizonvector_vpz[1, :])
#     scaled_vpz[0] = horizonvector_vpz[1, 0] * re_width / net_width
#     scaled_vpz[1] = horizonvector_vpz[1, 1] * re_height / net_height

#     horizon_vectorform = np.hstack((horizonvector_vpz[0, :2], 1))
#     horizon_vectorform[0] = horizon_vectorform[0] / (re_width / net_width)
#     horizon_vectorform[1] = horizon_vectorform[1] / (re_height / net_height)
#     horizon_vectorform = horizon_vectorform / horizon_vectorform[2]

#     slope, intercept = get_slope_intercept_from_abc_line(horizon_vectorform)
#     abline(slope, intercept)
#     if show_vz:
#         ax.plot(scaled_vpz[0], scaled_vpz[1], color)

#     return ax


def get_intrinisic_extrinsic_params_from_horizonvector_vpz(
        img_dims, horizonvector_vpz, net_dims, verbose=False):
    re_width, re_height = img_dims
    net_width, net_height = net_dims

    image_centre = np.array([re_width / 2, re_height / 2, 0])

    scaled_vpz = np.zeros_like(horizonvector_vpz[1, :])
    scaled_vpz[0] = horizonvector_vpz[1, 0] * re_width / net_width
    scaled_vpz[1] = horizonvector_vpz[1, 1] * re_height / net_height

    horizon_vectorform = np.hstack((horizonvector_vpz[0, :2], 1))

    # rescaling the horizon line according to the new size of the image
    # see https://math.stackexchange.com/questions/2864486/how-does-equation-of-a-line-change-as-scale-of-axes-changes?
    # noredirect=1#comment5910386_2864489

    horizon_vectorform[0] = horizon_vectorform[0] / (re_width / net_width)
    horizon_vectorform[1] = horizon_vectorform[1] / (re_height / net_height)
    horizon_vectorform = horizon_vectorform / horizon_vectorform[2]

    # Doing for getting horizon as image centre
    horizon_translate_coordz = horizon_vectorform[2] + (
        (horizon_vectorform[0] * (re_width / 2) + horizon_vectorform[1] * (re_height / 2)))
    horizon_vectorform_center = horizon_vectorform / horizon_translate_coordz

    # m = -a/b when line in vector form ([a, b, c] from ax+by+c=0)
    roll_from_horizon = (
        degrees(atan(-horizon_vectorform_center[0] / horizon_vectorform_center[1])))

    # Both parameters used for calculating fx/fy are currently measured from
    # image centre

    fx = np.sqrt(
        np.abs(
            (scaled_vpz[0] -
             image_centre[0]) /
            horizon_vectorform_center[0]))

    fy = np.sqrt(
        np.abs(
            (scaled_vpz[1] -
             image_centre[1]) /
            horizon_vectorform_center[1]))

    norm_vpz = np.sqrt((scaled_vpz[0] - image_centre[0])
                       ** 2 + (scaled_vpz[1] - image_centre[1]) ** 2)
    # subtracted 90, so now tilt from top as well
    my_tilt = 90 - degrees(atan(norm_vpz / fy))
    my_tilt = radians(my_tilt)

    # y=mx+c -> c = y-mx. Line form: mx-y+c = 0
    hor_slope = - horizon_vectorform[0] / horizon_vectorform[1]
    perp_slope = -1 / hor_slope
    perp_intercept = image_centre[1] - perp_slope * image_centre[0]
    perp_eq = [perp_slope, -1, perp_intercept]
    perp_eq /= perp_eq[2]
    normal_to_hor_from_imcentre = np.cross(horizon_vectorform, perp_eq)
    normal_to_hor_from_imcentre /= normal_to_hor_from_imcentre[2]
    if verbose:
        print("normal_to_hor_from_imcentre:", normal_to_hor_from_imcentre)
    norm_hor = np.sqrt((normal_to_hor_from_imcentre[0] - image_centre[0]) ** 2 + (
        normal_to_hor_from_imcentre[1] - image_centre[1]) ** 2)
    my_tilt_hor = atan(norm_hor / fy)  # tilt from top
    if verbose:
        print("Tilt from hor:", degrees(my_tilt_hor))

    my_fx = np.sqrt(norm_hor * norm_vpz)
    if verbose:
        print("My way for fx:", my_fx)

    if verbose:
        print("Predicted:")
        print("fx:", fx, "fy:", fy, "roll:", roll_from_horizon,
              "tilt(rad):", my_tilt, "tilt(deg):", degrees(my_tilt))

    return fx, fy, roll_from_horizon, my_tilt


def get_overhead_hmatrix_from_4cameraparams(
        fx, fy, my_tilt, my_roll, img_dims, verbose=False):
    width, height = img_dims

    origin, xaxis, yaxis, zaxis = [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    K3x3 = np.array([[fx, 0, width / 2],
                     [0, fy, height / 2],
                     [0, 0, 1]])
    """ K3x3 = np.array([[fx, 0, 0],
                     [0, fy, 0],
                     [0, 0, 1]]) """

    inv_K3x3 = np.linalg.inv(K3x3)
    if verbose:
        print("K3x3:\n", K3x3)

    R_overhead = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    if verbose:
        print("R_overhead:\n", R_overhead)

    R_slant = rotation_matrix((pi / 2) + my_tilt, xaxis)[:3, :3]
    if verbose:
        print("R_slant:\n", R_slant)

    R_roll = rotation_matrix(my_roll, zaxis)[:3, :3]

    middle_rotation = np.dot(R_overhead, np.dot(
        np.linalg.inv(R_slant), R_roll))

    overhead_hmatrix = np.dot(K3x3, np.dot(middle_rotation, inv_K3x3))
    est_range_u, est_range_v = modified_matrices_calculate_range_output_without_translation(
        height, width, overhead_hmatrix, verbose=False)

    if verbose:
        print("Estimated destination range: u=",
              est_range_u, "v=", est_range_v)

    moveup_camera = np.array(
        [[1, 0, -est_range_u[0]], [0, 1, -est_range_v[0]], [0, 0, 1]])
    if verbose:
        print("moveup_camera:\n", moveup_camera)

    overhead_hmatrix = np.dot(moveup_camera, np.dot(
        K3x3, np.dot(middle_rotation, inv_K3x3)))
    if verbose:
        print("overhead_hmatrix:\n", overhead_hmatrix)

    return overhead_hmatrix, est_range_u, est_range_v


def get_scaled_homography(
        H,
        target_height,
        estimated_xrange,
        estimated_yrange):
    # if don't want to scale image, then pass target_height = np.inf

    current_height = estimated_yrange[1] - estimated_yrange[0]
    target_height = min(target_height, current_height)
    (tw, th) = int(np.round((estimated_xrange[1] - estimated_xrange[0]))), int(
        np.round((estimated_yrange[1] - estimated_yrange[0])))

    tr = target_height / float(th)
    target_dim = (int(tw * tr), target_height)

    scaling_matrix = np.array([[tr, 0, 0], [0, tr, 0], [0, 0, 1]])
    scaled_H = np.dot(scaling_matrix, H)

    return scaled_H, target_dim


def modified_matrices_calculate_range_output_without_translation(
        height, width, overhead_hmatrix, verbose=False):
    range_u = np.array([np.inf, -np.inf])
    range_v = np.array([np.inf, -np.inf])

    i = 0
    j = 0
    u, v, w = np.dot(overhead_hmatrix, [j, i, 1])
    u = u / w
    v = v / w
    out_upperpixel = v
    if verbose:
        print(u, v)
    range_u[0] = min(u, range_u[0])
    range_v[0] = min(v, range_v[0])
    range_u[1] = max(u, range_u[1])
    range_v[1] = max(v, range_v[1])
    i = height - 1
    j = 0
    u, v, w = np.dot(overhead_hmatrix, [j, i, 1])
    u = u / w
    v = v / w
    out_lowerpixel = v
    if verbose:
        print(u, v)
    range_u[0] = min(u, range_u[0])
    range_v[0] = min(v, range_v[0])
    range_u[1] = max(u, range_u[1])
    range_v[1] = max(v, range_v[1])
    i = 0
    j = width - 1
    u, v, w = np.dot(overhead_hmatrix, [j, i, 1])
    u = u / w
    v = v / w
    if verbose:
        print(u, v)
    range_u[0] = min(u, range_u[0])
    range_v[0] = min(v, range_v[0])
    range_u[1] = max(u, range_u[1])
    range_v[1] = max(v, range_v[1])
    i = height - 1
    j = width - 1
    u, v, w = np.dot(overhead_hmatrix, [j, i, 1])
    u = u / w
    v = v / w
    if verbose:
        print(u, v)
    range_u[0] = min(u, range_u[0])
    range_v[0] = min(v, range_v[0])
    range_u[1] = max(u, range_u[1])
    range_v[1] = max(v, range_v[1])

    range_u = np.array(range_u, dtype=np.int)
    range_v = np.array(range_v, dtype=np.int)

    # it means that while transforming, after some bottom lower image was transformed,
    # upper output pixels got greater than lower
    if out_upperpixel > out_lowerpixel:

        # range_v needs to be updated
        max_height = height * 3
        upper_range = out_lowerpixel
        best_lower = upper_range  # since out_lowerpixel was lower value than out_upperpixel
        #                           i.e. above in image than out_lowerpixel
        x_best_lower = np.inf
        x_best_upper = -np.inf

        for steps_h in range(2, height):
            temp = np.dot(overhead_hmatrix, np.vstack((np.arange(0, width), np.ones(
                (1, width)) * (height - steps_h), np.ones((1, width)))))
            temp = temp / temp[2, :]

            lower_range = temp.min(axis=1)[1]
            x_lower_range = temp.min(axis=1)[0]
            x_upper_range = temp.max(axis=1)[0]
            if x_lower_range < x_best_lower:
                x_best_lower = x_lower_range
            if x_upper_range > x_best_upper:
                x_best_upper = x_upper_range

            # enforcing max_height of destination image
            if (upper_range - lower_range) > max_height:
                lower_range = upper_range - max_height
                break
            if lower_range > upper_range:
                lower_range = best_lower
                break
            if lower_range < best_lower:
                best_lower = lower_range
            if verbose:
                print(steps_h, lower_range, x_best_lower, x_best_upper)
        range_v = np.array([lower_range, upper_range], dtype=np.int)

        # for testing
        range_u = np.array([x_best_lower, x_best_upper], dtype=np.int)

    return range_u, range_v
