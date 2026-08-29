# Diagnosis and ML

## Diagnosis Engine

File:

```text
backend/diagnosis_engine.py
```

The diagnosis engine converts raw monitoring signals into professional operational root-cause categories. It should never return vague messages such as `Camera Error`.

## Diagnosis Categories

Supported diagnosis categories:

- Power Failure
- PoE Failure
- Switch Port Failure
- Ethernet Cable Failure
- Camera Hardware Failure
- Camera Firmware Failure
- RTSP Service Failure
- Authentication Failure
- IP Conflict
- High Packet Loss
- High Latency
- Unknown Failure

## Diagnosis Output

Every diagnosis should include:

- Diagnosis
- Confidence percentage
- Severity
- Recommended solution
- Timestamp
- Resolution status

## Recommendation Engine

Recommendations are stored centrally in the backend so they can be reused by alerts, diagnosis history, reports, and UI pages.

Example diagnosis:

```text
PoE Failure
```

Example recommendation:

```text
Verify PoE output, inspect the switch port, check the Ethernet cable, and confirm camera LED status.
```

## Diagnosis History

Diagnosis records are stored in `diagnosis_history`.

Typical record includes:

- Camera ID
- Camera name
- Diagnosis
- Confidence
- Severity
- Recommendation
- Resolution status
- Created timestamp
- Resolved timestamp

## ML Module

The ML module is preserved and exposed through read-only API data.

Primary endpoint:

```text
/api/ml/statistics
```

The frontend displays backend-provided values only:

- Model Status
- Prediction Accuracy
- Prediction Coverage
- Last Prediction
- High Risk Cameras

No fake ML values should be generated in the frontend.

## Prediction Data

Prediction endpoints:

```text
/api/predictions
/api/predictions/{camera_id}
/api/predictions/run
```

The run endpoint is protected and should be used by authorized users only.

## Operational Use

Diagnosis and ML help operations teams answer:

- Which cameras are most at risk?
- Is the issue likely camera-side or network-side?
- Which switch may be affecting multiple cameras?
- What action should maintenance perform first?
