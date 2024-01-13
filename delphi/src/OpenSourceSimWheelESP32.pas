{ ****************************************************************************
  * @author Ángel Fernández Pineda. Madrid. Spain.
  * @date 2023-01-17
  * @brief Configuration app for ESP32-based open source sim wheels
  *
  * @copyright Creative Commons Attribution 4.0 International (CC BY 4.0)
  *
  **************************************************************************** }

unit OpenSourceSimWheelESP32;

interface

uses
  System.SysUtils;

{$Z1}

type
  // TSimWheel = class;
  // TSimWheelList = TList<TSimWheel>;
  TSimWheelDiscoveryProc = TProc<string, Uint64>;

  TSimWheel = class
  public type
    TCapabilities = (CAP_CLUTCH_BUTTON = 0, CAP_CLUTCH_ANALOG, CAP_ALT,
      CAP_DPAD, CAP_BATTERY, CAP_BATTERY_CALIBRATION_AVAILABLE);
    TClutchMode = (CF_CLUTCH = 0, CF_AXIS, CF_ALT, CF_BUTTON);

    TConfigReport = packed record
      ReportID: UInt8;
      ClutchMode: UInt8;
      AltMode: UInt8;
      BitePoint: UInt8;
      SimpleCommand: UInt8;
      DPadMode: UInt8;
    end;

    TButtonsMapReport = packed record
      RawButton: UInt8;
      UserButton: UInt8;
      UserButtonAlt: UInt8;
    end;

    PConfigReport = ^TConfigReport;
    PButtonMapReport = TButtonsMapReport;

  protected
    FdevicePath: string;
    Fcapabilities: UInt16;
    FConfig: TConfigReport;
    FMap: TButtonsMapReport;
    FdataMajorVersion: UInt16;
    FdataMinorVersion: UInt16;
    FInputReportSize: integer;
    FFeatureReportSize: integer;
    FOutputReportSize: integer;
    FDeviceID: Uint64;
    FHandle: THandle;

    function GetClutchMode: TSimWheel.TClutchMode;
    function GetAltMode: boolean;
    function GetDPADMode: boolean;
    procedure SetAltMode(const aMode: boolean);
    procedure SetDPADMode(const aMode: boolean);
    procedure SetClutchMode(const aMode: TSimWheel.TClutchMode);
    procedure SetBitePoint(const BitePoint: UInt8);

  protected
    procedure ClearConfigReport(const pReport: PConfigReport);
    procedure SendConfigReport(const pReport: PConfigReport);

  public

    class procedure GetDevices(onDiscovery: TSimWheelDiscoveryProc);

  private
    // constructor Create(const handle: THandle; const devicePath: string;
    // const majorVersion: UInt16; const minorVersion: UInt16;
    // const flags: UInt16; const inputReportSize, outputReportSize,
    // featureReportSize: integer); overload;

  public
    constructor Create(const devicePath: string); overload;
    destructor Destroy; override;

    procedure ForceAnalogAxesCalibration;
    procedure ForceBatteryAutocalibration;
    function HasCapability(aCap: TSimWheel.TCapabilities): boolean;
    function Update: boolean;
    procedure ResetButtonsMap;
    procedure SaveNow;
    procedure SetConfig(const [Ref] aConfig: TConfigReport);

    property AltMode: boolean read GetAltMode write SetAltMode;
    property BitePoint: UInt8 read FConfig.BitePoint write SetBitePoint;
    property Capabilities: UInt16 read Fcapabilities;
    property ClutchMode: TSimWheel.TClutchMode read GetClutchMode
      write SetClutchMode;
    property DataMajorVersion: UInt16 read FdataMajorVersion;
    property DataMinorVersion: UInt16 read FdataMinorVersion;
    property DeviceID: Uint64 read FDeviceID;
    property devicePath: string read FdevicePath;
    property DPadMode: boolean read GetDPADMode write SetDPADMode;
    property LastBatteryLevel: UInt8 read FConfig.SimpleCommand;

  end;

implementation

// --------------------------------------------------------------------------

uses
  // System.SysUtils,
  Winapi.Windows,
  Winapi.Hid,
  Winapi.SetupApi;

const
  EXPECTED_INPUT_REPORT_SIZE = 21;
  // EXPECTED_OUTPUT_REPORT_SIZE = 0;

const
  RID_INPUT_GAMEPAD = $01;
  RID_FEATURE_CAPABILITIES = $02;
  RID_FEATURE_CONFIG = $03;
  RID_FEATURE_BUTTONS_MAP = $04;

const
  CONTROLLER_TYPE = $05;

const
  DATA_MAJOR_VERSION = 1;
  DATA_MINOR_VERSION = 1;

