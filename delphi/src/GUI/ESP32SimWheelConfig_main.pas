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
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants,
  System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, OpenSourceSimWheelESP32,
  Vcl.StdCtrls, Vcl.ExtCtrls, Vcl.ButtonGroup;

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
    Lbl_DeviceReady: TLabel;
    Lbl_DeviceNotReady: TLabel;
    Lbl_TooManyDevices: TStaticText;
    Btn_LoadFromFile: TButton;
    Btn_SaveToFile: TButton;
    Dlg_FileOpen: TFileOpenDialog;
    Dlg_FileSave: TFileSaveDialog;
    Page_DPad: TTabSheet;
    RG_DPadMode: TRadioGroup;
    Page_ButtonsMap: TTabSheet;
    LV_ButtonsMap: TListView;
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
  private
    { Private declarations }
    SimWheel: TSimWheel;
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
  Lbl_DeviceReady.Visible := false;
  Lbl_DeviceNotReady.Visible := true;
  Lbl_TooManyDevices.Visible := false;
  PC_main.ActivePage := Page_Devices;
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
      RG_ClutchMode.ItemIndex := integer(SimWheel.ClutchMode);
      TB_BitePoint.Position := integer(SimWheel.BitePoint);
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
  count: integer;
  lastPath: string;
begin
  FreeAndNil(SimWheel);
  count := 0;
  try
    TSimWheel.GetDevices(
      procedure(devicePath: string; ID: UInt64)
      begin
        inc(count);
        lastPath := devicePath;
      end);
    if (count = 1) then
      SimWheel := TSimWheel.Create(lastPath);
  except
  end;
  Lbl_DeviceReady.Visible := (SimWheel <> nil);
  Lbl_DeviceNotReady.Visible := not Lbl_DeviceReady.Visible;
  Lbl_TooManyDevices.Visible := (count > 1);
  if (SimWheel <> nil) then
    OnDeviceConnected
  else
    OnDeviceNotConnected;
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
  SimWheel := nil;
  Page_Devices.TabVisible := true;
  PC_main.ActivePageIndex := Page_Devices.PageIndex;
  ScanDevices;
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
    begin
      SimWheel.ForceBatteryAutocalibration;
      RefreshDeviceState;
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
  auxBool: boolean;
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
        strm.Read(cfg.DPadMode, sizeof(cfg.DPADMode));
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

end.
