
import typing

from src.HEAD import *

# import config

import src.math_utils as math_utils




def find_in_list(element, list_, default_value: int = -1) -> int:
    for i in range(len(list_)):
        if list_[i] == element:
            return i
    return default_value






DIMENSIONS_CLASSES = (
    KAPI7.IAngleDimension,
    KAPI7.IBreakAngleDimension,

    KAPI7.IArcDimension,
    KAPI7.IBreakLineDimension,
    KAPI7.IBreakRadialDimension,
    KAPI7.IDiametralDimension,
    KAPI7.IHeightDimension,
    KAPI7.ILineDimension,
    KAPI7.IRadialDimension,
)

DIMENSIONS_CLASSES_ANGLE = (
    KAPI7.IAngleDimension,
    KAPI7.IBreakAngleDimension,
)


class DimensionSign(int):
    Nothing = 0  # нет значка
    Diameter = 1  # диаметр
    Square = 2  # квадрат
    Radius = 3  # радиус
    MetricThread = 4  # метрическая резьба





def iterate_selected_dimensions():
    doc: KAPI7.IKompasDocument2D = open_doc2d("")
    ds: list[KAPI7.IDrawingObject] = get_selected_dimensions(doc)
    for d in ds:
        dt: KAPI7.IDimensionText = KAPI7.IDimensionText(d)
        dp: KAPI7.IDimensionParams = KAPI7.IDimensionParams(d)
        yield (d, dt, dp)


def round_selected_dimensions(multiple: float = 1, middle_coef: float = 0.5, is_angle_DMS: bool = True) -> None:
    for d, dt, dp in iterate_selected_dimensions():
        is_angle = isinstance(d, DIMENSIONS_CLASSES_ANGLE)
        nv = dt.NominalValue
        nt: KAPI7.ITextLine = dt.NominalText
        old = nt.Str

        if is_angle:
            x = nv
            if is_angle_DMS:
                if math_utils.do_floats_equal(x, 0):
                    new = "0°"
                else:
                    # rounding in seconds
                    x = round(math_utils.round_to_number(x * 3600, multiple * 3600, middle_coef))

                    sign = -1 if x < 0 else +1
                    x = abs(x)
                    v = int(x / 3600)
                    m = int(x / 60 - v * 60)
                    s = int(x - v * 3600 - m * 60)

                    new = f"{sign * v}°"
                    if m != 0:
                        new += f"{m}'"
                    if s != 0:
                        new += f"{s}\""

                    vr = v + m/60 + s/3600
            else:
                new = math_utils.round_to_number_str(nv, multiple, middle_coef).replace(".", ",") + "°"
        else:
            new = math_utils.round_to_number_str(nv, multiple, middle_coef).replace(".", ",")

        dt.AutoNominalValue = False
        nt.Str = new
        d.Update()


def remove_rounding_in_selected_dimensions() -> None:
    for d, dt, dp in iterate_selected_dimensions():
        dt.AutoNominalValue = True
        d.Update()


def toggle_star_in_selected_dimensions() -> None:
    ds = list(iterate_selected_dimensions())
    if len(ds) == 0:
        return
    d0, dt0, dp0 = ds[0]
    suffix0: str = dt0.Suffix.Str
    has_star: bool = suffix0.endswith("*")

    if has_star:
        # убираем звездочку в конце
        for d, dt, dp in ds:
            old: str = dt.Suffix.Str
            dt.Suffix.Str = old[:old.find("*")]
            d.Update()
    else:
        # добавляем звездочку в конце
        for d, dt, dp in ds:
            old: str = dt.Suffix.Str
            if not old.endswith("*"):
                dt.Suffix.Str = old + "*"
                d.Update()



def set_sign_in_selected_dimensions(sign: DimensionSign) -> None:
    for d, dt, dp in iterate_selected_dimensions():
        dt.Sign = sign
        d.Update()



def get_selected_dimensions(doc: KAPI7.IKompasDocument2D) -> list[KAPI7.IDrawingObject]:
    active_doc = KAPI7.IKompasDocument2D1(doc)
    sm: KAPI7.ISelectionManager = active_doc.SelectionManager
    s_objs: typing.Iterable[KAPI7.IKompasAPIObject] = [sm.SelectedObjects] if not isinstance(sm.SelectedObjects, tuple) else sm.SelectedObjects

    dms: list[KAPI7.IDrawingObject] = []

    for obj in s_objs:
        if isinstance(obj, DIMENSIONS_CLASSES):
            dms.append(obj)
    return dms