const
  MAGIC_NUMBER = $BF51;

const
  CMD_AXIS_RECALIBRATE = 1;
  CMD_BATT_RECALIBRATE = 2;
  CMD_RESET_BUTTONS_MAP = 3;
  CMD_SAVE_NOW = 4;

type
  TCapabilitiesReport = packed record
    ReportID: UInt8;
    magicNumber: UInt16;
    majorVersion: UInt16;
    minorVersion: UInt16;
    flags: UInt16;
    DeviceID: Uint64;
  end;

  PCapabilitiesReport = ^TCapabilitiesReport;

resourcestring
  MSG_INVALID_PATH = 'Not a valid path to a simwheel device';

  // --------------------------------------------------------------------------
  // class methods
  // --------------------------------------------------------------------------

  {
    Check if the HID capabilites suits that of an open simwheel
  }
function CheckDevCaps(const pDevCaps: PHIDCaps): boolean;
begin
  Result := (pDevCaps^.UsagePage = 1) and (pDevCaps^.Usage = CONTROLLER_TYPE)
    and (pDevCaps^.InputReportByteLength >= EXPECTED_INPUT_REPORT_SIZE) and
  // (capabilities.OutputReportByteLength >=
  // EXPECTED_OUTPUT_REPORT_SIZE) and
    (pDevCaps^.FeatureReportByteLength >= sizeof(TCapabilitiesReport)) and
    (pDevCaps^.FeatureReportByteLength >= sizeof(TSimWheel.TConfigReport)) and
    (pDevCaps^.FeatureReportByteLength >= sizeof(TSimWheel.TButtonsMapReport));
end;

// --------------------------------------------------------------------------

{
  Inspect report ID 2 (capabilites) in order to discard a sim wheel with
  no user settings
}
function CheckCapabilitiesReport(const pCaps: PCapabilitiesReport): boolean;

  function hasNoCap(const aCap: TSimWheel.TCapabilities; const flags: UInt16)
    : boolean; inline;
  begin
    Result := (flags and (1 shl UInt16(aCap))) = 0;
  end;

begin
  Result := (pCaps^.magicNumber = MAGIC_NUMBER) and
    (pCaps^.majorVersion = DATA_MAJOR_VERSION) and
    (pCaps^.minorVersion >= DATA_MINOR_VERSION);
  if (Result and hasNoCap(CAP_CLUTCH_BUTTON, pCaps^.flags) and
    hasNoCap(CAP_CLUTCH_ANALOG, pCaps^.flags) and hasNoCap(CAP_ALT,
    pCaps^.flags) and (hasNoCap(CAP_BATTERY, pCaps^.flags) or
    not hasNoCap(CAP_BATTERY_CALIBRATION_AVAILABLE, pCaps^.flags)) and
    hasNoCap(CAP_DPAD, pCaps^.flags)) then
    Result := false;
end;

// --------------------------------------------------------------------------

{
  Discover open sim wheel devices:
  1. Discover present devices
  2. Get device path
  3. Open device
  4. Get HID capabilities
  5. Read feature report ID #2 (sim wheel capabilities)
  6. If everything fits, execute discovery callback.
}
class procedure TSimWheel.GetDevices(onDiscovery: TSimWheelDiscoveryProc);
var
  hidGuid: TGUID;
  devInfo: HDEVINFO;
  devItfData: TSPDeviceInterfaceData;
  memberIndex: DWORD;
  devItfDetailDataBuffer: PSPDeviceInterfaceDetailData;
  devItfDetailDataSize: DWORD;
  devHandle: THandle;
  ppd: PHIDPPreparsedData;
  devCaps: THIDPCaps;
  devicePath: string;
  capabilitiesReport: PCapabilitiesReport;
