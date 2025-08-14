# Unified Motor Movement Endpoint with Retry Logic

The motor movement functions have been combined into a single endpoint with built-in retry verification to ensure accurate positioning.

## Endpoint: `/move_motor/{amount}/{relative}`

### Parameters:
- `amount` (float): Motor position or movement amount
- `relative` (int): Flag to determine movement type
  - `0`: Absolute movement to position
  - `1`: Relative movement by amount

## Retry Mechanism:
The endpoint automatically verifies that the motor reached the target position and retries if needed:
- **Max Retries**: 5 attempts (configurable in `config.py`)
- **Position Tolerance**: 0.01 motor units (configurable)
- **Settle Time**: 0.5 seconds after each movement
- **Retry Delay**: 1.0 seconds between attempts

## Usage Examples:

### 1. Absolute Movement
```
GET /move_motor/45.0/0
```
- Moves motor to absolute position 45.0
- Verifies position and retries if needed

### 2. Relative Movement
```
GET /move_motor/10.0/1
```
- Moves motor by +10.0 from current position
- Verifies final position matches target

### 3. Negative Relative Movement
```
GET /move_motor/-5.0/1
```
- Moves motor by -5.0 from current position

## Response Format (Success):
```json
{
    "message": "Motor moved successfully (absolute movement)",
    "target_position": 45.0,
    "actual_position": 45.001,
    "position_error": 0.001,
    "target_angle_degrees": 126.5625,
    "movement_amount": 45.0,
    "movement_type": "absolute",
    "attempts_required": 1
}
```

## Response Format (Failure):
```json
{
    "detail": "Motor position verification failed after 5 attempts. Target: 320.0, Actual: 1.0, Error: 319.0"
}
```

## cURL Examples:
```bash
# Absolute movement
curl "http://localhost:8000/move_motor/45.0/0"

# Relative movement
curl "http://localhost:8000/move_motor/10.0/1"

# Move to problematic position (will retry automatically)
curl "http://localhost:8000/move_motor/320.0/0"
```

## Configuration (config.py):
```python
MOTOR_MAX_RETRIES = 5           # Maximum retry attempts
MOTOR_POSITION_TOLERANCE = 0.01 # Position verification tolerance
MOTOR_RETRY_DELAY = 1.0         # Delay between retries (seconds)
MOTOR_SETTLE_TIME = 0.5         # Motor settling time (seconds)
```

## Benefits:
- **Robust Operation**: Automatically handles cases where motor doesn't reach target
- **Position Verification**: Confirms actual position matches target within tolerance
- **Configurable Retries**: Adjustable retry count and timing parameters
- **Detailed Logging**: Console output shows each attempt and verification
- **Dynamic EPICS Paths**: Uses `which caget/caput` for portability
- **Comprehensive Response**: Returns both target and actual positions
