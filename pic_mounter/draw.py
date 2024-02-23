import math
from functools import lru_cache
from typing import Any, Literal, cast, overload

from PIL import Image, ImageColor, ImageDraw, ImageFont

MM_PER_INCH = 25.4
type Point_T = tuple[float, float]
type Vector_T = tuple[float, float]
type XY_T = tuple[Point_T, Point_T]
type RGBA_T = tuple[float, float, float, float]


def mm_to_pixel(x: float, /, ppi: float) -> float:
    return x / MM_PER_INCH * ppi


def pixel_to_mm(x: float, /, ppi: float) -> float:
    return x * MM_PER_INCH / ppi


@overload
def pos_mm_to_pixel(pos: Point_T,
                    ppi: float,
                    method: None = ...) -> tuple[float, float]: ...


@overload
def pos_mm_to_pixel(pos: Point_T,
                    ppi: float,
                    method: Literal['floor', 'round'] = ...) -> tuple[int, int]: ...


def pos_mm_to_pixel(pos: Point_T,
                    ppi: float,
                    method: Literal['floor', 'round', None] = 'round') -> tuple[float, float] | tuple[int, int]:
    x, y = pos
    match method:
        case None:
            return (mm_to_pixel(x, ppi), mm_to_pixel(y, ppi))
        case 'floor':
            return (math.floor(mm_to_pixel(x, ppi)), math.floor(mm_to_pixel(y, ppi)))
        case 'round':
            return (round(mm_to_pixel(x, ppi)), round(mm_to_pixel(y, ppi)))
        case _:
            raise ValueError


@lru_cache
def _get_empty_draw() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new('RGBA', (0, 0)))


def get_text_height(text: str, font: ImageFont.FreeTypeFont, **kwargs: Any) -> int:
    return (_get_empty_draw().multiline_textbbox((0, 0), text, font, 'la', **kwargs)[3]
            - _get_empty_draw().multiline_textbbox((0, 0), text, font, 'ld', **kwargs)[3])


def calc_alpha(radius: float, distance: float) -> float:
    if distance <= radius - 1 / 2:
        return 1
    if distance >= radius + 1 / 2:
        return 0
    return radius + 1 / 2 - distance


def mix_number(foreground: float, background: float, alpha: float) -> float:
    return foreground * alpha + background * (1 - alpha)


def mix_tuple[Tuple_T: tuple[float, ...]](foreground: Tuple_T, background: Tuple_T, alpha: float) -> Tuple_T:
    assert len(foreground) == len(background), ValueError('foreground and background must have same length.')
    return cast(Tuple_T, tuple(mix_number(x, y, alpha) for x, y in zip(foreground, background)))


def round_tuple(x: tuple[float, ...], /) -> tuple[int, ...]:
    return tuple(round(y) for y in x)


def mix_color_number(foreground_number: float,
                     foreground_alpha: float,
                     background_number: float,
                     background_alpha: float,
                     alpha: float) -> float:
    return ((background_number * background_alpha * (1 - alpha * foreground_alpha)
             + foreground_number * alpha * foreground_alpha)
            / (background_alpha + alpha * foreground_alpha - background_alpha * alpha * foreground_alpha))


def mix_color_alpha(foreground_alpha: float, background_alpha: float, alpha: float) -> float:
    return background_alpha + alpha * foreground_alpha - background_alpha * alpha * foreground_alpha


def mix_color(foreground: RGBA_T, background: RGBA_T, alpha: float) -> RGBA_T:
    foreground_color = foreground[:3]
    foreground_alpha = foreground[3]
    background_color = background[:3]
    background_alpha = background[3]
    if alpha == 0:
        return background
    elif alpha == 1:
        return foreground
    else:
        return cast(
            RGBA_T,
            (tuple(mix_color_number(foreground_number, foreground_alpha, background_number, background_alpha, alpha)
                   for foreground_number, background_number in zip(foreground_color, background_color))
             + (mix_color_alpha(foreground_alpha, background_alpha, alpha),))
        )


def _get_circle_image(center: Point_T,
                      radius: float,
                      color) -> tuple[Image.Image, tuple[int, int]]:
    center_x, center_y = center
    color_rgba: tuple[int, int, int, int] = ImageColor.getcolor(color, 'RGBA')  # type: ignore
    color_rgb: tuple[int, int, int] = color_rgba[:3]
    color_alpha: int = color_rgba[3]
    left_x: int = math.floor(center_x - radius)
    right_x: int = math.ceil(center_x + radius)
    top_y: int = math.floor(center_y - radius)
    bottom_y: int = math.ceil(center_y + radius)
    layer_width: int = right_x - left_x
    layer_height: int = bottom_y - top_y
    layer: Image.Image = Image.new('RGBA', (layer_width, layer_height))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(layer)
    for x_in_layer in range(layer_width):
        for y_in_layer in range(layer_height):
            x: float = x_in_layer + left_x + 1 / 2
            y: float = y_in_layer + top_y + 1 / 2
            distance: float = math.dist(center, (x, y))
            alpha: float = calc_alpha(radius, distance)
            if alpha == 0:
                continue
            layer_color: tuple[int, int, int, int] = color_rgb + (round(color_alpha * alpha),)
            draw.point((x_in_layer, y_in_layer), layer_color)
    return layer, (left_x, top_y)


@lru_cache
def _get_circle_image_with_cache(center: Point_T,
                                 radius: float,
                                 color: Any) -> tuple[Image.Image, tuple[int, int]]:
    return _get_circle_image(center, radius, color)


