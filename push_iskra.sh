#!/bin/bash

# Проверка, что архив есть
if [ ! -f "iskra_repo_final.zip" ]; then
  echo "Файл iskra_repo_final.zip не найден. Положи его в эту папку."
  exit 1
fi

# Распаковка
unzip -o iskra_repo_final.zip -d iskra_repo
cd iskra_repo || exit 1

# Инициализация и коммит
git init
git add .
git commit -m "Init: Искра v10"

# Настройка удаленного репозитория
echo "Вставь ссылку на свой GitHub-репозиторий (HTTPS):"
read -r repo_url

git remote add origin "$repo_url"
git branch -M main
git push -u origin main
