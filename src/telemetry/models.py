from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TemperatureMetrics(BaseModel):
    engine_coolant: float = Field(..., description="Engine Coolant Temperature (ECT) in °C")
    intake_air: float = Field(..., description="Intake Air Temperature (IAT) in °C")
    transmission_fluid: float = Field(..., description="Transmission Fluid Temperature (TFT) in °C")
    ambient_air: float = Field(..., description="Outside ambient air temperature in °C")

class FluidMetrics(BaseModel):
    oil_level_percentage: float = Field(..., ge=0.0, le=100.0, description="Electronic dipstick reading (0-100%)")
    oil_temperature: float = Field(..., description="Engine oil temperature in °C")
    oil_pressure_psi: float = Field(..., ge=0.0, description="Engine oil pressure in PSI")
    fuel_level_percentage: float = Field(..., ge=0.0, le=100.0, description="Fuel tank level percentage")

class EnginePerformanceMetrics(BaseModel):
    rpm: int = Field(..., ge=0, description="Engine rotations per minute")
    speed_kph: float = Field(..., ge=0.0, description="Vehicle speed in km/h")
    throttle_position_percentage: float = Field(..., ge=0.0, le=100.0, description="Accelerator pedal position")
    calculated_load_percentage: float = Field(..., ge=0.0, le=100.0, description="Calculated engine load capacity")
    mass_air_flow_gps: float = Field(..., ge=0.0, description="MAF sensor reading in grams per second (g/s)")

class ElectricalEmissionsMetrics(BaseModel):
    battery_voltage: float = Field(..., ge=0.0, description="Bus voltage (Alternator/Battery) in Volts")
    short_term_fuel_trim: float = Field(..., description="STFT percentage (positive = adding fuel, negative = removing)")
    long_term_fuel_trim: float = Field(..., description="LTFT percentage continuous baseline")
    o2_sensor_voltage: float = Field(..., ge=0.0, le=1.2, description="Oxygen sensor output voltage (typically 0.1V to 0.9V)")
    ignition_timing_advance: float = Field(..., description="Ignition timing advance in degrees relative to TDC")

class VehicleTelemetryPayload(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vin: str = Field(..., description="Vehicle Identification Number to map correct service manual")
    temperatures: TemperatureMetrics
    fluids: FluidMetrics
    performance: EnginePerformanceMetrics
    electrical_emissions: ElectricalEmissionsMetrics
    dtc_codes: List[str] = Field(default_factory=list, description="Active Diagnostic Trouble Codes (e.g., ['P0171', 'P0300'])")