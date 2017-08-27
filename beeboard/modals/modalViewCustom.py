from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup


class ModalViewCustom(ModalView):

    # ****************************************************************************************
    #       Function that closes the current Modal
    # ****************************************************************************************
    def cancel(self):
        self.dismiss()


class PopUpWarning(Popup):

    # ****************************************************************************************
    #       Function that closes the current PopUp
    # ****************************************************************************************
    def cancel(self):
        self.dismiss()