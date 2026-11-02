from calibre.customize import EditBookToolPlugin


class LectrixThemesEditor(EditBookToolPlugin):
    name = 'Lectrix themes for Edit book'
    description = (
        "Lectrix's light and dark themes for the book editor: the title bar, fields, buttons,"
        ' menus and tooltips, and Lectrix syntax themes.'
    )
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Mark'
    version = (1, 2, 0)
    minimum_calibre_version = (7, 0, 0)
