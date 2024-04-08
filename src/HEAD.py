import Kompas6API5 as KAPI5
import KompasAPI7 as KAPI7
from win32com.client import Dispatch
import LDefin2D
import LDefin3D
import MiscellaneousHelpers as MH

import pythoncom


import os


def is_kompas_running() -> bool:
    try:
        pythoncom.connect('KOMPAS.Application.5')
        iKompasObject5, iKompasObject7 = get_kompas_objects()
        app = get_app7(iKompasObject7)
        if not app.Visible:
            app.Visible = True
        return True
    except Exception as e:
        return False


def ensure_folder(filepath: str) -> None:
    filepath = os.path.abspath(filepath)
    if not os.path.isdir(filepath):
        os.makedirs(filepath)



def get_kompas_objects() -> tuple[KAPI5.KompasObject, KAPI7.IKompasAPIObject]:
    pythoncom.CoInitialize()

    iKompasObject5 = Dispatch('KOMPAS.Application.5')
    iKompasObject5 = KAPI5.KompasObject(iKompasObject5._oleobj_.QueryInterface(KAPI5.KompasObject.CLSID, pythoncom.IID_IDispatch))

    iKompasObject7 = Dispatch('KOMPAS.Application.7')
    iKompasObject7 = KAPI7.IKompasAPIObject(iKompasObject7._oleobj_.QueryInterface(KAPI7.IKompasAPIObject.CLSID, pythoncom.IID_IDispatch))

    return (iKompasObject5, iKompasObject7)


def get_app7(iKompasObject7: KAPI7.IKompasAPIObject) -> KAPI7.IApplication:
    app: KAPI7.IApplication = iKompasObject7.Application
    return app


class DocumentTypeEnum(int):
    ksDocumentUnknown = 0  # Неизвестный тип
    ksDocumentDrawing = 1  # Чертеж
    ksDocumentFragment = 2  # Фрагмент
    ksDocumentSpecification = 3  # Спецификация
    ksDocumentPart = 4  # Деталь
    ksDocumentAssembly = 5  # Сборка
    ksDocumentTextual = 6  # Текстовый доку­мент
    ksDocumentTechnologyAssembly = 7  # Технологиче­ская сборка

    type_2D = 100
    type_2D_text = 101
    type_2D_spc = 102
    type_3D = 103


def get_document_type(doc: KAPI7.IKompasDocument) -> int:
    if doc.DocumentType == DocumentTypeEnum.ksDocumentPart \
            or doc.DocumentType == DocumentTypeEnum.ksDocumentAssembly \
            or doc.DocumentType == DocumentTypeEnum.ksDocumentTechnologyAssembly:
        return DocumentTypeEnum.type_3D
    elif doc.DocumentType == DocumentTypeEnum.ksDocumentDrawing \
            or doc.DocumentType == DocumentTypeEnum.ksDocumentFragment:
        return DocumentTypeEnum.type_2D
    elif doc.DocumentType == DocumentTypeEnum.ksDocumentTextual:
        return DocumentTypeEnum.type_2D_text
    elif doc.DocumentType == DocumentTypeEnum.ksDocumentSpecification:
        return DocumentTypeEnum.type_2D_spc
    else:
        return DocumentTypeEnum.ksDocumentUnknown


def color_traditional_to_kompas(color_traditional: int) -> int:
    r = (color_traditional & 0xff0000) >> 16
    g = (color_traditional & 0x00ff00) >> 8
    b = color_traditional & 0x0000ff
    return (b << 16) | (g << 8) | r

def color_kompas_to_traditional(color_kompas: int) -> int:
    r = color_kompas & 0x0000ff
    g = (color_kompas & 0x00ff00) >> 8
    b = (color_kompas & 0xff0000) >> 16
    return (r << 16) | (g << 8) | b

def pretty_print_color(color: int) -> str:
    return hex(color)[2:].rjust(6, "0")




def get_view_by_name(doc: KAPI7.IKompasDocument2D, view_name: str) -> KAPI7.IView:
    assert get_document_type(doc) == DocumentTypeEnum.type_2D
    vlm: KAPI7.IViewsAndLayersManager = doc.ViewsAndLayersManager
    views: KAPI7.IViews = vlm.Views
    view: KAPI7.IView = views.View(view_name)
    return view


