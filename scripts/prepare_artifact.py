import json

with open('build/ProofWork.bin', 'r') as f:
    bytecode = f.read().strip()

with open('build/ProofWork.abi', 'r') as f:
    abi = json.load(f)

artifact = {
    'abi': abi,
    'bytecode': '0x' + bytecode
}

with open('build/ProofWork.json', 'w') as f:
    json.dump(artifact, f)

print("Artifact created at build/ProofWork.json")
