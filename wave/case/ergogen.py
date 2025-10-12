import json
from ocp_vscode import *


import yaml
import sympy

from dataclasses import dataclass, field
from build123d import *
from typing import Callable, Dict, List, Any
import re
from copy import copy


@dataclass
class Point:
    p: Vector = Vector(0, 0) 
    r: float = 0
    meta: dict = field(default_factory=dict)

def load_config(config_path: str) -> Dict:
    """Load the ergogen YAML config."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def evaluate_expression(expr: any, context: Dict[str, float]) -> float:
    try:
        return float(sympy.parse_expr(str(expr), transformations='all', local_dict=context))
    except:
        print(f"Could not evaluate expression '{expr}' with sympy, returning as is")
        return expr

def visit_all(d: Dict | list, visitor: Callable[[dict|list, str, any], any], path: list[str] = [], complete_dict: Dict | None = None) -> None:
    """Recursively visit all keys in a nested dictionary or list, applying the visitor function.
    The visitor function will be called with 
    - the new dictionary or list being built,
    - the current key and entry,
    - the value to be set (can be None)
    - the path to the current key as a list of strings
    - the complete dictionary before the traversal begun
    """
    if complete_dict is None:
        complete_dict = d

    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            path.append(key)
            visitor(result, key, visit_all(value, visitor, path, complete_dict), path, complete_dict)
            path.pop()
        return result
    elif isinstance(d, list):
        result = []
        dummy = {}
        for index, value in enumerate(d):
            path.append(str(index))
            visitor(dummy, 'dummykey', visit_all(value, visitor, path, complete_dict), path, complete_dict)
            result.append(dummy.get('dummykey', None))
            path.pop()
        return result
    return d

def get_nested_value(d: Dict, path: str, default: Any = None) -> Any:
    """Get a nested value from a dictionary using a list of keys."""
    keys = path.split('.')
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def set_nested_value(d: Dict, path: str, value: Any, *_) -> None:
    """Set a nested value in a dictionary using a list of keys."""
    if value is None:
        value = {}
    keys = path.split('.')
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

def unflatten_dot_notation(config: Dict) -> Dict:
    return visit_all(config, set_nested_value)

def handle_inheritance(config: Dict) -> Dict:
    """Handle inheritance in the config by processing 'inherit' keys."""
    def visitor(d: Dict, key: str, value: Any, path: list[str], complete_dict: Dict) -> None:
        if isinstance(value, dict) and value.get('$extends', None) is not None:
            candidates = value.get('$extends')
            candidates = [candidates] if not isinstance(candidates, list) else candidates
            merged = [value]
            while candidates:
                path = candidates.pop()

                other = get_nested_value(complete_dict, path)

                parents = other.get('$extends', [])
                parents = [parents] if not isinstance(parents, list) else parents
                candidates.extend(parents)

                merged.insert(0, other)

            result = {}
            for d in merged:
                result.update(d)
                    
            del value['$extends']
        d[key] = value

    return visit_all(config, visitor)


def parameterize(config: Dict) -> Dict:
    """Parameterize the config by evaluating all string expressions."""   
    def visitor(d: Dict, key: str, value: Any, path: list[str], complete_dict: Dict) -> None:
        if not isinstance(value, Dict):
            d[key] = value
            return

        if value.get('$skip', False):
            return

        params = value.get('$params', None)
        args = value.get('$args', None)       
        if params is None and args is None:
            d[key] = value
            return
        if params is not None and args is None:
            return
        if params is None and args is not None:
            return

        params = [params] if not isinstance(params, list) else params
        args = [args] if not isinstance(args, list) else args

        value: str = json.dumps(value)
        for pattern, replacement in zip(params, args):
            value = re.sub(rf"{pattern}", replacement, value)
        value = json.loads(value)

        del value['$params']
        del value['$args']
        d[key] = value

    return visit_all(config, visitor)


def parse_units(config: Dict) -> Dict[str, float]:
    """Extract and evaluate all variables from the 'units' section, including predefined units."""
    default_units = {
        'U': 19.05,
        'u': 19,
        'cx': 18,
        'cy': 17,
        'haa': 'cx',
        '$default_stagger': 0,
        '$default_spread': 'u',
        '$default_splay': 0,
        '$default_height': 'u-1',
        '$default_width': 'u-1',
        '$default_padding': 'u',
        '$default_autobind': 10
    }
    raw_units = {**default_units, **config.get('units', {}), **config.get('variables', {})}
    units = {}
    for key, val in raw_units.items():
        units[key] = evaluate_expression(val, units)
    return units

def template(s: str, vals: Dict) -> str:
    def replacer(match):
        return str(get_nested_value(vals, match.group(1)) or '')
    regex = re.compile(r'\{\{([^}]*)\}\}')
    return regex.sub(replacer, s)

def render_zone(zone_name: str, zone: Dict, anchor: Point, global_key: Dict, units: Dict[str, float]) -> Dict[str, Point]:
    """Render a zone and return the generated points."""
    cols = zone.get('columns', {})
    zone_wide_rows: Dict[str, Any] = zone.get('rows', {})
    zone_wide_key = zone.get('key', {})

    # algorithm prep
    points: Dict[str, Point] = {}
    rotations: List[Point] = []

    zone_anchor = copy(anchor)
    # transferring the anchor rotation to "real" rotations
    rotations.append(zone_anchor)
    # and now clear it from the anchor so that we don't apply it twice
    zone_anchor = Point(p=zone_anchor.p)
    
    # column layout
    if len(cols.keys()) == 0:
        cols['default'] = {}
    first_col = True
    for col_name, col in cols.items():
        # combining row data from zone-wide defs and col-specific defs
        actual_rows = list({**zone_wide_rows, **col.get('rows', {})}.keys())
        if not actual_rows:
            actual_rows.append('default')

        # getting key config through the 5-level extension
        keys = []
        default_key = {
            'stagger': units['$default_stagger'],
            'spread': units['$default_spread'],
            'splay': units['$default_splay'],
            'origin': [0, 0],
            'orient': 0,
            'shift': [0, 0],
            'rotate': 0,
            'adjust': {},
            'width': units['$default_width'],
            'height': units['$default_height'],
            'padding': units['$default_padding'],
            'autobind': units['$default_autobind'],
            'skip': False,
            'asym': 'both',
            'colrow': '{{col.name}}_{{row}}',
            'name': '{{zone.name}}_{{colrow}}'
        }
        for row in actual_rows:
            key = {**default_key, **global_key, **zone_wide_key, **col.get('key', {}), **zone_wide_rows.get(row, {}), **col.get('rows', {}).get(row, {})}

            key['zone'] = zone
            key['zone']['name'] = zone_name
            key['col'] = col
            key['col']['name'] = col_name
            key['row'] = row

            key['stagger'] = evaluate_expression(key['stagger'], units)
            key['spread'] = evaluate_expression(key['spread'], units)
            key['splay'] = evaluate_expression(key['splay'], units)
            key['origin'] = Vector(*[evaluate_expression(v, units) for v in key['origin']])
            key['orient'] = evaluate_expression(key['orient'], units)
            key['shift'] = Vector(*[evaluate_expression(v, units) for v in key['shift']])
            key['rotate'] = evaluate_expression(key['rotate'], units)
            key['width'] = evaluate_expression(key['width'], units)
            key['height'] = evaluate_expression(key['height'], units)
            key['padding'] = evaluate_expression(key['padding'], units)
            key['skip'] = bool(key['skip'])

            # templating support
            for k, v in key.items():
                if isinstance(v, str):
                    key[k] = template(v, key)

            keys.append(key)
        
        # setting up column-level anchor without rotation (it's already in the rotations)
        zone_anchor.p += Vector(keys[0]['spread'] if not first_col else 0, keys[0]['stagger'])
        col_anchor = Point(p=zone_anchor.p)

        # applying col-level rotation (cumulatively, for the next columns as well)
        if angle := keys[0]['splay']:
            origin = col_anchor.p + keys[0]['origin']
            candidate = origin
            for r in rotations:
                candidate = (candidate - r.p).rotate(Axis.Z, r.r) + r.p
            rotations.append(Point(p=candidate, r=angle))

        # actually laying out keys
        running_anchor = copy(col_anchor)

        for r in rotations:
            running_anchor.p = (running_anchor.p - r.p).rotate(Axis.Z, r.r) + r.p
            running_anchor.r += r.r

        for key in keys:
            # copy the current column anchor
            point = copy(running_anchor)
            # apply cumulative per-key adjustments
            point.r += key['orient']
            point.p += key['shift'].rotate(Axis.Z, point.r)
            point.r += key['rotate']

            # commit running anchor
            running_anchor = copy(point)

            # apply independent adjustments
            point = parse_anchor(key['adjust'], f"{key['name']}.adjust", {}, point, units)

            # save new keyp(key['adjust'],
            point.meta = key
            points[key['name']] = point

            # advance the running anchor to the next position
            running_anchor.p += Vector(0, key['padding']).rotate(Axis.Z, running_anchor.r)

        first_col = False
    return points

def average (parts: list[Point]) -> Point:
        pos_sum: Vector = sum(part.p for part in parts)
        orien_sum = sum(part.r for part in parts)
        return Point(p=pos_sum/len(parts), r=orien_sum/len(parts))

def intersect(parts: list[Point]) -> Point:
        # // a line is generated from a point by taking their
        # // (rotated) Y axis. The line is not extended to
        # // +/- Infinity as that doesn't work with makerjs.
        # // An arbitrary offset of 1 meter is considered
        # // sufficient for practical purposes, and the point
        # // coordinates are used as pivot point for the rotation.
        def get_line_from_point(point: Point):
            offset = Vector(0, 1000)
            return Line(point.p - offset, point.p + offset)\
                .rotate(Axis.Z, point.r)

        line1 = get_line_from_point(parts[0])
        line2 = get_line_from_point(parts[1])
        intersection = line1.intersect(line2)[0]
        return Point(p=Vector(intersection.X, intersection.Y))

def parse_anchor(raw, name, points: Dict[str, Point] = {}, start: Point = Point(), units: Dict[str, float] = {}) -> Point:
    """Parse an anchor definition and return the resulting Point."""
    if isinstance(raw, list):
        current = copy(start)
        for index, step in enumerate(raw, start=1):
            current = parse_anchor(step, f"{name}[{index}]", points, current, units)
        return current

    raw = {'ref': raw} if isinstance(raw, str) else raw

    point = copy(start)
    if ref := raw.get('ref'):
        if isinstance(ref, str):
            point = copy(points[ref])
        else:
            point = parse_anchor(ref, f"{name}.ref", points, start, units)

    if aggregate := raw.get('aggregate'):
        part_points: list[Location] = []
        for i, part in enumerate(aggregate['parts'], start=1):
            part_points.append(parse_anchor(part, f"{name}.aggregate.parts[{i}]", points, start, units))

        method = aggregate.get('method', 'average')
        if method == 'average' :
            point = average(part_points)
        elif method == 'intersect':
            point = intersect(part_points)

    def rotator(config, name, point: Point):
        try:
            # simple case: number gets added to point rotation
            angle = evaluate_expression(config, units)
            return Point(p=point.p, r=point.r + angle)
        except:
            target = parse_anchor(config, name, points, start, units)
            return Point(p=point.p, r=target.p.get_angle(point.p))

    if orient := raw.get('orient'):
        point = rotator(orient, f"{name}.orient", point)
    if shift := raw.get('shift'):
        xyval = [shift, shift] if not isinstance(shift, list) else shift
            
        xyval = [evaluate_expression(v, units) for v in xyval]
        point.p += Vector(xyval).rotate(Axis.Z, point.r)

    if rotate := raw.get('rotate'):
        point = rotator(rotate, f"{name}.rotate", point)

    if affect := raw.get('affect'):
        candidate = copy(point)
        point = copy(start)
        point.meta = candidate.meta
        affect = list(affect) if isinstance(affect, str) else affect
        for aff in affect:
            if aff == 'x':
                point.p.X = candidate.p.X
            elif aff == 'y':
                point.p.Y = candidate.p.Y
            elif aff == 'r':
                point.r = candidate.r

    return point

def parse_points(config: Dict, units: Dict[str, float]) -> Dict[str, Point]:
    """Parse the points section of the config."""
    zones = get_nested_value(config, 'zones')
    global_key = get_nested_value(config, 'key') or {}
    global_rotate = get_nested_value(config, 'rotate') or 0

    points: Dict[str, Point] = {}

    # rendering zones
    for zone_name, zone in zones.items():
        # extracting keys that are handled here, not at the zone render level
        anchor = parse_anchor(zone.get('anchor', {}), f'points.zones.{zone_name}.anchor', points, Point(), units)
        if 'anchor' in zone:
            del zone['anchor']

        rotate: float = evaluate_expression(zone.get('rotate', 0), units)
        if 'rotate' in zone:
            del zone['rotate']

        # creating new points
        new_points = render_zone(zone_name, zone, anchor, global_key, units)

        default_postfix = '_default'
        keys_with_default_postfix = [k for k in new_points.keys() if k.endswith(default_postfix)]
        for key in keys_with_default_postfix:
            new_key = key[:-len(default_postfix)]
            new_points[new_key] = new_points[key]
            new_points[new_key].meta['name'] = new_key
            del new_points[key]

        for new_point in new_points.values():
            if rotate:
                new_point.p = new_point.p.rotate(Axis.Z, rotate)
                new_point.r += rotate

        points.update(new_points)

    # applying global rotation
    for point in points.values():
        point.p = point.p.rotate(Axis.Z, global_rotate)
        point.r += global_rotate

    filtered = {k: p for k, p in points.items() if not p.meta.get('skip', False)}

    return filtered


def main(config_path: str):
    global config
    config = load_config(config_path)
    config = unflatten_dot_notation(config)
    config = handle_inheritance(config)
    config = parameterize(config)

    units = parse_units(config)
    points = parse_points(config.get('points', {}), units)
    
    with BuildSketch() as sketch:
        for point in points.values():
            with Locations(point.p):
                Rectangle(point.meta.get('width', 18), point.meta.get('height', 18), rotation=point.r)

    push_object(sketch.sketch, name="Points")


if __name__ == "__main__":
    import sys, os

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.ergogen.yml')
    main(config_path)

    
    set_port(3939)
    show_clear()
    set_defaults(ortho=True, default_edgecolor="#121212", reset_camera=Camera.KEEP)
    set_colormap(ColorMap.seeded(colormap="rgb", alpha=1, seed_value="wave"))
    show_objects()


