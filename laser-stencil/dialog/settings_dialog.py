"""Subclass of settings_dialog, which is generated by wxFormBuilder."""
import os
import re

import wx

from . import dialog_base


def pop_error(msg):
    wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)


class SettingsDialog(dialog_base.SettingsDialogBase):
    def __init__(self, extra_data_func, config_save_func,
                 file_name_format_hint, version):
        dialog_base.SettingsDialogBase.__init__(self, None)
        self.panel = SettingsDialogPanel(self, extra_data_func, config_save_func, file_name_format_hint)
        best_size = self.panel.BestSize
        # hack for some gtk themes that incorrectly calculate best size
        best_size.IncBy(dx=0, dy=30)
        self.SetClientSize(best_size)
        self.SetTitle('LaserStencil %s' % version)

    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        try:
            # wxPython 3
            self.SetSizeHintsSz(sz1, sz2)
        except TypeError:
            # wxPython 4
            super(SettingsDialog, self).SetSizeHints(sz1, sz2)

    # def set_extra_data_path(self, extra_data_file):
    #     self.panel.extra.netlistFilePicker.Path = extra_data_file
    #     self.panel.extra.OnNetlistFileChanged(None)


# Implementing settings_dialog
class SettingsDialogPanel(dialog_base.SettingsDialogPanel):
    def __init__(self, parent, extra_data_func, config_save_func,
                 file_name_format_hint):
        self.config_save_func = config_save_func
        dialog_base.SettingsDialogPanel.__init__(self, parent)
        self.general = GeneralSettingsPanel(self.notebook,file_name_format_hint)
        self.notebook.AddPage(self.general, "General")

    def OnExit(self, event):
        self.GetParent().EndModal(wx.ID_CANCEL)

    def OnSaveSettings(self, event):
        self.config_save_func(self)

    def OnGenerateBom(self, event):
        self.GetParent().EndModal(wx.ID_OK)


# Implementing GeneralSettingsPanelBase
class GeneralSettingsPanel(dialog_base.GeneralSettingsPanelBase):

    def __init__(self, parent, file_name_format_hint):
        dialog_base.GeneralSettingsPanelBase.__init__(self, parent)
        self.file_name_format_hint = file_name_format_hint

    def OnComponentBlacklistAdd(self, event):
        item = wx.GetTextFromUser(
                "Characters except for A-Z 0-9 and * will be ignored.",
                "Add blacklist item")
        item = re.sub('[^A-Z0-9*]', '', item.upper())
        if item == '':
            return
        found = self.blacklistBox.FindString(item)
        if found != wx.NOT_FOUND:
            self.blacklistBox.SetSelection(found)
            return
        self.blacklistBox.Append(item)
        self.blacklistBox.SetSelection(
                self.blacklistBox.Count - 1)

    def OnComponentBlacklistRemove(self, event):
        selection = self.blacklistBox.Selection
        if selection != wx.NOT_FOUND:
            self.blacklistBox.Delete(selection)
            if self.blacklistBox.Count > 0:
                self.blacklistBox.SetSelection(max(selection - 1, 0))

    def OnNameFormatHintClick(self, event):
        wx.MessageBox(self.file_name_format_hint, 'File name format help',
                      style=wx.ICON_NONE | wx.OK)

    def OnSize(self, event):
        # Trick the listCheckBox best size calculations
        tmp = self.componentSortOrderBox.GetStrings()
        self.componentSortOrderBox.SetItems([])
        self.Layout()
        self.componentSortOrderBox.SetItems(tmp)
