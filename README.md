# Compressor de Imagens ENEM

Esta aplicação Python comprime as imagens dos dados do ENEM de 2009 a 2023 usando a biblioteca Pillow.

## Funcionalidades

- Compressão automática de imagens PNG, JPEG, BMP, TIFF e WEBP
- Configurações personalizáveis através de arquivo JSON
- Suporte a redimensionamento de imagens
- Backup opcional dos arquivos originais
- Estatísticas detalhadas de compressão
- Log de processamento em arquivo e console

## Instalação

1. Certifique-se de ter Python 3.7+ instalado
2. Instale as dependências:
   ```bash
   pip install Pillow
   ```

## Uso

### Execução Básica
```bash
python main.py
```

### Configuração

Edite o arquivo `compression_config.json` para personalizar as configurações:

```json
{
  "quality": 85,              // Qualidade JPEG (1-100)
  "format": "JPEG",           // Formato de saída: JPEG, PNG, WEBP
  "max_width": null,          // Largura máxima (null = sem limite)
  "max_height": null,         // Altura máxima (null = sem limite)
  "optimize": true,           // Otimizar arquivo
  "progressive": true,        // JPEG progressivo
  "backup_original": false,   // Fazer backup do original
  "output_suffix": "_compressed", // Sufixo para arquivos comprimidos
  "delete_original_on_format_change": true // Excluir original quando formato muda
}
```

### Parâmetros de Configuração

- **quality**: Qualidade da compressão JPEG (1-100, onde 100 é a melhor qualidade)
- **format**: Formato de saída da imagem (JPEG, PNG, WEBP)
- **max_width/max_height**: Redimensionamento máximo (null para manter tamanho original)
- **optimize**: Ativar otimização adicional
- **progressive**: Para JPEG, criar imagem progressiva
- **backup_original**: Se true, mantém arquivo original com extensão .bak
- **output_suffix**: Sufixo adicionado ao nome do arquivo (se backup_original = true)
- **delete_original_on_format_change**: Se true, exclui arquivo original quando há mudança de formato (ex: PNG → JPEG)

## Estrutura de Dados

A aplicação espera a seguinte estrutura de diretórios:

```
assets/
└── enem_data/
    ├── enem-2009/
    │   ├── 102-images/
    │   ├── 106-images/
    │   └── ...
    ├── enem-2010/
    └── ...
```

Cada diretório `*-images` pode conter:
- `alt_img_*.png`
- `context_img_*.png`
- Outras imagens nos formatos suportados

## Saída

- **compression.log**: Log detalhado do processamento
- **Estatísticas**: Resumo da compressão no console
- **Arquivos comprimidos**: Na mesma localização dos originais (ou com sufixo se configurado)

## Exemplo de Uso Avançado

Para comprimir apenas com qualidade 60 e redimensionar para máximo 800px de largura:

```json
{
  "quality": 60,
  "format": "JPEG",
  "max_width": 800,
  "max_height": null,
  "optimize": true,
  "progressive": true,
  "backup_original": true,
  "output_suffix": "_small"
}
```

## Logs e Monitoramento

A aplicação gera:
- Log em tempo real no console
- Arquivo `compression.log` com histórico completo
- Estatísticas de compressão ao final do processamento

## Tratamento de Erros

- Arquivos não encontrados são ignorados com aviso
- Erros de compressão são logados e a execução continua
- Estatísticas incluem contagem de erros

## Performance

- Processa múltiplos formatos de imagem
- Otimização automática baseada no formato
- Redimensionamento eficiente com algoritmo Lanczos
- Processamento sequencial para estabilidade