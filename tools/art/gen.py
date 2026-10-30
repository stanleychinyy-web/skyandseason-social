"""Fresh artwork for reels. Runs on the GitHub Actions runner (open internet), not on a laptop.
Route A: pollinations.ai (free, no key). Route B (fallback): Stable Diffusion Turbo on CPU (open source).
python3 tools/art/gen.py <out_dir> <prompts.json>   # prompts.json = {"name": "prompt", ...}
"""
import json, os, sys, time, urllib.parse, urllib.request

out, spec = sys.argv[1], json.load(open(sys.argv[2]))
os.makedirs(out, exist_ok=True)
STYLE = ("cinematic vertical painting, moody editorial photography look, rich texture, soft volumetric light, "
         "no text, no letters, no watermark, no people faces, high detail")

def pollinations(prompt, path, seed):
    q = urllib.parse.quote(f"{prompt}, {STYLE}")
    url = f"https://image.pollinations.ai/prompt/{q}?width=1080&height=1920&model=flux&nologo=true&seed={seed}&enhance=false"
    req = urllib.request.Request(url, headers={"User-Agent": "skyandseason-reels/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    if len(data) < 20000: raise RuntimeError(f"tiny response {len(data)}")
    open(path, "wb").write(data)

def sd_turbo(prompt, path, seed):
    import torch
    from diffusers import AutoPipelineForText2Image
    pipe = sd_turbo.pipe = getattr(sd_turbo, "pipe", None) or AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)
    g = torch.Generator().manual_seed(seed)
    im = pipe(prompt=f"{prompt}, {STYLE}", num_inference_steps=2, guidance_scale=0.0, height=768, width=432, generator=g).images[0]
    im.resize((1080, 1920)).save(path, quality=92)

log = []
for i, (name, prompt) in enumerate(spec.items()):
    path = f"{out}/{name}.jpg"; seed = int(time.time()) % 100000 + i * 7919
    for route in ("pollinations", "sd_turbo"):
        try:
            t0 = time.time(); (pollinations if route == "pollinations" else sd_turbo)(prompt, path, seed)
            log.append(f"{name}: {route} ok {time.time() - t0:.0f}s"); break
        except Exception as e:
            log.append(f"{name}: {route} failed: {str(e)[:120]}")
    else:
        log.append(f"{name}: NO IMAGE")
print("\n".join(log)); json.dump(log, open(f"{out}/_log.json", "w"), indent=1)
