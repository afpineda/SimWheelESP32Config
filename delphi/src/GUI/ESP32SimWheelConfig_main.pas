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
    procedure FormCreate(Sender: TObject);
    procedure PC_mainChange(Sender: TObject);
    procedure RG_AltButtonsModeClick(Sender: TObject);
    procedure RG_ClutchModeClick(Sender: TObject);
    procedure TB_BitePointChange(Sender: TObject);
    procedure Btn_ClutchAutocalClick(Sender: TObject);
    procedure Btn_AutocalBatteryClick(Sender: TObject);
    procedure Btn_ScanClick(Sender: TObject);
  private
    { Private declarations }
    SimWheel: TSimWheel;
    procedure OnDeviceNotConnected;
    procedure OnDeviceConnected;
    procedure RefreshDeviceState;
    procedure ScanDevices;
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
    Btn_AutocalBattery.Visible := not SimWheel.HasCapability
      (CAP_BATTERY_CALIBRATION_AVAILABLE);
    Btn_ClutchAutocal.Visible := SimWheel.HasCapability(CAP_CLUTCH_ANALOG);

    if (Page_Clutch.TabVisible) then
      PC_main.ActivePageIndex := Page_Clutch.PageIndex
    else if (Page_AltButtons.TabVisible) then
      PC_main.ActivePageIndex := Page_AltButtons.PageIndex
    else if (Page_battery.TabVisible) then
      PC_main.ActivePageIndex := Page_battery.PageIndex;
  end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.RefreshDeviceState;
begin
  if (SimWheel <> nil) then
  begin
    SimWheel.Update;
    RG_ClutchMode.ItemIndex := integer(SimWheel.ClutchMode);
    TB_BitePoint.Position := integer(SimWheel.BitePoint);
    TB_BitePoint.SelEnd := TB_BitePoint.Position;
    if (SimWheel.AltMode) then
      RG_AltButtonsMode.ItemIndex := 0
    else
      RG_AltButtonsMode.ItemIndex := 1;
    Lbl_SOC.Caption := Format('%d%%', [SimWheel.LastBatteryLevel]);
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
      procedure(devicePath: string)
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
  begin
    SimWheel.AltMode := (RG_AltButtonsMode.ItemIndex = 0);
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
  begin
    SimWheel.ClutchMode := TSimWheel.TClutchMode(RG_ClutchMode.ItemIndex);
  end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.TB_BitePointChange(Sender: TObject);
begin
  if (SimWheel <> nil) then
  begin
    SimWheel.BitePoint := byte(TB_BitePoint.Position);
    RefreshDeviceState;
  end
  else
    OnDeviceNotConnected;
end;

procedure TForm_main.Btn_ClutchAutocalClick(Sender: TObject);
begin
  if (SimWheel <> nil) then
  begin
    SimWheel.ForceAnalogAxesCalibration;
    Application.MessageBox
      ('Move both clutch paddles from end to end for autocalibration', 'Notice',
      MB_OK or MB_ICONINFORMATION);
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

end.
