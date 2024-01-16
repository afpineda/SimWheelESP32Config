{ ****************************************************************************
  * @author Ángel Fernández Pineda. Madrid. Spain.
  * @date 2023-01-17
  * @brief Configuration app for ESP32-based open source sim wheels
  *
  * @copyright Creative Commons Attribution 4.0 International (CC BY 4.0)
  *
  **************************************************************************** }

unit ESP32SimWheelConfig_main;

interface

uses
  System.Generics.Collections,
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants,
  System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, OpenSourceSimWheelESP32,
  Vcl.StdCtrls, Vcl.ExtCtrls, Vcl.ButtonGroup, Vcl.Samples.Spin;

type
  TForm_main = class(TForm)
    PC_main: TPageControl;
    Page_Devices: TTabSheet;
    Page_Clutch: TTabSheet;
    Page_battery: TTabSheet;
    Page_AltButtons: TTabSheet;
    Page_Presets: TTabSheet;
    RG_ClutchMode: TRadioGroup;
    Panel_BitePoint: TPanel;
    Lbl_BitePoint: TLabel;
    TB_BitePoint: TTrackBar;
    ButtonGroup1: TButtonGroup;
    Btn_ClutchAutocal: TButton;
    RG_AltButtonsMode: TRadioGroup;
    Btn_AutocalBattery: TButton;
    Lbl_SocHeader: TLabel;
    Lbl_SOC: TLabel;
    Btn_Scan: TButton;
    Btn_LoadFromFile: TButton;
    Btn_SaveToFile: TButton;
    Dlg_FileOpen: TFileOpenDialog;
    Dlg_FileSave: TFileSaveDialog;
    Page_DPad: TTabSheet;
    RG_DPadMode: TRadioGroup;
    Page_ButtonsMap: TTabSheet;
    LV_ButtonsMap: TListView;
    Btn_MapRefresh: TButton;
    Btn_SaveMap: TButton;
    Panel_EditMap: TPanel;
    Edit_MapNoAlt: TSpinEdit;
    Edit_MapAlt: TSpinEdit;
    Lbl_MapNoAlt: TLabel;
    Lbl_MapAlt: TLabel;
    Btn_MapApply: TButton;
    Lbl_MapFirmware: TLabel;
    Lbl_MapSelected: TLabel;
    Btn_MapDefaults: TButton;
    List_AvailableDevices: TListBox;
    procedure FormCreate(Sender: TObject);
    procedure PC_mainChange(Sender: TObject);
    procedure RG_AltButtonsModeClick(Sender: TObject);
    procedure RG_ClutchModeClick(Sender: TObject);
    procedure TB_BitePointChange(Sender: TObject);
    procedure Btn_ClutchAutocalClick(Sender: TObject);
    procedure Btn_AutocalBatteryClick(Sender: TObject);
    procedure Btn_ScanClick(Sender: TObject);
    procedure Btn_SaveToFileClick(Sender: TObject);
    procedure Btn_LoadFromFileClick(Sender: TObject);
    procedure RG_DPadModeClick(Sender: TObject);
    procedure OnRefreshButtonsMap(Sender: TObject);
    procedure LV_ButtonsMapSelectItem(Sender: TObject; Item: TListItem;
      Selected: Boolean);
    procedure Btn_MapApplyClick(Sender: TObject);
    procedure Btn_SaveMapClick(Sender: TObject);
    procedure Btn_MapDefaultsClick(Sender: TObject);
    procedure List_AvailableDevicesData(Control: TWinControl; Index: Integer;
      var Data: string);
    procedure List_AvailableDevicesClick(Sender: TObject);
  private
    { Private declarations }
    SimWheel: TSimWheel;
    AvailableDevices: TList<TSimWheel>;
    procedure OnDeviceNotConnected;
    procedure OnDeviceConnected;
    procedure RefreshDeviceState;
    procedure ScanDevices;
    procedure OnDeviceError;
  public
    { Public declarations }
  end;

var
  Form_main: TForm_main;

implementation

{$R *.dfm}
// ---------------------------------------------------------------------------
// Auxiliary methods
// ---------------------------------------------------------------------------

