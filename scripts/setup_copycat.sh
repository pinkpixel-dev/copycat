#!/usr/bin/env bash
# Interactive environment setup for CopyCat.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_VENV="${ROOT_DIR}/.venv"

BANNER_LINES=(
"  ██████╗ ██████╗ ██████╗ ██╗   ██╗ ██████╗ █████╗ ████████╗"
" ██╔════╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗╚══██╔══╝"
" ██║     ██║   ██║██████╔╝ ╚████╔╝ ██║     ███████║   ██║   "
" ██║     ██║   ██║██╔═══╝   ╚██╔╝  ██║     ██╔══██║   ██║   "
" ╚██████╗╚██████╔╝██║        ██║   ╚██████╗██║  ██║   ██║   "
"  ╚═════╝ ╚═════╝ ╚═╝        ╚═╝    ╚═════╝╚═╝  ╚═╝   ╚═╝   "
""  
"                    🐾 Linux Clipboard Superpower 🐾"
)
BANNER_COLORS=(31 33 32 36 34 35)

print_banner() {
  printf '\n'
  for i in "${!BANNER_LINES[@]}"; do
    local color="${BANNER_COLORS[$((i % ${#BANNER_COLORS[@]}))]}"
    if [[ "${BANNER_LINES[$i]}" == "" ]]; then
      printf '\n'
    else
      printf '\e[1;%sm%s\e[0m\n' "$color" "${BANNER_LINES[$i]}"
    fi
  done
  printf '\n'
}

require_cmd() {
  local cmd="$1"
  local msg="${2:-Please install it and retry.}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '\e[31mMissing required command: %s\e[0m\n%s\n' "$cmd" "$msg"
    exit 1
  fi
}

run_pip_setup() {
  local venv_dir="$1"
  require_cmd python3 "Python 3.9+ is required."
  python3 -m venv "$venv_dir"
  "${venv_dir}/bin/python" -m pip install --upgrade pip
  if [ -s "${ROOT_DIR}/requirements.txt" ]; then
    "${venv_dir}/bin/pip" install -r "${ROOT_DIR}/requirements.txt"
  fi
  "${venv_dir}/bin/pip" install "${ROOT_DIR}"
  printf '\n\e[32mCopyCat is installed in %s\e[0m\n' "$venv_dir"
  printf 'Activate with: source "%s/bin/activate"\n' "$venv_dir"
}

run_uv_setup() {
  local venv_dir="$1"
  require_cmd uv "uv is required for this option. Install from https://github.com/astral-sh/uv"
  uv venv "$venv_dir"
  "${venv_dir}/bin/python" -m pip install --upgrade pip
  if [ -s "${ROOT_DIR}/requirements.txt" ]; then
    uv pip install -r "${ROOT_DIR}/requirements.txt" --python "${venv_dir}/bin/python"
  fi
  uv pip install "${ROOT_DIR}" --python "${venv_dir}/bin/python"
  printf '\n\e[32mCopyCat is installed in %s (uv environment)\e[0m\n' "$venv_dir"
  printf 'Activate with: source "%s/bin/activate"\n' "$venv_dir"
}

run_conda_setup() {
  require_cmd conda "Conda is required for this option."
  read -r -p "Environment name [copycat]: " env_name
  env_name="${env_name:-copycat}"
  conda env create --force -f "${ROOT_DIR}/environment.yml" -n "$env_name"
  printf "\n\e[32mCopyCat conda environment '%s' created.\e[0m\n" "$env_name"
  printf 'Activate with: conda activate %s\n' "$env_name"
}

print_banner
printf 'Welcome to the CopyCat environment wizard!\n\n'
printf 'Where should the virtual environment live?\n'
printf 'Press Enter to use the default [%s]\n' "$DEFAULT_VENV"
read -r -p "Virtual environment path: " venv_path
venv_path="${venv_path:-$DEFAULT_VENV}"

cat <<'MENU'
Choose an installer:
  [1] pip (uses python -m venv)
  [2] uv  (lightning-fast virtualenv)
  [3] conda (environment.yml)
MENU

read -r -p "Selection [1/2/3]: " choice
case "$choice" in
  1|"")
    run_pip_setup "$venv_path"
    ;;
  2)
    run_uv_setup "$venv_path"
    ;;
  3)
    run_conda_setup
    ;;
  *)
    printf '\e[31mUnknown selection: %s\e[0m\n' "$choice"
    exit 1
    ;;
esac

printf '\nHappy hacking with CopyCat! 🐾\n'
