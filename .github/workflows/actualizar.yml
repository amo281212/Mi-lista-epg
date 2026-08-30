name: Actualizar EPG Automatizado

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Descargar repositorio
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Instalar dependencias necesarias
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 lxml urllib3

      - name: Ejecutar script Python
        run: python actualizar_epg.py

      - name: Guardar cambios en GitHub
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "EPG actualizada automáticamente"
          file_pattern: "epg_final.xml *.xml"
