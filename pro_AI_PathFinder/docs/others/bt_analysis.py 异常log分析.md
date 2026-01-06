

# bt_analysis.py 异常log分析

## boardtest_basic_analysis

这些字符串均为代码中用于匹配失败信息的关键字或正则表达式模式，涵盖了各类硬件测试、状态检查和故障诊断的场景。

### 从 `fail_item.find` 提取的字符串：

1. `TEST_APPLICATION_LAUNCH_MODE`
2. `Q_REMOTE_IS_AVAILABLE`
3. `eBT_BOX_Status_Is_Closed`
4. `VERIFY_TRACK_ID_FROM_UTAG`
5. `VERIFY_TRACK_ID_FROM_UTAG_STATUS`
6. `FIB_TRACKID_OVERWRITE_STATUS`
7. `production_name_status`
8. `BP_BOOTLOADER_VERSION`
9. `OTG_VBUS_ON_VOLTAGE_STATUS`
10. `eBT_OTG_VBUS_OFF_VOLTAGE_STATUS`

### 从 `re.search` 提取的正则表达式字符串：

1. `RF_PARAMETER_MANAGER_INIT`
2. `LOAD_BAND_DATA_AND_ACCESSORY_LOSSES`
3. `ACCESSORY_ON_CURRENT_BOARD\S*`
4. `ACCESSORY_TURN_ON_STATUS_BOARD\S*`
5. `WAIT_FOR_BLAN_NETWORK_DEVICE_ARRIVAL\S*`
6. `CONNECT_TO_BLAN_NETWORK_DEVICE\S*`
7. `VERIFY_PHONE_DHCP_DISABLED\S*`
8. `BATTERY_CURRENT_CHECK_UNDER_ACC_POWER\S*`
9. `Power Up Checkpoint Query\S*`
10. `WAIT_FOR_ADB_DEVICE_ARRIVAL\S*`
11. `CONNECT_TO_ADB_DEVICE\S*`
12. `WAIT_FOR_MTK_KERNEL_PORT_ARRIVAL\S*`
13. `RTCC_SET_SYSTEM_TIME_TO_NOW_STATUS\S*`
14. `(READ|WRITE)_FACTORY_INFO_BYTE_STATUS`
15. `READ_FACTORY_INFO_BYTE_STATUS`
16. `WRITE_FACTORY_INFO_BYTE_STATUS`
17. `READ_LOG_PANIC_ANDROID\S+`
18. `SWITCH_TO_(BATTERY|ACCESSORY)\S*`
19. `BATTERY_ON_CURRENT_BOARD\S*`
20. `MEAS_BATTERY_ON_CURRENT_BOARD_STATUS\S*`
21. `MEAS_BATT_ON_CURRENT_BOARD\S*`
22. `NFC_FIRMWARE_DOWNLOAD_COMPLETE\S*`
23. `SUSPEND_\d+`
24. `UTAG_VERIFY_RADIO_\d+`
25. `THERMISTOR_TEMP_(\S+)_THERM\S*`
26. `ACCELEROMETER_SELF_TEST`
27. `GYROSCOPE_SELF_TEST`
28. `MAGNETOMETER_(X|Y|Z)_AXIS_ABSOLUTE_MAG_FIELD`
29. `Absolute_Self_Test_Magnetic_Field_(X|Y|Z)_Axis`
30. `CAP_SENSOR_VENDOR_ID_INTEGER`
31. `CAP_SENSOR_VENDOR_ID_READ_STATUS`
32. `CAP(\d)_COMP_BRD_VALUE_CS(\d+)`
33. `CAP(\d)_COMP_DIFF_IDAC_BRD_VALUE_CS(\d+)`
34. `^ANT_CAP_SENSOR_BRD_RESULT_STATUS\S*`
35. `RDWR_IO_(ENABLE|disable)_SW_FACT_KILL`
36. `^TURBO_CHARGER_TEST_ADDRESS_\S+`
37. `GET_USB_C_ORIENTATION\S*`
38. `USB_C_ORIENTATION_\d`
39. `GET_USB_C_ORIENTATION_\d_STATUS`
40. `BATTERY_CHARGER_PMIC8996_\S*`
41. `BATT_(ENABLE|DISABLE)_FET_PATH`
42. `BATT_(ENABLE|DISABLE)_CAPSWITCH_CHARGER_PATH`
43. `ACCESSORY_CURRENT_CAPSWITCH_\d{1}$`
44. `ACCESSORY_CURRENT_CAPSWITCH_\d{1}_STATUS$`
45. `BATTERY_ON_CURRENT_CAPSWITCH_CHARGER_\d{1}$`
46. `MEAS_BATTERY_ON_CURRENT_CAPSWT_CHARGER_STATUS_\d{1}$`
47. `^AUD(?:IO)*_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_(AMPL|FREQ|STATUS)`
48. `^AUD_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_AMPL`
49. `^AUD_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_FREQ`
50. `^AUDIO_SAMP_(PRIMARY|SEC|TERTIARY)_MIC_BRD_LEVEL_STATUS`
51. `MTK_RF_CONNECTOR_DETECTE`
52. `TEST_SET_10MHz_REFERENCE_STATUS`
53. `10MHz_REFERENCE_VERIFY_OVERALL_STATUS`
54. `MTK_META_DUT_CONNECT`
55. `MTK_META_AP_TO_MODEM_MODE`
56. `MTK_META_MODEM_TO_AP_MODE`
57. `MTK_META_DUT_DISCONNECT`
58. `P2K_SAVE_TO_HOB`
59. `P2K_VERIFY_HOB`
60. `BATTERY_OFF_CURRENT_BOARD(_\d+)*`
61. `^BATTERY_OFF_CURRENT_BOARD(_\d+)*`
62. `BATTERY_OFF_CURRENT_BOARD\S+Status`



