import wx
import wx.xrc

###########################################################################
## Class SettingsDialogBase
###########################################################################

class SettingsDialogBase ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, 
          title = u"LaserStencil", pos = wx.DefaultPosition, 
          size = wx.Size( 463,497 ), 
          style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.BORDER_DEFAULT )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )


        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


###########################################################################
## Class SettingsDialogPanel
###########################################################################

class SettingsDialogPanel ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 400,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer20 = wx.BoxSizer( wx.VERTICAL )

        self.notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP|wx.BORDER_DEFAULT )

        bSizer20.Add( self.notebook, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer39 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button41 = wx.Button( self, wx.ID_ANY, u"Save current settings", wx.DefaultPosition, wx.DefaultSize, 0|wx.BORDER_DEFAULT )
        bSizer39.Add( self.m_button41, 0, wx.ALL, 5 )


        bSizer39.Add( ( 50, 0), 0, wx.EXPAND, 5 )

        self.m_button42 = wx.Button( self, wx.ID_ANY, u"Generate GCode", wx.DefaultPosition, wx.DefaultSize, 0|wx.BORDER_DEFAULT )

        self.m_button42.SetDefault()
        bSizer39.Add( self.m_button42, 0, wx.ALL, 5 )

        self.m_button43 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0|wx.BORDER_DEFAULT )
        bSizer39.Add( self.m_button43, 0, wx.ALL, 5 )


        bSizer20.Add( bSizer39, 0, wx.ALIGN_CENTER, 5 )


        self.SetSizer( bSizer20 )
        self.Layout()

        # Connect Events
        self.m_button41.Bind( wx.EVT_BUTTON, self.OnSaveSettings )
        self.m_button42.Bind( wx.EVT_BUTTON, self.OnGenerateBom )
        self.m_button43.Bind( wx.EVT_BUTTON, self.OnExit )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnSaveSettings( self, event ):
        event.Skip()

    def OnGenerateBom( self, event ):
        event.Skip()

    def OnExit( self, event ):
        event.Skip()


###########################################################################
## Class GeneralSettingsPanelBase
###########################################################################

