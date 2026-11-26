"""Create a Helico pet ZIP and catalog entry from a manifest and WebP atlases."""

import argparse
import base64
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from zipfile import ZipFile, ZipInfo

from PIL import Image


def pack_release(assets, release, repository="run-bigpig/helico"):
    manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("rig"), dict):
        raise ValueError("expected a manifest with a rig object")
    pet_id, version = manifest["id"], manifest["version"]
    if manifest["format"] != 1 or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", pet_id):
        raise ValueError("expected a Format 1 manifest with a valid pet ID")
    if pet_id in {"helico-butterfly", "helico-dusk", "clay", "moss", "zip"}:
        raise ValueError(f"{pet_id} is reserved, choose a new pet ID")
    if not re.fullmatch(r"(?:0|[1-9][0-9]{0,8})(?:\.(?:0|[1-9][0-9]{0,8})){2}", version):
        raise ValueError("expected a version such as 1.0.0")
    if not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("expected a GitHub owner/repository")
    for field in ("name", "description"):
        for language in ("zh", "en"):
            value = manifest[field][language]
            if not isinstance(value, str) or not 1 <= len(value.encode("utf-16-le")) // 2 <= 160:
                raise ValueError(f"{field}.{language} must contain 1–160 UTF-16 code units")

    dimensions = {"poses.webp": (1024, 1024), "walk.webp": (1024, 768), "face.webp": (288, 80)}
    if manifest["rig"].get("typing") is not None:
        dimensions.update({"typing.webp": (512, 512), "typing-base.webp": (512, 512)})
    files = {}
    manifest["assets"] = {}
    for name, size in dimensions.items():
        path = assets / name
        if path.stat().st_size > 2 << 20:
            raise ValueError(f"{name} exceeds 2 MiB")
        data = path.read_bytes()
        with Image.open(BytesIO(data)) as sheet:
            if sheet.format != "WEBP" or sheet.size != size or sheet.n_frames != 1:
                raise ValueError(f"{name} must be a static {size[0]} × {size[1]} WebP")
            sheet.load()
        files[name] = data
        manifest["assets"][name] = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    files["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(files["manifest.json"]) > 64 << 10:
        raise ValueError("the manifest exceeds 64 KiB")

    package = BytesIO()
    with ZipFile(package, "w") as archive:
        for name in sorted(files):
            archive.writestr(ZipInfo(name), files[name])
    zipped = package.getvalue()
    if len(zipped) > 4 << 20:
        raise ValueError("the pet ZIP exceeds 4 MiB")

    preview = BytesIO()
    with Image.open(BytesIO(files["poses.webp"])) as sheet:
        idle = sheet.crop((0, 0, 256, 256))
        idle.thumbnail((160, 160), Image.Resampling.LANCZOS)
        idle.save(preview, format="WEBP", lossless=True, method=6)
    preview_url = "data:image/webp;base64," + base64.b64encode(preview.getvalue()).decode("ascii")
    if len(preview_url) > 48000:
        raise ValueError("the preview exceeds 48,000 characters, simplify the idle sprite")

    stem = f"{pet_id}-{version}"
    entry = {key: manifest[key] for key in ("id", "version", "name", "description")}
    entry.update(
        size=len(zipped), sha256=hashlib.sha256(zipped).hexdigest(),
        url=f"https://github.com/{repository}/releases/download/{pet_id}-v{version}/{stem}.zip",
        preview=preview_url,
    )
    release.mkdir(parents=True, exist_ok=True)
    (release / f"{stem}.zip").write_bytes(zipped)
    (release / f"{stem}-preview.webp").write_bytes(preview.getvalue())
    (release / "catalog-v2.json").write_text(
        json.dumps({"format": 1, "pets": [entry]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assets", type=Path, help="directory with manifest.json and the WebP atlases")
    parser.add_argument("output", type=Path)
    parser.add_argument("--repository", default="run-bigpig/helico", help="GitHub owner/repository for the release URL")
    args = parser.parse_args()
    try:
        pack_release(args.assets, args.output, args.repository)
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Could not package the pet: {error}\n")
