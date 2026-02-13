# Phase 2: ONNX + MQL5 EA Roadmap

1. Export sklearn logistic model to ONNX with `skl2onnx`.
2. Add `scripts/export_onnx.py` to save `models/model.onnx`.
3. Build MQL5 Expert Advisor skeleton that:
   - Loads ONNX model from `MQL5/Files/model.onnx`
   - Builds feature vector on each new bar
   - Runs ONNX inference
   - Applies same risk filters (spread, daily loss, max trades)
   - Sends orders via native MQL5 trade classes
4. Validate parity between Python signal and EA signal for same bars.

TODOs are documented in README.