def get_circle_image(center: Point_T,
                     radius: float,
                     color) -> tuple[Image.Image, tuple[int, int]]:
    if center == (1 / 2, 1 / 2):
        return _get_circle_image_with_cache(center, radius, color)
    else:
        return _get_circle_image(center, radius, color)


def draw_circle(image: Image.Image,
                center: Point_T,
                radius: float,
                color,
                anti_alias: Literal['off', 'fast', 'accurate'] = 'fast') -> None:
    match anti_alias:
        case 'off':
            draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)
            x, y = center
            xy: tuple[tuple[int, int], tuple[int, int]] = ((round(x - radius), round(y - radius)),
                                                           (round(x + radius), round(y + radius)))
            draw.ellipse(xy, color, width=0)

        case 'fast':
            center_x, center_y = center
            circle_image, destination = get_circle_image((1 / 2, 1 / 2), radius, color)
            delta_x, delta_y = destination
            image.alpha_composite(circle_image, (math.floor(center_x) + delta_x, math.floor(center_y) + delta_y))

        case 'accurate':
            circle_image, destination = get_circle_image(center, radius, color)
            image.alpha_composite(circle_image, destination)

        case _:
            raise ValueError


def dot_product_2d(vector_0: Vector_T, vector_1: Vector_T, /) -> float:
    x0, y0 = vector_0
    x1, y1 = vector_1
    return x0 * x1 + y0 * y1


def distance_point_to_line_ABC(point: Point_T, line_A: float, line_B: float, line_C: float, abs_: bool = True) -> float:
    x, y = point
    distance_with_sign: float = (line_A * x + line_B * y + line_C) / math.hypot(line_A, line_B)
    return abs(distance_with_sign) if abs_ else distance_with_sign


def distance_point_to_line_xy(point: Point_T, line_xy: XY_T) -> float:
    (x0, y0), (x1, y1) = line_xy
    line_A: float = y1 - y0
    line_B: float = x0 - x1
    line_C: float = x1 * y0 - x0 * y1
    return distance_point_to_line_ABC(point, line_A, line_B, line_C)


def distance_point_to_line_segment(point: Point_T, line_xy: XY_T) -> float:
    x, y = point
    (x0, y0), (x1, y1) = line_xy
    vector_AB: Vector_T = (x1 - x0, y1 - y0)
    vector_AP: Vector_T = (x - x0, y - y0)
    vector_BP: Vector_T = (x - x1, y - y1)
    is_in_A_side: bool = dot_product_2d(vector_AB, vector_AP) < 0
    is_in_B_side: bool = dot_product_2d(vector_AB, vector_BP) >= 0  # Vector_BA * Vector_BP < 0
    if is_in_A_side:
        return math.dist(point, line_xy[0])
    elif is_in_B_side:
        return math.dist(point, line_xy[1])
    else:  # middle
        return distance_point_to_line_xy(point, line_xy)


def get_line_image(line_xy: XY_T,
                   color,
                   width: float) -> tuple[Image.Image, tuple[int, int]]:
    (x0, y0), (x1, y1) = line_xy
    delta_x: float = x1 - x0
    delta_y: float = y1 - y0
    if abs(delta_y) > abs(delta_x):  # Avoid ZeroDivisionError or accuracy loss
        image, (destination_y, destination_x) = get_line_image(((y0, x0), (y1, x1)), color, width)
        return image.transpose(Image.Transpose.TRANSVERSE), (destination_x, destination_y)

    slope: float = delta_y / delta_x
    sec_alpha: float = math.hypot(1, slope)

    color_rgba: tuple[int, int, int, int] = ImageColor.getcolor(color, 'RGBA')  # type: ignore
    color_rgb: tuple[int, int, int] = color_rgba[:3]
    color_alpha: int = color_rgba[3]

    left_x: int = math.floor(min(x0, x1) - width / 2)
    right_x: int = math.ceil(max(x0, x1) + width / 2)
    top_y: int = math.floor(min(y0, y1) - width / 2)
    bottom_y: int = math.ceil(max(y0, y1) + width / 2)
    layer_width: int = right_x - left_x
    layer_height: int = bottom_y - top_y
    layer: Image.Image = Image.new('RGBA', (layer_width, layer_height))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(layer)
    for x_in_layer in range(layer_width):
        x: float = x_in_layer + left_x + 1 / 2
        intersection_y: float = slope * (x - x0) + y0
        down_border: float = intersection_y - (width / 2 + 1 / 2) * sec_alpha
        up_border: float = intersection_y + (width / 2 + 1 / 2) * sec_alpha
        possible_min: int = max(0, round(down_border) - top_y)
        possible_max: int = min(layer_height, round(up_border) - top_y)
        for y_in_layer in range(possible_min, possible_max):
            y: float = y_in_layer + top_y + 1 / 2
            distance: float = distance_point_to_line_segment((x, y), line_xy)
            alpha: float = calc_alpha(width / 2, distance)
            if alpha == 0:
                continue
            layer_color: tuple[int, int, int, int] = color_rgb + (round(color_alpha * alpha),)
            draw.point((x_in_layer, y_in_layer), layer_color)
    return layer, (left_x, top_y)


def draw_line(image: Image.Image,
              line_xy: XY_T,
              width: float,
              color,
              anti_alias: Literal['off', 'accurate'] = 'accurate') -> None:
    (x0, y0), (x1, y1) = line_xy
    match anti_alias:
        case 'off':
            draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)
            line_xy = (math.floor(x0), math.floor(y0)), (math.floor(x1), math.floor(y1))
            draw.line(line_xy, color, round(width))

        case 'accurate':
            line_image, destination = get_line_image(line_xy, color, width)
            image.alpha_composite(line_image, destination)

        case _:
            raise ValueError