procedure TForm_main.OnDeviceNotConnected;
begin
  Page_Clutch.TabVisible := false;
  Page_battery.TabVisible := false;
  Page_AltButtons.TabVisible := false;
  Page_Presets.TabVisible := false;
  Page_DPad.TabVisible := false;
  Page_ButtonsMap.TabVisible := false;
  PC_main.ActivePage := Page_Devices;
  LV_ButtonsMap.Selected := nil;
  LV_ButtonsMap.OnSelectItem(LV_ButtonsMap, nil, false);
  ScanDevices;
end;

procedure TForm_main.OnDeviceConnected;
begin
  if (SimWheel <> nil) then
  begin
    RefreshDeviceState;
    Page_Clutch.TabVisible := SimWheel.HasCapability(CAP_CLUTCH_BUTTON) or
      SimWheel.HasCapability(CAP_CLUTCH_ANALOG);
    Page_AltButtons.TabVisible := SimWheel.HasCapability(CAP_ALT);
    Page_battery.TabVisible := SimWheel.HasCapability(CAP_BATTERY);
    Page_DPad.TabVisible := SimWheel.HasCapability(CAP_DPAD);
    Page_Presets.TabVisible := Page_Clutch.TabVisible or
      Page_AltButtons.TabVisible or Page_DPad.TabVisible;
    Page_ButtonsMap.TabVisible := true;
    LV_ButtonsMap.Clear;
    LV_ButtonsMap.OnSelectItem(LV_ButtonsMap, nil, false);
    Btn_AutocalBattery.Visible := not SimWheel.HasCapability
      (CAP_BATTERY_CALIBRATION_AVAILABLE);
    Btn_ClutchAutocal.Visible := SimWheel.HasCapability(CAP_CLUTCH_ANALOG);

    if (Page_Clutch.TabVisible) then
      PC_main.ActivePageIndex := Page_Clutch.PageIndex
    else if (Page_AltButtons.TabVisible) then
      PC_main.ActivePageIndex := Page_AltButtons.PageIndex
    else if (Page_DPad.TabVisible) then
      PC_main.ActivePageIndex := Page_DPad.PageIndex
    else if (Page_battery.TabVisible) then
      PC_main.ActivePageIndex := Page_battery.PageIndex;
  end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.RefreshDeviceState;
begin
  if (SimWheel <> nil) then
    try
      SimWheel.Update;
      RG_ClutchMode.ItemIndex := Integer(SimWheel.ClutchMode);
      TB_BitePoint.Position := Integer(SimWheel.BitePoint);
      TB_BitePoint.SelStart := 0;
      TB_BitePoint.SelEnd := TB_BitePoint.Position;
      if (SimWheel.AltMode) then
        RG_AltButtonsMode.ItemIndex := 0
      else
        RG_AltButtonsMode.ItemIndex := 1;
      if (SimWheel.DPadMode) then
        RG_DPadMode.ItemIndex := 0
      else
        RG_DPadMode.ItemIndex := 1;
      Lbl_SOC.Caption := Format('%d%%', [SimWheel.LastBatteryLevel]);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.ScanDevices;
var
  i: Integer;
begin
  PC_main.ActivePage := Page_Devices;
  for i := 0 to AvailableDevices.Count - 1 do
    FreeAndNil(AvailableDevices[i]);
  AvailableDevices.Clear;

  SimWheel := nil;
  try
    TSimWheel.GetDevices(
      procedure(devicePath: string; ID: UInt64)
      begin
        AvailableDevices.Add(TSimWheel.Create(devicePath));
      end);
  except
  end;
  List_AvailableDevices.Count := AvailableDevices.Count;
  if (AvailableDevices.Count = 1) then
  begin
    List_AvailableDevices.ItemIndex := 0;
    List_AvailableDevices.OnClick(List_AvailableDevices);
  end;
end;

procedure TForm_main.OnDeviceError;
begin
  // Application.MessageBox('Device no longer present', 'Error',
  // MB_ICONSTOP or MB_OK);
  // FreeAndNil(SimWheel);
  OnDeviceNotConnected;
end;

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

