"""
MySQL Database Manager Module for Healthnest / HackSprint
----------------------------------------------------------
Handles MySQL database connection, table initialization, and CRUD operations
for Alerts and Appointments with graceful fallback handling.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from security import (
    hybrid_encrypt_patient_data,
    hybrid_decrypt_patient_data,
    hash_password_hmac,
    verify_password_hmac
)

logger = logging.getLogger("healthnest.db")

# Flag indicating whether MySQL is accessible
IS_MYSQL_AVAILABLE = False

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_INSTALLED = True
except ImportError:
    PYMYSQL_INSTALLED = False
    logger.warning("PyMySQL is not installed. Run 'pip install pymysql' to enable MySQL.")


def get_server_connection():
    """Establish connection to MySQL server without selecting a database."""
    if not PYMYSQL_INSTALLED:
        return None
    
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=3
    )


def get_db_connection():
    """Establish connection to the healthnest_db database."""
    if not PYMYSQL_INSTALLED:
        return None
    
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    db_name = os.getenv("MYSQL_DB", "healthnest_db")

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=3
    )


def init_db() -> bool:
    """
    Initialize MySQL Database & Create Tables if they don't exist.
    Returns True if connection and setup succeeded, False otherwise.
    """
    global IS_MYSQL_AVAILABLE
    
    use_mysql = os.getenv("USE_MYSQL", "True").lower() in ("true", "1", "yes")
    if not use_mysql or not PYMYSQL_INSTALLED:
        IS_MYSQL_AVAILABLE = False
        logger.info("[INFO] MySQL integration disabled or PyMySQL missing. Using In-Memory fallback.")
        return False

    try:
        db_name = os.getenv("MYSQL_DB", "healthnest_db")

        # 1. Create database if it does not exist
        conn_server = get_server_connection()
        if not conn_server:
            IS_MYSQL_AVAILABLE = False
            return False

        with conn_server.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn_server.close()

        # 2. Connect to the specific database and create tables
        conn = get_db_connection()
        if not conn:
            IS_MYSQL_AVAILABLE = False
            return False

        with conn.cursor() as cursor:
            # Alerts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id VARCHAR(64) PRIMARY KEY,
                patient_id VARCHAR(64) NOT NULL,
                patient_name VARCHAR(128) DEFAULT '',
                title VARCHAR(255) NOT NULL,
                event_type VARCHAR(64) NOT NULL,
                message TEXT,
                time_str VARCHAR(64),
                timestamp VARCHAR(128),
                severity VARCHAR(32) DEFAULT 'medium',
                risk_level VARCHAR(32) DEFAULT 'medium',
                confidence FLOAT DEFAULT 0.0,
                location VARCHAR(128) DEFAULT 'Bedroom',
                acknowledged TINYINT(1) DEFAULT 0,
                caregiver_status VARCHAR(64) DEFAULT 'pending',
                acknowledged_by VARCHAR(128) DEFAULT NULL,
                acknowledged_at VARCHAR(128) DEFAULT NULL,
                escalated_at VARCHAR(128) DEFAULT NULL,
                escalation_reason TEXT DEFAULT NULL,
                screenshot_url VARCHAR(255) DEFAULT NULL,
                ntfy_status VARCHAR(32) DEFAULT 'pending',
                source VARCHAR(32) DEFAULT 'live',
                raw_json TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Appointments Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id VARCHAR(64) PRIMARY KEY,
                patient_id VARCHAR(64) NOT NULL,
                patient_name VARCHAR(128) DEFAULT '',
                doctor_id VARCHAR(64) NOT NULL,
                doctor_name VARCHAR(128) NOT NULL,
                specialty VARCHAR(128) NOT NULL,
                hospital VARCHAR(255) DEFAULT '',
                distance_km FLOAT DEFAULT 0.0,
                apt_date VARCHAR(32) NOT NULL,
                apt_time VARCHAR(32) NOT NULL,
                status VARCHAR(32) DEFAULT 'confirmed',
                apt_type VARCHAR(32) DEFAULT 'in_person',
                reason TEXT DEFAULT NULL,
                created_at VARCHAR(128) DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

        conn.close()
        IS_MYSQL_AVAILABLE = True
        logger.info("[SUCCESS] MySQL Database & Tables Initialized Successfully.")
        print("[SUCCESS] MySQL Database & Tables Initialized Successfully.")
        return True

    except Exception as e:
        IS_MYSQL_AVAILABLE = False
        logger.warning(f"[WARNING] MySQL Connection/Setup failed: {e}. Falling back to In-Memory storage.")
        print(f"[WARNING] MySQL Connection/Setup failed: {e}. Falling back to In-Memory storage.")
        return False


# ==============================================================================
# ALERTS CRUD OPERATIONS
# ==============================================================================

def db_save_alert(alert_data: Dict[str, Any]) -> bool:
    """Save or update an alert in MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        # Hybrid Encrypt sensitive message payload using AES-256 + RSA-2048
        raw_message = alert_data.get("message", "")
        enc_res = hybrid_encrypt_patient_data(raw_message)
        encrypted_message = enc_res.get("encrypted_data", raw_message)
        encrypted_key = enc_res.get("encrypted_key", "")

        with conn.cursor() as cursor:
            sql = """
            INSERT INTO alerts (
                id, patient_id, patient_name, title, event_type, message,
                time_str, timestamp, severity, risk_level, confidence, location,
                acknowledged, caregiver_status, acknowledged_by, acknowledged_at,
                escalated_at, escalation_reason, screenshot_url, ntfy_status, source, raw_json
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                acknowledged=VALUES(acknowledged),
                caregiver_status=VALUES(caregiver_status),
                acknowledged_by=VALUES(acknowledged_by),
                acknowledged_at=VALUES(acknowledged_at),
                escalated_at=VALUES(escalated_at),
                escalation_reason=VALUES(escalation_reason);
            """
            cursor.execute(sql, (
                alert_data.get("id"),
                alert_data.get("patientId", "P-101"),
                alert_data.get("patientName", "Patient"),
                alert_data.get("title", "Alert"),
                alert_data.get("eventType", "ALERT"),
                encrypted_message,
                alert_data.get("time", ""),
                alert_data.get("timestamp", datetime.now().isoformat()),
                alert_data.get("severity", "medium"),
                alert_data.get("riskLevel", "medium"),
                float(alert_data.get("confidence", 0.0)),
                alert_data.get("location", "Bedroom"),
                1 if alert_data.get("acknowledged") else 0,
                alert_data.get("caregiverStatus", "pending"),
                alert_data.get("acknowledgedBy"),
                alert_data.get("acknowledgedAt"),
                alert_data.get("escalatedAt"),
                alert_data.get("escalationReason"),
                alert_data.get("screenshotUrl"),
                alert_data.get("ntfyStatus", "delivered"),
                alert_data.get("source", "simulation"),
                json.dumps(alert_data)
            ))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to save alert to MySQL: {e}")
        return False


