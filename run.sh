#!/usr/bin/env bash
# Автоматичне налаштування та запуск main.py.
# Використання: bash run.sh
set -e

cd "$(dirname "$0")"

say() { printf "\n\033[1;34m▸ %s\033[0m\n" "$*"; }
ok()  { printf "   \033[1;32m✓\033[0m %s\n" "$*"; }
warn(){ printf "\n\033[1;33m! %s\033[0m\n" "$*"; }
err() { printf "\n\033[1;31m✖ %s\033[0m\n" "$*" >&2; }

say "Перевіряю Java..."

# Спроба отримати реальну версію Java (ігноруємо macOS-заглушку)
JAVA_OUT=""
if command -v java >/dev/null 2>&1; then
  JAVA_OUT=$(java -version 2>&1 || true)
fi

JAVA_VER=""
if [[ "$JAVA_OUT" =~ version\ \"([0-9]+) ]]; then
  JAVA_VER="${BASH_REMATCH[1]}"
fi

if [ -z "$JAVA_VER" ] || [ "$JAVA_VER" -lt 11 ]; then
  warn "Робочу Java не знайдено (вивід був: ${JAVA_OUT:-порожньо})."

  # Спробуємо встановити OpenJDK 17 через Homebrew
  if ! command -v brew >/dev/null 2>&1; then
    err "Homebrew не встановлено. Встановіть з https://brew.sh, потім запустіть скрипт знову."
    exit 1
  fi

  echo "   Встановлюю openjdk@17 через Homebrew (це може зайняти кілька хвилин)..."
  brew install openjdk@17

  BREW_PREFIX=$(brew --prefix)
  export JAVA_HOME="$BREW_PREFIX/opt/openjdk@17"
  export PATH="$JAVA_HOME/bin:$PATH"

  # Для macOS corretto-style symlink вимагає sudo; натомість користуємося JAVA_HOME
  JAVA_OUT=$("$JAVA_HOME/bin/java" -version 2>&1 || true)
  if [[ "$JAVA_OUT" =~ version\ \"([0-9]+) ]]; then
    JAVA_VER="${BASH_REMATCH[1]}"
  fi
fi

if [ -z "$JAVA_VER" ] || [ "$JAVA_VER" -lt 11 ]; then
  err "Java >= 11 так і не з'явилася. Перевірте встановлення вручну: brew install openjdk@17"
  exit 1
fi
ok "Java $JAVA_VER"

say "Налаштовую venv..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ok "Створено .venv"
else
  ok ".venv вже існує"
fi

# shellcheck disable=SC1091
source .venv/bin/activate

say "Перевіряю PySpark..."
if ! python -c "import pyspark" >/dev/null 2>&1; then
  echo "   Встановлюю PySpark..."
  pip install --quiet --upgrade pip
  pip install --quiet pyspark
fi
ok "PySpark готовий"

say "Запускаю main.py..."
export SPARK_LOCAL_IP=127.0.0.1
export SPARK_LOCAL_HOSTNAME=localhost
# Якщо ми щойно встановили openjdk@17, переконаймося, що JAVA_HOME виставлено
if [ -z "${JAVA_HOME:-}" ] && command -v brew >/dev/null 2>&1; then
  if brew --prefix openjdk@17 >/dev/null 2>&1; then
    export JAVA_HOME="$(brew --prefix openjdk@17)"
    export PATH="$JAVA_HOME/bin:$PATH"
  fi
fi
python main.py
