set	(GROUP_SRC_DRIVERS_STM32F1XX_HAL_DRIVER
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_rcc_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_i2c.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_flash.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_pwr.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_flash_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_spi_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_spi.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_dma.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_gpio.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_rcc.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_uart.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_cortex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_gpio_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_rtc_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_rtc.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_adc_ex.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_adc.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_iwdg.c
		../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_crc.c
	)

set	(GROUP_SRC_DRIVERS_CMSIS
		../Src/system_stm32f1xx.c
	)

set	(GROUP_SRC_APPLICATION_USER
		../Src/spi.c
		../Src/usart.c
		../Src/gpio.c
		../Src/stm32f1xx_hal_msp.c
		../Src/stm32f1xx_it.c
		../Src/tim.c
		../Src/dma.c
		../Src/main.c
		../Src/i2c.c
		../Src/hex_gen.c
		../Src/rtc.c
		../Src/data_acquisition.c
#		../Inc/nctrl.h
		../Src/MPVV436744-013.c
		../Src/adc.c
		../Src/Ana_board.c
		../Src/my_comm.c
		../Src/xprintf.c
#		../Inc/globaldef.h
		../Src/ftoa.c
		../Src/freertos.c
		../Src/stm32f1xx_hal_timebase_TIM.c
		../Src/enc28j60.c
		../Src/lan.c
		../Src/MQTT_SN_task.c
		../Src/json.c
		../Src/watchdog.c
		../Src/iwdg.c
		../Src/ntp.c
		../Src/nvmem.c
		../Src/conf_fn.c
		../Src/crc.c
		../Src/tftp_server.c
		../Src/mystrcpy.c
		../Src/TFTP_ser_desesr.c
#		../Inc/TFTP_data.h
#		../Inc/debug_settings.h
	)

set	(GROUP_SRC_APPLICATION_MDK_ARM
#		startup_stm32f103xb.s
	)

set	(GROUP_SRC_MIDDLEWARES_FREERTOS
		../Middlewares/Third_Party/FreeRTOS/Source/event_groups.c
		../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.c
		../Middlewares/Third_Party/FreeRTOS/Source/tasks.c
		../Middlewares/Third_Party/FreeRTOS/Source/queue.c
		../Middlewares/Third_Party/FreeRTOS/Source/croutine.c
		../Middlewares/Third_Party/FreeRTOS/Source/portable/RVDS/ARM_CM3/port.c
		../Middlewares/Third_Party/FreeRTOS/Source/list.c
		../Middlewares/Third_Party/FreeRTOS/Source/timers.c
	)

set	(GROUP_SRC_MQTTSNPACKET
		../Src/MQTTSNPacket/MQTTSNConnectClient.c
		../Src/MQTTSNPacket/MQTTSNConnectServer.c
		../Src/MQTTSNPacket/MQTTSNDeserializePublish.c
		../Src/MQTTSNPacket/MQTTSNPacket.c
		../Src/MQTTSNPacket/MQTTSNSearchClient.c
		../Src/MQTTSNPacket/MQTTSNSearchServer.c
		../Src/MQTTSNPacket/MQTTSNSerializePublish.c
		../Src/MQTTSNPacket/MQTTSNSubscribeClient.c
		../Src/MQTTSNPacket/MQTTSNSubscribeServer.c
		../Src/MQTTSNPacket/MQTTSNUnsubscribeClient.c
		../Src/MQTTSNPacket/MQTTSNUnsubscribeServer.c
#		../Inc/MQTTSNPacket/StackTrace.h
	)

set	(GROUP_SRC___CMSIS
	)

set	(LIST_OF_SOURCES
		GROUP_SRC_DRIVERS_STM32F1XX_HAL_DRIVER
		GROUP_SRC_DRIVERS_CMSIS
		GROUP_SRC_APPLICATION_USER
		GROUP_SRC_APPLICATION_MDK_ARM
		GROUP_SRC_MIDDLEWARES_FREERTOS
		GROUP_SRC_MQTTSNPACKET
		GROUP_SRC___CMSIS
	)

