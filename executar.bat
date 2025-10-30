@echo off
echo ========================================
echo    Compressor de Imagens ENEM
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não está instalado ou não está no PATH
    echo Por favor, instale o Python e tente novamente
    pause
    exit /b 1
)

REM Verificar se Pillow está instalado
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependência Pillow...
    pip install Pillow
    if errorlevel 1 (
        echo ERRO: Falha ao instalar Pillow
        pause
        exit /b 1
    )
)

echo Dependências verificadas com sucesso!
echo.

REM Executar o programa principal
echo Iniciando compressão de imagens...
echo.
python main.py

echo.
echo Processamento concluído!
pause