# LLM-Augmented Entity Linking

<p align="center">
    <a href="https://arxiv.org/abs/2407.04020"><img alt="Paper" src="https://img.shields.io/badge/📖-Paper-orange"></a>
    <a href="https://huggingface.co/THU-KEG/LLMAEL-ReFinED-FT"><img alt="Pretrained Models" src="https://img.shields.io/badge/🤗HuggingFace-Pretrained Models-green"></a>
    <a href="https://github.com/THU-KEG"><img src="https://img.shields.io/badge/THU-KEG_Group-blueviolet"></a>
</p>

Datasets, scripts, and fine-tuned model for the paper LLMAEL: Large Language Models are Good Context Augmenters for Entity Linking.

<p align="justify">

* 📖 Paper: [LLMAEL: Large Language Models are Good Context Augmenters for Entity Linking](https://arxiv.org/abs/2407.04020)

* Fine-tuned ReFinED model on 🤗HuggingFace: [LLMAEL-REFINED-FT](https://huggingface.co/THU-KEG/LLMAEL-ReFinED-FT)

</p>

We introduce <b>LLM</b>-<b>A</b>ugmented <b>E</b>ntity <b>L</b>inking (<b>LLMAEL</b>), a plug-and-play approach to enhance entity linking through LLM data augmentation. We leverage LLMs as knowledgeable context augmenters, generating mention-centered descriptions as additional input, while preserving traditional EL models for EL execution. Experiments on 6 standard datasets show that the vanilla LLMAEL outperforms baseline EL models in most cases, while the fine-tuned LLMAEL set the new state-of-the-art results across all 6 benchmarks. 


## Repository Content
This repository contains LLMAEL's testing and training datasets, LLM prompts, data fusion scripts, and the fine-tuned ReFinED model checkpoint.

For the `datasets` directory:
1. The `original_el_benchmarks` sub-directory stores the original EL benchmarks of 3 EL models [BLINK](https://github.com/facebookresearch/BLINK), [GENRE](https://github.com/facebookresearch/GENRE), and [ReFinED](https://github.com/amazon-science/ReFinED), downloaded from their respective github repositories. 
2. The  `llm_raw_augmentations` sub-directory contains raw context generated by backbone LLMs, specifically short entity descriptions based on the original mentions and contexts. These entries precisely match the content and order of their corresponding benchmarks in `original_el_benchmarks`.
3. The `llm_augmented_el_benchmarks` sub-directory stores the final LLM-augmented EL benchmarks, infusing data from `llm_raw_augmentations` into `original_el_benchmarks` (Data from this repository needs to be generated using augment_all_datasets.sh. See section "To Generate Testing and Training Data").


## Installation

``` bash
git clone https://github.com/THU-KEG/LLMAEL.git
cd LLMAEL
```


## To Generate Testing and Training Data

To generate the testing and training datasets used in our paper's main experiment and ablation studies, run the following commands:

``` bash
cd scripts
bash augment_all_datasets.sh
```

To generate datasets with other options, select and run the following python scripts:

``` bash
python augment_blink_datasets_with_llm.py
python augment_genre_datasets_with_llm.py
python augment_refined_datasets_with_llm.py
```

with your custom parameters `--llm_name`, `--join_strategy`, `--original_benchmarks_path`, `--llm_contexts_path`, `--output_path`.


## To Download our Fine-tuned ReFinED Model

Please download from our 🤗HuggingFace hub: [LLMAEL-REFINED-FT](https://huggingface.co/THU-KEG/LLMAEL-ReFinED-FT)


## To Reproduce our Results

1. Clone the official github repositories of our 3 selected EL models: [BLINK](https://github.com/facebookresearch/BLINK), [GENRE](https://github.com/facebookresearch/GENRE), and [ReFinED](https://github.com/amazon-science/ReFinED)
2. Find the official test script of each model, respectively
3. Change the test datasets to our augmented datasets from `llm_augmented_el_benchmarks`, and run the official test script. Our main experiments are conducted using the 6 augmented test sets synthesized under context-joining strategy 4. For the vanilla LLMAEL, we used BLINK's full cross-encoder model, GENRE's AIDA model without the candidate set, and ReFinED's AIDA model. For fine-tuned LLMAEL, we customly fine-tuned ReFinED's wikipedia model using Llama3-70-b augmented AIDA train dataset. 

Our results (accuracy) are as follows:
| Method | AIDA | MSNBC |  AQUA  | ACE04  | CWEB | WIKI | AVG |
|--------|:----:|:-----:|:------:|:------:|:----:|:----:|:---:|
| LLMAEL x BLINK |  81.94 | 86.56 | 85.16 | 86.01 | 69.17 | 81.14 | 81.61 |
| LLMAEL x GENRE |  88.27 | 85.67 | 85.14 | 85.21 | 70.67 | 82.95 | 82.99 |
| LLMAEL x ReFinED |  92.38 | 86.94 | 88.09 | 88.14 | 73.16 | 85.90 | 85.76 |
| LLMAEL x ReFinED (FT) |  92.34 | 88.79 | 89.06 | 88.14 | 75.07 | 86.62 | 86.67 |


We report

## Citation
```bibtex
@misc{xin2024llmael,
  title={LLMAEL: Large Language Models are Good Context Augmenters for Entity Linking},
  author={Xin, Amy and Qi, Yunjia and Yao, Zijun and Zhu, Fangwei and Zeng, Kaisheng and Bin, Xu and Hou, Lei and Li, Juanzi},
  journal={arXiv preprint arXiv:2407.04020},
  year={2024}
}
```