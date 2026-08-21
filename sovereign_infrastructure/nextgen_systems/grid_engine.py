"""
SYSTEM 5: GRID — Global Regional Hardware Telemetry & Mesh Entitlement System
Model: Spatio-Temporal Hardware Telemetry Consensus & Mesh Entitlement Distribution
Validates hardware device telemetry (Wear OS, Mobile, Edge Nodes), geofence rules,
and dynamic mesh hardware entitlement synchronization for RevenueCat multi-store access,
integrated with General Ledger equipment capitalization & Accounts Payable vendor bills.
"""

import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GRID_Engine")

class GRIDEngine:
    """GRID System: IoT Hardware Telemetry & Mesh Entitlement Engine integrated with Full SaaS Accounting"""

    def __init__(self, gl: Optional[Any] = None, ap: Optional[Any] = None):
        self.gl = gl
        self.ap = ap
        self.registered_devices: Dict[str, Dict[str, Any]] = {}
        self.active_mesh_nodes: Dict[str, List[str]] = {}
        logger.info("[GRID System] Initialized IoT Hardware & Mesh Entitlement Core.")

    def set_accounting_suite(self, gl: Any = None, ap: Any = None):
        """Inject General Ledger and Accounts Payable engines."""
        self.gl = gl
        self.ap = ap

    def register_device(self, device_id: str, device_type: str, region: str, hardware_cost_usd: float = 1200.0) -> Dict[str, Any]:
        """
        Registers an IoT or mobile hardware device to the substrate.
        Capitalizes edge hardware into Equipment & Hardware (Account 1500) in General Ledger.
        """
        device = {
            "device_id": device_id,
            "device_type": device_type,
            "region": region,
            "hardware_cost_usd": hardware_cost_usd,
            "status": "ONLINE",
            "health_score": 1.0
        }
        self.registered_devices[device_id] = device

        gl_entry_id = None
        if self.gl:
            try:
                # Debit Equipment 1500, Credit Accounts Payable 2010
                entry = self.gl.record_journal_entry(
                    description=f"GRID Device Capitalization ({device_id} - {device_type})",
                    debits={"1500": round(hardware_cost_usd, 2)},
                    credits={"2010": round(hardware_cost_usd, 2)},
                    entry_type="GRID_DEVICE_CAPEX",
                    reference=f"GRID-{device_id}"
                )
                gl_entry_id = entry.get("entry_id")
            except Exception as e:
                logger.warning(f"[GRID] GL device capitalization warning: {e}")

        if self.ap:
            try:
                self.ap.create_vendor_bill(
                    vendor=f"GRID IoT Hardware Vendor ({region})",
                    amount=hardware_cost_usd,
                    due_days=30,
                    account_code="5030"
                )
            except Exception as e:
                logger.warning(f"[GRID] AP bill creation warning: {e}")

        logger.info(f"[GRID] Registered Device: {device_id} ({device_type}, Region: {region})")
        return {
            **device,
            "gl_entry_id": gl_entry_id
        }

    def evaluate_device_telemetry(self, device_id: str, cpu_usage_pct: float, mem_usage_pct: float, latency_ms: float) -> float:
        """
        Calculates Hardware Telemetry Health Index H_i in [0.0 - 1.0].
        H_i = w1 * (1 - cpu/100) + w2 * (1 - mem/100) + w3 * max(0, 1 - latency/500)
        """
        w_cpu, w_mem, w_lat = 0.4, 0.4, 0.2
        s_cpu = max(0.0, 1.0 - (cpu_usage_pct / 100.0))
        s_mem = max(0.0, 1.0 - (mem_usage_pct / 100.0))
        s_lat = max(0.0, 1.0 - (latency_ms / 500.0))

        health_index = w_cpu * s_cpu + w_mem * s_mem + w_lat * s_lat
        health_score = round(max(0.0, min(1.0, health_index)), 4)

        if device_id in self.registered_devices:
            self.registered_devices[device_id]["health_score"] = health_score

        logger.info(f"[GRID] Telemetry Health for {device_id}: {health_score:.4f}")
        return health_score

    def verify_mesh_entitlement_consensus(self, user_id: str, device_ids: List[str]) -> Dict[str, Any]:
        """
        Verifies mesh consensus across subscriber's active hardware devices.
        Quorum requires >= 50% healthy devices (health_score >= 0.50).
        """
        healthy_count = 0
        total_devices = len(device_ids)

        for dev_id in device_ids:
            dev = self.registered_devices.get(dev_id, {})
            if dev.get("health_score", 0.0) >= 0.50 and dev.get("status") == "ONLINE":
                healthy_count += 1

        quorum_reached = (healthy_count / max(1, total_devices)) >= 0.50
        status = "ENTITLED_MESH_ACTIVE" if quorum_reached else "QUORUM_FAILED"

        self.active_mesh_nodes[user_id] = device_ids
        logger.info(f"[GRID] Mesh Consensus for {user_id}: {status} ({healthy_count}/{total_devices} nodes healthy)")
        return {
            "system": "GRID",
            "user_id": user_id,
            "total_nodes": total_devices,
            "healthy_nodes": healthy_count,
            "quorum_reached": quorum_reached,
            "entitlement_status": status
        }

    def enforce_geofenced_tier_access(self, device_id: str, lat: float, lon: float, allowed_center: tuple = (37.7749, -122.4194), max_radius_km: float = 500.0) -> Dict[str, Any]:
        """
        Enforces spatial geofencing for tier access using Haversine distance.
        """
        lat1, lon1 = math.radians(lat), math.radians(lon)
        lat2, lon2 = math.radians(allowed_center[0]), math.radians(allowed_center[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        r_earth_km = 6371.0
        distance_km = round(r_earth_km * c, 2)

        within_geofence = distance_km <= max_radius_km
        status = "ACCESS_GRANTED" if within_geofence else "GEOFENCE_RESTRICTED"

        logger.info(f"[GRID] Geofence Check for {device_id}: {status} ({distance_km} km from center)")
        return {
            "system": "GRID",
            "device_id": device_id,
            "distance_km": distance_km,
            "max_radius_km": max_radius_km,
            "access_status": status
        }

    def get_device_telemetry_status(self, device_id: str) -> Dict[str, Any]:
        """Returns registered status and health index of a hardware device."""
        return self.registered_devices.get(device_id, {"status": "UNKNOWN", "health_score": 0.0})
