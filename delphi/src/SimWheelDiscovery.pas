unit SimWheelDiscovery;

interface

uses
  OpenSourceSimWheelESP32,
  System.SyncObjs,
  System.Classes;

type
  TSimWheelDiscovery = class
  private

    FOnArrival: TNotifyEvent;
    FOnRemoval: TNotifyEvent;
    FPollingInterval: cardinal;
    discoveryThread: TThread;
    runEvent: TEvent;
    // procedure SetOnArrival(const Arrival: TNotifyEvent);
    // procedure SetOn
  public
    constructor Create(const PollingIntervalMs: cardinal);
    destructor Destroy; override;
    procedure Force;
    property onArrival: TNotifyEvent read FOnArrival write FOnArrival;
    property onRemoval: TNotifyEvent read FOnRemoval write FOnRemoval;
  end;

implementation

type
  TDiscoveryThread = class(TThread)
    FOwner: TSimWheelDiscovery;
    constructor Create(const AOwner: TSimWheelDiscovery);
    procedure Execute; override;
  end;

constructor TDiscoveryThread.Create(const AOwner: TSimWheelDiscovery);
begin
  FOwner := AOwner;
  inherited Create(true);
end;

procedure TDiscoveryThread.Execute;
var
  wr: TWaitResult;
  count: integer;
begin
  while (not Terminated) do
    try
      wr := FOwner.runEvent.WaitFor(FOwner.FPollingInterval);
      if (not Terminated) and (wr <> TWaitResult.wrAbandoned) and
        (wr <> TWaitResult.wrError) and Assigned(FOwner.FOnArrival) and
        Assigned(FOwner.FOnRemoval) then
      begin
        // FOwner.runEvent.ResetEvent;
        count := 0;
        TSimWheel.GetDevices(
          procedure(devicePath: string)
          begin
            inc(count);
          end);
      end;
    except
      Terminate;
    end;
end;

constructor TSimWheelDiscovery.Create(const PollingIntervalMs: cardinal);
begin
  FPollingInterval := PollingIntervalMs;
  runEvent := TEvent.Create(nil, false, false, '', false);
  FOnArrival := nil;
  FOnRemoval := nil;
  discoveryThread := TDiscoveryThread.Create(self);
  discoveryThread.FreeOnTerminate := true;
end;

destructor TSimWheelDiscovery.Destroy;
begin
  discoveryThread.Terminate;
  runEvent.Free;
  discoveryThread.Start;
  discoveryThread.Suspended := false;
  inherited;
end;

procedure TSimWheelDiscovery.Force;
begin
  runEvent.SetEvent;
end;

end.
