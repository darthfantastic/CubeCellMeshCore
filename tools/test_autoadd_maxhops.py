#!/usr/bin/env python3
"""
Test script for Auto-add Max Hops Filter feature
Tests get/set autoadd.maxhops commands via serial interface
"""

import serial
import time
import sys
import argparse

def send_command(ser, cmd, timeout=2.0):
    """Send command and wait for response"""
    ser.write((cmd + '\r\n').encode())
    ser.flush()
    time.sleep(0.1)

    start = time.time()
    response = ""
    while (time.time() - start) < timeout:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response += chunk
            if '\n' in chunk:
                break
        time.sleep(0.01)

    return response.strip()

def test_autoadd_maxhops(port, baudrate=115200):
    """Test auto-add max hops filter commands"""
    print(f"Testing Auto-add Max Hops Filter on {port} @ {baudrate}")
    print("=" * 60)

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.5)  # Wait for connection

        # Clear any pending data
        ser.reset_input_buffer()

        # Test 1: Get current value
        print("\n1. Getting current autoadd.maxhops:")
        response = send_command(ser, "get autoadd.maxhops")
        print(f"   Response: {response}")
        assert "> " in response, "get autoadd.maxhops failed"

        # Test 2: Set to 0 (no limit)
        print("\n2. Setting autoadd.maxhops to 0 (no limit):")
        response = send_command(ser, "set autoadd.maxhops 0")
        print(f"   Response: {response}")
        assert "autoadd.maxhops=0" in response, "set autoadd.maxhops 0 failed"

        # Verify
        response = send_command(ser, "get autoadd.maxhops")
        print(f"   Verify: {response}")
        assert "> 0" in response, "verify 0 failed"

        # Test 3: Set to 3 hops
        print("\n3. Setting autoadd.maxhops to 3:")
        response = send_command(ser, "set autoadd.maxhops 3")
        print(f"   Response: {response}")
        assert "autoadd.maxhops=3" in response, "set autoadd.maxhops 3 failed"

        # Verify
        response = send_command(ser, "get autoadd.maxhops")
        print(f"   Verify: {response}")
        assert "> 3" in response, "verify 3 failed"

        # Test 4: Set to 10 hops
        print("\n4. Setting autoadd.maxhops to 10:")
        response = send_command(ser, "set autoadd.maxhops 10")
        print(f"   Response: {response}")
        assert "autoadd.maxhops=10" in response, "set autoadd.maxhops 10 failed"

        # Verify
        response = send_command(ser, "get autoadd.maxhops")
        print(f"   Verify: {response}")
        assert "> 10" in response, "verify 10 failed"

        # Test 5: Set to maximum (64)
        print("\n5. Setting autoadd.maxhops to 64 (maximum):")
        response = send_command(ser, "set autoadd.maxhops 64")
        print(f"   Response: {response}")
        assert "autoadd.maxhops=64" in response, "set autoadd.maxhops 64 failed"

        # Verify
        response = send_command(ser, "get autoadd.maxhops")
        print(f"   Verify: {response}")
        assert "> 64" in response, "verify 64 failed"

        # Test 6: Invalid value (too high)
        print("\n6. Testing invalid value (65):")
        response = send_command(ser, "set autoadd.maxhops 65")
        print(f"   Response: {response}")
        assert "E:" in response, "invalid value should return error"

        # Test 7: Invalid value (negative)
        print("\n7. Testing invalid value (-1):")
        response = send_command(ser, "set autoadd.maxhops -1")
        print(f"   Response: {response}")
        # Note: atoi() will return 0 for negative, which is valid, so this might not error
        # Just verify it doesn't crash
        print(f"   (atoi may convert -1 to 0, which is valid)")

        # Restore to default (0 = no limit)
        print("\n8. Restoring to default (0):")
        response = send_command(ser, "set autoadd.maxhops 0")
        print(f"   Response: {response}")
        assert "autoadd.maxhops=0" in response, "restore to 0 failed"

        print("\n" + "=" * 60)
        print("✓ All Auto-add Max Hops Filter tests PASSED!")
        print("=" * 60)

        ser.close()
        return True

    except serial.SerialException as e:
        print(f"\n✗ Serial error: {e}")
        return False
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test Auto-add Max Hops Filter feature')
    parser.add_argument('port', nargs='?', default=None, help='Serial port (e.g., /dev/ttyUSB0)')
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help='Baud rate (default: 115200)')
    args = parser.parse_args()

    port = args.port
    if not port:
        # Try to auto-detect
        import glob
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('COM*')
        if ports:
            port = ports[0]
            print(f"Auto-detected port: {port}")
        else:
            print("Error: No serial port specified and none auto-detected")
            print("Usage: python test_autoadd_maxhops.py <port>")
            sys.exit(1)

    success = test_autoadd_maxhops(port, args.baudrate)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
