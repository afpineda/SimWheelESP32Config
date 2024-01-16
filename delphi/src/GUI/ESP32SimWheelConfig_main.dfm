object Form_main: TForm_main
  Left = 0
  Top = 0
  BorderIcons = [biSystemMenu, biMinimize]
  BorderStyle = bsSingle
  Caption = 'ESP32 Simwheel config'
  ClientHeight = 303
  ClientWidth = 462
  Color = clBtnFace
  Constraints.MinHeight = 350
  Constraints.MinWidth = 480
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  Position = poDefault
  OnCreate = FormCreate
  TextHeight = 13
  object PC_main: TPageControl
    Left = 0
    Top = 0
    Width = 462
    Height = 303
    ActivePage = Page_ButtonsMap
    Align = alClient
    TabOrder = 0
    OnChange = PC_mainChange
    object Page_Devices: TTabSheet
      Caption = 'Devices'
      object Btn_Scan: TButton
        Left = 0
        Top = 233
        Width = 454
        Height = 42
        Align = alBottom
        Caption = 'Scan'
        TabOrder = 0
        OnClick = Btn_ScanClick
      end
      object List_AvailableDevices: TListBox
        Left = 0
        Top = 0
        Width = 454
        Height = 233
        Style = lbVirtual
        Align = alClient
        BevelInner = bvNone
        BevelOuter = bvNone
        TabOrder = 1
        OnClick = List_AvailableDevicesClick
        OnData = List_AvailableDevicesData
        ExplicitTop = 82
        ExplicitHeight = 151
      end
    end
    object Page_Clutch: TTabSheet
      Caption = 'Clutch paddles'
      ImageIndex = 1
      object RG_ClutchMode: TRadioGroup
        Left = 0
        Top = 0
        Width = 454
        Height = 123
        Align = alTop
        Caption = 'Working mode'
        Items.Strings = (
          'F1-style clutch'
          'Analog axes'
          'ALT buttons'
          'Regular buttons')
        TabOrder = 0
        OnClick = RG_ClutchModeClick
      end
      object Panel_BitePoint: TPanel
        Left = 0
        Top = 123
        Width = 454
        Height = 152
        Align = alClient
        BevelOuter = bvNone
        Caption = 'Panel1'
        Constraints.MinHeight = 81
        ShowCaption = False
        TabOrder = 1
        object Lbl_BitePoint: TLabel
          Left = 0
          Top = 0
          Width = 454
          Height = 24
          Align = alTop
          Alignment = taCenter
          AutoSize = False
          Caption = 'Bite point'
          Layout = tlCenter
          ExplicitTop = 6
          ExplicitWidth = 386
        end
        object TB_BitePoint: TTrackBar
          Left = 0
          Top = 24
          Width = 454
          Height = 49
          Align = alTop
          Max = 254
          PageSize = 10
          Frequency = 10
          Position = 30
          PositionToolTip = ptTop
          SelStart = 50
          TabOrder = 0
          TickMarks = tmBoth
          OnChange = TB_BitePointChange
        end
        object ButtonGroup1: TButtonGroup
          Left = 496
          Top = 232
          Width = 73
          Height = 1
          Items = <>
          TabOrder = 1
        end
        object Btn_ClutchAutocal: TButton
          Left = 0
          Top = 110
          Width = 454
          Height = 42
          Align = alBottom
          Caption = 'Autocalibrate analog clutch paddles'
          TabOrder = 2
          OnClick = Btn_ClutchAutocalClick
        end
      end
    end
    object Page_AltButtons: TTabSheet
      Caption = 'ALT buttons'
      ImageIndex = 3
      object RG_AltButtonsMode: TRadioGroup
        Left = 0
        Top = 0
        Width = 454
        Height = 81
        Align = alTop
        Caption = 'Working mode'
        Items.Strings = (
          'ALT buttons'
          'Regular buttons')
        TabOrder = 0
        OnClick = RG_AltButtonsModeClick
      end
    end
    object Page_DPad: TTabSheet
      Caption = 'DPad'
      ImageIndex = 5
      object RG_DPadMode: TRadioGroup
        Left = 0
        Top = 0
        Width = 454
        Height = 81
        Align = alTop
        Caption = 'Working mode'
        Items.Strings = (
          'Navigation'
          'Regular buttons')
        TabOrder = 0
        OnClick = RG_DPadModeClick
      end
    end
    object Page_battery: TTabSheet
      Caption = 'Battery'
      ImageIndex = 2
      object Lbl_SocHeader: TLabel
        Left = 0
        Top = 0
        Width = 454
        Height = 13
        Align = alTop
        Alignment = taCenter
        AutoSize = False
        Caption = 'Last state of charge'
        ExplicitTop = 19
        ExplicitWidth = 386
      end
      object Lbl_SOC: TLabel
        Left = 0
        Top = 13
        Width = 454
        Height = 60
        Align = alTop
        Alignment = taCenter
        AutoSize = False
        Caption = '100%'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -21
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        Layout = tlCenter
        ExplicitTop = 19
        ExplicitWidth = 326
      end
      object Btn_AutocalBattery: TButton
        Left = 0
        Top = 233
        Width = 454
        Height = 42
        Align = alBottom
        Caption = 'Autocalibrate battery'
        TabOrder = 0
        OnClick = Btn_AutocalBatteryClick
      end
    end
    object Page_Presets: TTabSheet
      Caption = 'Presets'
      ImageIndex = 4
      object Btn_LoadFromFile: TButton
        Left = 0
        Top = 33
        Width = 454
        Height = 33
        Align = alTop
        Caption = 'Load from file'
        TabOrder = 0
        OnClick = Btn_LoadFromFileClick
      end
      object Btn_SaveToFile: TButton
        Left = 0
        Top = 0
        Width = 454
        Height = 33
        Align = alTop
        Caption = 'Save to file'
        TabOrder = 1
        OnClick = Btn_SaveToFileClick
      end
    end
    object Page_ButtonsMap: TTabSheet
      Caption = 'Buttons map'
      ImageIndex = 6
      DesignSize = (
        454
        275)
      object LV_ButtonsMap: TListView
        Left = 16
        Top = 47
        Width = 345
        Height = 214
        Anchors = [akLeft, akTop, akRight, akBottom]
        Columns = <
          item
            Caption = 'Firmware Button'
            MinWidth = 100
            Width = 100
          end
          item
            Caption = 'HID button'
            MinWidth = 100
            Width = 100
          end
          item
            Caption = 'HID button (alt mode)'
            MinWidth = 100
            Width = 120
          end>
        ColumnClick = False
        Items.ItemData = {
          05340000000100000000000000FFFFFFFFFFFFFFFF02000000FFFFFFFF000000
          000474006500730074000131008020B82B013200A003B82BFFFFFFFF}
        ReadOnly = True
        RowSelect = True
        TabOrder = 0
        ViewStyle = vsReport
        OnSelectItem = LV_ButtonsMapSelectItem
      end
      object Btn_MapRefresh: TButton
        Left = 367
        Top = 47
        Width = 75
        Height = 25
        Anchors = [akTop, akRight]
        Caption = 'Refresh'
        TabOrder = 1
        OnClick = OnRefreshButtonsMap
      end
      object Btn_SaveMap: TButton
        Left = 367
        Top = 78
        Width = 75
        Height = 25
        Anchors = [akTop, akRight]
        Caption = 'Save'
        TabOrder = 2
        OnClick = Btn_SaveMapClick
      end
      object Panel_EditMap: TPanel
        Left = 0
        Top = 0
        Width = 454
        Height = 41
        Align = alTop
        BevelEdges = []
        BevelOuter = bvNone
        Caption = 'Panel1'
        ShowCaption = False
        TabOrder = 3
        DesignSize = (
          454
          41)
        object Lbl_MapNoAlt: TLabel
          Left = 142
          Top = 10
          Width = 25
          Height = 16
          Caption = 'HID:'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -13
          Font.Name = 'Tahoma'
          Font.Style = []
          ParentFont = False
        end
        object Lbl_MapAlt: TLabel
          Left = 248
          Top = 10
          Width = 61
          Height = 16
          Caption = 'HID (ALT):'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -13
          Font.Name = 'Tahoma'
          Font.Style = []
          ParentFont = False
        end
        object Lbl_MapFirmware: TLabel
          Left = 22
          Top = 12
          Width = 60
          Height = 16
          Caption = 'Firmware:'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -13
          Font.Name = 'Tahoma'
          Font.Style = []
          ParentFont = False
        end
        object Lbl_MapSelected: TLabel
          Left = 88
          Top = 8
          Width = 18
          Height = 21
          Caption = '00'
          Font.Charset = DEFAULT_CHARSET
          Font.Color = clWindowText
          Font.Height = -17
          Font.Name = 'Tahoma'
          Font.Style = []
          ParentFont = False
        end
        object Edit_MapNoAlt: TSpinEdit
          Left = 170
          Top = 8
          Width = 47
          Height = 22
          AutoSize = False
          MaxValue = 127
          MinValue = 0
          TabOrder = 0
          Value = 100
        end
        object Edit_MapAlt: TSpinEdit
          Left = 312
          Top = 8
          Width = 49
          Height = 22
          AutoSize = False
          MaxValue = 127
          MinValue = 0
          TabOrder = 1
          Value = 100
        end
        object Btn_MapApply: TButton
          Left = 367
          Top = 8
          Width = 75
          Height = 25
          Anchors = [akTop, akRight]
          Caption = 'Apply'
          TabOrder = 2
          OnClick = Btn_MapApplyClick
        end
      end
      object Btn_MapDefaults: TButton
        Left = 367
        Top = 238
        Width = 75
        Height = 25
        Anchors = [akLeft, akRight, akBottom]
        Caption = 'Defaults'
        TabOrder = 4
        OnClick = Btn_MapDefaultsClick
      end
    end
  end
  object Dlg_FileOpen: TFileOpenDialog
    DefaultExtension = '*.swh'
    FavoriteLinks = <>
    FileTypes = <
      item
        DisplayName = 'Sim wheel presets'
        FileMask = '*.swh'
      end>
    Options = [fdoStrictFileTypes, fdoPathMustExist, fdoFileMustExist, fdoNoTestFileCreate, fdoDontAddToRecent]
    Title = 'Load from file'
    Left = 65529
    Top = 179
  end
  object Dlg_FileSave: TFileSaveDialog
    DefaultExtension = '*.swh'
    FavoriteLinks = <>
    FileTypes = <
      item
        DisplayName = 'Sim wheel preset'
        FileMask = '*.swh'
      end>
    Options = [fdoOverWritePrompt, fdoStrictFileTypes, fdoPathMustExist, fdoCreatePrompt, fdoNoReadOnlyReturn, fdoDontAddToRecent]
    Title = 'Save to file'
    Left = 65534
    Top = 131
  end
end