begin
  if (not Assigned(onDiscovery)) then
    Exit;

  HidD_GetHidGuid(hidGuid);
  devItfData.cbSize := sizeof(devItfData);
  devInfo := SetupDiGetClassDevs(@hidGuid, nil, THandle(0), DIGCF_PRESENT or
    DIGCF_DEVICEINTERFACE);
  if (devInfo = Pointer(INVALID_HANDLE_VALUE)) then
    RaiseLastOSError;

  try
    memberIndex := 0;
    while (SetupDiEnumDeviceInterfaces(devInfo, nil, hidGuid, memberIndex,
      devItfData)) do
    begin
      SetupDiGetDeviceInterfaceDetail(devInfo, @devItfData, nil, 0,
        devItfDetailDataSize, nil);
      if (GetLastError <> ERROR_INSUFFICIENT_BUFFER) then
        RaiseLastOSError;

      devItfDetailDataBuffer := GetMemory(devItfDetailDataSize);
      try
        if (sizeof(Pointer) = 8) then
          PSPDeviceInterfaceDetailData(devItfDetailDataBuffer)^.cbSize := 8
        else
          PSPDeviceInterfaceDetailData(devItfDetailDataBuffer)^.cbSize := 5;

        if (SetupDiGetDeviceInterfaceDetail(devInfo, @devItfData,
          devItfDetailDataBuffer, devItfDetailDataSize, devItfDetailDataSize,
          nil)) then
        begin
          devicePath := WideCharToString(devItfDetailDataBuffer^.devicePath);

          devHandle :=
            CreateFile(PSPDeviceInterfaceDetailData(devItfDetailDataBuffer)
            ^.devicePath, GENERIC_READ or GENERIC_WRITE, FILE_SHARE_READ or
            FILE_SHARE_WRITE, nil, OPEN_EXISTING, 0, 0);

          if (devHandle <> INVALID_HANDLE_VALUE) then
            try
              if (not HidD_GetPreparsedData(devHandle, ppd)) then
                RaiseLastOSError;

              if (HidP_GetCaps(ppd, devCaps) = HIDP_STATUS_SUCCESS) then
              begin
                if CheckDevCaps(@devCaps) then
                begin
                  capabilitiesReport :=
                    GetMemory(devCaps.FeatureReportByteLength);
                  capabilitiesReport^.ReportID := RID_FEATURE_CAPABILITIES;
                  if (HidD_GetFeature(devHandle, capabilitiesReport^,
                    devCaps.FeatureReportByteLength)) then
                  begin
                    if (CheckCapabilitiesReport(capabilitiesReport)) then
                    begin
                      onDiscovery(devicePath, capabilitiesReport^.DeviceID);
                    end;
                  end;
                  FreeMemory(capabilitiesReport);
                end;
              end;

            finally
              CloseHandle(devHandle);
            end;
        end;

      finally
        FreeMemory(devItfDetailDataBuffer);
      end;

      inc(memberIndex);
    end; // while
  finally
    SetupDiDestroyDeviceInfoList(devInfo);
  end;

end;

// --------------------------------------------------------------------------
// Constructor / destructor
// --------------------------------------------------------------------------

// constructor TSimWheel.Create(const handle: THandle; const devicePath: string;
// const majorVersion: UInt16; const minorVersion: UInt16; const flags: UInt16;
// const inputReportSize, outputReportSize, featureReportSize: integer);
// begin
// FdevicePath := devicePath;
// FdataMinorVersion := minorVersion;
// FdataMajorVersion := majorVersion;
// Fcapabilities := flags;
// FInputReportSize := inputReportSize;
// FOutputReportSize := outputReportSize;
// FFeatureReportSize := featureReportSize;
// FHandle := handle;
// Update;
// end;

// --------------------------------------------------------------------------

constructor TSimWheel.Create(const devicePath: string);
var
  ppd: PHIDPPreparsedData;
  devCaps: THIDPCaps;
  capabilitiesReport: TCapabilitiesReport;
begin
  FdevicePath := devicePath;
  FHandle := CreateFile(PWideChar(devicePath), GENERIC_READ or GENERIC_WRITE,
    FILE_SHARE_READ or FILE_SHARE_WRITE, nil, OPEN_EXISTING, 0, 0);
  if (FHandle = INVALID_HANDLE_VALUE) then
    raise EPathNotFoundException.Create(MSG_INVALID_PATH);

  if (not HidD_GetPreparsedData(FHandle, ppd)) then
    raise EPathNotFoundException.Create(MSG_INVALID_PATH);

  if (HidP_GetCaps(ppd, devCaps) <> HIDP_STATUS_SUCCESS) or
    (not CheckDevCaps(@devCaps)) then
    raise EPathNotFoundException.Create(MSG_INVALID_PATH);

  FInputReportSize := devCaps.InputReportByteLength;
  FOutputReportSize := devCaps.OutputReportByteLength;
  FFeatureReportSize := devCaps.FeatureReportByteLength;

  capabilitiesReport.ReportID := RID_FEATURE_CAPABILITIES;
  if (not HidD_GetFeature(FHandle, capabilitiesReport,
    sizeof(capabilitiesReport))) or
    (not CheckCapabilitiesReport(@capabilitiesReport)) then
    raise EPathNotFoundException.Create(MSG_INVALID_PATH);

  FdataMajorVersion := capabilitiesReport.majorVersion;
  FdataMinorVersion := capabilitiesReport.minorVersion;
  Fcapabilities := capabilitiesReport.flags;
  FDeviceID := capabilitiesReport.DeviceID;
  Update;
end;

// --------------------------------------------------------------------------

destructor TSimWheel.Destroy;
begin
  CloseHandle(FHandle);
  inherited;