class GeneralSettingsPanelBase ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

        bSizer32 = wx.BoxSizer( wx.VERTICAL )

        sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Bom destination" ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.AddGrowableCol( 1 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText8 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Directory", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )

        fgSizer1.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.bomDirPicker = wx.DirPickerCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select bom folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_SMALL|wx.DIRP_USE_TEXTCTRL|wx.BORDER_SIMPLE )
        fgSizer1.Add( self.bomDirPicker, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

        self.m_staticText9 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Name format", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )

        fgSizer1.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        bSizer20 = wx.BoxSizer( wx.HORIZONTAL )

        self.fileNameFormatTextControl = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer20.Add( self.fileNameFormatTextControl, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_button12 = wx.Button( sbSizer6.GetStaticBox(), wx.ID_ANY, u"?", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
        bSizer20.Add( self.m_button12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 4 )

        fgSizer1.Add( bSizer20, 1, wx.EXPAND, 5 )

        sbSizer6.Add( fgSizer1, 1, wx.EXPAND, 5 )

        bSizer32.Add( sbSizer6, 0, wx.ALL|wx.EXPAND, 5 )


        blacklistSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Component blacklist" ), wx.VERTICAL )

        bSizer412 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer612 = wx.BoxSizer( wx.VERTICAL )

        blacklistBoxChoices = []
        self.blacklistBox = wx.ListBox( blacklistSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, blacklistBoxChoices, wx.LB_SINGLE|wx.LB_SORT|wx.BORDER_SIMPLE )
        bSizer612.Add( self.blacklistBox, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer412.Add( bSizer612, 1, wx.EXPAND, 5 )

        bSizer512 = wx.BoxSizer( wx.VERTICAL )

        self.m_button112 = wx.Button( blacklistSizer.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size( 30,30 ), 0|wx.BORDER_DEFAULT )
        bSizer512.Add( self.m_button112, 0, wx.ALL, 5 )

        self.m_button212 = wx.Button( blacklistSizer.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size( 30,30 ), 0|wx.BORDER_DEFAULT )
        bSizer512.Add( self.m_button212, 0, wx.ALL, 5 )

        bSizer412.Add( bSizer512, 0, 0, 5 )

        blacklistSizer.Add( bSizer412, 1, wx.EXPAND, 5 )

        self.m_staticText1 = wx.StaticText( blacklistSizer.GetStaticBox(), wx.ID_ANY, u"Globs are supported, e.g. MH*", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )

        blacklistSizer.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.blacklistVirtualCheckbox = wx.CheckBox( blacklistSizer.GetStaticBox(), wx.ID_ANY, u"Blacklist virtual components", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.blacklistVirtualCheckbox.SetValue(True)
        blacklistSizer.Add( self.blacklistVirtualCheckbox, 0, wx.ALL, 5 )

        self.blacklistEmptyValCheckbox = wx.CheckBox( blacklistSizer.GetStaticBox(), wx.ID_ANY, u"Blacklist components with empty value", wx.DefaultPosition, wx.DefaultSize, 0 )
        blacklistSizer.Add( self.blacklistEmptyValCheckbox, 0, wx.ALL, 5 )


        bSizer32.Add( blacklistSizer, 1, wx.ALL|wx.EXPAND|wx.TOP, 5 )

# -------------------------------------------------------------

        sbSizer6m = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Laser Settings" ), wx.VERTICAL )

        bSizer10m = wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText8m = wx.StaticText( sbSizer6m.GetStaticBox(), wx.ID_ANY,
           u"Pad Cut Laser Power", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8m.Wrap( -1 )
        bSizer10m.Add( self.m_staticText8m, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.laserPowerTextControl = wx.TextCtrl( sbSizer6m.GetStaticBox(), 
          wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10m.Add( self.laserPowerTextControl, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer20m = wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText9m = wx.StaticText( sbSizer6m.GetStaticBox(), wx.ID_ANY,
           u"Pad Cut Laser Passes", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9m.Wrap( -1 )
        bSizer20m.Add( self.m_staticText9m, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.laserPassesTextControl = wx.TextCtrl( sbSizer6m.GetStaticBox(), 
          wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer20m.Add( self.laserPassesTextControl, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer30m = wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText7m = wx.StaticText( sbSizer6m.GetStaticBox(), wx.ID_ANY,
           u"Cuting Speed", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7m.Wrap( -1 )
        bSizer30m.Add( self.m_staticText7m, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.laserSpeedTextControl = wx.TextCtrl( sbSizer6m.GetStaticBox(), 
          wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer30m.Add( self.laserSpeedTextControl, 1, wx.ALL|wx.EXPAND, 5 )

        bSizer40m = wx.BoxSizer( wx.HORIZONTAL )
        self.m_staticText6m = wx.StaticText( sbSizer6m.GetStaticBox(), wx.ID_ANY,
           u"Border Mark Laser Power", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6m.Wrap( -1 )
        bSizer40m.Add( self.m_staticText6m, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.borderPowerTextControl = wx.TextCtrl( sbSizer6m.GetStaticBox(), 
          wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer40m.Add( self.borderPowerTextControl, 1, wx.ALL|wx.EXPAND, 5 )

        sbSizer6m.Add( bSizer10m, 1, wx.ALL|wx.EXPAND, 5 )
        sbSizer6m.Add( bSizer30m, 1, wx.ALL|wx.EXPAND, 5 )
        sbSizer6m.Add( bSizer20m, 1, wx.ALL|wx.EXPAND, 5 )
        sbSizer6m.Add( bSizer40m, 1, wx.ALL|wx.EXPAND, 5 )
        bSizer32.Add( sbSizer6m, 0, wx.ALL|wx.EXPAND, 5 )

# -------------------------------------------------------------

        self.SetSizer( bSizer32 )
        self.Layout()
        bSizer32.Fit( self )

        # Connect Events
        self.Bind( wx.EVT_SIZE, self.OnSize )
        self.m_button12.Bind( wx.EVT_BUTTON, self.OnNameFormatHintClick )
        self.m_button112.Bind( wx.EVT_BUTTON, self.OnComponentBlacklistAdd )
        self.m_button212.Bind( wx.EVT_BUTTON, self.OnComponentBlacklistRemove )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnSize( self, event ):
        event.Skip()

    def OnNameFormatHintClick( self, event ):
        event.Skip()

    def OnComponentBlacklistAdd( self, event ):
        event.Skip()

    def OnComponentBlacklistRemove( self, event ):
        event.Skip()
