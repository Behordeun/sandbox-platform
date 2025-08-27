#!/usr/bin/env python3
"""Mock data generator for DPI sandbox testing"""

import json
import random

# Nigerian names for realistic testing
NIGERIAN_FIRST_NAMES = [
    "Adebayo",
    "Chioma",
    "Emeka",
    "Fatima",
    "Ibrahim",
    "Kemi",
    "Olumide",
    "Aisha",
    "Chinedu",
    "Folake",
    "Musa",
    "Ngozi",
    "Tunde",
    "Zainab",
]

NIGERIAN_LAST_NAMES = [
    "Ogundimu",
    "Okoro",
    "Adebayo",
    "Mohammed",
    "Okafor",
    "Adeleke",
    "Bello",
    "Chukwu",
    "Danjuma",
    "Eze",
    "Garba",
    "Hassan",
    "Igwe",
]


def generate_nin():
    """Generate mock NIN for testing"""
    return "".join([str(random.randint(0, 9)) for _ in range(11)])


def generate_bvn():
    """Generate mock BVN for testing"""
    return "".join([str(random.randint(0, 9)) for _ in range(11)])


def generate_phone():
    """Generate Nigerian phone number"""
    prefixes = ["0803", "0806", "0813", "0816", "0703", "0706", "0708"]
    return f"+234{random.choice(prefixes)[1:]}{random.randint(1000000, 9999999)}"


def generate_test_user():
    """Generate complete test user data"""
    first_name = random.choice(NIGERIAN_FIRST_NAMES)
    last_name = random.choice(NIGERIAN_LAST_NAMES)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{first_name.lower()}.{last_name.lower()}@test.ng",
        "phone": generate_phone(),
        "nin": generate_nin(),
        "bvn": generate_bvn(),
        "date_of_birth": f"19{random.randint(80, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
    }


if __name__ == "__main__":
    print("🇳🇬 DPI Sandbox Mock Data Generator")
    print("=" * 40)

    # Generate 5 test users
    for i in range(5):
        user = generate_test_user()
        print(f"\nTest User {i+1}:")
        print(json.dumps(user, indent=2))

    print("\n📱 Test Phone Numbers:")
    for i in range(3):
        print(f"  {generate_phone()}")

    print("\n🆔 Test NIDs:")
    for i in range(3):
        print(f"  {generate_nin()}")

    print("\n🏦 Test BVNs:")
    for i in range(3):
        print(f"  {generate_bvn()}")