end;

// --------------------------------------------------------------------------
// Protected Methods
// --------------------------------------------------------------------------

procedure TSimWheel.ClearConfigReport(const pReport: PConfigReport);
begin
  pReport^.ReportID := RID_FEATURE_CONFIG;
  pReport^.ClutchMode := $FF;
  pReport^.AltMode := $FF;
  pReport^.BitePoint := $FF;
  pReport^.SimpleCommand := $FF;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SendConfigReport(const pReport: PConfigReport);
begin
  pReport^.ReportID := RID_FEATURE_CONFIG;
  if (not HidD_SetFeature(FHandle, pReport^, sizeof(TConfigReport))) then
    RaiseLastOSError;
end;

// --------------------------------------------------------------------------

function TSimWheel.GetAltMode: boolean;
begin
  Result := (FConfig.AltMode <> 0);
end;

// --------------------------------------------------------------------------

function TSimWheel.GetDPADMode: boolean;
begin
  Result := (FConfig.DPadMode <> 0);
end;

// --------------------------------------------------------------------------

function TSimWheel.GetClutchMode: TSimWheel.TClutchMode;
begin
  Result := TSimWheel.TClutchMode(FConfig.ClutchMode);
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SetClutchMode(const aMode: TSimWheel.TClutchMode);
begin
  ClearConfigReport(@FConfig);
  FConfig.ClutchMode := UInt8(aMode);
  SendConfigReport(@FConfig);
  Update;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SetAltMode(const aMode: boolean);
begin
  ClearConfigReport(@FConfig);
  if (aMode) then
    FConfig.AltMode := 1
  else
    FConfig.AltMode := 0;
  SendConfigReport(@FConfig);
  Update;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SetDPADMode(const aMode: boolean);
begin
  ClearConfigReport(@FConfig);
  if (aMode) then
    FConfig.DPadMode := 1
  else
    FConfig.DPadMode := 0;
  SendConfigReport(@FConfig);
  Update;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SetBitePoint(const BitePoint: UInt8);
begin
  ClearConfigReport(@FConfig);
  FConfig.BitePoint := UInt8(BitePoint);
  SendConfigReport(@FConfig);
  Update;
end;

// --------------------------------------------------------------------------
// Public Methods
// --------------------------------------------------------------------------

function TSimWheel.HasCapability(aCap: TSimWheel.TCapabilities): boolean;
begin
  Result := (Fcapabilities and (1 shl UInt16(aCap))) <> 0;
end;

// --------------------------------------------------------------------------

function TSimWheel.Update: boolean;
var
  auxConfigReport: TConfigReport;
begin
  Result := false;
  auxConfigReport.ReportID := RID_FEATURE_CONFIG;
  if HidD_GetFeature(FHandle, auxConfigReport, sizeof(auxConfigReport)) then
  begin
    Result := not CompareMem(@auxConfigReport, @FConfig, sizeof(FConfig));
    if (Result) then
      CopyMemory(@FConfig, @auxConfigReport, sizeof(FConfig));
  end
  else
    RaiseLastOSError;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.ForceBatteryAutocalibration;
var
  auxConfigReport: TConfigReport;
begin
  if HasCapability(TSimWheel.TCapabilities.CAP_BATTERY) then
  begin
    ClearConfigReport(@auxConfigReport);
    auxConfigReport.SimpleCommand := CMD_BATT_RECALIBRATE;
    SendConfigReport(@auxConfigReport);
  end;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.ForceAnalogAxesCalibration;
var
  auxConfigReport: TConfigReport;
begin
  if HasCapability(TSimWheel.TCapabilities.CAP_CLUTCH_ANALOG) then
  begin
    ClearConfigReport(@auxConfigReport);
    auxConfigReport.SimpleCommand := CMD_AXIS_RECALIBRATE;
    SendConfigReport(@auxConfigReport)
  end;
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SaveNow;
var
  auxConfigReport: TConfigReport;
begin
  ClearConfigReport(@auxConfigReport);
  auxConfigReport.SimpleCommand := CMD_SAVE_NOW;
  SendConfigReport(@auxConfigReport)
end;

// --------------------------------------------------------------------------

procedure TSimWheel.ResetButtonsMap;
var
  auxConfigReport: TConfigReport;
begin
  ClearConfigReport(@auxConfigReport);
  auxConfigReport.SimpleCommand := CMD_RESET_BUTTONS_MAP;
  SendConfigReport(@auxConfigReport)
end;

// --------------------------------------------------------------------------

procedure TSimWheel.SetConfig(const [Ref] aConfig: TSimWheel.TConfigReport);
begin
  SendConfigReport(@aConfig);
  Update;
end;

end.
