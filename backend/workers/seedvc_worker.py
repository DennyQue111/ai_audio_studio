import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument("--python", required=True)
parser.add_argument("--repo", required=True)
parser.add_argument("--source", required=True)
parser.add_argument("--reference", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--models", required=True)
args = parser.parse_args()

command = [
    args.python,
    f"{args.repo}/inference_v2.py",
    "--source",
    args.source,
    "--target",
    args.reference,
    "--output",
    args.output,
    "--diffusion-steps",
    "25",
    "--intelligibility-cfg-rate",
    "0.7",
    "--similarity-cfg-rate",
    "0.7",
    "--convert-style",
    "true",
    "--cfm-checkpoint-path",
    f"{args.models}/v2/cfm_small.pth",
    "--ar-checkpoint-path",
    f"{args.models}/v2/ar_base.pth",
]
result = subprocess.run(command, capture_output=True, text=True)
if result.returncode:
    raise SystemExit((result.stderr or result.stdout or "Seed-VC 转换失败")[-4000:])
