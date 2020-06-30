# RCLC 2019 Baseline 

In this repository we include the code to execute the baseline model and evaluate it. The model is based on our project for the Rich Context Competition carried out in the last quarter of 2018 and begining of 2019. You can find the slides of explaining the project here: https://coleridgeinitiative.org/assets/docs/RCC/kaist.pptx


Our model is located in the folder project. There we included [DocumentQA ](https://github.com/allenai/document-qa), a MRQA model, and [Ultra-Fine Entity Typing](https://github.com/uwnlp/open_type), an entity typing model. We use both models in our system.


To run this code you need to create a conda environment and import requirements.txt. You can do so with: 

```
$ conda create -n new environment --file requirements.txt
```

Instructions to execute and evaluate our model can be found on project/RCLC.ipynb
