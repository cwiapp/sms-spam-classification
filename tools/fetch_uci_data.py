"""Fetch the pinned UCI SMS Spam Collection snapshot into ignored raw data."""

from pathlib import Path
import urllib.request

from sms_filter.dataset import EXPECTED_SHA256, SOURCE_URL, sha256


ROOT = Path(__file__).resolve().parents[1]
destination = ROOT / "data" / "raw" / "sms_spam_collection_uci.zip"
destination.parent.mkdir(parents=True, exist_ok=True)

if destination.exists():
    if sha256(destination) != EXPECTED_SHA256:
        raise SystemExit("Existing file has a different checksum; inspect it before replacing")
else:
    temporary = destination.with_suffix(".download")
    urllib.request.urlretrieve(SOURCE_URL, temporary)
    if sha256(temporary) != EXPECTED_SHA256:
        temporary.unlink()
        raise SystemExit("Downloaded file has a different checksum; source may have changed")
    temporary.replace(destination)

print(f"Verified UCI dataset: {destination.name} ({EXPECTED_SHA256})")
