mkdir -p ../datasets/llm_augmented_el_benchmarks
mkdir -p ../datasets/llm_augmented_el_benchmarks/blink
mkdir -p ../datasets/llm_augmented_el_benchmarks/genre
mkdir -p ../datasets/llm_augmented_el_benchmarks/refined
mkdir -p ../datasets/llm_augmented_el_benchmarks/blink/llama-3-70b
mkdir -p ../datasets/llm_augmented_el_benchmarks/genre/llama-3-70b
mkdir -p ../datasets/llm_augmented_el_benchmarks/refined/llama-3-70b
mkdir -p ../datasets/llm_augmented_el_benchmarks/refined/gpt-3.5-turbo
mkdir -p ../datasets/llm_augmented_el_benchmarks/refined/glm-4

# Main experiments
python3 augment_blink_datasets_with_llm.py --llm_name llama-3-70b --join_strategy 4
python3 augment_genre_datasets_with_llm.py --llm_name llama-3-70b --join_strategy 4
python3 augment_refined_datasets_with_llm.py --llm_name llama-3-70b --join_strategy 4

# Ablation experiments
python3 augment_blink_datasets_with_llm.py --llm_name llama-3-70b --join_strategy 1
python3 augment_refined_datasets_with_llm.py --llm_name gpt-3.5-turbo --join_strategy 4
python3 augment_refined_datasets_with_llm.py --llm_name glm-4 --join_strategy 4
