#!/usr/bin/env bash
# Автоматичний захват 6 скриншотів термінала — по одному на кожен етап.
#
# Запуск: bash capture.sh
# Після запуску термінал одразу повернеться до prompt. У фоні піде серія
# знімків через `screencapture`. Перед кожним знімком з'явиться macOS-
# нотифікація й прозвучить звуковий сигнал; у вас буде 8 секунд, щоб
# прокрутити iTerm до потрібного етапу.

cd "$(dirname "$0")"
mkdir -p screenshots

notify() {
  osascript -e "display notification \"$2\" with title \"$1\"" >/dev/null 2>&1
  osascript -e 'beep 1' >/dev/null 2>&1
}

(
  # Коротка підготовча пауза
  sleep 2

  for entry in \
      "p1_input_dataframes:ETAP 1 — users/purchases/products" \
      "p2_cleaned_dataframes:ETAP 2 — очищені DataFrame-и" \
      "p3_category_totals:ETAP 3 — суми за категоріями" \
      "p4_category_totals_age_18_25:ETAP 4 — суми для 18-25" \
      "p5_category_share_18_25:ETAP 5 — частки %" \
      "p6_top3_categories_18_25:ETAP 6 — ТОП-3"
  do
    name="${entry%%:*}"
    label="${entry#*:}"
    notify "Scroll to: $label" "Знімок за 8 секунд. Прокрутіть термінал, щоб показати цей етап."
    sleep 8
    screencapture -x "screenshots/${name}.png"
    notify "Saved" "screenshots/${name}.png"
  done

  notify "Готово" "Усі 6 скриншотів збережено в screenshots/"
) >/dev/null 2>&1 &

disown

echo "Запущено у фоні. Дивіться системні нотифікації macOS."
