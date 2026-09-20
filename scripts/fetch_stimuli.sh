#!/usr/bin/env bash
# Download the Ego4D Moment Queries clips this experiment uses.
#
# Requires an Ego4D licence and AWS credentials under the [ego4d] profile in
# ~/.aws/credentials. Those credentials EXPIRE -- if you get a 403 Forbidden,
# request fresh ones from https://ego4d-data.org/docs/start-here/ and rerun.
#
#   bash scripts/fetch_stimuli.sh [EGO4D_ROOT]     # default: ~/ego4d_data
set -euo pipefail

EGO4D_ROOT="${1:-$HOME/ego4d_data}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Stimuli come from two Ego4D downloads, because moments clips are capped at
# 480 s and one stimulus is longer than that (see README).
CLIP_UIDS=$(awk -F, 'NR>1 && $4=="clip_256ss" && $2!="" {printf "%s ", $2}' "$HERE/stimuli/videos.csv")
VIDEO_UIDS=$(awk -F, 'NR>1 && $4=="video_540ss" && $3!="" {printf "%s ", $3}' "$HERE/stimuli/videos.csv")

echo "Ego4D root : $EGO4D_ROOT"
echo "Main clips : $CLIP_UIDS"
echo "Full videos: $VIDEO_UIDS"
echo

ego4d --output_directory "$EGO4D_ROOT" --version v2 --aws_profile_name ego4d -y \
      --datasets clips_256ss --video_uids $CLIP_UIDS

ego4d --output_directory "$EGO4D_ROOT" --version v2 --aws_profile_name ego4d -y \
      --datasets video_540ss --video_uids $VIDEO_UIDS

echo
echo "Done. Now run:  python scripts/prepare_stimuli.py --ego4d-root $EGO4D_ROOT"
