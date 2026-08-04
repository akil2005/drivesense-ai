import random
import math
from datetime import datetime
from .models import (
    TemperatureMetrics,
    FluidMetrics,
    EnginePerformanceMetrics,
    ElectricalEmissionsMetrics,
    VehicleTelemetryPayload
)

class VehicleSimulator:
    def __init__(self):
        # Initial resting state of the car
        self.current_speed = 0.0
        self.current_rpm = 800
        self.coolant_temp = 40.0  # Cold start
        self.fuel_level = 100.0
        
        # --- LOCAL EDGE COMPUTING MEMORY ---
        # Exponential Moving Average (EMA) baseline to track thermal trend locally on the ECU
        self.ema_coolant_temp = 40.0
        self.alpha = 0.15  # Smoothing factor (weight given to new incoming sensor readings)

    def generate_next_step(self, throttle_pct: float, simulation_step: int) -> VehicleTelemetryPayload:
        """
        Calculates physics-correlated telemetry based on throttle input and time,
        and executes local EMA calculations to detect abnormal temperature trends early.
        """
        # 1. Physics Correlation: RPM follows throttle, Speed follows RPM
        target_rpm = 800 + (throttle_pct * 55) # Max ~6300 RPM
        self.current_rpm += (target_rpm - self.current_rpm) * 0.2 
        
        target_speed = (self.current_rpm / 60) * 2.0 if self.current_rpm > 1000 else 0.0
        self.current_speed += (target_speed - self.current_speed) * 0.1

        # 2. Thermodynamic Correlation: Engine heats up based on workload
        thermal_load = (self.current_rpm / 3000)
        target_temp = 90.0 + (thermal_load * 5)
        self.coolant_temp += (target_temp - self.coolant_temp) * 0.02

        # 3. Micro-Oscillations (Sensor noise)
        noise = random.uniform(-0.3, 0.3)
        rpm_jitter = random.randint(-15, 15)

        # 4. Burn fuel proportional to RPM
        self.fuel_level -= (self.current_rpm * 0.00001)

        # --- 5. EDGE PREDICTIVE MATHEMATICS ---
        actual_coolant = self.coolant_temp + noise
        
        # Update local Exponential Moving Average
        self.ema_coolant_temp = (self.alpha * actual_coolant) + ((1 - self.alpha) * self.ema_coolant_temp)
        
        # Calculate instantaneous divergence (thermal surge rate)
        thermal_surge = actual_coolant - self.ema_coolant_temp
        
        edge_alerts = {}
        # If the temp surges significantly faster than historical EMA baseline, flag predictive warning.
        # This catches early failure trends (e.g. at 96°C) well before reaching critical 105°C/115°C limits.
        if thermal_surge > 1.8:
            edge_alerts["cooling_degradation"] = True

        return VehicleTelemetryPayload(
            vin="DYNAMIC-TEST-001",
            timestamp=datetime.utcnow(),
            temperatures=TemperatureMetrics(
                engine_coolant=round(actual_coolant, 2),
                intake_air=30.0 + (noise * 0.1),
                transmission_fluid=80.0 + (self.current_speed * 0.1),
                ambient_air=25.0
            ),
            fluids=FluidMetrics(
                oil_level_percentage=95.0,
                oil_temperature=round(self.coolant_temp + 5.0 + noise, 2),
                oil_pressure_psi=20.0 + (self.current_rpm * 0.01),
                fuel_level_percentage=max(0.0, round(self.fuel_level, 4))
            ),
            performance=EnginePerformanceMetrics(
                rpm=int(self.current_rpm + rpm_jitter),
                speed_kph=round(self.current_speed, 1),
                throttle_position_percentage=throttle_pct,
                calculated_load_percentage=round(throttle_pct * 0.9 + 10, 1),
                mass_air_flow_gps=round(4.0 + (self.current_rpm * 0.015), 2)
            ),
            electrical_emissions=ElectricalEmissionsMetrics(
                battery_voltage=round(14.0 + random.uniform(-0.1, 0.1), 2),
                short_term_fuel_trim=round(random.uniform(-1.5, 1.5), 2),
                long_term_fuel_trim=0.5,
                o2_sensor_voltage=round(0.45 + (noise * 0.5), 2),
                ignition_timing_advance=10.0 + (self.current_rpm * 0.002)
            ),
            dtc_codes=[],
            edge_computed_alerts=edge_alerts  # Passes local ECU alerts to LangGraph
        )