def switch_remote_lines_in_selected_dimensions() -> None:
    ds = list(iterate_selected_dimensions())
    if len(ds) == 0:
        return
    d0, dt0, dp0 = ds[0]

    state = 0b10 * int(dp0.RemoteLine1) + 0b01 * int(dp0.RemoteLine2)
    states = [0b11, 0b10, 0b01, 0b00]
    next_i = (find_in_list(state, states, -1) + 1) % len(states)
    next_state = states[next_i]

    for d, dt, dp in ds:
        dp.RemoteLine1 = bool(0b10 & next_state)
        dp.RemoteLine2 = bool(0b01 & next_state)
        d.Update()


def switch_arrows_in_selected_dimensions() -> None:
    ds = list(iterate_selected_dimensions())
    if len(ds) == 0:
        return
    d0, dt0, dp0 = ds[0]

    print(dp0.ArrowType1, dp0.ArrowType2)

    state = 0b10 * int(2 != dp0.ArrowType1) + 0b01 * int(2 != dp0.ArrowType2)
    states = [0b00, 0b10, 0b01, 0b11]
    next_i = (find_in_list(state, states, -1) + 1) % len(states)
    next_state = states[next_i]

    for d, dt, dp in ds:
        dp.ArrowType1 = 2 + 3 * int(bool(0b10 & next_state))
        dp.ArrowType2 = 2 + 3 * int(bool(0b01 & next_state))
        d.Update()


def get_all_dimensions(filter_function = lambda dim: True) -> list[KAPI7.IKompasAPIObject]:
    dims: list[KAPI7.IKompasAPIObject] = []

    doc2d: KAPI7.IKompasDocument2D = open_doc2d("")
    vlm = KAPI7.IViewsAndLayersManager = doc2d.ViewsAndLayersManager
    vs: KAPI7.IViews = vlm.Views

    for i in range(vs.Count):
        v: KAPI7.IView = vs.View(i)
        sc = KAPI7.ISymbols2DContainer(v)

        linedims: KAPI7.ILineDimensions = sc.LineDimensions
        for j in range(linedims.Count):
            dim = linedims.LineDimension(j)
            if filter_function(dim):
                dims.append(dim)

        radialdims: KAPI7.IRadialDimensions = sc.RadialDimensions
        for j in range(radialdims.Count):
            dim = radialdims.RadialDimension(j)
            if filter_function(dim):
                dims.append(dim)

        angledims: KAPI7.IAngleDimensions = sc.AngleDimensions
        for j in range(angledims.Count):
            dim = angledims.AngleDimension(j)
            if filter_function(dim):
                dims.append(dim)

        arcdims: KAPI7.IArcDimensions = sc.ArcDimensions
        for j in range(arcdims.Count):
            dim = arcdims.ArcDimension(j)
            if filter_function(dim):
                dims.append(dim)

        breaklinedims: KAPI7.IBreakLineDimensions = sc.BreakLineDimensions
        for j in range(breaklinedims.Count):
            dim = breaklinedims.BreakLineDimension(j)
            if filter_function(dim):
                dims.append(dim)

        breakradialdims: KAPI7.IBreakRadialDimensions = sc.BreakRadialDimensions
        for j in range(breakradialdims.Count):
            dim = breakradialdims.BreakRadialDimension(j)
            if filter_function(dim):
                dims.append(dim)

        diamdims: KAPI7.IDiametralDimensions = sc.DiametralDimensions
        for j in range(diamdims.Count):
            dim = diamdims.DiametralDimension(j)
            if filter_function(dim):
                dims.append(dim)

        heightdims: KAPI7.IHeightDimensions = sc.HeightDimensions
        for j in range(heightdims.Count):
            dim = heightdims.HeightDimension(j)
            if filter_function(dim):
                dims.append(dim)

    return dims



def check_if_dimension_not_auto(d) -> bool:
    dt: KAPI7.IDimensionText = KAPI7.IDimensionText(d)
    return not dt.AutoNominalValue


def select_rounded_dimensions() -> None:
    doc: KAPI7.IKompasDocument2D = open_doc2d("")

    dims = get_selected_dimensions(doc)
    if len(dims) == 0:
        dims = get_all_dimensions()

    active_doc = KAPI7.IKompasDocument2D1(doc)
    sm: KAPI7.ISelectionManager = active_doc.SelectionManager
    sm.UnselectAll()

    for dim in dims:
        if check_if_dimension_not_auto(dim):
            sm.Select(dim)




if __name__ == "__main__":
    switch_remote_lines_in_selected_dimensions()
