object Form_main: TForm_main
  Left = 0
  Top = 0
  BorderIcons = [biSystemMenu, biMinimize]
  BorderStyle = bsSingle
  Caption = 'ESP32 Simwheel config'
  ClientHeight = 344
  ClientWidth = 513
  Color = clBtnFace
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
    Width = 513
    Height = 344
    ActivePage = Page_Presets
    Align = alClient
    TabOrder = 0
    OnChange = PC_mainChange
    object Page_Devices: TTabSheet
      Caption = 'Devices'
      object Lbl_DeviceReady: TLabel
        Left = 0
        Top = 0
        Width = 505
        Height = 41
        Align = alTop
        Alignment = taCenter
        AutoSize = False
        Caption = 'Ready'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clGreen
        Font.Height = -16
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        Layout = tlCenter
        ExplicitTop = -6
        ExplicitWidth = 386
      end
      object Lbl_DeviceNotReady: TLabel
        Left = 0
        Top = 41
        Width = 505
        Height = 41
        Align = alTop
        Alignment = taCenter
        AutoSize = False
        Caption = 'Not Ready'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clRed
        Font.Height = -16
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        Layout = tlCenter
        ExplicitTop = 8
        ExplicitWidth = 386
      end
      object Btn_Scan: TButton
        Left = 0
        Top = 274
        Width = 505
        Height = 42
        Align = alBottom
        Caption = 'Scan'
        TabOrder = 0
        OnClick = Btn_ScanClick
      end
      object Lbl_TooManyDevices: TStaticText
        Left = 0
        Top = 82
        Width = 505
        Height = 71
        Align = alTop
        Alignment = taCenter
        AutoSize = False
        Caption = 
          'Two or more devices were found. Only one device is supported. Tu' +
          'rn off unneeded devices then scan again.'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clWindowText
        Font.Height = -16
        Font.Name = 'Tahoma'
        Font.Style = []
        ParentFont = False
        TabOrder = 1
      end
    end
    object Page_Clutch: TTabSheet
      Caption = 'Clutch paddles'
      ImageIndex = 1
      object RG_ClutchMode: TRadioGroup
        Left = 0
        Top = 0
        Width = 505
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
        ExplicitWidth = 326
      end
      object Panel_BitePoint: TPanel
        Left = 0
        Top = 123
        Width = 505
        Height = 193
        Align = alClient
        BevelOuter = bvNone
        Caption = 'Panel1'
        Constraints.MinHeight = 81
        ShowCaption = False
        TabOrder = 1
        ExplicitWidth = 326
        ExplicitHeight = 120
        object Lbl_BitePoint: TLabel
          Left = 0
          Top = 0
          Width = 505
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
          Width = 505
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
          ExplicitWidth = 326
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
          Top = 151
          Width = 505
          Height = 42
          Align = alBottom
          Caption = 'Autocalibrate analog clutch paddles'
          TabOrder = 2
          OnClick = Btn_ClutchAutocalClick
          ExplicitTop = 78
          ExplicitWidth = 326
        end
      end
    end
    object Page_AltButtons: TTabSheet
      Caption = 'ALT buttons'
      ImageIndex = 3
      object RG_AltButtonsMode: TRadioGroup
        Left = 0
        Top = 0
        Width = 505
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
        Width = 505
        Height = 81
        Align = alTop
        Caption = 'Working mode'
        Items.Strings = (
          'Navigation'
          'Regular buttons')
        TabOrder = 0
        OnClick = RG_DPadModeClick
        ExplicitTop = 8
      end
    end
    object Page_battery: TTabSheet
      Caption = 'Battery'
      ImageIndex = 2
      object Lbl_SocHeader: TLabel
        Left = 0
        Top = 0
        Width = 505
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
        Width = 505
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
        Top = 274
        Width = 505
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
        Width = 505
        Height = 33
        Align = alTop
        Caption = 'Load from file'
        TabOrder = 0
        OnClick = Btn_LoadFromFileClick
      end
      object Btn_SaveToFile: TButton
        Left = 0
        Top = 0
        Width = 505
        Height = 33
        Align = alTop
        Caption = 'Save to file'
        TabOrder = 1
        OnClick = Btn_SaveToFileClick
        ExplicitTop = -6
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
    Left = 199
    Top = 220
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
    Left = 267
    Top = 220
  end
end