def db_get_alerts() -> Optional[List[Dict[str, Any]]]:
    """Retrieve all alerts from MySQL ordered by created_at DESC."""
    if not IS_MYSQL_AVAILABLE:
        return None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC;")
            rows = cursor.fetchall()
        conn.close()

        alerts = []
        for r in rows:
            if r.get("raw_json"):
                try:
                    alert_dict = json.loads(r["raw_json"])
                    # Update fields from DB columns
                    alert_dict["acknowledged"] = bool(r["acknowledged"])
                    alert_dict["caregiverStatus"] = r["caregiver_status"]
                    alert_dict["acknowledgedBy"] = r["acknowledged_by"]
                    alert_dict["acknowledgedAt"] = r["acknowledged_at"]
                    alert_dict["escalatedAt"] = r["escalated_at"]
                    alert_dict["escalationReason"] = r["escalation_reason"]
                    alerts.append(alert_dict)
                    continue
                except Exception:
                    pass
            
            alerts.append({
                "id": r["id"],
                "patientId": r["patient_id"],
                "patientName": r["patient_name"],
                "title": r["title"],
                "eventType": r["event_type"],
                "message": r["message"],
                "time": r["time_str"],
                "timestamp": r["timestamp"],
                "severity": r["severity"],
                "riskLevel": r["risk_level"],
                "confidence": r["confidence"],
                "location": r["location"],
                "acknowledged": bool(r["acknowledged"]),
                "caregiverStatus": r["caregiver_status"],
                "acknowledgedBy": r["acknowledged_by"],
                "acknowledgedAt": r["acknowledged_at"],
                "escalatedAt": r["escalated_at"],
                "escalationReason": r["escalation_reason"],
                "screenshotUrl": r["screenshot_url"],
                "ntfyStatus": r["ntfy_status"],
                "source": r["source"]
            })
        return alerts
    except Exception as e:
        logger.error(f"Failed to fetch alerts from MySQL: {e}")
        return None


