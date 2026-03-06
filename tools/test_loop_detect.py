#!/usr/bin/env python3
"""
Test script for Loop Detection feature
Tests get/set loop.detect commands via serial interface
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

def test_loop_detect(port, baudrate=115200):
    """Test loop detection commands"""
    print(f"Testing Loop Detection on {port} @ {baudrate}")
    print("=" * 60)

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.5)  # Wait for connection

        # Clear any pending data
        ser.reset_input_buffer()

        # Test 1: Get current mode
        print("\n1. Getting current loop.detect mode:")
        response = send_command(ser, "get loop.detect")
        print(f"   Response: {response}")
        assert "> " in response, "get loop.detect failed"

        # Test 2: Set to OFF
        print("\n2. Setting loop.detect to OFF:")
        response = send_command(ser, "set loop.detect off")
        print(f"   Response: {response}")
        assert "loop.detect=off" in response, "set loop.detect off failed"

        # Verify
        response = send_command(ser, "get loop.detect")
        print(f"   Verify: {response}")
        assert "> off" in response, "verify off failed"

        # Test 3: Set to MINIMAL
        print("\n3. Setting loop.detect to MINIMAL:")
        response = send_command(ser, "set loop.detect minimal")
        print(f"   Response: {response}")
        assert "loop.detect=minimal" in response, "set loop.detect minimal failed"

        # Verify
        response = send_command(ser, "get loop.detect")
        print(f"   Verify: {response}")
        assert "> minimal" in response, "verify minimal failed"

        # Test 4: Set to MODERATE
        print("\n4. Setting loop.detect to MODERATE:")
        response = send_command(ser, "set loop.detect moderate")
        print(f"   Response: {response}")
        assert "loop.detect=moderate" in response, "set loop.detect moderate failed"

        # Verify
        response = send_command(ser, "get loop.detect")
        print(f"   Verify: {response}")
        assert "> moderate" in response, "verify moderate failed"

        # Test 5: Set to STRICT (default)
        print("\n5. Setting loop.detect to STRICT:")
        response = send_command(ser, "set loop.detect strict")
        print(f"   Response: {response}")
        assert "loop.detect=strict" in response, "set loop.detect strict failed"

        # Verify
        response = send_command(ser, "get loop.detect")
        print(f"   Verify: {response}")
        assert "> strict" in response, "verify strict failed"

        # Test 6: Invalid mode
        print("\n6. Testing invalid mode:")
        response = send_command(ser, "set loop.detect invalid")
        print(f"   Response: {response}")
        assert "E:" in response, "invalid mode should return error"

        print("\n" + "=" * 60)
        print("✓ All Loop Detection tests PASSED!")
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
    parser = argparse.ArgumentParser(description='Test Loop Detection feature')
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
            print("Usage: python test_loop_detect.py <port>")
            sys.exit(1)

    success = test_loop_detect(port, args.baudrate)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
