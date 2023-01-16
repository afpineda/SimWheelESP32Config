program ESP32SimWheelConfig;

uses
  Vcl.Forms,
  ESP32SimWheelConfig_main in '..\src\GUI\ESP32SimWheelConfig_main.pas' {Form_main},
  OpenSourceSimWheelESP32 in '..\src\OpenSourceSimWheelESP32.pas',
  SimWheelDiscovery in '..\src\SimWheelDiscovery.pas',
  WinApi.Hid in '..\src\WinApi.Hid.pas',
  WinApi.SetupApi in '..\src\WinApi.SetupApi.pas';

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TForm_main, Form_main);
  Application.Run;
end.
