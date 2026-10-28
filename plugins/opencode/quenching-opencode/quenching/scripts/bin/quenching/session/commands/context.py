"""Generated Codex refusal: source transcript tokens cannot measure this host."""
from quenching.common.output import refuse

def cmd_context(args) -> int:
    return refuse({"code": "se-codex-telemetry-unavailable",
                   "message": "Codex token usage not measured: use host telemetry when available; source transcript accounting is unsupported."}, args.json)