procedure TForm_main.FormCreate(Sender: TObject);
begin
  AvailableDevices := TList<TSimWheel>.Create;
  SimWheel := nil;
  Page_Devices.TabVisible := true;
  PC_main.ActivePageIndex := Page_Devices.PageIndex;
  LV_ButtonsMap.Clear;
  OnDeviceNotConnected;
end;

// ---------------------------------------------------------------------------
// Page control
// ---------------------------------------------------------------------------

procedure TForm_main.PC_mainChange(Sender: TObject);
begin
  RefreshDeviceState;
end;

// ---------------------------------------------------------------------------
// Page: ALT buttons
// ---------------------------------------------------------------------------

procedure TForm_main.RG_AltButtonsModeClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.AltMode := (RG_AltButtonsMode.ItemIndex = 0);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

// ---------------------------------------------------------------------------
// Page: DPAD
// ---------------------------------------------------------------------------

procedure TForm_main.RG_DPadModeClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.DPadMode := (RG_DPadMode.ItemIndex = 0);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

// ---------------------------------------------------------------------------
// Page: Clutch paddles
// ---------------------------------------------------------------------------

procedure TForm_main.RG_ClutchModeClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.ClutchMode := TSimWheel.TClutchMode(RG_ClutchMode.ItemIndex);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.TB_BitePointChange(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.BitePoint := byte(TB_BitePoint.Position);
      RefreshDeviceState;
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.Btn_ClutchAutocalClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.ForceAnalogAxesCalibration;
      Application.MessageBox
        ('Move both clutch paddles from end to end for autocalibration',
        'Notice', MB_OK or MB_ICONINFORMATION);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.Btn_ScanClick(Sender: TObject);
begin
  ScanDevices;
end;

// ---------------------------------------------------------------------------
// Page: Battery
// ---------------------------------------------------------------------------

procedure TForm_main.Btn_AutocalBatteryClick(Sender: TObject);
begin
  if (Application.MessageBox
    ('Ensure battery is at full charge before continuing', 'Confirm',
    MB_OKCANCEL or MB_ICONWARNING) = IDOK) then
  begin
    if (SimWheel <> nil) then
      try
        SimWheel.ForceBatteryAutocalibration;
        RefreshDeviceState;
      except
        OnDeviceError;
      end
    else
      OnDeviceNotConnected;
  end;
end;

// ---------------------------------------------------------------------------
// Page: Load/Save
// ---------------------------------------------------------------------------

procedure TForm_main.Btn_SaveToFileClick(Sender: TObject);
var
  strm: TFileStream;
  auxBool: Boolean;
  auxUint8: UInt8;
begin
  if (SimWheel = nil) then
  begin
    OnDeviceNotConnected;
    exit;
  end;

  if (Dlg_FileSave.Execute) then
    try
      strm := TFileStream.Create(Dlg_FileSave.FileName, fmCreate);
      try
        auxUint8 := UInt8(SimWheel.ClutchMode);
        strm.Write(auxUint8, sizeof(auxUint8));
        strm.Write(SimWheel.BitePoint, sizeof(SimWheel.BitePoint));
        auxBool := SimWheel.AltMode;
        strm.Write(auxBool, sizeof(auxBool));
        auxBool := SimWheel.DPadMode;
        strm.Write(auxBool, sizeof(auxBool));
      finally
        strm.Free;
      end;
    except
      Application.MessageBox('Unable to save file', 'Error',
        MB_OK or MB_ICONSTOP);
    end;
end;

procedure TForm_main.Btn_LoadFromFileClick(Sender: TObject);
var
  strm: TFileStream;
  cfg: TSimWheel.TConfigReport;
begin
  if (SimWheel = nil) then
  begin
    OnDeviceNotConnected;
    exit;
  end;

  if (Dlg_FileOpen.Execute) then
    try
      strm := TFileStream.Create(Dlg_FileOpen.FileName, fmOpenRead);
      try
        strm.Read(cfg.ClutchMode, sizeof(cfg.ClutchMode));
        strm.Read(cfg.BitePoint, sizeof(cfg.BitePoint));
        strm.Read(cfg.AltMode, sizeof(cfg.AltMode));
        strm.Read(cfg.DPadMode, sizeof(cfg.DPadMode));
        cfg.SimpleCommand := $FF;
        SimWheel.SetConfig(cfg);
      finally
        strm.Free;
      end;
    except
      Application.MessageBox('Unable to load file', 'Error',
        MB_OK or MB_ICONSTOP);
    end;
  RefreshDeviceState;
end;

// ---------------------------------------------------------------------------
// Page: Buttons map
// ---------------------------------------------------------------------------

procedure TForm_main.OnRefreshButtonsMap(Sender: TObject);
var
  success: Boolean;
  Item: TListItem;
begin
  if (SimWheel <> nil) then
    try
      LV_ButtonsMap.Clear;
      success := SimWheel.GetButtonsMap(
        procedure(raw: TFirmwareButton; noAlt, alt: TUserButton)
        begin
          Item := LV_ButtonsMap.Items.Add;
          Item.Caption := IntToStr(raw);
          Item.SubItems.Add(IntToStr(noAlt));
          Item.SubItems.Add(IntToStr(alt));
        end);
      if (not success) then
      begin
        LV_ButtonsMap.Clear();
        Application.MessageBox('Unable to get buttons map. Try later.',
          'Failure', MB_OK or MB_ICONSTOP);
      end;
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.List_AvailableDevicesClick(Sender: TObject);
begin
  if (List_AvailableDevices.ItemIndex >= 0) then
  begin
    SimWheel := AvailableDevices[List_AvailableDevices.ItemIndex];
  end
  else
    SimWheel := nil;
  if (SimWheel <> nil) then
    OnDeviceConnected
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.List_AvailableDevicesData(Control: TWinControl;
Index: Integer; var Data: string);
begin
  if (Index >= 0) and (Index < AvailableDevices.Count) then
    Data := AvailableDevices[Index].Name;
end;

procedure TForm_main.LV_ButtonsMapSelectItem(Sender: TObject; Item: TListItem;
Selected: Boolean);
begin
  Panel_EditMap.Enabled := (Item <> nil);
  if (Panel_EditMap.Enabled) then
  begin
    Lbl_MapSelected.Caption := Item.Caption;
    Edit_MapNoAlt.Value := StrToIntDef(Item.SubItems[0], 0);
    Edit_MapAlt.Value := StrToIntDef(Item.SubItems[1], 0);
    Edit_MapNoAlt.Visible := true;
    Edit_MapAlt.Visible := true;
    Btn_MapApply.Enabled := true;
  end
  else
  begin
    Lbl_MapSelected.Caption := '';
    Edit_MapNoAlt.Visible := false;
    Edit_MapAlt.Visible := false;
    Btn_MapApply.Enabled := false;
  end;
end;

procedure TForm_main.Btn_MapApplyClick(Sender: TObject);
var
  raw: UInt8;
  noAlt: TUserButton;
  alt: TUserButton;
begin
  raw := StrToIntDef(Lbl_MapSelected.Caption, $FF);
  if ((Edit_MapNoAlt.Value < low(TUserButton)) or
    (Edit_MapNoAlt.Value > high(TUserButton))) then
    raw := $FF;
  if ((Edit_MapAlt.Value < low(TUserButton)) or
    (Edit_MapAlt.Value > high(TUserButton))) then
    raw := $FF;
  if (raw = $FF) then
    exit;

  alt := Edit_MapAlt.Value;
  noAlt := Edit_MapNoAlt.Value;

  if (LV_ButtonsMap.Selected <> nil) and (SimWheel <> nil) then
    try
      SimWheel.SetButtonMap(TFirmwareButton(raw), noAlt, alt);
      LV_ButtonsMap.Selected.SubItems[0] := IntToStr(noAlt);
      LV_ButtonsMap.Selected.SubItems[1] := IntToStr(alt);
    except
      OnDeviceError;
    end
  else if (SimWheel = nil) then
    OnDeviceNotConnected;
end;

procedure TForm_main.Btn_MapDefaultsClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.ResetButtonsMap;
      OnRefreshButtonsMap(Form_main);
    except
      OnDeviceError;
    end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.Btn_SaveMapClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
    try
      SimWheel.SaveNow
    except
      OnDeviceNotConnected;
    end
  else
    OnDeviceNotConnected;
end;

end.
