"""Fresh artwork for reels. Runs on the GitHub Actions runner (open internet), not on a laptop.
Routes (open source, run on the runner CPU): lcm = SDXL + LCM-LoRA (quality), turbo = SDXL-Turbo (fast). pollinations.ai was tried 30 Oct: 1 free image, then HTTP 402 and a watermark, so it is out.
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
    """SDXL-Turbo, open source, ~1 min per image on the 4-core runner."""
    import torch
    from diffusers import AutoPipelineForText2Image
    pipe = getattr(sd_turbo, "pipe", None)
    if pipe is None:
        pipe = sd_turbo.pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float32)
        pipe.enable_attention_slicing()
    g = torch.Generator().manual_seed(seed)
    im = pipe(prompt=f"{prompt}, {STYLE}", num_inference_steps=4, guidance_scale=0.0, height=1024, width=576, generator=g).images[0]
    im.resize((1080, 1920), 1).save(path, quality=92)

def sdxl_lcm(prompt, path, seed):
    """SDXL base + LCM-LoRA (8 steps), open source, higher quality, ~4-6 min per image on the runner."""
    import torch
    from diffusers import DiffusionPipeline, LCMScheduler
    pipe = getattr(sdxl_lcm, "pipe", None)
    if pipe is None:
        pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float32, variant="fp16", use_safetensors=True)
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        pipe.load_lora_weights("latent-consistency/lcm-lora-sdxl"); pipe.fuse_lora()
        pipe.enable_attention_slicing(); pipe.enable_vae_slicing(); sdxl_lcm.pipe = pipe
    g = torch.Generator().manual_seed(seed)
    im = pipe(prompt=f"{prompt}, {STYLE}", negative_prompt="text, letters, watermark, logo, blurry, cartoon, clipart, emoji, childish",
              num_inference_steps=8, guidance_scale=1.5, height=1344, width=768, generator=g).images[0]
    im.resize((1080, 1920), 1).save(path, quality=92)

log = []
for i, (name, prompt) in enumerate(spec.items()):
    path = f"{out}/{name}.jpg"
    if os.path.exists(path): continue
    seed = int(time.time()) % 100000 + i * 7919
    ROUTES = {"turbo": sd_turbo, "lcm": sdxl_lcm}
    for route in os.environ.get("ART_ROUTES", "lcm,turbo").split(","):
        try:
            t0 = time.time(); ROUTES[route](prompt, path, seed)
            log.append(f"{name}: {route} ok {time.time() - t0:.0f}s"); break
        except Exception as e:
            log.append(f"{name}: {route} failed: {str(e)[:120]}")
    else:
        log.append(f"{name}: NO IMAGE")
print("\n".join(log)); json.dump(log, open(f"{out}/_log.json", "w"), indent=1)
