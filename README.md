### **Estrutura do Trabalho**

Esta estrutura tem como objetivo processar arquivos DICOM, realizar a classificação de achados médicos utilizando um modelo pré-treinado, gerar relatórios estruturados no formato DICOM SR (Structured Report), e integrar essas informações com um PACS (Picture Archiving and Communication System) local, implementado com o Orthanc. A estrutura de arquivos é a seguinte:

```plaintext
📦 Projeto DICOM SR
├── data/                # Pasta para inserir os arquivos DICOM
├── generate_sr.py       # Script para gerar relatórios estruturados (DICOM SR)
├── process_dicom.py     # Script para processar os DICOM e classificar usando TorchXRayVision
├── upload_dicom.py      # Script para enviar arquivos DICOM ao PACS
└── README.md            # Este documento explicando o projeto
```

### **Descrição dos Arquivos**

1. **data/**: Esta pasta serve como repositório para os arquivos DICOM que serão processados e classificados. Todos os arquivos DICOM devem ser colocados nesta pasta antes da execução dos scripts.

2. **README.md**: Este documento fornece a descrição completa do projeto, instruções sobre como configurar o ambiente, e uma explicação das funções de cada script no processo.

3. **generate_sr.py**: Este script é responsável por criar relatórios estruturados DICOM (DICOM SR) com base nos resultados obtidos na classificação das imagens. Esses relatórios contêm informações sobre o paciente, estudo e série.

4. **process_dicom.py**: Script que processa os arquivos DICOM. Ele usa a biblioteca `TorchXRayVision` para ler e classificar as imagens médicas. Após a classificação, os resultados são armazenados para serem posteriormente integrados no relatório estruturado.

5. **upload_dicom.py**: Este script é responsável por enviar os arquivos DICOM e DICOM SR gerados para o servidor PACS Orthanc via API REST. Ele garante que tanto as imagens quanto os relatórios sejam devidamente integrados ao sistema de arquivamento.

---

### **Execução das Etapas**

1. **Configurar e rodar um PACs OrthanC, utilizando Docker**  
Executei o seguinte comando para baixar e iniciar o Orthanc:
```docker
docker run -p 8042:8042 -p 4242:4242 jodogne/orthanc-plugins
```
Onde:

8042: Porta para acessar a interface web.

4242: Porta para comunicação DICOM (envio de imagens).

Esse comando executa o Orthanc PACS com suporte a plugins, facilitando o processamento de DICOMs.

Verificar o Orthanc: Após o comando acima ser executado com sucesso, é só acessar através do navegador no endereço:
```
http://localhost:8042
```
O nome de usuário e senha padrão são ambos "orthanc".

2. Utilizar um script Python para enviar arquivos DICOM:
   
O script ```upload_dicom.py``` realiza o upload dos arquivos DICOM para o ambiente PACS.

3. Utilizando os mesmos arquivos DICOM, computar os resultados de classificação de achados utilizando o modelo pré-treinado e instruções encontradas na seção "Get Started"  do README do TorchXRayVision:

O script ```process_dicom.py``` realiza a classificação de todas os arquivos no ```data/dicoms``` e cria um arquivo .json chamado ```classification_results.json``` com todas as métricas.

4(Extra).Criar um DICOM SR (Structured Report) para cada arquivo DICOM com os resultados do modelo, e enviar os DICOM SR para o PACS local OrthanC. Note que o DICOM SR deve ser do paciente/estudo/série correta: 

O script ```generate_sr.py``` faz exatamente isso, cada arquivo DICOM já classificado tem o seu SR gerado e enviado ao PACS do Orthanc.

### Como Executar o Projeto

1. **Executando o PACS OrthanC**
   Primeiro, você precisa rodar o PACS OrthanC. Certifique-se de que o container está ativo e escutando na porta correta.

2. **Processando Arquivos DICOM**
   Com os arquivos DICOM dentro da pasta `data/`, execute o script `process_dicom.py` para classificar os achados com o TorchXRayVision.

   ```bash
   python3 process_dicom.py
   ```

3. **Gerando Relatórios Estruturados (DICOM SR)**
   Após o processamento, use o script `generate_sr.py` para criar os DICOM SR com base nos resultados do modelo.

   ```bash
   python3 generate_sr.py
   ```

4. **Enviando Arquivos DICOM para o PACS**
   Finalmente, use o script `upload_dicom.py` para fazer o upload dos arquivos DICOM para o PACS OrthanC.

   ```bash
   python3 upload_dicom.py
   ```

### Dificuldades Encontradas

Durante o desenvolvimento deste projeto, algumas dificuldades foram encontradas:

1. **Compatibilidade de DICOM SR:** A criação de Relatórios Estruturados (DICOM SR) envolveu entender as tags DICOM corretas para manter a consistência de paciente/estudo/série nos novos arquivos gerados, que ainda acho não estar 100% completo.

2. **Envio para o PACS:** Embora o OrthanC tenha uma API bem documentada, a integração e envio dos arquivos DICOM e DICOM SR envolveu garantir que o PACS estivesse configurado corretamente e que a comunicação estivesse fluindo, tendo que debbugar algumas vezes para verificação do upload.

3. **Configuração do Dockerfile:** Não ficou muito claro no texto de que forma seria configurada meu dockerfile, por via das dúvidas optei por não incluí-lo aqui no github, também tive problemas em minha máquina com o docker em si.
### O que Aprendi

Este PS foi uma excelente oportunidade para entender mais profundamente o padrão DICOM, especialmente no que diz respeito à criação e modificação de arquivos DICOM e como funcionar seu armazenamento. Trabalhar com um PACS como o OrthanC foi uma área totalmente diferente do que já havia trabalhado, apesar de algumas semelhanças no fluxo de aplicação das coisas, mas integrar isso a uma pipeline de classificação foi uma experiência desafiadora e trabalhosa.

---

Este README serve como guia para o uso do projeto. Sinta-se à vontade para explorar os scripts e adaptá-los conforme necessário.
