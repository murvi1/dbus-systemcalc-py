#!/usr/bin/env python
import unittest

# This adapts sys.path to include all relevant packages
import context

# our own packages
from base import TestSystemCalcBase

# Monkey patching for unit tests
import patches


class VoltageSenseTest(TestSystemCalcBase):
	def __init__(self, methodName='runTest'):
		TestSystemCalcBase.__init__(self, methodName)

	def setUp(self):
		TestSystemCalcBase.setUp(self)
		self._add_device('com.victronenergy.vebus.ttyO1',
			product_name='Multi',
			values={
				'/Ac/ActiveIn/L1/P': 123,
				'/Ac/ActiveIn/ActiveInput': 0,
				'/Ac/ActiveIn/Connected': 1,
				'/Ac/Out/L1/P': 100,
				'/Dc/0/Voltage': 12.25,
				'/Dc/0/Current': -8,
				'/Dc/0/Temperature': None,
				'/DeviceInstance': 0,
				'/Devices/0/Assistants': [0x55, 0x1] + (26 * [0]),  # Hub-4 assistant
				'/Dc/0/MaxChargeCurrent': None,
				'/Soc': 53.2,
				'/State': 3,
				'/BatteryOperationalLimits/MaxChargeVoltage': None,
				'/BatteryOperationalLimits/MaxChargeCurrent': None,
				'/BatteryOperationalLimits/MaxDischargeCurrent': None,
				'/BatteryOperationalLimits/BatteryLowVoltage': None,
				'/BatterySense/Voltage': None,
				'/BatterySense/Temperature': None,
				'/FirmwareFeatures/BolFrame': 1,
				'/FirmwareFeatures/BolUBatAndTBatSense': 1
			})
		self._add_device('com.victronenergy.settings',
			values={
				'/Settings/SystemSetup/AcInput1': 1,
				'/Settings/SystemSetup/AcInput2': 2,
			})

	def test_voltage_sense_no_battery_monitor_old_vebus_firmware(self):
		self._monitor.set_value('com.victronenergy.vebus.ttyO1', '/FirmwareFeatures/BolUBatAndTBatSense', 0)
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.32,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		self._check_values({
			'/Dc/Battery/Voltage': 12.25,
			'/Dc/Battery/VoltageService': 'com.victronenergy.vebus.ttyO1'
		})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': None},
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': None}})

	def test_voltage_sense_no_battery_monitor_old_mppt_firmware(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Voltage', None)
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Dc/0/Voltage': 12.32,
			'/Dc/0/Current': 9.7,
			'/Link/NetworkMode': 5,
			'/Link/VoltageSense': None},
			connection='VE.Direct')
		self._update_values(5000)
		self._check_values({
			'/Dc/Battery/Voltage': 12.25,
			'/Dc/Battery/VoltageService': 'com.victronenergy.vebus.ttyO1'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': 12.25}})

	def test_voltage_sense_no_battery_monitor(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Voltage', None)
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		self._check_values({
			'/Dc/Battery/Voltage': 12.25,
			'/Dc/Battery/VoltageService': 'com.victronenergy.vebus.ttyO1'
		})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': None},
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': 12.25}})

	def test_sense_mppt_and_battery_monitor(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Voltage', None)
		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Dc/0/Temperature': 25,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		self._check_values({
			'/Dc/Battery/Voltage': 12.15,
			'/Dc/Battery/Temperature': 25,
			'/Dc/Battery/VoltageService': 'com.victronenergy.battery.ttyO2'
		})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': 12.15},
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': 12.15}})

		# Temperature is slower
		self._update_values(13000)
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Temperature': 25},
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': 25}})

	def test_voltage_sense_vebus_and_battery_monitor(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Voltage', None)
		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._update_values(5000)
		self._check_values({
			'/Control/SolarChargerVoltageSense': 1,
			'/Dc/Battery/Voltage': 12.15,
			'/Dc/Battery/VoltageService': 'com.victronenergy.battery.ttyO2'
		})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': 12.15}})

	def test_voltage_sense_disabled(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/BatterySense/Voltage', None)
		self._set_setting('/Settings/SystemSetup/SharedVoltageSense', 0)

		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		# Check that voltagesense is indicated as inactive
		self._check_values({
			'/Control/SolarChargerVoltageSense': 0,
		})
		# Check that other devices were left alone
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': None}})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/SenseVoltage': None}})

	def test_temp_sense_disabled(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/BatterySense/Voltage', None)
		self._set_setting('/Settings/SystemSetup/SharedTemperatureSense', 0)

		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Dc/0/Temperature': 27,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		# Check that tempsense is indicated as inactive
		self._check_values({
			'/Control/SolarChargerTemperatureSense': 0,
		})
		# Check that other devices were left alone
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Temperature': None}})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': None}})

	def test_no_dvcc_no_sense(self):
		self._set_setting('/Settings/Services/Bol', 0)
		self._set_setting('/Settings/SystemSetup/SharedVoltageSense', 1)
		self._set_setting('/Settings/SystemSetup/SharedTemperatureSense', 1)

		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1',
			'/BatterySense/Voltage', None)

		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Dc/0/Temperature': 26,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7},
			connection='VE.Direct')
		self._update_values(5000)
		# Check that voltagesense is indicated as inactive
		self._check_values({
			'/Control/SolarChargerVoltageSense': 0,
		})
		# Check that other devices were left alone
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Voltage': None,
				'/BatterySense/Temperature': None}})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/SenseVoltage': None,
				'/Link/TemperatureSense': None}})

	def test_shared_temperature_sense(self):
		self._set_setting('/Settings/Services/Bol', 1)

		# This solarcharger has no temperature sensor
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7,
			'/Dc/0/Temperature': None},
			connection='VE.Direct')
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': None,
			'/Dc/Battery/TemperatureService': None,
			'/AutoSelectedTemperatureService': None
		})

		# If the battery has temperature, use it
		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Dc/0/Temperature': 8,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': 8,
			'/Dc/Battery/TemperatureService': 'com.victronenergy.battery.ttyO2',
			'/AutoSelectedTemperatureService': 'battery on dummy'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': 8}})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Temperature': 8}})


	def test_temperature_sense_order(self):
		self._set_setting('/Settings/Services/Bol', 1)

		# This solarcharger has no temperature sensor
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7,
			'/Dc/0/Temperature': None},
			connection='VE.Direct')

		# A temperature sensor of the wrong kind is not used
		self._set_setting('/Settings/SystemSetup/TemperatureService', 'com.victronenergy.temperature/4/Temperature')
		self._add_device('com.victronenergy.temperature.ttyO4',
			product_name='temperature sensor',
			values={
				'/Temperature': -9,
				'/TemperatureType': 1,
				'/DeviceInstance': 4})
		self._update_values(3000)
		self._check_values({
			'/Dc/Battery/Temperature': None,
			'/Dc/Battery/TemperatureService': None,
			'/AutoSelectedTemperatureService': None
		})

		# The right kind is used.
		self._set_setting('/Settings/SystemSetup/TemperatureService', 'com.victronenergy.temperature/3/Temperature')
		self._add_device('com.victronenergy.temperature.ttyO3',
			product_name='temperature sensor',
			values={
				'/Temperature': 9,
				'/TemperatureType': 0,
				'/DeviceInstance': 3})
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': 9,
			'/Dc/Battery/TemperatureService': 'com.victronenergy.temperature.ttyO3',
			'/AutoSelectedTemperatureService': 'temperature sensor on dummy'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': 9}})

		# Multi as temp sense
		self._set_setting('/Settings/SystemSetup/TemperatureService', 'com.victronenergy.vebus/0/Dc/0/Temperature')
		self._monitor.set_value('com.victronenergy.vebus.ttyO1', '/Dc/0/Temperature', 7)
		self._monitor.set_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Temperature', None)
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': 7,
			'/Dc/Battery/TemperatureService': 'com.victronenergy.vebus.ttyO1',
			'/AutoSelectedTemperatureService': 'Multi on dummy'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': 7}})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Temperature': None}})

		# Battery as temp sense. First check that battery is used as default.
		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Dc/0/Temperature': 8,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		for selected in ('default', 'com.victronenergy.battery/2/Dc/0/Temperature'):
			self._set_setting('/Settings/SystemSetup/TemperatureService', selected)
			self._update_values(9000)
			self._check_values({
				'/Dc/Battery/Temperature': 8,
				'/Dc/Battery/TemperatureService': 'com.victronenergy.battery.ttyO2',
				'/AutoSelectedTemperatureService': 'battery on dummy'
			})
			self._check_external_values({
				'com.victronenergy.solarcharger.ttyO1': {
					'/Link/TemperatureSense': 8}})
			self._check_external_values({
				'com.victronenergy.vebus.ttyO1': {
					'/BatterySense/Temperature': 8}})

		# No sense
		self._set_setting('/Settings/SystemSetup/TemperatureService', 'nosensor')
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': None,
			'/Dc/Battery/TemperatureService': None,
			'/AutoSelectedTemperatureService': None
		})

		# If Multi is battery service and it has a temp sensor, use it
		self._set_setting('/Settings/SystemSetup/BatteryService', 'com.victronenergy.vebus/0')
		self._set_setting('/Settings/SystemSetup/TemperatureService', 'default')
		self._monitor.set_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Temperature', None)
		self._update_values(9000)
		self._check_values({
			'/Dc/Battery/Temperature': 7,
			'/Dc/Battery/TemperatureService': 'com.victronenergy.vebus.ttyO1',
			'/AutoSelectedTemperatureService': 'Multi on dummy'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/TemperatureSense': 7}})
		self._check_external_values({
			'com.victronenergy.vebus.ttyO1': {
				'/BatterySense/Temperature': None}})

	def test_multi_for_vsense(self):
		self._set_setting('/Settings/Services/Bol', 1)
		self._set_setting('/Settings/SystemSetup/SharedVoltageSense', 1)
		self._set_setting('/Settings/SystemSetup/MultiHasVsense', 1)

		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/FirmwareFeatures/BolUBatAndTBatSense', 1)
		self._monitor.add_value('com.victronenergy.vebus.ttyO1', '/BatterySense/Voltage', None)
		self._add_device('com.victronenergy.battery.ttyO2',
			product_name='battery',
			values={
				'/Dc/0/Voltage': 12.15,
				'/Dc/0/Current': 5.3,
				'/Dc/0/Power': 65,
				'/Soc': 15.3,
				'/DeviceInstance': 2})
		self._add_device('com.victronenergy.solarcharger.ttyO1', {
			'/State': 0,
			'/Link/NetworkMode': 0,
			'/Link/VoltageSense': None,
			'/Link/TemperatureSense': None,
			'/Dc/0/Voltage': 12.2,
			'/Dc/0/Current': 9.7,
			'/Dc/0/Temperature': None},
			connection='VE.Direct')
		self._update_values(5000)
		self._check_values({
			'/Control/SolarChargerVoltageSense': 1,
			'/Dc/Battery/Voltage': 12.15, # From the battery service
			'/Dc/Sense/Voltage': 12.25, # From VE.Bus
			'/Dc/Sense/Service': 'com.victronenergy.vebus.ttyO1',
			'/Dc/Battery/VoltageService': 'com.victronenergy.battery.ttyO2'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': 12.25}}) # Use the one from VE.Bus

		self._set_setting('/Settings/SystemSetup/MultiHasVsense', 0)
		self._update_values(5000)
		self._check_values({
			'/Control/SolarChargerVoltageSense': 1,
			'/Dc/Battery/Voltage': 12.15, # From the battery service
			'/Dc/Sense/Voltage': 12.15, # Also from battery
			'/Dc/Sense/Service': 'com.victronenergy.battery.ttyO2',
			'/Dc/Battery/VoltageService': 'com.victronenergy.battery.ttyO2'
		})
		self._check_external_values({
			'com.victronenergy.solarcharger.ttyO1': {
				'/Link/VoltageSense': 12.15}}) # Use the one from the battery