## plat_MTK_task_failure_analysis

这些字符串主要用于匹配不同类型的校准任务、测试任务或具体的失败项，从而确定对应的对应的对应的故障分析结果。

1. `'SELF_CALIBRATION'`（用于判断 `fail_task` 或 `fail_item` 中是否包含该字符串）
2. `'DPD_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
3. `'DPD_RFCal'`（用于判断 `fail_item` 中是否包含该字符串）
4. `'ET_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
5. `'ET_RFCal'`（用于判断 `fail_item` 中是否包含该字符串）
6. `'TADC_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
7. `'TEMPERATURE_SENSOR_CALIBRATION'`（用于判断 `fail_item` 中是否包含该字符串）
8. `'AFC_CALIBRATION'`（用于判断 `fail_task` 或 `fail_item` 中是否包含该字符串）
9. `'CO-TMS_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
10. `'TMS_CALIBRATION'`（用于判断 `fail_item` 中是否包含该字符串）
11. `'GGE_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
12. `'GSM_FHC_DTS_AGC_RFCal_DONE'`（用于精确匹配 `fail_item`）
13. `'GSM_FHC_UTS_RFCal_DONE'`（用于精确匹配匹配 `fail_item`）
14. `'GSM_PATH_TEST_RFCal_DONE'`（用于精确匹配 `fail_item`）
15. `'WCDMA_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
16. `'WCDMA_FHC_V7_RFCal_DONE'`（用于精确匹配 `fail_item`）
17. `'LTE_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
18. `'LTE_FHC_TRX_RFCal_DONE'`（用于精确匹配 `fail_item`）
19. `'NR_CALIBRATION'`（用于判断 `fail_task` 中是否包含该字符串）
20. `'NR_FHC_TRX_RFCal_DONE'`（用于精确匹配 `fail_item`）
21. `'_NSFT'`（用于判断 `fail_task` 中是否包含该字符串）
22. `'NSFT\S+_DONE'`（正则表达式，用于判断 `fail_item` 中是否包含符合该模式的字符串）
23. `'CAL_DATA_DOWNLOAD_CHECK_TEST'`（用于判断 `fail_task` 中是否包含该字符串）
24. `'TRANSCEIVER_POWER_TEST'`（用于判断 `fail_task` 中是否包含该字符串）

## plat_MTK_measure_failure_analysis

这些正则表达式主要用于匹配不同类型的测量失败项，涵盖了 AFC 校准、CO-TMS 校准、GSM/WCDMA/LTE/NR 等不同制式的信号测量失败场景，通过捕获分组（如频段号、连接器编号等）实现更精准的故障分析。

1. `r"MMAFC_LTE_B(\d+)_CARKIT(\d+)_CAPID_CAL_UPLINK_SIGNAL_MEASURE"`
2. `r"LTE_AFC_B(\d+)_Carkit(\d+)_TX_FREQERR_MEASURE"`
3. `r"GSM_(GMSK|EPSK)_FHC_UTS_Ex_APC_TX_Measure"`
4. `r"(GMSK|EPSK)_GSM850_FHC_UTS_Ex_512p_Measure"`
5. `r"WCDMA_Band(\d+)_FHC_TX_Measure"`
6. `r"LTE_Band(\d+)_TxCarkit(\d+)_\S+_Measure"`
7. `r"NR_Band(\d+)_TxCarkit(\d+)_\S+_Measure"`
8. `r"(GSM|WCDMA)_NSFT_LIST_MODE_Measure_\d+"`
9. `r"(LTE|NRFR1)_SFFT_LIST_MODE_Measure_\d+"`
10. `r"WCDMA_B(\d+)_CH(\d+)_AntPath(\d+)_LNA(\d+)_RxCalSeq(\d+)_RSSI_MEASURE"`



## plat_MTK_META_failure_analysis

这些正则表达式主要用于匹配与 DUT（设备 - under-test）测试命令相关的失败项，涵盖了 LTE/NR/WCDMA 等不同制式的 FHC 校准和 NSFT 测试场景，通过捕获分组（如制式类型、频段号、连接器编号等）实现更具体的故障分析。

1. `r"\S+_(Dut_FHC_StartCmd|SendDutFhcCmd|INIT_DUT_TEST)\S*"`（带有 `re.IGNORECASE` 标志，忽略大小写匹配）
2. `r'(LTE|NR)_Band(\d+)_TxCarkit(\d+)\S*_CalExecutor_SendDutFhcCmd'`
3. `r'WCDMA_Band(\d+)_Dut_FHC_StartCmd'`



## plat_MTK_radio_failure_analysis

这些正则表达式主要用于匹配各类无线电校准和测试失败项，覆盖了温度传感器校准、AFC 校准、TMS 校准以及 GSM、EDGE、WCDMA、LTE、NR 等多种制式的射频参数校准场景，通过捕获分组提取具体的频段、信道、功率等级等信息，实现精准的故障分析。

1. `r"TADC_RFIC0-TEMP\d+"`
2. `r"CAP_ID_VALUE"`
3. `r"TMS_Temperature_\d+"`
4. `r"_CoTMS.C(\d+)"`
5. `r"GSM_FHC_DTS_Ex_Pathloss_AntIndex(\d+)_Result_OK_Check"`
6. `r"GSM_DLCH(\d+)_(GSM850|GSM900|DCS1800|PCS1900)_DLP(\S+)_LNA-(UtraHigh|High|Middle|Low)-(PRx|DRx)Loss"`
7. `r"GSM_B(850|900|1800|1900)_ULCH(\d+)_GMSK_SubBand_TxPCL(\d+)-FreqComp(DAC|Weighting)"`
8. `r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-PCL(\d+)-FreqCompWeighting"`
9. `r"GSM_ULCH(\d+)_GMSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power"`
10. `r"EDGE_(GSM850|GSM900|DCS1800|PCS1900)_PCL(\d+)_APC_PA_GAIN_DAC"`
11. `r"EDGE_ULCH(\d+)_EPSK_(GSM850|GSM900|DCS1800|PCS1900)-Tx-APC-PCL(\d+)_Power"`
12. `r"WCDMA_B(\d+)_MidChan(\d+)_TX_PA_Mode(\d+)_Sect(\d+)_TxPower-Prf(\d+)"`
13. `r"WCDMA_B(\d+)_DLCH(\d+)_AGC-Rx-(Main|Div)Path-LNA\(\d+\)-(HPM|LPM|TKM)-Loss"`
14. `r"WCDMA_B(\d+)_ULCH(\d+)_PWR(\d+)_PwrS(\d+)_Tx-PA(\d+)-GainDAC"`
15. `r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossDAC"`
16. `r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-GainCompensationDAC"`
17. `r"WCDMA_B(\d+)_ULCH(\d+)_Tx-PA(\d+)-CouplerLossCompensationDAC"`
18. `r"(LTE|NR)_B(\d+)_F(\d+)_CalIdx(\d+)_SxIdx(\d+)_FeIdx(\d+)_BwIdx(\d+)_Carkit(\d+)_TxPower-Prf(\d+)"`
19. `r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_PwrS(\d+)_FE(\d+)_SX(\d+)_MidCH-PAGain"`
20. `r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_MidCH-Coupler-Loss"`
21. `r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\d+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PAGain"`
22. `r"Tx_Cal_(LTE_B|N)(\d+)_ULF(\S+)M_CKG(\S+)_CalIdx(\S+)_BWIdx(\d+)_FE(\d+)_SX(\d+)_PowMode(\d+)_Subband-PDCouplerLoss"`
23. `r"Rx_SC_Cal_(LTE_B|N)(\d+)_DLF(\S+)M_Rout(\d+)_RUT(\d+)_CKG(\S+)_CalIdx(\d+)_PwrS(\d+)_FE(\d+)_FEL(\d+)_Ant(\d+)_(HPM|`