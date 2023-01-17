{****************************************************************************
 * @brief Partial translation of "setupapi.h"
 *
 * Portions created by Microsoft are
 * Copyright (C) 1995-1999 Microsoft Corporation.
 * All Rights Reserved.
 *
****************************************************************************}

unit WinApi.SetupApi;

interface

uses
  Windows;

// --------------------------------------------------------------------------
// Types
// --------------------------------------------------------------------------

type
  HDEVINFO = Pointer;

  TSPDevInfoData = packed record
    cbSize: DWORD;
    ClassGuid: TGUID;
    DevInst: DWORD;
    Reserved: ULONG_PTR;
  end;

  PSPDevInfoData = ^TSPDevInfoData;

  TSPDeviceInterfaceData = packed record
    cbSize: DWORD;
    InterfaceClassGuid: TGUID;
    Flags: DWORD;
    Reserved: ULONG_PTR;
  end;

  PSPDeviceInterfaceData = ^TSPDeviceInterfaceData;

  TSPDeviceInterfaceDetailData = packed record
    cbSize: DWORD;
    DevicePath: array [0 .. ANYSIZE_ARRAY - 1] of WideChar;
  end;

  PSPDeviceInterfaceDetailData = ^TSPDeviceInterfaceDetailData;

  // --------------------------------------------------------------------------
  // Constants
  // --------------------------------------------------------------------------

const
  SetupApiDLL = 'SetupApi.dll';

const
  // Flags for SetupDiGetClassDevs()
  DIGCF_DEFAULT = $00000001;
  DIGCF_PRESENT = $00000002;
  DIGCF_ALLCLASSES = $00000004;
  DIGCF_PROFILE = $00000008;
  DIGCF_DEVICEINTERFACE = $00000010;

  // --------------------------------------------------------------------------
  // Prototypes
  // --------------------------------------------------------------------------

function SetupDiGetClassDevs(ClassGuid: PGUID; const Enumerator: PWideChar;
  hwndParent: HWND; Flags: DWORD): HDEVINFO; stdcall;
  external SetupApiDLL name 'SetupDiGetClassDevsW';

function SetupDiDestroyDeviceInfoList(DeviceInfoSet: HDEVINFO): LongBool;
  stdcall; external SetupApiDLL;

function SetupDiEnumDeviceInterfaces(DeviceInfoSet: HDEVINFO;
  DeviceInfoData: PSPDevInfoData; const InterfaceClassGuid: TGUID;
  MemberIndex: DWORD; var DeviceInterfaceData: TSPDeviceInterfaceData)
  : LongBool; stdcall; external SetupApiDLL;

function SetupDiGetDeviceInterfaceDetail(DeviceInfoSet: HDEVINFO;
  DeviceInterfaceData: PSPDeviceInterfaceData;
  DeviceInterfaceDetailData: PSPDeviceInterfaceDetailData;
  DeviceInterfaceDetailDataSize: DWORD; var RequiredSize: DWORD;
  Device: PSPDevInfoData): LongBool; stdcall;
  external SetupApiDLL name 'SetupDiGetDeviceInterfaceDetailW';

implementation

end.
