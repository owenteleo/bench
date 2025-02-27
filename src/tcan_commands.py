from enum import IntEnum, unique

@unique
class TCAN_ID(IntEnum):
    """
    Enum for CAN IDs used in the TCAN system.
    """

    CAN_ID_OTA_COMMAND = 0x400
    CAN_ID_OTA_RESPONSE = 0x410
    CAN_ID_OTA_DATA = 0x420

    CAN_ID_CONTROLLER_COMMAND_SYS = 0x500
    CAN_ID_CONTROLLER_COMMAND_PWM = 0x510
    CAN_ID_CONTROLLER_COMMAND_SPST = 0x520
    CAN_ID_CONTROLLER_COMMAND_SPDT = 0x530
    CAN_ID_CONTROLLER_COMMAND_HC = 0x540
    CAN_ID_CONTROLLER_COMMAND_CUSTOM_1 = 0x550
    CAN_ID_CONTROLLER_COMMAND_CAN_AXIS = 0x560
    CAN_ID_CONTROLLER_COMMAND_UNUSED_7 = 0x570
    CAN_ID_CONTROLLER_COMMAND_UNUSED_8 = 0x580
    CAN_ID_CONTROLLER_COMMAND_UNUSED_9 = 0x590
    CAN_ID_CONTROLLER_COMMAND_UNUSED_A = 0x5A0
    CAN_ID_CONTROLLER_COMMAND_UNUSED_B = 0x5B0
    CAN_ID_CONTROLLER_COMMAND_UNUSED_C = 0x5C0
    CAN_ID_CONTROLLER_COMMAND_UNUSED_D = 0x5D0
    CAN_ID_CONTROLLER_COMMAND_UNUSED_E = 0x5E0
    CAN_ID_CONTROLLER_COMMAND_RDAC = 0x5F0

    CAN_ID_PDU_CONTROL = 0x60F

    CAN_ID_TCU_HEARTBEAT = 0x700
    CAN_ID_TCU_STAT_PWM = 0x710
    CAN_ID_TCU_STAT_SPST = 0x720
    CAN_ID_TCU_STAT_SPDT = 0x730
    CAN_ID_TCU_STAT_HC = 0x740
    CAN_ID_TCU_STAT_CUSTOM = 0x750
    CAN_ID_TCU_STAT_CAN_AXIS = 0x760
    CAN_ID_TCU_STAT_UNUSED_7 = 0x770
    CAN_ID_TCU_STAT_UUID = 0x780
    CAN_ID_TCU_STAT_AIN_C = 0x790
    CAN_ID_TCU_STAT_GIT_SHA = 0x7A0
    CAN_ID_TCU_STAT_AIN_A = 0x7B0
    CAN_ID_TCU_STAT_AIN_B = 0x7C0
    CAN_ID_MCAN_STATUS = 0x7D0
    CAN_ID_TCU_STAT_AIN_D = 0x7E0
    CAN_ID_REPLAY_CONTROLLER_HB = 0x7F0


@unique
class SystemMode(IntEnum):
    """
    Enum for JTECU system modes.
    """

    MANUAL = 0
    REMOTE = 1
    EMERGENCY = 2
    OTA = 3
