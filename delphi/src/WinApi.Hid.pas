{****************************************************************************
 * @brief Partial translation of "Hidsdi.h"
 *
 * Portions created by Microsoft are
 * Copyright (C) 1995-1999 Microsoft Corporation.
 * All Rights Reserved.
 *
****************************************************************************}

unit WinApi.Hid;

interface

// --------------------------------------------------------------------------
// Types
// --------------------------------------------------------------------------

type
  THIDDAttributes = record
    Size: LongWord;
    VendorID: Word;
    ProductID: Word;
    VersionNumber: Word;
  end;

  PHIDPPreparsedData = Pointer;

  TUsage = Word;

  THIDPCaps = record
    Usage: TUsage;
    UsagePage: TUsage;
    InputReportByteLength: Word;
    OutputReportByteLength: Word;
    FeatureReportByteLength: Word;
    Reserved: array [0 .. 16] of Word;

    NumberLinkCollectionNodes: Word;

    NumberInputButtonCaps: Word;
    NumberInputValueCaps: Word;
    NumberInputDataIndices: Word;

    NumberOutputButtonCaps: Word;
    NumberOutputValueCaps: Word;
    NumberOutputDataIndices: Word;

    NumberFeatureButtonCaps: Word;
    NumberFeatureValueCaps: Word;
    NumberFeatureDataIndices: Word;
  end;

  PHIDCaps = ^THIDPCaps;

  // --------------------------------------------------------------------------
  // Constants
  // --------------------------------------------------------------------------
const
  HidDLL = 'HID.dll';

  HIDP_STATUS_SUCCESS = LongInt($00110000);
  HIDP_STATUS_NULL = LongInt($80110001);
  HIDP_STATUS_INVALID_PREPARSED_DATA = LongInt($C0110001);
  HIDP_STATUS_INVALID_REPORT_TYPE = LongInt($C0110002);
  HIDP_STATUS_INVALID_REPORT_LENGTH = LongInt($C0110003);
  HIDP_STATUS_USAGE_NOT_FOUND = LongInt($C0110004);
  HIDP_STATUS_VALUE_OUT_OF_RANGE = LongInt($C0110005);
  HIDP_STATUS_BAD_LOG_PHY_VALUES = LongInt($C0110006);
  HIDP_STATUS_BUFFER_TOO_SMALL = LongInt($C0110007);
  HIDP_STATUS_INTERNAL_ERROR = LongInt($C0110008);
  HIDP_STATUS_I8042_TRANS_UNKNOWN = LongInt($C0110009);
  HIDP_STATUS_INCOMPATIBLE_REPORT_ID = LongInt($C011000A);
  HIDP_STATUS_NOT_VALUE_ARRAY = LongInt($C011000B);
  HIDP_STATUS_IS_VALUE_ARRAY = LongInt($C011000C);
  HIDP_STATUS_DATA_INDEX_NOT_FOUND = LongInt($C011000D);
  HIDP_STATUS_DATA_INDEX_OUT_OF_RANGE = LongInt($C011000E);
  HIDP_STATUS_BUTTON_NOT_PRESSED = LongInt($C011000F);
  HIDP_STATUS_REPORT_DOES_NOT_EXIST = LongInt($C0110010);
  HIDP_STATUS_NOT_IMPLEMENTED = LongInt($C0110020);

  // --------------------------------------------------------------------------
  // Prototypes
  // --------------------------------------------------------------------------

  // Device Discovery and Setup

function HidD_GetAttributes(HidDeviceObject: THandle;
  var HidAttrs: THIDDAttributes): LongBool; stdcall; external HidDLL;

procedure HidD_GetHidGuid(var HidGuid: TGUID); stdcall; external HidDLL;

function HidD_GetIndexedString(HidDeviceObject: THandle; Index: Integer;
  Buffer: PWideChar; BufferLength: Integer): LongBool; stdcall; external HidDLL;

function HidD_GetManufacturerString(HidDeviceObject: THandle; Buffer: PWideChar;
  BufferLength: Integer): LongBool; stdcall; external HidDLL;

function HidD_GetPhysicalDescriptor(HidDeviceObject: THandle; var Buffer;
  BufferLength: Integer): LongBool; stdcall; external HidDLL;

function HidD_GetPreparsedData(HidDeviceObject: THandle;
  var PreparsedData: PHIDPPreparsedData): LongBool; stdcall; external HidDLL;

function HidD_GetProductString(HidDeviceObject: THandle; Buffer: PWideChar;
  BufferLength: Integer): LongBool; stdcall; external HidDLL;

function HidD_GetSerialNumberString(HidDeviceObject: THandle; Buffer: PWideChar;
  BufferLength: Integer): LongBool; stdcall; external HidDLL;

function HidD_GetNumInputBuffers(HidDeviceObject: THandle; var NumBufs: Integer)
  : LongBool; stdcall; external HidDLL;

function HidD_SetNumInputBuffers(HidDeviceObject: THandle; NumBufs: Integer)
  : LongBool; stdcall; external HidDLL;

// Data Movement

function HidD_GetInputReport(HidDeviceObject: THandle; Buffer: Pointer;
  BufferLength: LongWord): LongBool; stdcall; external HidDLL;

function HidD_SetOutputReport(HidDeviceObject: THandle; Buffer: Pointer;
  BufferLength: LongWord): LongBool; stdcall; external HidDLL;

function HidD_SetFeature(HidDeviceObject: THandle; var Report; Size: Integer)
  : LongBool; stdcall; external HidDLL;

function HidD_GetFeature(HidDeviceObject: THandle; var Report; Size: Integer)
  : LongBool; stdcall; external HidDLL;

// Other

function HidD_FlushQueue(HidDeviceObject: THandle): LongBool; stdcall;
  external HidDLL;

function HidD_FreePreparsedData(PreparsedData: PHIDPPreparsedData): LongBool;
  stdcall; external HidDLL;

// Parsing

function HidP_GetCaps(PreparsedData: PHIDPPreparsedData;
  var Capabilities: THIDPCaps): LongInt; stdcall; external HidDLL;

implementation

end.
