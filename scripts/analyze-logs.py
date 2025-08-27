#!/usr/bin/env python3
"""
Log Analysis Script for DPI Sandbox Platform
Analyzes user activities and service usage patterns
"""

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime


def parse_log_line(line):
    """Parse a log line and extract structured data."""
    try:
        # Extract timestamp
        timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if not timestamp_match:
            return None

        timestamp = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S")

        # Extract JSON data if present
        json_match = re.search(r"({.*})", line)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                data["parsed_timestamp"] = timestamp
                return data
            except json.JSONDecodeError:
                pass

        # Extract basic info for non-JSON logs
        return {"parsed_timestamp": timestamp, "raw_line": line.strip()}
    except Exception:
        return None


def update_user_stats(
    stats, _data, timestamp, service, activity_type, success, client_ip
):
    stats["total_requests"] += 1
    if success:
        stats["successful_requests"] += 1
    else:
        stats["failed_requests"] += 1
    stats["services_used"].add(service)
    stats["activity_types"][activity_type] += 1
    stats["unique_ips"].add(client_ip)
    if not stats["first_seen"] or timestamp < stats["first_seen"]:
        stats["first_seen"] = timestamp
    if not stats["last_seen"] or timestamp > stats["last_seen"]:
        stats["last_seen"] = timestamp


def print_user_summary(user_stats):
    print("\n👥 USER ACTIVITY SUMMARY")
    print("=" * 50)
    print(f"Total unique users: {len(user_stats)}")
    print("\n🔥 TOP 10 MOST ACTIVE USERS:")
    sorted_users = sorted(
        user_stats.items(), key=lambda x: x[1]["total_requests"], reverse=True
    )
    for i, (user_id, stats) in enumerate(sorted_users[:10], 1):
        success_rate = (
            (stats["successful_requests"] / stats["total_requests"] * 100)
            if stats["total_requests"] > 0
            else 0
        )
        print(
            f"{i:2d}. User {user_id}: {stats['total_requests']} requests ({success_rate:.1f}% success)"
        )
        print(f"    Services: {', '.join(stats['services_used'])}")
        print(f"    Duration: {stats['first_seen']} to {stats['last_seen']}")


def print_service_usage(service_stats):
    print("\n🔧 SERVICE USAGE:")
    for service, count in service_stats.most_common():
        print(f"  {service}: {count} requests")


def print_peak_hours(hourly_activity):
    print("\n⏰ PEAK ACTIVITY HOURS:")
    sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
    for hour, count in sorted_hours[:10]:
        print(f"  {hour}: {count} requests")


def analyze_user_activity(log_file):
    """Analyze user activity patterns."""
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found")
        return

    user_stats = defaultdict(
        lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "services_used": set(),
            "activity_types": Counter(),
            "first_seen": None,
            "last_seen": None,
            "unique_ips": set(),
        }
    )
    service_stats = Counter()
    hourly_activity = defaultdict(int)

    print(f"\n📊 Analyzing {log_file}...")

    def process_line(line):
        data = parse_log_line(line)
        if not data:
            return
        timestamp = data.get("parsed_timestamp")
        user_id = data.get("user_id")
        service = data.get("service", "unknown")
        activity_type = data.get("activity_type", "unknown")
        success = data.get("success", True)
        client_ip = data.get("client_ip", "unknown")
        if timestamp:
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            hourly_activity[hour_key] += 1
        if user_id:
            stats = user_stats[user_id]
            update_user_stats(
                stats, data, timestamp, service, activity_type, success, client_ip
            )
        service_stats[service] += 1

    with open(log_file, "r") as f:
        for line in f:
            process_line(line)

    print_user_summary(user_stats)
    print_service_usage(service_stats)
    print_peak_hours(hourly_activity)


def _parse_security_event(line):
    """Parse a line for security event information."""
    data = parse_log_line(line)
    if not data:
        return None
    if "SECURITY_EVENT" in line or "ACCESS_DENIED" in line:
        return data
    return None


def _collect_failed_logins(log_file):
    """Collect failed login attempts and suspicious IPs from log file."""
    failed_logins = defaultdict(list)
    suspicious_ips = defaultdict(int)
    with open(log_file, "r") as f:
        for line in f:
            data = _parse_security_event(line)
            if not data:
                continue
            client_ip = data.get("client_ip", "unknown")
            activity_type = data.get("activity_type")
            success = data.get("success", True)
            if not success and activity_type == "user_login":
                failed_logins[client_ip].append(data)
                suspicious_ips[client_ip] += 1
    return failed_logins, suspicious_ips


def _report_failed_logins(failed_logins, suspicious_ips):
    """Report failed login attempts and suspicious IPs."""
    print("\n🚨 SECURITY ANALYSIS:")
    print("=" * 50)
    if failed_logins:
        print("\n❌ FAILED LOGIN ATTEMPTS:")
        for ip, attempts in sorted(
            suspicious_ips.items(), key=lambda x: x[1], reverse=True
        ):
            if attempts > 3:  # Suspicious threshold
                print(f"  🚩 {ip}: {attempts} failed attempts")
                recent_attempts = [
                    a for a in failed_logins[ip] if a.get("parsed_timestamp")
                ]
                if recent_attempts:
                    latest = max(recent_attempts, key=lambda x: x["parsed_timestamp"])
                    print(f"     Latest attempt: {latest.get('parsed_timestamp')}")
    else:
        print("✅ No suspicious login activity detected")


def analyze_security_events(log_file):
    """Analyze security-related events."""
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found")
        return

    print(f"\n🔒 Analyzing {log_file}...")
    failed_logins, suspicious_ips = _collect_failed_logins(log_file)
    _report_failed_logins(failed_logins, suspicious_ips)


def main():
    parser = argparse.ArgumentParser(description="Analyze DPI Sandbox Platform logs")
    parser.add_argument(
        "--user-activity", action="store_true", help="Analyze user activity logs"
    )
    parser.add_argument(
        "--security", action="store_true", help="Analyze security events"
    )
    parser.add_argument("--all", action="store_true", help="Analyze all log types")
    parser.add_argument(
        "--logs-dir", default="services/logs", help="Directory containing log files"
    )

    args = parser.parse_args()

    if not any([args.user_activity, args.security, args.all]):
        args.all = True

    print("🇳🇬 DPI Sandbox Platform - Log Analysis")
    print("=" * 60)

    if args.all or args.user_activity:
        analyze_user_activity(os.path.join(args.logs_dir, "user_activity.log"))
        analyze_user_activity(os.path.join(args.logs_dir, "api_access.log"))

    if args.all or args.security:
        analyze_security_events(os.path.join(args.logs_dir, "security_events.log"))
        analyze_security_events(os.path.join(args.logs_dir, "user_activity.log"))

    print(
        f"\n📈 Analysis complete! Check individual log files in {args.logs_dir}/ for detailed information."
    )


if __name__ == "__main__":
    main()