def get_system_view(doc: KAPI7.IKompasDocument2D) -> KAPI7.IView:
    assert doc.DocumentType == DocumentTypeEnum.ksDocumentFragment
    vlm: KAPI7.IViewsAndLayersManager = doc.ViewsAndLayersManager
    views: KAPI7.IViews = vlm.Views
    view: KAPI7.IView = views.View(0)
    return view


def create_document2d(
        app: KAPI7.IApplication,
        type_: DocumentTypeEnum,
        is_visible = True,
        path_to_save: str = "",
        ) -> KAPI7.IKompasDocument2D:
    docs: KAPI7.IDocuments = app.Documents
    doc: KAPI7.IKompasDocument2D = KAPI7.IKompasDocument2D(
        docs.Add(type_, is_visible)
    )
    if path_to_save != "":
        doc.SaveAs(path_to_save)
    return doc


def get_active_part(app: KAPI7.IApplication) -> tuple[KAPI7.IKompasDocument3D, KAPI7.IPart7]:
    active_doc: KAPI7.IKompasDocument3D = KAPI7.IKompasDocument3D(app.ActiveDocument)
    return (active_doc, active_doc.TopPart)


def open_part(filepath: str, app: KAPI7.IApplication) -> tuple[KAPI7.IKompasDocument3D, KAPI7.IPart7]:
    """ Если `filepath == ""`, то возвращается текущий документ и его компонент верхнего уровня. """
    if filepath == "":
        return get_active_part(app)

    docs: KAPI7.IDocuments = app.Documents

    for i in range(docs.Count):
        doc: KAPI7.IKompasDocument = docs.Item(i)
        if doc.PathName == filepath:
            break
    else:
        doc: KAPI7.IKompasDocument = docs.Open(filepath, True, False)

    if doc is None:
        raise Exception(f"Cannot open document '{filepath}'")

    doc3d: KAPI7.IKompasDocument3D = KAPI7.IKompasDocument3D(doc)
    return (doc3d, doc3d.TopPart)


def open_part_K5(filepath: str = "") -> tuple[KAPI5.ksDocument3D, KAPI5.ksPart]:
    iKompasObject5, iKompasObject7 = get_kompas_objects()

    if filepath != "":
        doc: KAPI5.ksDocument3D = iKompasObject5.Document3D()
        doc.Open(filepath, False)
    else:
        doc: KAPI5.ksDocument3D = iKompasObject5.ActiveDocument3D()

    if doc is None:
        raise Exception("Файл детали некорректный")

    part: KAPI5.ksPart = doc.GetPart(LDefin3D.pTop_Part)

    return doc, part


def open_doc2d(filepath: str = "") -> KAPI7.IKompasDocument2D:
    """ Если `filepath == ""`, то возвращается `app.ActiveDocument`. """
    iKompasObject5, iKompasObject7 = get_kompas_objects()
    app: KAPI7.IApplication = get_app7(iKompasObject7)

    if filepath == "":
        if app.ActiveDocument is None:
            raise Exception("Не обнаружен открытый документ.")
        active_doc: KAPI7.IKompasDocument2D = KAPI7.IKompasDocument2D(app.ActiveDocument)
        if get_document_type(active_doc) != DocumentTypeEnum.type_2D:
            raise Exception("Текущий документ не является 2D-документом")
        return active_doc

    docs: KAPI7.IDocuments = app.Documents
    doc: KAPI7.IKompasDocument = docs.Open(filepath, True, False)

    if doc is None:
        raise Exception(f"Cannot open document '{filepath}'")

    doc2d: KAPI7.IKompasDocument2D = KAPI7.IKompasDocument2D(doc)
    return doc2d



def create_part(
        app: KAPI7.IApplication,
        type3d: DocumentTypeEnum,
        is_visible = True,
        path_to_save: str = "",
        ) -> tuple[KAPI7.IKompasDocument3D, KAPI7.IPart7]:
    docs: KAPI7.IDocuments = app.Documents
    doc: KAPI7.IKompasDocument3D = KAPI7.IKompasDocument3D(
        docs.Add(type3d, is_visible)
    )
    if path_to_save != "":
        doc.SaveAs(path_to_save)
    return (doc, doc.TopPart)
