from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="pszemraj/long-t5-tglobal-base-16384-book-summary",
    local_dir="./models/long-t5-tglobal-base-16384-book-summary",
    local_dir_use_symlinks=False
)