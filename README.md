dbus_systemcalc_py
==================

Publish PV totals and other system readings on D-Bus, getting info from other D-Bus services. D-Bus servicename:
  
    com.victronenergy.system

Results are available under these D-Bus paths

    /Ac/PvOnGenset/L1/Power to L3/Power
    /Ac/PvOnGenset/NumberOfPhases
    /Ac/PvOnGenset/Total/Power

    /Ac/PvOnGrid/L1/Power to L3/Power
    /Ac/PvOnGrid/NumberOfPhases
    /Ac/PvOnGrid/Total/Power
    
    /Ac/PvOnOutput/L1/Power to L3/Power
    /Ac/PvOnOutput/NumberOfPhases
    /Ac/PvOnOutput/Total/Power
    
    /Dc/Battery/Voltage, Current, /Power, Soc and /State (0 = Idle, 1 = Charging, 2 = Discharging

    /Dc/Charger/Power
    /Dc/Pv/Current and /Power
    /Dc/System/Power

Select battery service
----------------------

    /AutoSelectedBatteryService
    /AvailableBatteryServices

Lets a user select which battery monitor he wants to use. Possible battery monitors include vebus.
    
In the GUI, under System setup, there is a dropdown in which the user selects the battery monitor that
is to be used for the overviews and system calculations. Available systems are enumerated by
dbus_systemcalc_py, and available in com.victronenergy.system /AvailableBatteryServices. It contains
a JSON string with the format: {"key": "value", "key": "value", etc.}. 

The key of the selected item needs to be stored in com.victronenergy.settings, path:

    /Settings/SystemSetup/BatteryService.
    
Two special items, No battery and Automatic:

Automatic:
dbus_system_calc automatically selects the best battery monitor available: If a battery (ie BMV or
Lynx Shunt) service is available, it will select and use that. If not, it checks if it is probably a 
hub-2 system: no battery monitor, vebus system, no solar charger and no chargers. In that case will 
auto-select the vebus system. The selected service is visible under path /AutoSelectedBatteryService.

No battery:
Situation that 'No battery' solves: a system where there is only a Multi connected to the CCGX, and no
battery monitor. But that system does have other DC loads or other chargers, making the SOC from the
Multi incorrect. The Autoselect option would autoselect the Multi, causing incorrect values to be shown
to a user