def db_acknowledge_alert(alert_id: str, action_type: str, caregiver_name: str, ack_at: str) -> bool:
    """Mark alert as acknowledged in MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        status = "checking" if action_type == "checking" else "resolved"
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE alerts
                SET acknowledged=1, caregiver_status=%s, acknowledged_by=%s, acknowledged_at=%s
                WHERE id=%s;
            """, (status, caregiver_name, ack_at, alert_id))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to acknowledge alert in MySQL: {e}")
        return False


def db_escalate_alert(alert_id: str, reason: str, escalated_at: str) -> bool:
    """Escalate alert in MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE alerts
                SET caregiver_status='escalated', escalated_at=%s, escalation_reason=%s
                WHERE id=%s;
            """, (escalated_at, reason, alert_id))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to escalate alert in MySQL: {e}")
        return False


# ==============================================================================
# APPOINTMENTS CRUD OPERATIONS
# ==============================================================================

def db_save_appointment(apt_data: Dict[str, Any]) -> bool:
    """Save an appointment to MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO appointments (
                id, patient_id, patient_name, doctor_id, doctor_name, specialty,
                hospital, distance_km, apt_date, apt_time, status, apt_type, reason, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status=VALUES(status);
            """
            cursor.execute(sql, (
                apt_data.get("id"),
                apt_data.get("patientId", "P-101"),
                apt_data.get("patientName", "Rahul Sharma"),
                apt_data.get("doctorId", ""),
                apt_data.get("doctorName", ""),
                apt_data.get("specialty", ""),
                apt_data.get("hospital", ""),
                float(apt_data.get("distanceKm", 0.0)),
                apt_data.get("date", ""),
                apt_data.get("time", ""),
                apt_data.get("status", "confirmed"),
                apt_data.get("type", "in_person"),
                apt_data.get("reason", ""),
                apt_data.get("createdAt", datetime.now().isoformat())
            ))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to save appointment to MySQL: {e}")
        return False


def db_get_appointments(patient_id: str = "P-101") -> Optional[List[Dict[str, Any]]]:
    """Retrieve appointments for a patient from MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM appointments WHERE patient_id=%s ORDER BY apt_date ASC, apt_time ASC;", (patient_id,))
            rows = cursor.fetchall()
        conn.close()

        apts = []
        for r in rows:
            apts.append({
                "id": r["id"],
                "patientId": r["patient_id"],
                "patientName": r["patient_name"],
                "doctorId": r["doctor_id"],
                "doctorName": r["doctor_name"],
                "specialty": r["specialty"],
                "hospital": r["hospital"],
                "distanceKm": r["distance_km"],
                "date": r["apt_date"],
                "time": r["apt_time"],
                "status": r["status"],
                "type": r["apt_type"],
                "reason": r["reason"],
                "createdAt": r["created_at"]
            })
        return apts
    except Exception as e:
        logger.error(f"Failed to fetch appointments from MySQL: {e}")
        return None


def db_cancel_appointment(apt_id: str) -> bool:
    """Cancel an appointment in MySQL."""
    if not IS_MYSQL_AVAILABLE:
        return False
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("UPDATE appointments SET status='cancelled' WHERE id=%s;", (apt_id,))
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to cancel appointment in MySQL: {e}")
        return False

if __name__ == "__main__":
    init_db()
