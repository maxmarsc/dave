from PySide6.QtWidgets import QFrame


class EntitySidePanelInfo(QFrame):
    """
    A small textbox with information on the entity.

    It should not exceed 60 pixels of height
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame | QFrame.Shadow.Plain)
